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
