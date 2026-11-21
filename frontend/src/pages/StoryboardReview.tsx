/** Author: Codex | Modified: 2026-11-21 15:30:00 +08:00 | Matrix candidate review. */
﻿import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { api, mediaUrl } from "../api";
import type {
  Storyboard,
  Recommendations,
  Approvals,
  SceneApproval,
  Candidate,
} from "../types";
import { SceneMedia } from "../components/SceneMedia";
import { VideoPlayer } from "../components/VideoPlayer";

/** Review previews and persist separate select and approve actions. */
export function StoryboardReview() {
  const { projectId } = useParams<{ projectId: string }>();
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [recs, setRecs] = useState<Recommendations | null>(null);
  const [approvals, setApprovals] = useState<Approvals | null>(null);
  const [selectedScene, setSelectedScene] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [notesDraft, setNotesDraft] = useState<Record<string, string>>({});
  const [error, setError] = useState<string>("");

  const load = useCallback(async () => {
    if (!projectId) return;
    try {
      const [sb, rc, ap, templates] = await Promise.all([
        api.getStoryboard(projectId),
        api.getRecommendations(projectId),
        api.getApprovals(projectId),
        api.getTemplates(),
      ]);
      setStoryboard(sb);
      const available = new Set(templates.templates.map(t => t.templateId));
      setRecs({...rc, scenes:rc.scenes.map(r=>({...r,candidates:r.candidates.filter(c=>available.has(c.templateId))}))});
      setApprovals(ap);
      if (!selectedScene && sb.scenes.length > 0) {
        setSelectedScene(sb.scenes[0].sceneId);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, selectedScene]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <div className="p-8 text-ms-muted">加载中...</div>;
  if (error && !storyboard) return <div className="p-8 text-red-400">错误: {error}</div>;
  if (!storyboard) return <div className="p-8 text-ms-muted">无 storyboard</div>;

  const scenes = storyboard.scenes;
  const currentScene = scenes.find((s) => s.sceneId === selectedScene) ?? scenes[0];
  const sceneRec = recs?.scenes.find((r) => r.sceneId === currentScene?.sceneId);
  const sceneApproval = approvals?.approvals.find((a) => a.sceneId === currentScene?.sceneId);

  // 审核操作
  const doSelect = async (c: Candidate) => {
    if (!projectId || !currentScene || !recs) return;
    try {
      const ap = await api.select({
        projectId,
        sceneId: currentScene.sceneId,
        templateId: c.templateId,
        templateVersion: c.templateVersion,
        basedOnRecommendationRevision: recs.recommendationRevision,
      });
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const doApprove = async () => {
    if (!projectId || !currentScene) return;
    try {
      const ap = await api.approve(projectId, currentScene.sceneId);
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const doRevoke = async () => {
    if (!projectId || !currentScene) return;
    try {
      const ap = await api.revoke(projectId, currentScene.sceneId);
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const doReselect = async () => {
    if (!projectId || !currentScene) return;
    const notes = notesDraft[currentScene.sceneId] ?? sceneApproval?.modificationNotes ?? "";
    try {
      const ap = await api.reselect(projectId, currentScene.sceneId, notes);
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const doNoMotion = async () => {
    if (!projectId || !currentScene) return;
    try {
      const ap = await api.noMotion(projectId, currentScene.sceneId);
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const saveNotes = async () => {
    if (!projectId || !currentScene) return;
    const notes = notesDraft[currentScene.sceneId] ?? "";
    try {
      const ap = await api.setNotes(projectId, currentScene.sceneId, notes);
      setApprovals(ap);
    } catch (e: any) {
      setError(e.message);
    }
  };

  // Count current storyboard scenes, including those without an approval record.
  const currentApprovals = scenes.map(scene => approvals?.approvals.find(a=>a.sceneId===scene.sceneId));
  const stats = {
    total: scenes.length,
    approved: currentApprovals.filter(a=>a?.approvalStatus==="APPROVED" && a.locked).length,
    noMotion: currentApprovals.filter(a=>a?.approvalStatus==="NO_MOTION" && a.locked).length,
    selected: currentApprovals.filter(a=>a?.approvalStatus==="SELECTED").length,
    pending: currentApprovals.filter(a=>!a || a.approvalStatus==="PENDING").length,
    reselect: currentApprovals.filter(a=>a?.approvalStatus==="RECOMMEND_AGAIN").length,
  };
  const allConfirmed = stats.approved + stats.noMotion === stats.total && stats.total > 0;

  return (
    <div className="flex flex-col h-full">
      {/* 顶部栏 */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-ms-border bg-ms-panel">
        <div className="flex items-center gap-4">
          <Link to="/projects" className="text-ms-muted hover:text-white text-sm">← 返回</Link>
          <h1 className="text-lg font-semibold">{projectId}</h1>
          <Link className="text-xs text-ms-accent" to={`/editor/${projectId}`}>分镜编辑 ↗</Link>
          <Link className="text-xs text-ms-accent" to={`/outputs/${projectId}`}>成片审看 ↗</Link>
          <span className="text-xs text-ms-muted">SB rev {storyboard.projectRevision}</span>
          {recs && <span className="text-xs text-ms-muted">REC rev {recs.recommendationRevision}</span>}
        </div>
        <div className="flex items-center gap-4 text-sm">
          <Badge label="已确认" value={stats.approved} color="green" />
          <Badge label="无需动效" value={stats.noMotion} color="gray" />
          <Badge label="已选中" value={stats.selected} color="blue" />
          <Badge label="待处理" value={stats.pending} color="yellow" />
          <Badge label="重选" value={stats.reselect} color="red" />
          {allConfirmed && <span className="text-green-400 text-xs px-2 py-1 rounded bg-green-500/20">✓ 已确认，回到 AI 继续制作</span>}
        </div>
      </div>

      {error && (
        <div className="px-6 py-2 bg-red-500/10 text-red-400 text-sm flex justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="review-handoff-hint">选择与确认会即时保存；填写意见后请点击“保存意见”。审核完成后，回到 Codex 或其他 AI 对话说“读取审核结果，继续制作”。</div>
      {/* 三栏布局 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左栏：分镜列表 */}
        <div className="w-72 shrink-0 border-r border-ms-border overflow-y-auto bg-ms-panel/30">
          <div className="px-3 py-2 text-xs text-ms-muted uppercase border-b border-ms-border">分镜列表 ({scenes.length})</div>
          {scenes.map((scene) => {
            const ap = approvals?.approvals.find((a) => a.sceneId === scene.sceneId);
            const status = ap?.approvalStatus ?? "PENDING";
            return (
              <div
                key={scene.sceneId}
                onClick={() => setSelectedScene(scene.sceneId)}
                className={`px-3 py-3 border-b border-ms-border/50 cursor-pointer transition-colors ${
                  selectedScene === scene.sceneId ? "bg-ms-accent/10 border-l-2 border-l-ms-accent" : "hover:bg-ms-border/30"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold">{scene.sceneId}</span>
                  <StatusBadge status={status} />
                </div>
                <div className="text-xs text-ms-muted mb-1">
                  {(scene.startMs / 1000).toFixed(1)}s - {(scene.endMs / 1000).toFixed(1)}s
                </div>
                <div className="text-xs text-gray-300 line-clamp-2">{scene.narration}</div>
                {ap?.selectedTemplateId && (
                  <div className="text-xs text-ms-accent mt-1">→ {ap.selectedTemplateId}</div>
                )}
              </div>
            );
          })}
        </div>

        {/* 中栏：候选动效 */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-4">
            <h2 className="text-lg font-semibold">{currentScene?.sceneId} 候选动效</h2>
            <p className="text-sm text-ms-muted mt-1">
              <span className="text-gray-300">口播：</span>{currentScene?.narration}
            </p>
            <p className="text-xs text-ms-muted mt-1">
              <span className="text-gray-400">视觉意图：</span>{currentScene?.visualIntent}
            </p>
          </div>

          {(!sceneRec || sceneRec.candidates.length === 0) && (
            <div className="text-center py-12 text-ms-muted">
              <p>该分镜暂无候选推荐。</p>
              <p className="text-xs mt-2">Codex 需通过 Skill 调用 <code className="text-ms-accent">publish-recommendations</code> 写入候选。</p>
            </div>
          )}

          <div className="candidate-matrix">
            {sceneRec?.candidates.map((c, idx) => {
              const isSelected = sceneApproval?.selectedTemplateId === c.templateId;
              const isApproved = sceneApproval?.approvalStatus === "APPROVED" && isSelected;
              const mp4Url = mediaUrl(c.previewPath);
              const posterUrl = c.posterPath ? mediaUrl(c.posterPath) : "";
              return (
                <div
                  key={`${c.templateId}-${idx}`}
                  className={`bg-ms-panel border rounded-xl overflow-hidden video-card ${
                    isSelected ? "border-ms-accent border-2" : "border-ms-border"
                  }`}
                >
                  <div className="candidate-card-layout">
                    {/* 视频预览 */}
                    <div className="candidate-card-preview bg-black">
                      <VideoPlayer src={mp4Url} poster={posterUrl} />
                    </div>
                    {/* 信息 */}
                    <div className="flex-1 p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="font-semibold text-base">{c.templateId}</div>
                          <div className="text-xs text-ms-muted">v{c.templateVersion} · 兼容性: {c.compatibility}</div>
                        </div>
                        {isSelected && (
                          <span className="text-xs px-2 py-1 rounded bg-ms-accent/20 text-ms-accent">
                            {isApproved ? "已确认" : "已选中"}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-300 mb-2">{c.recommendationReason}</div>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {c.requiredAssets.map((a) => (
                          <span key={a} className="text-xs px-1.5 py-0.5 rounded bg-ms-border text-ms-muted">{a}</span>
                        ))}
                      </div>
                      <div className="text-xs text-ms-muted">
                        得分 {(c.score * 100).toFixed(0)} · 源码可用
                      </div>
                      {/* 选择按钮 */}
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => doSelect(c)}
                          disabled={sceneApproval?.locked}
                          className={`text-sm px-4 py-1.5 rounded-lg transition-colors ${
                            isSelected
                              ? "bg-ms-accent text-black"
                              : "bg-ms-border text-gray-300 hover:bg-ms-accent/30"
                          } disabled:opacity-40 disabled:cursor-not-allowed`}
                        >
                          {isSelected ? "✓ 已选中" : "选择"}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 右栏：审核面板 */}
        <div className="w-80 shrink-0 border-l border-ms-border overflow-y-auto bg-ms-panel/30 p-4">
          <h3 className="font-semibold mb-3">审核面板</h3>
          {currentScene && (
            <>
            <ApprovalPanel
              sceneId={currentScene.sceneId}
              approval={sceneApproval}
              recRev={recs?.recommendationRevision ?? 0}
              onApprove={doApprove}
              onRevoke={doRevoke}
              onReselect={doReselect}
              onNoMotion={doNoMotion}
              onSaveNotes={saveNotes}
              notesDraft={notesDraft}
              setNotesDraft={setNotesDraft}
            />
            <SceneMedia projectId={projectId!} scene={currentScene} storyboard={storyboard} approval={sceneApproval} onSaved={setStoryboard}/>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/** Render scene review information. */
function ApprovalPanel({
  sceneId,
  approval,
  recRev,
  onApprove,
  onRevoke,
  onReselect,
  onNoMotion,
  onSaveNotes,
  notesDraft,
  setNotesDraft,
}: {
  sceneId: string;
  approval?: SceneApproval;
  recRev: number;
  onApprove: () => void;
  onRevoke: () => void;
  onReselect: () => void;
  onNoMotion: () => void;
  onSaveNotes: () => void;
  notesDraft: Record<string, string>;
  setNotesDraft: (v: Record<string, string>) => void;
}) {
  const status = approval?.approvalStatus ?? "PENDING";
  const selected = approval?.selectedTemplateId ?? "";
  const locked = approval?.locked ?? false;

  return (
    <div className="space-y-4">
      {/* 当前状态 */}
      <div className="bg-ms-panel border border-ms-border rounded-lg p-3">
        <div className="text-xs text-ms-muted mb-1">当前状态</div>
        <StatusBadge status={status} large />
        {selected && (
          <div className="mt-2 text-sm">
            <div className="text-xs text-ms-muted">选中模板</div>
            <div className="text-ms-accent">{selected}</div>
            <div className="text-xs text-ms-muted">v{approval?.selectedTemplateVersion}</div>
          </div>
        )}
        {locked && <div className="mt-2 text-xs text-yellow-400">⚠ 已锁定（确认后不可静默替换）</div>}
      </div>

      {/* 操作按钮 */}
      <div className="space-y-2">
        <div className="text-xs text-ms-muted uppercase">操作（选择与确认独立）</div>
        <button
          onClick={onApprove}
          disabled={!selected || locked}
          className="w-full text-sm px-3 py-2 rounded-lg bg-green-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-green-500"
        >
          {locked ? "✓ 已确认" : "确认动效（锁定）"}
        </button>
        <button
          onClick={onRevoke}
          disabled={!locked}
          className="w-full text-sm px-3 py-2 rounded-lg bg-ms-border text-gray-300 disabled:opacity-40 hover:bg-ms-border/70"
        >
          撤销确认
        </button>
        <button
          onClick={onNoMotion}
          disabled={locked && status === "NO_MOTION"}
          className="w-full text-sm px-3 py-2 rounded-lg bg-ms-border text-gray-300 disabled:opacity-40 hover:bg-ms-border/70"
        >
          无需动效
        </button>
        <button
          onClick={onReselect}
          className="w-full text-sm px-3 py-2 rounded-lg bg-ms-accent2/20 text-ms-accent2 hover:bg-ms-accent2/30"
        >
          要求重新推荐
        </button>
      </div>

      {/* 修改意见 */}
      <div>
        <div className="text-xs text-ms-muted uppercase mb-2">修改意见</div>
        <textarea
          value={notesDraft[sceneId] ?? approval?.modificationNotes ?? ""}
          onChange={(e) => setNotesDraft({ ...notesDraft, [sceneId]: e.target.value })}
          placeholder="输入对该分镜的修改意见..."
          className="w-full text-sm bg-ms-panel border border-ms-border rounded-lg p-2 h-24 resize-none focus:border-ms-accent outline-none"
        />
        <button
          onClick={onSaveNotes}
          className="mt-1 text-xs px-3 py-1 rounded bg-ms-border text-gray-300 hover:bg-ms-accent/30"
        >
          保存意见
        </button>
      </div>

      {/* 元信息 */}
      {approval && (
        <div className="text-xs text-ms-muted border-t border-ms-border pt-3">
          <div>basedOn rev: {approval.basedOnRecommendationRevision}</div>
          {approval.approvedAt && <div>确认时间: {new Date(approval.approvedAt).toLocaleString("zh-CN")}</div>}
        </div>
      )}
    </div>
  );
}

/** Render scene review information. */
function StatusBadge({ status, large }: { status: string; large?: boolean }) {
  const map: Record<string, { color: string; label: string }> = {
    PENDING: { color: "bg-yellow-500/20 text-yellow-400", label: "待处理" },
    SELECTED: { color: "bg-blue-500/20 text-blue-400", label: "已选中" },
    APPROVED: { color: "bg-green-500/20 text-green-400", label: "已确认" },
    RECOMMEND_AGAIN: { color: "bg-red-500/20 text-red-400", label: "重选" },
    NO_MOTION: { color: "bg-gray-500/20 text-gray-400", label: "无动效" },
  };
  const m = map[status] ?? map.PENDING;
  return (
    <span className={`${large ? "text-sm px-3 py-1" : "text-xs px-1.5 py-0.5"} rounded ${m.color}`}>
      {m.label}
    </span>
  );
}

/** Render scene review information. */
function Badge({ label, value, color }: { label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    green: "text-green-400",
    blue: "text-blue-400",
    yellow: "text-yellow-400",
    red: "text-red-400",
    gray: "text-gray-400",
  };
  return (
    <span className="text-xs">
      <span className="text-ms-muted">{label} </span>
      <span className={`font-semibold ${colors[color]}`}>{value}</span>
    </span>
  );
}
