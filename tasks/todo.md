# Frontend 切换动效优化

**方案**：零依赖（Tailwind keyframes + 一个可复用 crossfade hook），bundle +0KB
**范围**：主 tab + 子 tab + API 抽屉 + 全局 transition 收敛

## 背景：为什么现在「生硬」

`App.tsx:39` 的 `<div role="tabpanel" className="animate-fadeIn">` 在切 tab 时**不会 remount**
（React 复用同一 DOM 节点，只替换 children），而 CSS `animation` 只在挂载时播一次。
所以 `animate-fadeIn` **只在首屏生效**，之后每次切 tab 都是瞬间硬替换 —— 这不是动效差，是没动效。

## 已核实的外部依赖事实（不猜 API）

| 事实 | 验证方式 | 结果 |
|---|---|---|
| React 19.2.4 是否有 `<ViewTransition>` | grep `node_modules/react/cjs/react.production.js` | **无**，仅 experimental channel → 排除该方案 |
| Tailwind v4 `translate-x` 与 `-translate-y-1/2` 能否共存 | 读本项目 `dist/assets/*.css` 实际产物 | 能：`--tw-translate-x/y` 独立变量合成 `translate:` 简写 |
| v4 `transition-transform` 是否覆盖 CSS `translate` 属性 | grep `node_modules/tailwindcss/dist/lib.js` | 覆盖：`transition-property: transform, translate, scale, rotate` |
| `motion` 包真实版本 | `npm view motion version` | 12.43.0（本次未采用） |

## 任务

### 新增
- [ ] `src/config/motion.ts` — 时长/曲线单一来源 + `prefersReducedMotion()`
- [ ] `src/hooks/useCrossfade.ts` — 两阶段状态机（leaving → 换内容 → entering）
      时序由 CSS 拥有，靠 `animationend` 推进，JS 不重复声明时长（避免漂移）

### 修改
- [ ] `tailwind.config.js` — 加 `tabIn`/`tabOut` keyframes；重调 `fadeIn`/`slideUp`/`slideInRight`
      时长曲线（入场 220ms ease-out-expo，离场 120ms 更快更短 → 不拖沓）
- [ ] `src/styles/globals.css` — 收敛全局 `transition-all`；加 `prefers-reduced-motion` 块；
      加 `--ease-*` / `--dur-*` CSS 变量
- [ ] `src/App.tsx` — 接 `useCrossfade`，内容按 `rendered`（滞后一帧）渲染，nav 仍按 `activeTab` 立即响应
- [ ] `src/components/layout/TabNavigation.tsx` — 滑动指示器（ref 测量 + ResizeObserver 应对字体加载/i18n 改词宽）
- [ ] `src/components/ui/ApiDocsPanel.tsx` — `right` → `translate-x`；backdrop 淡入淡出；sub-tab 加 key
- [ ] `src/components/ui/ApiDocsToggle.tsx` — `right-[600px]` → `translate-x`；改用 `cn()` 让 `hidden`/`flex` 冲突确定性解析
- [ ] `src/components/tabs/VoiceClone/index.tsx` — upload/record 子 tab 复用同一 hook
- [ ] `.prettierrc` — 项目缺失（CLAUDE.md 常驻要求），与动效无关，单独标注

### 验证
- [ ] `npm run build`（tsc -b && vite build）通过
- [ ] `npm run lint` 无新增错误
- [ ] grep dist CSS 证明 Tailwind 真的产出了新 keyframes / 工具类（防止类名拼错被 purge 静默丢弃）

## 明确不做（避免引入 bug）

- **子元素 stagger**：`AudioPlayer` 自带 `animate-slideUp`，且 audio 状态在 `AppContext`
  里按 tab 持久化 —— 切回该 tab 时它会渲染，再叠 stagger 会与它自己的 `animation` 简写冲突。
  它本来也不在根因列表里。
- **容器高度锁定动画**：内容可能在过渡中变高（图片/表单），height lock 有真实 bug 面。
  改用 `min-h-[60vh]` + wait-mode crossfade（高度变化发生在 opacity 0 时，不可见）。

## Review

（实施后填写）

---

# Reference Audio 视觉修复 + dev-only API key 获取

**方案**：去掉 cyan 左边框套路、用项目自带播放器替换原生 `<audio controls>`、新增 opt-in 的 dev 端点让前端一键取 key
**范围**：`AudioRecorder` / `AudioUpload` / `AudioPlayer` / `ApiDocsPanel` / `ApiKeyConfig` + 后端 `dev.py`

## 已核实的外部依赖事实（不猜 API）

| 事实 | 验证方式 | 结果 |
|---|---|---|
| `settings.env` 在真实部署里是什么 | 读 `config.py:71` + grep `.env` / `docker-compose.yml` 的 environment 块 | **默认 `development`，且两处都没设 `ENV`** → 只按 env 判断等于不设防 |
| CORS 默认值 | 读 `app/main.py:125` | `allow_origins=["*"]` → 未鉴权 GET 可被任意站点跨域读取 |
| `request.client.host` 能否用于 loopback 判断 | Docker 端口发布 NAT + starlette `TestClient` 默认 `client=("testclient",50000)` | **不能**：Docker 下看到 bridge 网关；`ip_address("testclient")` 抛 `ValueError`；且挡不住浏览器 drive-by |
| `ipaddress` 对 IPv4-mapped 的判定 | 实际执行 | `ip_address('::ffff:127.0.0.1').is_loopback` 为 `False` → 必须 unwrap `.ipv4_mapped` |
| `Button` 的 loading 文案 | 读 `ui/Button.tsx` | `loadingText` 缺省是 `'Generating...'` → 必须显式传 |
| 仓库里还有几个原生播放器 | `grep -rn "<audio" src/` | 恰好 2 个（另一个是 `AudioPlayer` 内部隐藏元素） |

## 任务

### 新增
- [x] `src/hooks/useAudioPlayback.ts` — 播放逻辑抽取；`autoPlay` 只 gate `play()`；`onLoad` 移到 ref 出 deps
- [x] `src/components/audio/AudioPlayerControls.tsx` — 控件行；`size` 用数据表非 boolean；隐藏 `<audio>` 放 fragment 内、flex 行外（否则 `gap-md` 多出 16px 幽灵间距）
- [x] `src/components/audio/AudioPreview.tsx` — 无 autoplay / 无 metrics / 无 waveform / 无自带外框
- [x] `app/routers/dev.py` — `GET /api/v1/dev/api-key`，三重 404 gate + 掩码 WARNING 日志
- [x] `tests/unit/test_dev_api_key.py`

### 修改
- [x] `AudioRecorder.tsx` — 去掉 cyan 左边框与渐变外框；原生播放器换 `AudioPreview`
- [x] `AudioUpload.tsx` — 原生播放器换 `AudioPreview`
- [x] `AudioPlayer.tsx` — 改为 hook + Controls 组合，对外 props 不变
- [x] `ApiDocsPanel.tsx` — 4 处重复 callout 收敛为局部 `renderDescription`（该文件已有 `renderX` 家族）
- [x] `globals.css` — 删掉只在 Chrome 生效的 `::-webkit-media-controls-panel`
- [x] `app/config.py` — `expose_api_key`（默认 False，真正承重的那道闸）
- [x] `app/models/schemas.py` — `DevApiKeyResponse`
- [x] `app/main.py` — 条件注册 + 开机 WARNING
- [x] `ApiKeyConfig.tsx` — 获取按钮；顺手修 3 处绕过 `t()` 的硬编码英文 + 删死 import
- [x] i18n / `config/api.ts` / `types/api.ts` / `services/api.ts` / `.env.example` / README

### 验证
- [x] `npm run build`（exit 0）、`tsc -b`（exit 0）、`npm run lint`（44 → 41，只减不增）
- [x] `pytest tests/unit/` 54 passed（含新增 18）
- [x] curl 矩阵：flag 关→404、evil Origin→404、production→404、空 `API_KEYS`→`auth_required:false`
- [x] 浏览器实测（Playwright + system Chrome）：截图确认三处视觉、
      `native <audio controls>` 计数为 0、点 Fetch 后输入框与 localStorage 都变成服务器真实 key
- [ ] 未做：`tests/unit/test_audio_preprocessing.py` / `test_audio_validation.py` 无法收集
      （本机缺 `aiofiles`，阻塞点在未改动的 `app/utils/audio.py:11`，与本次改动无关）
- [ ] 未做：真实后端启动验证（本机缺 `qwen_tts`/`torch`，改用 stub 挂载真实 `dev` router + 打包产物代替）

## 明确不做（已核实存在，但不在本次范围）

- **`AudioWaveform` 可能让声音彻底消失**：`__audioSourceNode` 缓存在 element 上，但 unmount 时 `close()` 了
  AudioContext；remount 后新 context 复用旧 node 抛 `InvalidAccessError` 被 catch 吞掉，element 就挂在已关闭的
  context 上 → 没波形也没声音。`AudioPreview` 不带 waveform 天然免疫，生成播放器仍有此隐患。
- **WebM `duration` 可能是 `Infinity`**：`useAudioRecorder` 产出 `audio/webm`，进度条可能不走。原生控件同样有这问题，
  不算回归，但自定义进度条更显眼。需先在 Chrome/Safari 实测再改。
- **触摸拖拽**：播放器是 mouse-only，两个预览位在移动端失去拖拽（点击定位仍可用）。改 pointer events 会同时
  影响现存 3 个播放器，单独一个 commit。
- **`DEFAULT_API_KEY = 'your-api-key-1'`**：本次功能让它过时了，但改动会影响首次运行行为。

## Review

### 实施结果

三项诉求都已落地并有实测证据（截图 + 断言），不是"看起来对"：

1. **左边框**：5 处 `border-l-[3px] border-accent-cyan` 全部清除，`grep` 为空。录音提示面板的
   青色边框 + 渐变底也一并换成 `bg-bg-surface + border-border-subtle`，内层引用块改为完整
   `border-border-subtle`（保留层级，去掉套路）。青色只留在 `READ THIS TEXT ALOUD` 小标签上。
   ApiDocsPanel 那 4 处复制粘贴收敛成局部 `renderDescription`，顺带修掉了没有左边框后
   就没意义的 `rounded-r-md`。
2. **播放器**：原生 `<audio controls>` 归零。抽出 `useAudioPlayback` + `AudioPlayerControls`
   + `AudioPreview`，`AudioPlayer` 对外 props 完全不变，现存 3 个调用点无需改动。
3. **token**：`EXPOSE_API_KEY`（默认 false）+ `GET /api/v1/dev/api-key`，前端多一个
   "从服务器获取"按钮。浏览器实测：输入框从 `your-api-key-1` 变成服务器真实 key，
   并同步写入 localStorage（一次点击即生效，不用再点保存）。

### 过程中发现并修掉的既有 bug（不在原计划内）

**生成音频播放器的时间/进度条从来没动过。** 实测：element 的 `currentTime` 从 0.19→1→2、
`readyState` 4、`duration` 2，但界面一直显示 `0:00 / 0:00`，进度条宽度恒为 0。

根因：`AudioPlayer` 在 hooks 之后有 `if (!audioUrl) return null`。首帧 `audioUrl` 为 null，
`<audio>` 没渲染，监听 effect 撞上 `if (!audio) return` 什么都没绑；而它的依赖是 `[isDragging]`,
`audioUrl` 后来变成有值时**不会重跑**，于是监听器整个会话都没绑上。

原代码结构与依赖数组完全一致 —— 这是 main 上就存在的 bug，不是本次重构引入的。
`AudioPreview` 天然不受影响（它只在已有 URL 时才挂载）。

修法：监听 effect 依赖加上 `audioUrl`，并在绑定后用 `readyState >= 1` 兜底补一次状态
（元数据可能在 effect 跑之前就到了，那些事件不会再触发第二次），另外补 `durationchange`。
修完实测 `0:00/0:02 → 0:01/0:02`，进度条中段 50.4%。

### 诚实记录的偏差

- **eslint `react-hooks/refs` 误报**：`ref={playback.progressRef}` 被判成"render 期间读 ref"，
  连 `playback.handleMouseDown`（一个函数）也被报。该规则无法区分"转发 ref 对象"和"读 .current"。
  改为在组件顶部一次性解构即可消除，无需 disable 注释。lint 总数 44 → 41，diff 显示只减不增。
- **本机跑不了真实后端**：缺 `qwen_tts`/`torch`/`aiofiles` 等。改用 stub 挂载**真实**的
  `app.routers.dev` + 打包好的 `dist/`，同源真 HTTP 验证，只跳过模型推理。
- **`code` conda env 原本没有 pytest/numpy**，已装（两者都是本仓库声明的依赖）。
- 工作区里有**他人未提交的 crossfade 改动**（`useCrossfade.ts`、`role="tab"`、`.prettierrc` 等），
  全部用精确匹配编辑叠加，未覆盖任何一处。会话开始时给我的 git status 快照是过时的。
