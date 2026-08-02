# concurrent-requests 分支合并前修复

分支：`feature/concurrent-requests`（基于 review 的 6 个 blocker + 部分非阻塞项）

## 依赖版本核实（已完成，勿凭记忆改动）

conda `code` env / Python 3.12.0：`anyio 4.13.0`、`starlette 0.50.0`、`fastapi 0.124.4`、
`sse-starlette 3.3.4`、`pytest 9.1.1`、`numpy 2.5.1`。缺 `pydub`、`torch`
（→ `tests/unit/test_audio_preprocessing.py` 4 个失败为预存，`main` 上同样复现）。

实证结论（`anyio 4.13.0`）：

| 事实 | 验证结果 |
|---|---|
| `to_thread.run_sync(..., abandon_on_cancel=False)`（默认） | host task 被取消时，await 不返回，直到线程真正结束 |
| 取消场景下 `finally: limiter.release()` 时机 | 延后到线程结束，`borrowed` 全程保持 1 → 峰值并发 = 1 |
| `fail_after` 包裹 `limiter.acquire()` 超时 | 抛内置 `TimeoutError`（3.11+ 即 `asyncio.TimeoutError`），不漏 token |
| `CapacityLimiter.statistics()` | 提供 `borrowed_tokens` / `total_tokens` / `tasks_waiting` |
| 同一 task 嵌套 `acquire()` | `RuntimeError` —— `run_inference` 禁止嵌套，只能串行 |
| 现有 `asyncio.Semaphore` 实现 | limit=1 下取消时实测峰值并发 = 2（bug 复现） |

## 修复项（按依赖顺序）

- [ ] **A. finding 8 — 测试探不到新代码 + fail-open**
  - [ ] `tests/conftest.py` `api_client`：改为 `with TestClient(app) as client: yield client`，
        让 lifespan 真正执行（实测 starlette 0.50 下不加 `with` 执行 0 次）
  - [ ] `inference.py`：去掉「未初始化就裸跑、无并发上限」的 fail-open 分支，
        改为惰性创建 limiter（仍按配置封顶）+ warning，安全不变且不硬失败
  - [ ] 更新 `test_fallback_without_init`：断言新的惰性行为而非 fail-open
- [ ] **B. finding 1 — 503 被改写成 500**
  - [ ] `custom_voice.py:162` / `:227`、`voice_design.py:91` / `:155` 补 `except HTTPException: raise`
        （`base.py` 全部 6 处与两个 `/batch` 已有护栏，不动）
  - [ ] 回归测试：断言队列满时 `/generate` 与 `/batch` 都返回 503
- [ ] **C. finding 13 — 新配置缺校验**
  - [ ] `max_concurrent_inferences` 加 `ge=1`（`0` 会构造出永久锁死且健康检查全绿的服务器）
  - [ ] 超时项加 `gt=0`（`0` 会让完全空闲的服务器 100% 返回 503）
- [ ] **D. findings 2 / 4 / 7 / 15 — inference.py 基于 anyio 重写**
  - [ ] 用 `anyio.CapacityLimiter` + `anyio.to_thread.run_sync` 替换
        `asyncio.Semaphore` + 自建 `ThreadPoolExecutor(max_workers=2)`
        → 同时解决：取消时提前放行 permit（2）、硬编码 2 与配置不对账（7）、
          非 daemon 线程导致的进程退出挂起（15）
  - [ ] 超时只覆盖排队（`fail_after` + 手动 `acquire`），执行阶段不设 deadline；
        原因：CPython 无法抢占运行中的原生调用，给执行加 deadline 只会「付满 GPU 时间后再返回 503」
  - [ ] 配置项按真实语义改名为 `inference_queue_timeout_seconds`（未发布，改名无成本）
  - [ ] `run_inference` 默认从 settings 读超时 → 删掉 15 个调用点重复的 `timeout=` kwarg
        （消除「第 16 个调用点忘写就静默忽略运维配置」的漂移风险）
  - [ ] `functools.partial` 取代 lambda → 移除全仓唯一的 `# type: ignore`
  - [ ] 补可观测性：503 计数 + 日志、`borrowed`/`tasks_waiting`、`Retry-After` 头
  - [ ] 新增 `/health/inference` 暴露上述指标，让「唯一 permit 被卡死」可被发现
- [ ] **E. finding 3 — 缓存击穿回归（相对 main 的性能倒退）**
  - [ ] 新增 `app/utils/keyed_lock.py`：按 key 的 `asyncio.Lock` + 引用计数自动回收（可复用单元）
  - [ ] 把 base.py 两处重复 30 行的 get/compute/put 提取为
        `get_or_create_voice_prompt()`，内部双重检查加锁 → 同时消除重复与击穿
  - [ ] 回归测试：N 个相同并发请求只触发 1 次抽取

## 验证

- [x] `pytest` 在 conda `code` env 跑（补装了声明依赖 `aiofiles`、`pydub`）
- [x] 新增回归测试先在旧实现上确认失败（变异测试）
- [x] `tests/integration/` `tests/e2e/` 通过 conftest 打桩 `qwen_tts` 解锁，从 35 error → 35 passed
- [ ] `tests/real_model/` 仍无法本地验证（需真实模型权重与 GPU）

## Review

全部 6 个 blocker 与部分非阻塞项已修，全量 140 passed，连跑 8 轮 0 失败。

### 测试结果对比

| 范围 | 改动前 | 改动后 |
|---|---|---|
| `tests/unit/` | 84 passed | 105 passed |
| `tests/integration/` + `tests/e2e/` | 35 error（缺 `qwen_tts`，无法收集） | 35 passed |
| 合计 | 84 passed / 35 error | **140 passed** |

review 报告里「4 个 pydub 预存失败」并不存在 —— 那是 review 环境缺 `pydub` 造成的，
装上后基线全绿（84/84）。

### 关键修正：我在 review 汇总里给出的技术依据是错的

原建议「改用 `anyio.CapacityLimiter` + `anyio.to_thread.run_sync` 一次解决 findings 2/7/关机挂起」
**不成立**。回归测试直接把它否掉了：

    limit=1，裸 asyncio.Task.cancel() 下的峰值并发
      在 coroutine 的 finally 里归还 permit           -> 2  (BUG)
      anyio.to_thread.run_sync(..., limiter=limiter)  -> 2  (BUG)
      由 worker 线程归还 permit                        -> 1  (正确)

`abandon_on_cancel=False` 和 `limiter=` 只延后 **anyio 自己的 cancel scope**，挡不住裸
`asyncio.Task.cancel()` —— 而 Starlette 断连、uvicorn 关机、外层 `asyncio.timeout` 全都是后者，
即生产环境唯一会发生的取消方式。最终实现改为 `acquire_on_behalf_of(opaque_token)` +
在 worker 线程内经 `call_soon_threadsafe` 归还，permit 生命周期严格等于推理生命周期。

同样需要修正的一处夸大：关机挂起并没有被「消除」。实测 3s 推理在关机时在飞，
原实现 loop 于 0.20s 关闭、进程到 3.00s 才退出（2.8s 在 atexit 里，框架不可见）；
新实现两者同在 3.02s。运行中的原生调用无法中断，这段时间省不掉，
改动只是把它移进 uvicorn graceful-shutdown 能观测和约束的阶段。

### 有意未做（非阻塞，留作后续）

- finding 9：`X-Generation-Time` / `X-RTF` 仍含排队时间（需把 `tracker.start()` 拆到取到 permit 之后）
- finding 11：`-stream` 端点仍在拿到完整音频后才建 `EventSourceResponse`，TTFB 未改善
  （已在 CHANGELOG 里改掉原来「SSE streams no longer block」的错误表述）
- finding 5：SSE 帧双重包装（`streaming.py` 本 PR 未动），标准客户端拿不到 event 类型 ——
  最严重的既有缺陷，建议单独立 issue
- findings 6 / 10 / 12 / 14：模型加载在信号量外、队列深度无上限、`/clone` 两阶段 FIFO 尾部排队、
  batch `texts` 无 `max_length`

### 顺带修掉的既有测试问题

- `tests/unit/test_inference.py` 缺 `@pytest.mark.unit`（`pytest -m unit` 原本收集 0/10，现 16/16）
- 两处 mock 测试里的 `rtf > 0` / `gen_time > 0` 是**真实抖动源**（mock 亚毫秒返回 + 表头 `:.3f`
  格式化 → 满负载下舍成 `0.000`，实测 5 轮中 2 轮失败）。这正是原作者当初弱化断言的原因，
  review 判它为「无意义的恒真断言」时漏了这层背景。已改为「非负 + 有意义的上界」，
  上界才是能抓住 finding 9 排队污染的那一半；`tests/real_model/` 的 `> 0` 保持不动。
