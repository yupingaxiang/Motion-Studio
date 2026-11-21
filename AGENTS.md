# AGENTS.md — Motion Studio Agent 指南

> 本文件指导任何在 Motion Studio 仓库中工作的 AI Agent（Codex / 其他）如何理解与操作此项目。

## 项目定位

Motion Studio 是 **Codex Desktop 的配套可视化工作台**，不是独立 AI 视频生成网站。

- **Codex 是唯一 AI 决策与执行中心**：理解脚本、生成分镜、检索模板、推荐候选、生成素材、渲染预览、合成视频。
- **Web 工作台只负责**：浏览模板/素材/风格、展示分镜、播放候选 MP4、记录审核、观看预览与成片。
- **不开发**：独立 AI Chat、LLM 后端、模型选择器、第二套 Agent。

## 技术栈

- 前端：React 19 + TypeScript + Vite 5 + Tailwind CSS 3
- 后端：Python 3.14 + FastAPI + Pydantic 2
- 渲染：Remotion 4.0.545 + React 19（Node 24）
- 媒体：FFmpeg
- 数据：SQLite（可选）/ JSON 文件协议（主）
- CLI：Python（`scripts/motion_studio.py`）
- 平台：Windows 11 + PowerShell

## 环境约定

### Python

项目使用 `.venv`（Python 3.14），已安装 fastapi、uvicorn、pydantic、aiofiles、python-multipart。

```powershell
.venv\Scripts\python.exe   # 项目 Python
```

### Node / pnpm

系统 Node v12 过旧不可用。**必须使用 DSH 捆绑的 Node v24**：

- Node: `C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe`
- pnpm: `C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\bin\pnpm.mjs`

### FFmpeg

系统 PATH 中的 ffmpeg 可用（N-117676 版本）。

## 目录结构

```
motion-studio/
├── AGENTS.md                  # 本文件
├── README.md
├── scripts/
│   ├── motion_studio.py       # 主 CLI（Codex 调用）
│   └── gen_demo_recommendations.py  # demo 推荐生成器
├── backend/
│   └── app/
│       ├── main.py            # FastAPI 入口
│       ├── models/schemas.py  # Pydantic 数据协议
│       ├── services/          # library.py / projects.py
│       └── routers/           # library / projects / approvals / assets
├── frontend/
│   └── src/                   # React 工作台
├── remotion/
│   └── src/
│       ├── Root.tsx           # composition 注册
│       └── components/        # 六个动效组件
├── library/
│   ├── motions/<ID>/          # meta.json + preview.mp4 + poster.jpg
│   ├── styles/<id>/           # style.json
│   └── catalog.json           # 全库索引
├── skills/motion-studio/
│   ├── SKILL.md               # Codex Skill 主文件
│   └── references/            # 数据协议 / CLI / 排错
├── projects/demo-project/
│   ├── storyboard.json
│   ├── recommendations.json
│   ├── approvals.json
│   ├── previews/
│   └── output/
└── tests/test_acceptance.py
```

## 数据流

```
用户口播稿
  → Codex (Skill 阶段 A): 分析 + 检索模板/风格 + 写 storyboard.json + publish recommendations.json
  → Web 工作台: 三栏审核 (播放候选 MP4 + 选择 + 确认) → 写 approvals.json
  → Codex (Skill 阶段 B): 读 approvals + render-scene-preview + produce → output/<P>_final.mp4
```

## 关键规则（务必遵守）

1. **选择 ≠ 确认**。SELECTED 后还需 APPROVED 才锁定。两者是独立操作。
2. **APPROVED 后 locked**。Codex 不可静默覆盖已确认分镜的候选。用户需 RECOMMEND_AGAIN 才解锁。
3. **候选 previewPath 必须真实**。指向 `library/motions/<ID>/preview.mp4`，CLI publish 时校验。
4. **未确认不出片**。`produce` 命令在 `allConfirmed` 为 false 时退出码 2 拒绝。
5. **原子写入**。所有 JSON 用 tempfile + os.replace，附带 .meta 哈希校验。
6. **JSON 编码**。读取用 `utf-8-sig`（兼容 BOM）；写入不用 PowerShell Out-File（会加 BOM），用 write 工具或 Python json.dump。
7. **Remotion 渲染临时目录**。Puppeteer 需 TEMP 可写，CLI 自动设 `TEMP` 到 `.tmp`。
8. **DEMO-001 演示数据**。无真实录屏时用程序化假桌面，必须标记 "DEMO DATA"，不可伪装真实操作。

## 常用命令

```powershell
# 初始化
.venv\Scripts\python.exe scripts\motion_studio.py init

# 启动后端
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000

# 启动前端（另一个终端）
cd frontend; <node> <pnpm> run dev

# 渲染模板预览
.venv\Scripts\python.exe scripts\motion_studio.py render-template-previews --force

# 运行验收测试
.venv\Scripts\python.exe tests\test_acceptance.py
```

## Codex Skill 使用

Skill 位于 `skills/motion-studio/SKILL.md`。Codex Desktop 打开本项目后自动发现。

安装到用户级 Skills 目录（可选）：
```powershell
# 复制到 Codex 用户 Skills 目录（路径取决于 Codex 安装）
Copy-Item -Recurse skills\motion-studio $env:USERPROFILE\.codex\skills\
```

## 测试与验收

12 项验收测试见 `tests/test_acceptance.py`，覆盖：
1-3: 模板运行 + MP4 预览 + Web 播放
4-5: CLI 检索 + 分镜候选生成
6-8: 审核保存 + 刷新保留 + Codex 读取
9-10: 未确认拒绝出片 + 已确认不被替换
11-12: 场景预览 + 多分镜合成

## 里程碑状态

- **M1 基础设施**：✅ 完成（目录、数据协议、CLI、后端）
- **M2 动效与素材库**：✅ 完成（6 模板 + MP4 + 3 风格 + catalog）
- **M3 Web 审核工作台**：✅ 完成（三栏审核、候选视频、选择确认、素材浏览）
- **M4 Codex Skill**：✅ 完成（SKILL.md + references + CLI 集成）
- **M5 视频制作**：✅ 完成（场景预览 + 成片合成 + ffmpeg）


## 当前协作入口（2026-11-21）

收到分镜 Excel、脚本或“继续制作”时，先读 skills/motion-studio/SKILL.md。Excel 由当前 AI 对话读取；工作台仅管理素材与审片，不导入 Excel、不运行第二套 AI。AI 用 publish-storyboard / publish-recommendations 发布，用 review-brief 读取选择、修改意见、版本冲突及成片反馈。输出真实 MP4 到项目 output/，工作台负责播放与保存 output-reviews.json。当前仅四个 4:3 模板，已移除录屏聚焦和章节过渡。
