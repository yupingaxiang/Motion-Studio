# 数据协议完整说明

Motion Studio 中 Codex（通过 Skill + CLI）与 Web 工作台（通过 FastAPI）通过本地项目目录共享结构化数据。所有 JSON 文件用原子写入（临时文件 + rename）+ sha256 元数据校验，避免并发写损坏。

## 文件分布

| 文件 | 写入方 | 读取方 | 路径 |
|------|--------|--------|------|
| `storyboard.json` | Codex | Codex, Web | `projects/<P>/storyboard.json` |
| `recommendations.json` | Codex | Codex, Web | `projects/<P>/recommendations.json` |
| `approvals.json` | Web | Codex, Web | `projects/<P>/approvals.json` |
| `catalog.json` | CLI init | Codex, Web | `library/catalog.json` |
| `meta.json` | 模板入库 | Codex, Web | `library/motions/<ID>/meta.json` |
| `style.json` | 风格定义 | Codex, Web | `library/styles/<id>/style.json` |

每个 JSON 文件旁有 `<file>.meta`，含 sha256 与 updatedAt，用于乐观并发校验。

## storyboard.json

由 Codex 生成与修改。每次修改 `projectRevision +1`。

```typescript
interface Storyboard {
  projectId: string;
  projectRevision: number;      // 语义版本，每次修改递增
  script: string;               // 原始口播稿全文
  scenes: Scene[];
  updatedAt: string;            // ISO8601 UTC
}

interface Scene {
  sceneId: string;              // 如 "S01"
  narration: string;            // 该分镜口播文字
  startMs: number;              // 起始毫秒
  endMs: number;                // 结束毫秒（endMs > startMs）
  visualIntent: string;         // 视觉意图：要表现什么
  assets: SceneAssetRef[];      // 引用的素材
  styleId: string;              // 风格 id
}

interface SceneAssetRef {
  role: "main" | "background" | "overlay" | "icon" | "audio";
  assetId: string;
  localPath: string;
  description: string;
}
```

## recommendations.json

由 Codex 通过 `publish-recommendations` 命令写入。CLI 自动：
- 递增 `recommendationRevision`
- 校验所有 `previewPath` 指向真实存在的 MP4
- 检查冲突：已 APPROVED 且未要求 RECOMMEND_AGAIN 的分镜，拒绝覆盖（抛 PermissionError）

```typescript
interface Recommendations {
  projectId: string;
  recommendationRevision: number;
  basedOnStoryboardRevision: number;
  scenes: SceneRecommendation[];
  updatedAt: string;
}

interface SceneRecommendation {
  sceneId: string;
  recommendationRevision: number;
  candidates: Candidate[];      // 最多 3 个
  generatedAt: string;
}

interface Candidate {
  templateId: string;           // 如 "TEXT-001"
  templateVersion: string;      // 如 "1.0.0"
  previewPath: string;          // 必须指向真实存在的本地 MP4（相对项目根或绝对）
  posterPath: string;           // poster.jpg 路径
  recommendationReason: string; // 为什么匹配该分镜
  score: number;                // 0-1，匹配度
  requiredAssets: string[];     // 所需素材类型
  compatibility: "full" | "partial" | "needs-assets";
  proposedProps: Record<string, any>; // 基于分镜内容的具体参数
}
```

## approvals.json

由 Web 工作台写入。Codex 只读。

```typescript
interface Approvals {
  projectId: string;
  approvals: SceneApproval[];
  updatedAt: string;
}

interface SceneApproval {
  sceneId: string;
  selectedTemplateId: string;       // SELECTED 阶段写入
  selectedTemplateVersion: string;
  approvalStatus: "PENDING" | "SELECTED" | "APPROVED" | "RECOMMEND_AGAIN" | "NO_MOTION";
  modificationNotes: string;
  approvedAt: string;               // APPROVED 时写入
  basedOnRecommendationRevision: number;
  locked: boolean;                  // APPROVED 后 true，Codex 不可静默覆盖
}
```

### 状态流转

```
PENDING (Codex 写入推荐后)
  ↓ 用户选中
SELECTED (Web 写入，selectedTemplateId 填充)
  ↓ 用户确认
APPROVED (Web 写入，locked=true)  ← 正式制作门槛
  ↓ 用户撤销确认
SELECTED (locked=false)
  ↓ 用户要求重新推荐
RECOMMEND_AGAIN (locked=false，允许 Codex 覆盖候选)
  ↓ Codex 重新推荐 + 用户选中确认
APPROVED

NO_MOTION (独立分支，用户决定无需动效，locked=true)
```

### 冲突保护规则

1. **Codex 写 recommendations 时**：若某分镜 `approvalStatus == APPROVED && locked == true`，且该分镜 `approvalStatus != RECOMMEND_AGAIN`，CLI 抛 PermissionError，拒绝覆盖。
2. **Web 写 approvals 时**：若 `locked == true`，select 操作被拒绝（需先 revoke 或 reselect）。
3. **原子写入**：所有 JSON 通过 `tempfile.mkstemp` + `os.replace` 写入，避免半写状态。
4. **哈希校验**：每次写入同时生成 `<file>.meta` 含 sha256，用于检测外部并发修改。

## catalog.json

由 `CLI init` 或 `render-template-previews` 后自动生成。扫描 `library/motions/*/meta.json` 与 `library/styles/*/style.json` 汇总。

```typescript
interface Catalog {
  schemaVersion: string;       // "1.0.0"
  generatedAt: string;
  templates: CatalogEntry[];
  styles: StyleSummary[];
}
```

## 模板 meta.json

```typescript
interface TemplateMeta {
  templateId: string;
  name: string;
  description: string;
  version: string;             // 语义化版本
  status: "DRAFT" | "APPROVED" | "DEPRECATED";
  component: string;           // Remotion 组件文件名
  compositionId: string;       // Remotion composition id
  previewMp4: string;          // "preview.mp4"
  posterJpg: string;           // "poster.jpg"
  sourceAvailable: boolean;
  useCases: string[];
  notUseCases: string[];
  aspectRatios: string[];      // ["9:16"]
  durationFrames: number;      // 30fps
  minDurationFrames: number;
  maxDurationFrames: number;
  requiredAssets: string[];    // ["image"|"video"|"recording"|"audio"|"icon"]
  optionalAssets: string[];
  params: TemplateParam[];
  tags: string[];
  category: string;            // "TEXT"|"FLOW"|"COMP"|"DEMO"|"DATA"|"TRANS"
}
```

仅 `status == APPROVED` 的模板参与正式候选推荐。

## 风格 style.json

```typescript
interface StyleSpec {
  styleId: string;
  name: string;
  description: string;
  colors: { name: string; hex: string; usage: string }[];
  background: string;
  foreground: string;
  compositionRules: string[];
  fontSuggestions: string[];
  titleFont: string;
  bodyFont: string;
  animationRhythm: string[];
  imagePromptTemplate: string;
  negativePrompt: string;
  exampleImage: string;
  exampleVideo: string;
  recommendedScenes: string[];
  forbiddenScenes: string[];
  tags: string[];
}
```
