"""为 demo-project 生成候选推荐数据（模拟 Codex 阶段 A 输出）。

这个脚本演示 Codex Skill 应如何构造 recommendations 并调用 CLI 发布。
真实使用时由 Codex Agent 按 SKILL.md 流程完成视觉理解与候选选择，
然后调用 publish-recommendations 写入。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from backend.app.services import library as lib
from backend.app.services import projects as proj
from backend.app.models import now_iso


def build_demo_recommendations() -> dict:
    """为 demo-project 的 6 个分镜各生成最多 3 个候选。

    基于 storyboard 的 visualIntent 与模板 useCases 做匹配。
    """
    sb = proj.read_storyboard("demo-project")
    root = _ROOT
    scenes_out = []
    for scene in sb.scenes:
        # 用 CLI 的检索逻辑找候选
        results = lib.search_templates(scene.visualIntent, limit=5)
        # 取前 3 个有预览的
        candidates = []
        for meta, score in results:
            preview = lib.template_preview_abs(meta.templateId)
            if not preview:
                continue
            rel_preview = f"library/motions/{meta.templateId}/{meta.previewMp4}"
            rel_poster = f"library/motions/{meta.templateId}/{meta.posterJpg}"
            # 构造推荐理由
            reason = _build_reason(scene, meta, score)
            props = _build_props(scene, meta)
            candidates.append(
                {
                    "templateId": meta.templateId,
                    "templateVersion": meta.version,
                    "previewPath": rel_preview,
                    "posterPath": rel_poster,
                    "recommendationReason": reason,
                    "score": round(min(score, 1.0), 3),
                    "requiredAssets": meta.requiredAssets,
                    "compatibility": "full" if not meta.requiredAssets else "needs-assets",
                    "proposedProps": props,
                }
            )
            if len(candidates) >= 3:
                break
        # 若检索不足 3 个，补一些相关模板
        if len(candidates) < 2:
            # 兜底：TRANS-001 适合结尾分镜
            all_templates = lib.load_all_templates()
            existing_ids = {c["templateId"] for c in candidates}
            for meta in all_templates:
                if meta.templateId in existing_ids:
                    continue
                preview = lib.template_preview_abs(meta.templateId)
                if not preview:
                    continue
                # 简单匹配
                if scene.sceneId == "S06" and meta.templateId == "TRANS-001":
                    candidates.append(
                        {
                            "templateId": meta.templateId,
                            "templateVersion": meta.version,
                            "previewPath": f"library/motions/{meta.templateId}/{meta.previewMp4}",
                            "posterPath": f"library/motions/{meta.templateId}/{meta.posterJpg}",
                            "recommendationReason": "结尾分镜适合章节过渡，TRANS-001 色块扫入扫出收尾",
                            "score": 0.85,
                            "requiredAssets": meta.requiredAssets,
                            "compatibility": "full",
                            "proposedProps": {"title": scene.narration[:12]},
                        }
                    )
                    existing_ids.add(meta.templateId)
                if len(candidates) >= 3:
                    break
        scenes_out.append(
            {
                "sceneId": scene.sceneId,
                "recommendationRevision": 1,
                "candidates": candidates,
                "generatedAt": now_iso(),
            }
        )
    return {
        "projectId": "demo-project",
        "recommendationRevision": 1,
        "basedOnStoryboardRevision": sb.projectRevision,
        "scenes": scenes_out,
        "updatedAt": now_iso(),
    }


def _build_reason(scene, meta, score) -> str:
    """构造人类可读的推荐理由。"""
    intent = scene.visualIntent
    reasons = {
        "TEXT-001": f"该分镜需强调核心概念，TEXT-001 关键词揭示组件以高光汇聚形式呈现「{scene.narration[:6]}」",
        "FLOW-001": f"该分镜描述流程/循环，FLOW-001 节点展开串联展示因果链",
        "COMP-001": "该分镜涉及对比，COMP-001 左右分裂对比单利与复利",
        "DEMO-001": "该分镜涉及操作演示，DEMO-001 录屏聚焦（需真实录屏素材，当前为演示数据）",
        "DATA-001": f"该分镜含数字增长，DATA-001 数字滚动配合曲线展示增长趋势",
        "TRANS-001": "该分镜为过渡/结尾，TRANS-001 色块扫入收尾",
    }
    base = reasons.get(meta.templateId, f"模板 {meta.templateId} 与该分镜视觉意图匹配（得分 {score:.2f}）")
    return base


def _build_props(scene, meta) -> dict:
    props: dict = {}
    if meta.templateId.startswith("TEXT"):
        props["keyword"] = scene.visualIntent.split("：")[-1].split(":")[-1].strip()[:6] or scene.narration[:6]
        props["subtitle"] = scene.narration
    elif meta.templateId.startswith("FLOW"):
        props["nodes"] = ["本金", "收益", "新本金", "新收益"]
        props["title"] = scene.narration[:20]
    elif meta.templateId.startswith("COMP"):
        props["leftLabel"] = "单利"
        props["rightLabel"] = "复利"
        props["leftValue"] = "线性增长"
        props["rightValue"] = "指数增长"
    elif meta.templateId.startswith("DATA"):
        props["startValue"] = "1.00"
        props["endValue"] = "37.78"
        props["caption"] = scene.narration[:30]
    elif meta.templateId.startswith("TRANS"):
        props["title"] = scene.narration[:12]
    elif meta.templateId.startswith("DEMO"):
        props["caption"] = scene.narration[:20]
        props["steps"] = ["步骤一", "步骤二", "步骤三"]
    props["styleId"] = scene.styleId
    return props


if __name__ == "__main__":
    recs = build_demo_recommendations()
    out = _ROOT / "projects" / "demo-project" / "_recs_input.json"
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成推荐输入: {out}")
    for s in recs["scenes"]:
        print(f"  分镜 {s['sceneId']}: {len(s['candidates'])} 候选 {[c['templateId'] for c in s['candidates']]}")
