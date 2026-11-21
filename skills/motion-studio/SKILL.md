---
name: motion-studio
description: Use when the user provides a storyboard Excel, script or media in an AI conversation and wants Motion Studio candidate review, feedback-driven revisions, previews or final output. AI performs planning and production; the workbench manages assets and reviews.
---

# Motion Studio：AI 制作，工作台审片

## 职责与当前约定

用户在 Codex 或其他可访问项目文件的 AI 平台提供 Excel、脚本及素材。当前对话中的 AI 理解内容、选择模板、适配场景、调用本地工具制作。工作台只管理素材、展示分镜和真实视频、保存选择与意见。不得开发工作台 Excel 导入、AI Chat、模型选择器、后台 Agent 或控制桌面当前聊天。工作台保存后不会自动执行 AI；用户回到原 AI 对话说“继续”。

当前已安装四个真实模板：TEXT-001、FLOW-001、COMP-001、DATA-001，版本 1.1.0，4:3 / 1440×1080 / 30fps。黑白紫固定设计；风格库只是可检索规范，不声称当前模板支持换肤。不得推荐已删除的 DEMO-001、TRANS-001。模板选择不得代替真实内容适配。

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
