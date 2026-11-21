/** Author: Codex | Modified: 2026-11-21 16:00:00 +08:00 | Versioned scene asset API. */
/** API 客户端：封装所有后端调用。 */

import type {
  Catalog,
  TemplateMeta,
  StyleSpec,
  Storyboard,
  Recommendations,
  Approvals,
  ProjectStatus,
  AssetRecord,
} from "../types";

const BASE = "";

async function json<T>(resOrPromise: Response | Promise<Response>): Promise<T> {
  const res = await resOrPromise;
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status}: ${txt}`);
  }
  return res.json();
}

export const api = {
  // library
  getCatalog: () => json<Catalog>(fetch(`${BASE}/api/library/catalog`)),
  getTemplates: () =>
    json<{ count: number; templates: TemplateMeta[] }>(fetch(`${BASE}/api/library/templates`)),
  getTemplate: (id: string) =>
    json<TemplateMeta>(fetch(`${BASE}/api/library/templates/${id}`)),
  getStyles: () =>
    json<{ count: number; styles: StyleSpec[] }>(fetch(`${BASE}/api/library/styles`)),
  getStyle: (id: string) => json<StyleSpec>(fetch(`${BASE}/api/library/styles/${id}`)),
  getSummary: () => json<any>(fetch(`${BASE}/api/library/summary`)),

  // projects
  listProjects: () =>
    json<{ count: number; projects: ProjectStatus[] }>(fetch(`${BASE}/api/projects`)),
  getProject: (id: string) => json<ProjectStatus>(fetch(`${BASE}/api/projects/${id}`)),
  getStoryboard: (id: string) =>
    json<Storyboard>(fetch(`${BASE}/api/projects/${id}/storyboard`)),
  getRecommendations: (id: string) =>
    json<Recommendations>(fetch(`${BASE}/api/projects/${id}/recommendations`)),
  getApprovals: (id: string) =>
    json<Approvals>(fetch(`${BASE}/api/projects/${id}/approvals`)),
  getStatus: (id: string) =>
    json<ProjectStatus>(fetch(`${BASE}/api/projects/${id}/status`)),
  validate: (id: string) =>
    json<any>(fetch(`${BASE}/api/projects/${id}/validate`)),
  getPreviews: (id: string) =>
    json<any>(fetch(`${BASE}/api/projects/${id}/previews`)),

  bindAsset: (projectId: string, sceneId: string, assetId: string, scope: string, expectedRevision: number) => json<Storyboard>(fetch(`/api/projects/${encodeURIComponent(projectId)}/scenes/${encodeURIComponent(sceneId)}/asset`, {method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({assetId,scope,expectedRevision})})),

  getReviewBrief: (projectId:string) => json<any>(fetch(`/api/projects/${encodeURIComponent(projectId)}/review-brief`)),
  getOutputs: (projectId:string) => json<{outputs:{file:string;path:string;sizeBytes:number;notes:string}[]}>(fetch(`/api/projects/${encodeURIComponent(projectId)}/outputs`)),
  saveOutputReview: (projectId:string,file:string,notes:string) => json<any>(fetch(`/api/projects/${encodeURIComponent(projectId)}/output-review`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({file,notes})})),
  // approvals
  select: (body: {
    projectId: string;
    sceneId: string;
    templateId: string;
    templateVersion: string;
    basedOnRecommendationRevision: number;
  }) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/select`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
    ),
  approve: (projectId: string, sceneId: string) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, sceneId }),
      })
    ),
  revoke: (projectId: string, sceneId: string) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/revoke`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, sceneId }),
      })
    ),
  reselect: (projectId: string, sceneId: string, notes: string) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/reselect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, sceneId, notes }),
      })
    ),
  noMotion: (projectId: string, sceneId: string) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/no-motion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, sceneId }),
      })
    ),
  setNotes: (projectId: string, sceneId: string, notes: string) =>
    json<Approvals>(
      fetch(`${BASE}/api/approvals/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, sceneId, notes }),
      })
    ),

  // assets
  listAssets: (scope: string = "library") =>
    json<{ count: number; assets: AssetRecord[] }>(
      fetch(`${BASE}/api/assets?scope=${scope}`)
    ),
  importAsset: async (file: File, scope: string, tags: string, source: string, license: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("scope", scope);
    form.append("tags", tags);
    form.append("source", source);
    form.append("license", license);
    const res = await fetch(`${BASE}/api/assets/import`, { method: "POST", body: form });
    return json<{ ok: boolean; asset: AssetRecord }>(res);
  },
  deleteAsset: (assetId: string, scope: string = "library") =>
    json<{ ok: boolean }>(fetch(`${BASE}/api/assets/${assetId}?scope=${scope}`, { method: "DELETE" })),
};

/** 把后端返回的相对路径转成可访问的媒体 URL。 */
export function mediaUrl(relPath: string): string {
  if (!relPath) return "";
  if (relPath.startsWith("http") || relPath.startsWith("/")) return relPath;
  // relPath 形如 "library/motions/TEXT-001/preview.mp4" 或 "projects/.."
  return `${BASE}/media/${relPath}`;
}
