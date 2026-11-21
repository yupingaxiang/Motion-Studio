"""Author: Codex | Created: 2026-11-21 21:00:00 +08:00 | Versioned scene editor persistence and lock regressions."""
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.services import projects as proj
from backend.app.models import Storyboard,Scene,Approvals,SceneApproval
class EditorTest(unittest.TestCase):
    """Persist edits as separate reviewable data without altering recommendations."""
    def test_save_revision_conflict_and_handoff(self):
        """Saved overrides survive rereads, enter AI packet, and stale edits fail."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="hello",startMs=0,endMs=4000,visualIntent="text")]))
            result=proj.save_scene_edit("p","S1",{"templateId":"TEXT-001","templateVersion":"1.1.0","props":{"keyword":"edited"},"startMs":0,"endMs":3000},0)
            self.assertEqual(result["revision"],1)
            self.assertEqual(proj.review_brief("p")["sceneEdits"]["scenes"]["S1"]["props"]["keyword"],"edited")
            with self.assertRaises(ValueError):proj.save_scene_edit("p","S1",result["scenes"]["S1"],0)
    def test_locked_scene_rejects_changes(self):
        """Confirmed scenes require explicit unlock before any visual edit."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=4000,visualIntent="x")]))
            proj._save_approvals(Approvals(projectId="p",approvals=[SceneApproval(sceneId="S1",locked=True,approvalStatus="APPROVED")]))
            with self.assertRaises(PermissionError):proj.save_scene_edit("p","S1",{},0)
if __name__=="__main__":unittest.main()
