/** 前端类型定义，与后端 Pydantic 模型对应。 */

export interface TemplateParam {
  name: string;
  type: string;
  label: string;
  default: any;
  required?: boolean;
  description?: string;
  options?: string[];
  min?: number;
  max?: number;
}

export interface TemplateMeta {
  templateId: string;
  name: string;
  version: string;
  status: string;
  category: string;
  description: string;
  previewMp4: string | null;
  previewExists: boolean;
  posterJpg: string;
  sourceAvailable: boolean;
  useCases: string[];
  notUseCases: string[];
  aspectRatios: string[];
  durationFrames: number;
  requiredAssets: string[];
  tags: string[];
  params: TemplateParam[];
}

export interface CatalogEntry {
  templateId: string;
  name: string;
  version: string;
  status: string;
  category: string;
  previewMp4: string;
  posterJpg: string;
  sourceAvailable: boolean;
  useCases: string[];
  tags: string[];
  aspectRatios: string[];
  durationFrames: number;
  requiredAssets: string[];
}

export interface Catalog {
  schemaVersion: string;
  generatedAt: string;
  templates: CatalogEntry[];
  styles: any[];
}

export interface ColorSpec {
  name: string;
  hex: string;
  usage: string;
}

export interface StyleSpec {
  styleId: string;
  name: string;
  description: string;
  colors: ColorSpec[];
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

export interface SceneAssetRef {
  role: string;
  assetId: string;
  localPath: string;
  description: string;
}

export interface Scene {
  sceneId: string;
  narration: string;
  startMs: number;
  endMs: number;
  visualIntent: string;
  assets: SceneAssetRef[];
  styleId: string;
}

export interface Storyboard {
  projectId: string;
  projectRevision: number;
  script: string;
  scenes: Scene[];
  updatedAt: string;
}

export interface Candidate {
  templateId: string;
  templateVersion: string;
  previewPath: string;
  posterPath: string;
  recommendationReason: string;
  score: number;
  requiredAssets: string[];
  compatibility: string;
  proposedProps: Record<string, any>;
}

export interface SceneRecommendation {
  sceneId: string;
  recommendationRevision: number;
  candidates: Candidate[];
  generatedAt: string;
}

export interface Recommendations {
  projectId: string;
  recommendationRevision: number;
  basedOnStoryboardRevision: number;
  scenes: SceneRecommendation[];
  updatedAt: string;
}

export type ApprovalStatus =
  | "PENDING"
  | "SELECTED"
  | "APPROVED"
  | "RECOMMEND_AGAIN"
  | "NO_MOTION";

export interface SceneApproval {
  sceneId: string;
  selectedTemplateId: string;
  selectedTemplateVersion: string;
  approvalStatus: ApprovalStatus;
  modificationNotes: string;
  approvedAt: string;
  basedOnRecommendationRevision: number;
  locked: boolean;
}

export interface Approvals {
  projectId: string;
  approvals: SceneApproval[];
  updatedAt: string;
}

export interface ProjectStatus {
  projectId: string;
  hasStoryboard: boolean;
  storyboardRevision: number;
  hasRecommendations: boolean;
  recommendationRevision: number;
  hasApprovals: boolean;
  sceneCount: number;
  candidateCount: number;
  approvedCount: number;
  selectedCount: number;
  pendingCount: number;
  reselectCount: number;
  noMotionCount: number;
  allConfirmed: boolean;
  previews: string[];
  outputs: string[];
}

export interface AssetRecord {
  assetId: string;
  name: string;
  mediaType: string;
  localPath: string;
  previewPath: string;
  tags: string[];
  source: string;
  license: string;
  fileSizeBytes: number;
  createdAt: string;
}
