---
name: motion-studio
description: Use when the user provides a storyboard Excel, script or media in an AI conversation and wants Motion Studio candidate review, feedback-driven revisions, previews or final output. AI performs planning and production; the workbench manages assets and reviews.
---

# Motion Studio：AI 制作，工作台审片

## 职责与当前约定

用户在 Codex 或其他可访问项目文件的 AI 平台提供 Excel、脚本及素材。当前对话中的 AI 理解内容、选择模板、适配场景、调用本地工具制作。工作台只管理素材、展示分镜和真实视频、保存选择与意见。不得开发工作台 Excel 导入、AI Chat、模型选择器、后台 Agent 或控制桌面当前聊天。工作台保存后不会自动执行 AI；用户回到原 AI 对话说“继续”。

当前自有四个真实模板：TEXT-001、FLOW-001、COMP-001、DATA-001，版本 1.1.0，4:3 / 1440×1080 / 30fps。黑白紫固定设计；风格库只是可检索规范，不声称当前模板支持换肤。不得推荐已删除的 DEMO-001、TRANS-001。模板选择不得代替真实内容适配。

## 每次开始先读交接

若项目存在，先运行：

```powershell
.venv\Scripts\python.exe scripts/motion_studio.py review-brief --project <项目ID>
```

返回全文分镜、候选及 proposedProps、选中版本、locked、修改意见、成片反馈、版本冲突和 nextAction。不得只按确认数量推断制作许可。

- WAIT_FOR_REVIEW：准备或展示候选，等待用户逐段确认。
- RECOMMEND_AGAIN：仅重选用户解锁的段落，不改变其他锁定选择。
- RESOLVE_CONFLICTS：处理过时的脚本/候选或缺失版本；不得静默把旧模板升级为新模板。
- GENERATE_SCENE_PREVIEWS：模板审核完成，可适配并生成本期预览；仍核对实际素材、意见与输出规格。

成片反馈在 outputReviews 中，按准确文件名读取；反馈存在不等于用户解锁模板。

## 阶段 A：在 AI 对话读取 Excel 和规划

1. 使用当前平台可用的表格读取工具解析用户提供的 Excel；本地没有可用读取工具时如实说明，不能假装已读取。不要把读取移入工作台。
2. 核对表头与合并单元格，将段号、口播、画面描述、时间、素材路径映射到 Scene。保留原段号与原文；不清楚的字段再问，不重复询问表中已有内容。时间缺失可估算并明确说明，不能声称精确音画同步。
3. 在项目 assets 目录管理专属素材；公共资源在 library/assets。参考 registry.json 中登记的真实路径、来源与许可。不得虚构文件。
4. 输出 storyboard JSON，采用现有协议（见 references/data-protocol.md）。外部 AI 仅输出 JSON 时，由能访问本地文件的 AI 完成交接。
5. 用版本保护命令发布；新项目 expected-revision=0，现有项目使用 review-brief 返回的版本：

```powershell
.venv\Scripts\python.exe scripts/motion_studio.py publish-storyboard --project <P> --input <实际JSON路径> --expected-revision <N>
```

锁定分镜内容变化或删除将被拒绝。不要通过直接改文件绕过保护。

6. 按每段可见对象与动作检索模板，检查真实 MP4、源码、当前版本和画幅：

```powershell
.venv\Scripts\python.exe scripts/motion_studio.py search --query "对象与动作" --aspect 4:3
.venv\Scripts\python.exe scripts/motion_studio.py search-styles --query "风格意图"
```

7. 每段最多三个合适候选，填写具体推荐理由和真实 proposedProps。不能为凑三个候选推荐不相关模板；无合适模板报告缺口。候选含 ID、版本、真实 previewPath/posterPath、兼容性、所需素材。
8. 使用 publish-recommendations 发布 JSON，禁止覆盖已锁定候选；混合锁定项目先保留已有记录，遇拒绝先查原因，不绕过。
9. 给出工作台对应项目链接，说明“选中”和“确认”是两步。停止正式制作，等用户在 AI 对话中继续。

## 阶段 B：读审核、真实适配、预览

1. 用户说继续时重新运行 review-brief，不依赖上次聊天记忆。
2. 先处理重选/冲突。保留已确认 ID、版本和用户修改范围。
3. 使用所选候选的 proposedProps、分镜真实文案与素材，核对 4:3 布局。当前背景图片引用 role=background，可按内容哈希进入四个模板；视频/音频只支持管理与播放，时间线合成尚需按项目实现，不能声称已经接入。
4. 调用 render-scene-preview --project <P> --scene <S>。生成真实 MP4 和 manifest，工作台在分镜审核右侧刷新播放。
5. 阅读修改意见；先区分排版修改和模板重选。普通意见不自动解锁模板。
6. 渲染检查不等于视觉认可；检查关键帧和中间运动，实际素材、内容、版本对应。

## 阶段 C：输出与审片

全部分镜明确确认后，AI 才执行正式制作。现有 produce 仍有混合画幅、时长与音轨限制；先读实际实现并检查项目条件，不能直接承诺可靠整片。不得将 NO_MOTION 当成删段，不得用空白视频冒充成片。

实际完成的 MP4 放入 projects/<P>/output/，保留可定位版本。工作台“成片审看”自动列出真实 MP4，逐文件保存修改意见到 output-reviews.json。用户回到 AI 对话说“读取审片意见继续”，重新读交接包后修改和导出。

核对 1440×1080、4:3、帧率、时长、音轨、完整解码与主要接缝，只报告已执行的检查。无配音/时间戳时明确交付视觉样片。

## 文件所有权

- AI 写：storyboard.json、recommendations.json、previews/manifest.json、output/*.mp4。
- 工作台写：approvals.json、output-reviews.json、素材登记及显式的图片绑定。
- 共享文件使用现有原子 JSON 写入工具，读取 UTF-8 BOM 兼容。所有路径必须真实且在授权目录。
- 此 Skill 不发送外部消息、不上传私人媒体、不初始化或执行 Git。

## 安装与其他 AI 平台

当前项目的入口文件是本 SKILL.md。可在 AI 对话明确要求读取它。支持本地文件和命令的其他 AI 可复用同一协议；仅能对话的平台不能直接操作本机，不能假设自动连通。

可选用户级安装（用户自行执行）：

```powershell
Copy-Item -LiteralPath "D:\Motion Studio\skills\motion-studio" -Destination "$env:USERPROFILE\.agents\skills\motion-studio" -Recurse -Force
```

详细字段与现有命令见 references/data-protocol.md、references/cli-reference.md；旧文档与本页冲突时，以本页当前模板、4:3 和分工约定为准。


## FredTalk 外部模板

已接入公开源码的首批适配器：FRED-V087（荧光笔重点）、FRED-STACK（五图叠放/扇开/平铺）、FRED-RETYPE（删除重写）、FRED-FOCUS（双图焦点接力）。来源、MIT许可与哈希记录在 remotion/src/components/fred/provenance.json；非 V087 的原身份为上游文件名，不捏造目录编号。仅 status=APPROVED 且真实预览存在时参与正式推荐。

原960×540几何等比缩放并居中到1440×1080，保持4:3成片但上下留白；不是原生4:3重排。图片样例来自本项目封面，适配时将真实图片复制至Remotion public并填写srcs的相对路径。RETYPE当前节奏按四字词设计，长词需另查时序；长句高亮必须检查换行。不可把可执行来源验证当作本期新内容视觉认可。


## 数字递增与素材快切

新增独立 NUMBER-001（数字快进/落定）、MEDIA-001（图片或视频快切/停留）及 INTRO-001（两者共用帧时钟的组合开场），均4:3、1440×1080、30fps、默认5秒。可替换起止数字、countFrames、标题、副标题、srcs、cutFrames和dim。INTRO使用countFrames同时决定数字与素材快切结束；不另传flashFrames。

srcs必须指向Remotion public内真实本地图片或视频。AI复制项目授权素材后填写相对路径；MP4/WebM/MOV按视频播放，示例默认本项目自有封面。不能把快切示例称为用户真实软件操作。长标题应重新检查排版，数字超过三位时检查字号与单位。短视频素材需能覆盖该段停留时间；默认无配音和音乐。


## 用户确认：口播与动效对齐约定（2026-11-21）

以下为已确认的产品与制作约定，尚不代表相关功能全部实现：

- 项目素材夹统一管理分镜 Excel / 口播稿、实拍口播视频、带时间戳文本、讲解图片/视频，以及素材与模板的关联。
- 用户按分镜拍摄；以分镜 ID（如 S03）关联稿件、实拍、素材、屏幕文字、模板与预览。
- 句子/关键词时间戳以实际口播音频为准，由当前 Codex 或其他 AI 对齐原稿生成；不将稿件估算时间冒充精确时间。
- 屏幕文字可以提炼口播原文，但须保留语义，并通过文本锚点绑定实际口播时间。
- 素材出现、模板入场、强调、状态变化与退场由对应时间戳驱动，不仅整体拉伸模板时长。
- 画面默认 4:3；主区域展示讲解素材/动效，人物口播位于右下角，保持比例，保留原声。沿用个人视频偏好：圆角、无描边，不默认添加背景音乐或逐字字幕。
- 工作台管理素材、展示关联和同步预览、记录审核与意见；AI 对话负责读取 Excel、转录/对齐、选择与适配模板、渲染合成。不得把这些 AI 工作移入工作台后台。
- 视频剪掉空白或重排时，人物画面、原声、文本时间戳与动效时间必须一致映射；保留源片时间与成片时间的对应关系。
- 时间戳驱动不等于必须显示字幕。是否烧录字幕单独由用户决定。


## 贴纸风科普

STICKER-001为原生4:3贴纸讲解模板，最多5节点；title/labels/srcs/notes/summary均可替换。cueFrames为各节点实际出现帧，AI按本段口播文本时间戳（秒×30）填写，不必沿用默认等间隔。手绘连线跟随下一节点，便签跟随末节点。右下角保留人物小窗空间，当前模板本身不含真人视频。默认图标为本项目自绘SVG，不是参考作者的Logo或肖像。建议节点短词、标题短句；长内容重排并出真实预览检查。


## 分镜编辑手动覆盖（2026-11-21）

工作台“分镜编辑”通过真实Remotion Player编辑整张动效的声明参数、x/y/scale、局部startMs/endMs及有限模板的背景透明开关。修改保存在scene-edits.json（revision、scenes按分镜ID、updatedAt），与recommendations和approvals分离。review-brief的sceneEdits包含用户手调结果，AI不得覆盖或忽略；重新发布候选时保留手动内容与时间。

编辑选择的templateId/templateVersion若不同于审核候选，先更新候选并让用户审核，不能静默套用。已确认分镜写入被拒绝，需用户显式撤销确认。CLI在所选ID/版本匹配时合并手动props，并通过共享SCENE-EDIT组件应用时间/位置/缩放；不匹配则报错。

首版是一张动效卡/分镜，不是任意内部元素编辑器。支持透明前景预览的模板为TEXT/FLOW/COMP/DATA/NUMBER/STICKER；媒体全底图和Fred模板不宣称已透明化。项目口播视频可作预览参照或右下角小窗，不包含在该动效导出中。尚无透明MOV/WebM视频导出，不将H.264MP4当作带alpha的视频。


### 单元素位置覆盖
scene-edits.scenes.<sceneId>.elements 以模板稳定元素ID为键，例如 card-0、card-1、title、keyword；每项为{x,y}，表示1440×1080画布坐标下相对于原动画位置的偏移。拖动或修改一个元素不得改动其他元素和整体layout。CLI已将elements交给SCENE-EDIT；AI必须保留这些手调结果。Fred适配器内部960画布的1.5倍换算由渲染组件处理，AI不要重复换算。首页项目卡提供独立分镜编辑入口。


### 绑定背景（修复）
分镜assets中role=background的本地图片是真正的场景背景，铺在模板前景下方，不是低透明度纹理。CLI的_build_scene_props会为所有绑定背景的模板启用SCENE-EDIT，即便没有手调scene-edits；实际素材由_scene_media_props按内容哈希复制至public/scene-assets。模板卡片保留自身底板，全屏前景媒体会覆盖背景。背景绑定更新storyboard版本后，重新核对候选版本及渲染缓存，不能继续展示旧版本MP4冒充新背景。


### 真人进入/返回模板
PRESENTER-IN和PRESENTER-OUT为4:3组合场景：全屏→右下角知识讲解，或知识卡片收起→人物回全屏。默认预览6秒，DEMO DATA自绘人物仅用于模板展示，正式渲染须传presenterSrc真实本地视频。可用projects/<项目>/assets/<文件>、library/assets/<文件>或已暂存的public相对路径；CLI按哈希暂存，检查剩余时长并保留原音轨内容。sourceStartFrame以30fps帧数填写；相邻场景按源片与成片映射连续递增，避免重放/跳音。
transitionAt/transitionFrames控制转场，不等于剪掉前后口播；OUT需先预留24帧收卡。必须在最后一帧前完成转场。真人场景_editor.startMs=0/endMs=整段时长，layout为x0/y0/scale1；人物小窗用pipX/Y/Width/Height、cropX/Y或elements.presenter偏移调整，不改变全屏终点。其他cards与title可单独拖动。当前卡片内容为标题与最多三条知识点，未自动嵌套任意Fred模板。
