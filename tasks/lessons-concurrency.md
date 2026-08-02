# Lessons

## 并发原语的取消语义:必须按「生产里真实的取消来源」验证,而不是按库文档的措辞

**发生了什么**：在 review 汇总里推荐用 `anyio.to_thread.run_sync(..., limiter=limiter)`
「一行」解决 GPU permit 提前放行的问题，依据是 anyio 文档里 `abandon_on_cancel=False` 那句
"ignore cancellations in the host task until the operation has completed in the worker thread"，
并用 `anyio` 的 `cancel_scope.cancel()` 做了实验，实验通过。

**为什么错**：`abandon_on_cancel` 与 `limiter=` 只对 **anyio 自己的 cancel scope** 生效。
生产环境里的取消全部来自裸 `asyncio.Task.cancel()`（Starlette 客户端断连、uvicorn 关机、
外层 `asyncio.timeout`）。换成裸取消后，推荐方案与原 bug 表现完全一致（limit=1 下峰值并发 2）。

**规则**：
1. 验证并发/取消行为时，**取消必须由生产里真实的那个机制发出**。用库自带的取消原语做实验，
   验证的是库内部一致性，不是我的代码在这个框架下的行为。asyncio 上跑的 FastAPI，
   就用 `asyncio.Task.cancel()` 测。
2. 库文档说的「取消时会…」永远要追问「谁发出的取消」。跨抽象层（asyncio task ↔ anyio scope
   ↔ 线程池 work item）的取消不会自动贯通。
3. 只要有一个东西的生命周期必须严格等于「某个不可中断的操作」的生命周期，
   就让**执行该操作的那一方**负责释放（此处：worker 线程内 `call_soon_threadsafe` 归还），
   不要在 await 它的协程里用 `finally` 释放 —— `finally` 绑定的是 await 的结束，不是操作的结束。
4. 先写会失败的回归测试，再写实现。本次正是回归测试当场否掉了我自己的设计，
   否则这个 bug 会带着「已修复」的标签合进去。

## 说「预存失败」之前先确认是不是自己环境缺依赖

review 报告称有 4 个 pydub 相关的预存失败、并称 conda `code` env「没有 pytest/numpy/torch」。
实际 `code` env 有 pytest 9.1.1 和 numpy；缺的只是 `pydub` 和 `aiofiles`——
而这两个都写在 `requirements.txt` 里。补装后基线 84/84 全绿，那 4 个失败根本不存在。

**规则**：把测试失败归因为「预存问题」前，先对照 `requirements.txt` 检查缺的是不是声明依赖。
「基线也失败」只有在环境本身正确时才是有效论证。

## 弱化的断言可能在修一个真实的抖动,不要想当然判它是偷懒

review 把 `assert gen_time > 0` 改成 `>= 0` 判为「弱化成恒真断言」。实际根因是：
mock 生成在亚毫秒内返回，而响应头用 `:.3f` 格式化，满负载时会被舍成 `0.000`——
实测全量连跑 5 轮有 2 轮因此失败。原作者是在修一个真实的 flake。

**规则**：看到被放宽的断言，先问「收紧后它在什么条件下会失败」。正确做法是让断言表达
**在该测试条件下真正成立的语义**（此处：非负 + 有意义的上界），而不是在「恒真」和「抖动」之间二选一。
