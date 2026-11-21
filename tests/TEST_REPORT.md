# Motion Studio 测试报告

## 测试环境

- 操作系统：Windows 11
- Python：3.14.5（项目 .venv）
- Node：v24.21.0（DSH 捆绑）
- pnpm：11.28.5
- FFmpeg：N-117676 (20241031)
- Remotion：4.0.545
- React：19.3.1

## 验收测试结果

运行命令：`.venv\Scripts\python.exe tests\test_acceptance.py`

### 任务书第 12 节 12 项要求验证

| # | 要求 | 状态 | 说明 |
|---|------|------|------|
| 1 | 六个真实 Remotion 模板能够运行 | ✅ PASS | TEXT/FLOW/COMP/DEMO/DATA/TRANS 全部加载，源码存在 |
| 2 | 每个模板有真实 MP4 预览 | ✅ PASS | 6 个 preview.mp4 均存在，h264 1080×1920，90KB-383KB |
| 3 | Web 能够正常播放这些视频 | ✅ PASS | API 返回 6 模板 previewExists 全 true，静态媒体路由可访问 |
| 4 | Codex 可以通过本地工具检索模板 | ✅ PASS | CLI search/search-styles 成功，语义匹配正确 |
| 5 | Codex 可以生成分镜和候选 | ✅ PASS | storyboard 6 分镜，recommendations 每分镜 ≤3 候选，previewPath 真实 |
| 6 | Web 可以保存审核结果 | ✅ PASS | select→SELECTED，approve→APPROVED+locked |
| 7 | 页面刷新后审核状态不丢失 | ✅ PASS | 重新读取 approvals.json 状态保留 |
| 8 | Codex 可以读取审核状态 | ✅ PASS | CLI read-approvals 成功，输出含 S01/APPROVED |
| 9 | 未确认分镜无法正式出片 | ✅ PASS | produce 退出码 2 拒绝 |
| 10 | 已确认模板不会被静默替换 | ✅ PASS | publish-recommendations 退出码 2 拒绝，提示 APPROVED |
| 11 | 可以生成真实分镜预览 | ✅ PASS | render-scene-preview 生成 S01 预览 MP4 |
| 12 | 可以合成一个多分镜的测试 MP4 | ✅ PASS | produce 合成 demo-project_final.mp4 |

### 模板预览规格

| 模板 | 时长 | 分辨率 | 编码 | 大小 |
|------|------|--------|------|------|
| TEXT-001 | 3.0s | 1080×1920 | h264 | 230KB |
| FLOW-001 | 4.0s | 1080×1920 | h264 | 327KB |
| COMP-001 | 4.0s | 1080×1920 | h264 | 90KB |
| DEMO-001 | 4.0s | 1080×1920 | h264 | 195KB |
| DATA-001 | 5.0s | 1080×1920 | h264 | 383KB |
| TRANS-001 | 2.5s | 1080×1920 | h264 | 254KB |

所有预览均为 9:16 竖屏、30fps、H.264 MP4，符合任务书规格要求。

### 冲突保护验证

- **选择 ≠ 确认**：SELECTED 与 APPROVED 是两个独立状态，API 分两个端点
- **APPROVED 后 locked**：select 操作被 409 拒绝
- **Codex 不可静默覆盖**：publish-recommendations 对已 APPROVED 分镜抛 PermissionError
- **RECOMMEND_AGAIN 解锁**：用户要求重选后 locked=false，Codex 可重新推荐
- **原子写入**：所有 JSON 用 tempfile + os.replace，附 .meta 哈希校验

### 未使用 Mock 冒充

- 6 个模板均为真实 Remotion React 组件，渲染真实 MP4
- 候选 previewPath 指向真实存在的本地 MP4，CLI publish 时校验
- 场景预览与成片由 Remotion + ffmpeg 真实渲染生成
- DEMO-001 无真实录屏时用程序化演示数据，明确标记 "DEMO DATA"

## 里程碑完成状态

- **M1 基础设施**：✅ 完成（目录、数据协议、CLI、FastAPI 后端）
- **M2 动效与素材库**：✅ 完成（6 真实模板 + MP4 + 3 原创风格 + catalog）
- **M3 Web 审核工作台**：✅ 完成（三栏审核、候选视频播放、选择确认、素材/风格浏览）
- **M4 Codex Skill**：✅ 完成（SKILL.md + references + CLI 集成 + 语义检索）
- **M5 视频制作**：✅ 完成（场景预览渲染 + 多分镜成片合成 + ffmpeg 拼接）
