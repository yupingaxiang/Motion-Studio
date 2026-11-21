# 常见问题与排查

## 渲染问题

### Puppeteer EPERM: mkdtemp 权限不足

**症状**：`render` 或 `render-scene-preview` 报错：
```
Error: EPERM: operation not permitted, mkdtemp 'C:\Users\...\Temp\puppeteer_dev_chrome_profile-XXXXXX'
```

**原因**：Remotion 通过 Puppeteer 启动 headless Chrome 渲染帧，Chrome 需在临时目录创建 profile，但系统 Temp 目录权限不足。

**解决**：CLI 已自动设置 `TEMP`/`TMP`/`TMPDIR` 到项目 `.tmp` 目录。若仍失败，手动设置：
```powershell
$env:TEMP = "D:\Motion Studio\.tmp"
$env:TMP = "D:\Motion Studio\.tmp"
```

### esbuild build script 被忽略

**症状**：pnpm install 后提示 `[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: esbuild`。

**解决**：package.json 已配置 `"pnpm": {"onlyBuiltDependencies": ["esbuild"]}`。若 esbuild 二进制仍缺失：
```bash
cd remotion
node <pnpm路径> rebuild esbuild
```

### 渲染速度慢

首次渲染需编译 webpack bundle（约 30-60 秒）。后续渲染会复用缓存（`.remotion` 目录），快很多。`--concurrency=1` 最稳定。

### Remotion CLI 路径

入口是 `node_modules/@remotion/cli/remotion-cli.js`（不是 cli.mjs）。CLI 脚本已正确配置。

## 编码问题

### JSON 文件 BOM 导致解析失败

**症状**：`Unexpected UTF-8 BOM (decode using utf-8-sig)`。

**原因**：PowerShell `Out-File -Encoding utf8` 写入 BOM。

**解决**：后端读取统一用 `encoding="utf-8-sig"`（已修复）。写文件用 `write` 工具或 Python `json.dump` 而非 PowerShell。

### 控制台中文乱码

PowerShell 默认编码非 UTF-8，CLI 输出的中文可能乱码。不影响功能。设置：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Node / pnpm 环境

项目使用 DSH 捆绑的 Node v24 + pnpm 11，路径：
- Node: `C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe`
- pnpm: `C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\bin\pnpm.mjs`

系统 PATH 中的 Node v12 过旧，不可用。

## 数据冲突

### Codex 覆盖已确认分镜

**症状**：`publish-recommendations` 报 `PermissionError: 分镜 SX 已确认（APPROVED），用户未要求重新选择`。

**原因**：该分镜已被用户 APPROVED 并锁定。Codex 不可静默覆盖。

**解决**：用户需在 Web 工作台点击「要求重新推荐」（RECOMMEND_AGAIN），解锁后 Codex 才能重新推荐。

### Web 选择被拒绝

**症状**：`select` API 返回 409 `已确认锁定，无法更改选择`。

**解决**：先「撤销确认」（revoke）解锁，或「要求重新推荐」（reselect）。

## 音视频

### 无配音时间戳

无配音或字幕时间戳时，storyboard 的 startMs/endMs 是估算值（如每字 300ms）。此时只能制作视觉样片，**不可声称精确音画同步**。

### DEMO-001 无真实录屏

DEMO-001 在无真实录屏素材时使用程序化"假桌面"作为演示数据，画面标记 "DEMO DATA · 非真实操作"。正式项目必须替换为用户提供的真实录屏，不可伪装。

## 画幅与规格

默认：9:16，1080×1920，30fps，H.264 MP4。
Remotion composition 在 `Root.tsx` 中定义，所有组件共享此规格。
