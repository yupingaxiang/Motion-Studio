# CLI 完整参考

所有命令通过项目 venv 的 Python 执行：

```bash
.venv\Scripts\python.exe scripts\motion_studio.py <command> [options]
```

或用系统 Python（已安装 fastapi/uvicorn/pydantic）：

```bash
python scripts\motion_studio.py <command> [options]
```

## init

初始化库 catalog.json 与 demo 项目。

```bash
python scripts/motion_studio.py init
```

- 扫描 `library/motions/*/meta.json` 与 `library/styles/*/style.json`
- 生成 `library/catalog.json`
- 若 `projects/demo-project` 不存在，创建示例 storyboard
- 输出库摘要（模板数、预览就绪数、风格数）

## status

查看库或项目状态。

```bash
# 全局库状态
python scripts/motion_studio.py status

# 单项目状态
python scripts/motion_studio.py status --project demo-project
```

项目状态返回：sceneCount、approvedCount、selectedCount、pendingCount、allConfirmed、previews、outputs 等。

## validate

校验项目数据一致性。返回 errors（阻断）与 warnings（提醒）。

```bash
python scripts/motion_studio.py validate --project demo-project
```

校验项：
- storyboard/recommendations/approvals 文件可解析
- 分镜时间区间有效（endMs > startMs）
- 候选 previewPath 真实存在
- 推荐基于的 storyboard revision 是否过时
- SELECTED/APPROVED 的模板是否在当前推荐候选中
- approvals 是否含未知分镜

返回 `{"valid": bool, "errors": [...], "warnings": [...]}`。退出码 0=valid，1=有 error。

## search

语义检索动效模板。仅 APPROVED 模板参与。

```bash
python scripts/motion_studio.py search --query "关键词揭示" [--category TEXT] [--aspect 9:16] [--tags a,b] [--assets image,video] [--limit 10]
```

检索算法：
- 中英文分词（英文按词，中文做 2-gram）
- 匹配 useCases/tags/name/description
- useCases/tag 匹配权重更高
- notUseCases 匹配惩罚
- 返回 (template, score) 按分数降序

输出每个模板：templateId、name、version、score、previewMp4（绝对路径）、previewExists、useCases、params。

## search-styles

```bash
python scripts/motion_studio.py search-styles --query "极简科技" [--limit 5]
```

## publish-recommendations

Codex 写入候选推荐。**含冲突校验**。

```bash
python scripts/motion_studio.py publish-recommendations --project demo-project --input recs.json
```

`--input` 指向一个 JSON 文件，结构同 Recommendations。CLI 会：
1. 强制 projectId 与 --project 一致
2. 校验每个候选的 previewPath 真实存在（不存在则退出码 1）
3. 自动递增 recommendationRevision
4. 记录 basedOnStoryboardRevision
5. 冲突校验：已 APPROVED 且未 RECOMMEND_AGAIN 的分镜，抛 PermissionError（退出码 2）

退出码：0=成功，1=文件/校验错误，2=冲突拒绝。

## read-approvals

读取用户审核结果。Codex 在阶段 B 开始时调用。

```bash
python scripts/motion_studio.py read-approvals --project demo-project
```

输出完整 approvals.json。

## render-template-previews

批量渲染所有模板的 preview.mp4 与 poster.jpg。

```bash
python scripts/motion_studio.py render-template-previews [--only TEXT-001] [--force]
```

- 使用 Remotion CLI (`@remotion/cli`) 渲染每个模板的 composition
- 默认跳过已存在的 preview.mp4（--force 强制重渲染）
- 渲染后用 `still` 命令生成 poster.jpg（frame=15）
- 自动设置 TEMP 到项目 .tmp 目录（避免 Puppeteer 权限问题）
- 完成后重新生成 catalog.json

要求：`remotion/node_modules` 已安装（首次运行会自动 pnpm install）。

## render-scene-preview

渲染单个分镜的适配预览（Scene Preview）。

```bash
python scripts/motion_studio.py render-scene-preview --project demo-project --scene S01 [--force]
```

流程：
1. 读取 storyboard 的该分镜内容
2. 读取 approvals 中该分镜的 selectedTemplateId
3. 若未选中，退出（提示用户先 SELECTED）
4. 获取模板 meta，基于分镜内容构建 props（_build_scene_props）
5. 计算缓存键 = sceneId + templateId + version + propsHash
6. 缓存命中且未 --force 则跳过
7. 写 props 到 `previews/<cacheKey>.props.json`
8. Remotion render composition with --props
9. 生成 poster
10. 更新 `previews/manifest.json`

## produce

合成最终视频。**要求所有分镜已确认**（APPROVED 或 NO_MOTION）。

```bash
python scripts/motion_studio.py produce --project demo-project
```

流程：
1. 检查 `allConfirmed`，未确认则退出码 2
2. 对每个 APPROVED 分镜渲染场景片段到 `previews/<sceneId>_final.mp4`
3. 用 ffmpeg concat demuxer 拼接
4. 若 copy 失败则重编码（libx264, scale 1080x1920）
5. 用 ffprobe 校验产物（duration/size/codec/fps）
6. 输出到 `output/<project>_final.mp4`

退出码：0=成功，1=渲染错误，2=未确认拒绝。

## 退出码约定

- 0：成功
- 1：文件不存在、校验失败、渲染失败
- 2：冲突拒绝（已 APPROVED 不可覆盖）或未确认拒绝出片


## AI 交接命令（2026-11-21）

- `publish-storyboard --project P --input file.json --expected-revision N`：发布当前 AI 从 Excel/脚本整理出的分镜。项目 ID 必须一致，拒绝过时 revision、重复分镜 ID、无效时间、锁定段变更。
- `review-brief --project P`：只读 JSON，包含分镜、候选参数、用户意见、锁定、版本冲突、nextAction 和 outputReviews。审核后在原 AI 对话执行，工作台不调用 AI。
- 成片放 `projects/P/output/*.mp4`，工作台逐文件保存 `output-reviews.json`，AI 通过交接命令读取。
