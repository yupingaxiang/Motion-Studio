# Motion Studio

> Codex 驱动的 AI 视频动效与分镜审核系统。Codex Desktop 的配套可视化工作台。

## 这是什么

Motion Studio 是 **Codex Desktop 的配套可视化工作台**，不是独立 AI 视频生成网站。

- **Codex 是唯一 AI 决策与执行中心**：理解口播脚本、生成分镜、检索动效模板、检索素材与风格、推荐候选、生成素材、渲染预览、合成视频。
- **Web 工作台只负责**：浏览模板/素材/风格、展示分镜、播放候选 MP4、记录审核、观看预览与成片。

## 功能

### Web 工作台（5 个页面）

1. **项目列表** — 展示所有项目与审核进度
2. **分镜审核** — 三栏布局：分镜列表 / 候选动效（真实 MP4）/ 审核面板
3. **动效模板库** — 卡片展示 6 个真实模板，可直接播放 MP4，按用途/风格/画幅/关键词筛选
4. **素材库** — 导入、浏览、分类图片/视频/录屏/配音/音效/图标，校验类型与大小
5. **视觉风格库** — 3 个原创风格的完整规范（色彩、构图、字体、节奏、提示词、推荐/禁用场景）

### 分镜审核（核心）

- **左栏**：分镜列表（ID、时间区间、口播内容、审核状态）
- **中栏**：候选动效（最多 3 个真实 MP4 + poster + 名称 + 推荐理由 + 源码可用性 + 选择按钮）
- **右栏**：审核面板（选中、确认、撤销、修改意见、要求重选、无需动效、查看预览）

**选择与确认是两个独立操作**。页面刷新后审核结果保留（原子写入 JSON）。

### Remotion 动效模板库（6 个真实组件）

| ID | 名称 | 类别 | 时长 | 适用 |
|----|------|------|------|------|
| TEXT-001 | 关键词揭示 | TEXT | 3s | 强调核心概念、标题、开场 |
| FLOW-001 | 流程节点展开 | FLOW | 4s | 流程、循环、步骤 |
| COMP-001 | 左右概念对比 | COMP | 4s | 对比、差异、VS |
| DEMO-001 | 录屏聚焦 | DEMO | 4s | 操作演示（需录屏素材） |
| DATA-001 | 数字与趋势变化 | DATA | 5s | 数据增长、统计、倍数 |
| TRANS-001 | 章节过渡 | TRANS | 2.5s | 过渡、结尾、章节切换 |

每个模板提供：TypeScript/React 源码、统一 Props 接口、JSON 元数据、版本号、真实 preview.mp4、poster.jpg、适用/不适用场景、画幅约束、动效时长、素材需求。

### 视觉风格库（3 个原创）

| styleId | 名称 | 定位 |
|---------|------|------|
| minimal-tech | Minimal Tech 极简科技 | 深色高对比，青蓝高光，网格底纹 |
| blueprint | Blueprint 科技蓝图 | 工程图纸美学，等宽字体，标注线 |
| engraving | Engraving 铜版画/雕版 | 复古排线，羊皮纸底，铭刻字体 |

## 技术栈

- React 19 + TypeScript + Vite 5 + Tailwind CSS 3
- Python 3.14 + FastAPI + Pydantic 2
- Remotion 4.0.545 + React 19（Node 24）
- FFmpeg（H.264 MP4）
- JSON 文件协议（原子写入 + 哈希校验）

## 快速开始

### 1. 环境准备

需要：Python 3.14+、Node 24+、FFmpeg。

本项目在 Windows 11 + PowerShell 上开发，使用项目内 `.venv` 与 DSH 捆绑的 Node。

### 2. 一键启动

```powershell
# 使用启动脚本（自动初始化 + 启动后端 + 前端）
.\start.ps1
```

或手动分步：

```powershell
# 初始化（生成 catalog.json 与 demo 项目）
.venv\Scripts\python.exe scripts\motion_studio.py init

# 渲染模板预览（首次需要，约 2 分钟）
.venv\Scripts\python.exe scripts\motion_studio.py render-template-previews --force

# 启动后端（终端 1）
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000

# 启动前端（终端 2）
cd frontend
<node路径> <pnpm路径> run dev
```

打开浏览器访问前端（通常 http://localhost:5173）。

### 3. 使用流程

1. **Codex 阶段 A（规划）**：在 Codex Desktop 中打开本项目，加载 `motion-studio` Skill。贴入口播稿，Codex 按 SKILL.md 流程分析、生成分镜、检索模板、写入候选推荐。
2. **Web 审核**：打开工作台 → 项目列表 → 进入 demo-project → 三栏审核：播放候选 MP4 → 选择 → 确认。
3. **Codex 阶段 B（制作）**：告知 Codex 审核完成。Codex 读取 approvals，渲染场景预览，合成最终 MP4。

## Codex Skill 使用

Skill 位于 `skills/motion-studio/SKILL.md`。

### 在 Codex Desktop 中打开项目

1. 打开 Codex Desktop
2. 打开项目文件夹 `D:\Motion Studio`
3. Codex 自动发现 `skills/motion-studio/SKILL.md` 并加载
4. 在对话中说"帮我用 Motion Studio 把这段口播稿做成视频分镜"

### 安装到用户级 Skills 目录（可选）

```powershell
# 若想让 Codex 在任何项目中都能用此 Skill
Copy-Item -Recurse skills\motion-studio $env:USERPROFILE\.codex\skills\
```

## CLI 命令

```bash
.venv\Scripts\python.exe scripts\motion_studio.py <command>
```

| 命令 | 用途 |
|------|------|
| `init` | 初始化 catalog.json 与 demo 项目 |
| `status [--project P]` | 查看库或项目状态 |
| `validate --project P` | 校验项目数据一致性 |
| `search --query "关键词"` | 语义检索动效模板 |
| `search-styles --query "极简"` | 检索风格 |
| `publish-recommendations --project P --input recs.json` | 写入候选推荐（含冲突校验） |
| `read-approvals --project P` | 读取用户审核结果 |
| `render-template-previews [--force]` | 批量渲染模板预览 MP4 |
| `render-scene-preview --project P --scene S01` | 渲染单分镜适配预览 |
| `produce --project P` | 合成最终视频（要求全部确认） |

## 数据协议

Codex 与 Web 工作台通过本地项目目录共享结构化数据：

- `storyboard.json` — Codex 生成：分镜（sceneId/narration/startMs/endMs/visualIntent/styleId）
- `recommendations.json` — Codex 写入：候选（templateId/previewPath/recommendationReason，最多 3 个，路径必须真实）
- `approvals.json` — Web 写入：审核（SELECTED/APPROVED/RECOMMEND_AGAIN/NO_MOTION，APPROVED 后 locked）

**冲突保护**：原子写入（tempfile + os.replace）+ sha256 元数据 + 版本号。已 APPROVED 的分镜不可被 Codex 静默覆盖。

## 视频规格

默认：9:16，1080×1920，30fps，H.264 MP4。
无配音时间戳时只做视觉样片，不声称精确音画同步。

## 测试

```powershell
.venv\Scripts\python.exe tests\test_acceptance.py
```

12 项验收测试覆盖：模板运行、MP4 预览、Web 播放、CLI 检索、分镜生成、审核保存、刷新保留、Codex 读取、未确认拒绝出片、已确认不被替换、场景预览、多分镜合成。

## 项目结构

```
motion-studio/
├── AGENTS.md
├── README.md
├── start.ps1                   # Windows 启动脚本
├── scripts/motion_studio.py    # 主 CLI
├── backend/app/                # FastAPI 后端
├── frontend/src/               # React Web 工作台
├── remotion/src/               # Remotion 动效组件
├── library/                    # 模板/风格/素材/catalog
├── skills/motion-studio/       # Codex Skill
├── projects/demo-project/      # 示例项目
└── tests/test_acceptance.py    # 验收测试
```

## 参考项目

- [FredTalk](https://github.com/njrhts2kvv-star/FredTalk) — 借鉴组件登记、语义检索、真实视频预览、审核门禁
- [Lemo OpusCar](https://github.com/lemomo-ai/lemo-opuscar) — 借鉴风格组织思路（规则/示例分离、negative prompt 分散嵌入）

仅借鉴设计方法。所有动效组件、风格规范、代码均为原创。第三方媒体/字体/音乐需分别核验许可。

## 许可

项目源码原创。第三方依赖遵循各自许可（Remotion、React、FastAPI 等）。


## 2026-11-21 工作台与模板更新

项目与模板采用卡片矩阵；模板库提供关键词、类别、时长与画幅筛选及详情播放。TEXT/FLOW/COMP/DATA 已重做为 1440×1080、4:3、30fps 原生模板，版本 1.1.0。DEMO/TRANS 保留旧版。新模板统一使用白、近黑与紫色，不随旧 styleId 换肤。

设计参考 shadcn-ui/ui 的导航层级、InvokeAI 的媒体工作区及 FredTalk DESIGN.md 的视觉原则；本次未复制上游组件源码。

旧后端进程需重启才能识别新增 4:3 枚举。本次验证实例位于 http://127.0.0.1:8001/#/motions。候选 proposedProps 现已接入场景和最终片段渲染。旧项目中的 1.0.0 推荐不会自动升级，需明确重新推荐。完整混合画幅合成、音轨处理与审核并发保护不属于本轮完成范围。


## 项目素材文件夹与分镜背景（2026-11-21）

素材资源首页以文件夹卡片区分公共库和各项目。打开项目夹后上传会写入 projects/<项目>/assets/；可填写标签、来源、许可。分镜审核右侧可选择项目或公共图片作为背景，确认后的分镜需撤销确认才可修改。绑定会增加 storyboard revision；Codex 需重新核对候选与当前脚本版本。

四个模板渲染支持绑定背景图片（低透明度保留前景可读性），内容哈希用于素材身份与缓存。视频和音频支持上传、浏览播放，尚未加入视频时间线。适配预览面板读取真实 preview manifest，可刷新；历史未记录 storyboardRevision 的预览明确标为可能过时。页面不会自动启动 Codex 或正式制作。


## AI 与工作台分工（当前入口）

在 Codex 或其他有本地文件工具的 AI 对话中提供 Excel/脚本，并让 AI 读取 skills/motion-studio/SKILL.md。AI 解析 Excel、发布分镜和候选；工作台只管理素材与审核，不导入 Excel、不发起模型调用。审核完成后回到原 AI 对话说“读取审核结果，继续制作”。

新增 CLI：publish-storyboard --project P --input 实际JSON --expected-revision N（新项目 N=0）；review-brief --project P（读取分镜、审核、修改意见、冲突和成片反馈）。

生成后的真实 MP4 放在 projects/P/output/，在分镜页点击“成片审看”。逐文件意见保存到 output-reviews.json，AI 下次读 review-brief 即可收到。此流程不依赖特定聊天平台 API，纯聊天平台仍需本地工具协助交接。
# Motion-Studio
剪辑工作台


## FredTalk 首批源码接入

新增 FRED-V087（荧光笔重点）、FRED-STACK（图片叠放扇开）、FRED-RETYPE（删除重写）、FRED-FOCUS（双图焦点）。实际源码来自公开 FredTalk 项目，MIT 许可保存在 remotion/src/components/fred/LICENSE，来源/原始及本地哈希在 provenance.json。没有把上游 MP4 当作可执行组件。

四个输出为 1440×1080 / 4:3，原960×540几何等比居中，上下保留留白；不是原生4:3重排。工作台可按“模板来源 → FredTalk”筛选并查看来源和参数。图片演示使用本项目模板封面，新项目需AI换为实际图片。此次仅首批四个，不代表432条上游记录全部已接入。


## 数字与素材快切模板

参考用户提供的 library/video/1.mp4 开头机制，新增独立 NUMBER-001、MEDIA-001 和组合 INTRO-001，全部4:3 / 1440×1080 / 30fps。数字与快切速度可配置，标题在落定后展开。示例使用本项目授权模板图片/视频，没有将参考视频内容复制进模板。

AI把实际素材复制到Remotion public后，通过候选 proposedProps.srcs 填入相对路径。支持图片及MP4/WebM/MOV，视频默认从第30帧取材，videoStartFrames可设为0；短素材须先核对时长。组合模板由countFrames统一控制计数和快切结束，避免时间错位。


## 贴纸风科普

STICKER-001：薄荷绿纸纹、白边剪纸、手绘连线、便签与结论贴纸。原生1440×1080、4:3、30fps，默认9秒。通过cueFrames将最多5个节点绑定到实际口播时间，srcs可替换为Remotion public内的真实本地贴纸图片；未填使用自绘SVG。右下角为后续口播人物预留空间，不代表本模板已合成人物。


## 分镜编辑（首版）

从首页每张项目卡的“分镜编辑”按钮进入，或从分镜审核页点击“分镜编辑”，或访问 /#/editor/<项目ID>。中间为真实组件实时预览，下方播放/拖动时间及动效区间，右侧编辑模板声明参数、位置、缩放和出现/消失时间。显式保存到项目scene-edits.json，支持放弃未保存修改；确认锁定的分镜只读。AI通过review-brief读取手动编辑；匹配所选模板版本时场景渲染与最终片段渲染使用同一个SCENE-EDIT组件。

透明背景开关支持文字、流程、对比、数据、数字与贴纸六类；棋盘格不是导出背景。当前只提供透明预览，未实现透明视频导出。现支持模板声明的内部卡片、标题、数字、图表或贴纸分别选中并拖动；点击空白不移动整体。右栏可选择被遮挡的元素、精调坐标、恢复此元素位置。未实现任意新增元素、多轨层级和撤销历史。口播视频可作为本段参照（从该文件0秒起）或右下角小窗，仅用于预览。编辑器按需加载，无AI后端或自动模型调用。


## 素材文件夹与真实背景绑定
素材文件夹是项目/公共素材库的浏览与筛选，不是电脑目录选择器，不会自动扫描磁盘或应用素材。项目文件保存在projects/<项目ID>/assets/，公共文件保存在library/assets/。分镜编辑右侧“本分镜背景”支持切换素材来源、直接导入图片、选图、绑定和解除；导入/选图不自动绑定。未保存的动效修改需先保存或放弃，已确认分镜需先撤销确认。绑定立即保存到storyboard并更新实时预览。
背景按4:3铺满画面，位于模板前景下方；卡片底板保留，不再使用10%透明度的图片叠加。绑定也应用于没有手动编辑的分镜，CLI统一经SCENE-EDIT渲染。素材快切模板自己的全屏媒体可能覆盖背景，这是前景媒体的实际覆盖关系。通用候选MP4不会随项目绑定改变；项目适配预览需重新由AI渲染，旧分镜版本的预览不展示为当前结果。


## 真人讲解配对模板
PRESENTER-IN：真人全屏连续缩到右下角，再展开知识卡片。PRESENTER-OUT：卡片先收起，再由右下角人物放大回全屏。原生4:3/1440×1080/30fps，模板预览各6秒；时长可按分镜适配。原声沿单一视频实例连续播放，圆角无描边。模板库“真人讲解”分类可播放。
预览使用自绘演示人物并标注DEMO DATA；正式项目渲染必须提供本地presenterSrc，缺失或剩余时长不足会拒绝渲染。编辑器中选择项目视频，可改标题、最多三张卡片、转场开始帧/时长、小窗位置/大小和裁切焦点。拖动人物仅偏移小窗，全屏终点保持不变。真人模板占满本分镜时间，不允许裁掉人物声音或整体缩放破坏全屏。
配对时以同一源视频和连续sourceStartFrame衔接，例如前一段使用0..179帧，下一段从180帧开始；这是可复用模板，不是已替用户实拍视频完成整片合成。
