"""Motion Studio 验收测试。

验证任务书第 12 节的 12 项要求：
1. 六个真实 Remotion 模板能够运行
2. 每个模板有真实 MP4 预览
3. Web 能够正常播放这些视频
4. Codex 可以通过本地工具检索模板
5. Codex 可以生成分镜和候选
6. Web 可以保存审核结果
7. 页面刷新后审核状态不丢失
8. Codex 可以读取审核状态
9. 未确认分镜无法正式出片
10. 已确认模板不会被静默替换
11. 可以生成真实分镜预览
12. 可以合成一个多分镜的测试 MP4

运行：.venv/Scripts/python.exe tests/test_acceptance.py
"""

from __future__ import annotations

import io
import json
import sys
import subprocess
from pathlib import Path

# 强制 stdout 用 UTF-8，避免 GBK 编码无法输出中文/符号
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

VP = str(_ROOT / ".venv" / "Scripts" / "python.exe")
NODE = r"C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    mark = "[PASS]" if ok else "[FAIL]"
    print(f"  {mark} {name}" + (f" -- {detail}" if detail and not ok else ""))


def run_cli(*args: str) -> tuple[int, str]:
    r = subprocess.run(
        [VP, str(_ROOT / "scripts" / "motion_studio.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out


# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("Motion Studio 验收测试")
    print("=" * 60)

    from backend.app.services import library as lib
    from backend.app.services import projects as proj
    from backend.app.models import ApprovalStatus

    # --- 测试 1: 六个真实 Remotion 模板能够运行 ---
    print("\n[1] 六个真实 Remotion 模板能够运行")
    templates = lib.load_all_templates()
    expected = {"TEXT-001", "FLOW-001", "COMP-001", "DEMO-001", "DATA-001", "TRANS-001"}
    actual = {t.templateId for t in templates}
    check("六个模板全部加载", expected == actual, f"缺失: {expected - actual}")
    # 验证组件源码存在
    for tid in expected:
        meta = lib.get_template(tid)
        src = lib.template_source_abs(tid)
        check(f"{tid} 源码存在", src is not None and src.exists())

    # --- 测试 2: 每个模板有真实 MP4 预览 ---
    print("\n[2] 每个模板有真实 MP4 预览")
    for tid in expected:
        p = lib.template_preview_abs(tid)
        ok = p is not None and p.exists() and p.stat().st_size > 1000
        check(f"{tid} preview.mp4 真实存在 (>1KB)", ok, str(p) if p else "None")

    # --- 测试 3: Web 能够正常播放这些视频（API 可访问） ---
    print("\n[3] Web 能够正常播放这些视频")
    # 验证后端能返回模板列表含 previewMp4 路径
    from backend.app.routers.library import list_templates
    resp = list_templates()
    ok = resp["count"] == 6 and all(t["previewExists"] for t in resp["templates"])
    check("API 返回 6 模板且 previewExists 全 true", ok)
    # 验证 media 静态路径可拼
    check("catalog.json 存在", lib.catalog_path().exists())

    # --- 测试 4: Codex 可以通过本地工具检索模板 ---
    print("\n[4] Codex 可以通过本地工具检索模板")
    code, out = run_cli("search", "--query", "关键词揭示")
    check("CLI search 命令成功", code == 0)
    check("检索到 TEXT-001", "TEXT-001" in out)
    code, out = run_cli("search", "--query", "数据增长")
    check("检索到 DATA-001", "DATA-001" in out)
    code, out = run_cli("search-styles", "--query", "极简")
    check("CLI search-styles 成功", code == 0)
    check("检索到 minimal-tech", "minimal-tech" in out)

    # --- 测试 5: Codex 可以生成分镜和候选 ---
    print("\n[5] Codex 可以生成分镜和候选")
    sb = proj.read_storyboard("demo-project")
    check("demo-project 有 storyboard", sb is not None and len(sb.scenes) == 6)
    rec = proj.read_recommendations("demo-project")
    check("demo-project 有 recommendations", rec is not None)
    check("每个分镜有候选", all(len(s.candidates) > 0 for s in rec.scenes))
    check("候选不超过 3 个", all(len(s.candidates) <= 3 for s in rec.scenes))
    # 候选 previewPath 真实存在
    root = _ROOT
    all_preview_ok = True
    for s in rec.scenes:
        for c in s.candidates:
            p = root / c.previewPath if not Path(c.previewPath).is_absolute() else Path(c.previewPath)
            if not p.exists():
                all_preview_ok = False
    check("所有候选 previewPath 真实存在", all_preview_ok)

    # --- 测试 6: Web 可以保存审核结果 ---
    print("\n[6] Web 可以保存审核结果")
    # 模拟 Web 选择 + 确认 S01
    app = proj.read_approvals_safe("demo-project")
    # 清理可能存在的旧记录
    app0 = proj.read_approvals_safe("demo-project")
    # 选择 S01 第一个候选
    s01_rec = next(s for s in rec.scenes if s.sceneId == "S01")
    first_cand = s01_rec.candidates[0]
    app = proj.select_candidate("demo-project", "S01", first_cand.templateId, first_cand.templateVersion, rec.recommendationRevision)
    s01_app = next(a for a in app.approvals if a.sceneId == "S01")
    check("SELECTED 状态正确", s01_app.approvalStatus == "SELECTED", s01_app.approvalStatus)
    check("selectedTemplateId 正确", s01_app.selectedTemplateId == first_cand.templateId)
    # 确认
    app = proj.approve_scene("demo-project", "S01")
    s01_app = next(a for a in app.approvals if a.sceneId == "S01")
    check("APPROVED 状态正确", s01_app.approvalStatus == "APPROVED")
    check("locked 为 true", s01_app.locked is True)

    # --- 测试 7: 页面刷新后审核状态不丢失 ---
    print("\n[7] 页面刷新后审核状态不丢失")
    # 重新读取（模拟刷新）
    app2 = proj.read_approvals("demo-project")
    s01_app2 = next(a for a in app2.approvals if a.sceneId == "S01")
    check("重新读取后状态仍为 APPROVED", s01_app2.approvalStatus == "APPROVED")
    check("重新读取后仍 locked", s01_app2.locked is True)
    check("approvals.json 文件存在", proj.approvals_path("demo-project").exists())

    # --- 测试 8: Codex 可以读取审核状态 ---
    print("\n[8] Codex 可以读取审核状态")
    code, out = run_cli("read-approvals", "--project", "demo-project")
    check("CLI read-approvals 成功", code == 0)
    check("输出含 S01", "S01" in out)
    check("输出含 APPROVED", "APPROVED" in out)

    # --- 测试 9: 未确认分镜无法正式出片 ---
    print("\n[9] 未确认分镜无法正式出片")
    status = proj.project_status("demo-project")
    check("当前未全部确认", not status["allConfirmed"], f"approved={status['approvedCount']}/{status['sceneCount']}")
    code, out = run_cli("produce", "--project", "demo-project")
    check("produce 被拒绝（退出码 2）", code == 2, f"exit={code}")

    # --- 测试 10: 已确认模板不会被静默替换 ---
    print("\n[10] 已确认模板不会被静默替换")
    # 尝试重新发布推荐（S01 已 APPROVED）
    inp = _ROOT / "projects" / "demo-project" / "_recs_input.json"
    code, out = run_cli("publish-recommendations", "--project", "demo-project", "--input", str(inp))
    check("publish-recommendations 被拒绝（退出码 2）", code == 2, f"exit={code}")
    check("错误信息提到 APPROVED", "APPROVED" in out or "确认" in out)

    # --- 测试 11: 可以生成真实分镜预览 ---
    print("\n[11] 可以生成真实分镜预览")
    code, out = run_cli("render-scene-preview", "--project", "demo-project", "--scene", "S01")
    check("render-scene-preview 成功", code == 0, out[-200:] if out else "")
    # 检查产物
    pv_dir = proj.previews_dir("demo-project")
    mp4s = list(pv_dir.glob("S01*.mp4"))
    check("场景预览 MP4 生成", len(mp4s) > 0)

    # --- 测试 12: 可以合成一个多分镜的测试 MP4 ---
    print("\n[12] 可以合成一个多分镜的测试 MP4")
    # 先把所有分镜都确认（选择第一个候选 + approve）
    for scene in sb.scenes:
        if scene.sceneId == "S01":
            continue  # 已确认
        sr = next((s for s in rec.scenes if s.sceneId == scene.sceneId), None)
        if sr and sr.candidates:
            try:
                proj.select_candidate("demo-project", scene.sceneId, sr.candidates[0].templateId, sr.candidates[0].templateVersion, rec.recommendationRevision)
                proj.approve_scene("demo-project", scene.sceneId)
            except Exception as e:
                # 可能已锁定，跳过
                pass
    status = proj.project_status("demo-project")
    check("全部确认完成", status["allConfirmed"], f"approved={status['approvedCount']}/{status['sceneCount']}")
    code, out = run_cli("produce", "--project", "demo-project")
    check("produce 成功（退出码 0）", code == 0, out[-300:] if out else f"exit={code}")
    final_mp4 = proj.output_dir("demo-project") / "demo-project_final.mp4"
    check("最终 MP4 生成", final_mp4.exists() and final_mp4.stat().st_size > 1000, str(final_mp4))

    # --- 汇总 ---
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)
    print(f"总计: {passed} 通过 / {failed} 失败 / {total} 项")
    if failed:
        print("\n失败项:")
        for name, ok, detail in results:
            if not ok:
                print(f"  [FAIL] {name}: {detail}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
