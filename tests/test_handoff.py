"""Author: Codex | Created: 2026-11-21 17:00:00 +08:00 | AI/workbench handoff regressions."""
import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.services import projects as proj
from backend.app.models import Storyboard,Scene,Approvals,SceneApproval
class HandoffTest(unittest.TestCase):
    """Check scene-based review readiness and an explicit next action for AI."""
    def test_unknown_approval_cannot_confirm_current_scene(self):
        """Approval counts cannot substitute for matching scene IDs."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="hello",startMs=0,endMs=1000,visualIntent="text")]))
            proj._save_approvals(Approvals(projectId="p",approvals=[SceneApproval(sceneId="OTHER",approvalStatus="NO_MOTION",locked=True)]))
            self.assertFalse(proj.project_status("p")["allConfirmed"])
            brief=proj.review_brief("p")
            self.assertEqual(brief["scenes"][0]["approvalStatus"],"PENDING")
            self.assertEqual(brief["nextAction"],"WAIT_FOR_REVIEW")
    def test_reselection_and_notes_reach_ai(self):
        """A continuation packet contains user feedback and unlocked scene IDs."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="hello",startMs=0,endMs=1000,visualIntent="text")]))
            proj.request_reselect("p","S1","use a comparison")
            brief=proj.review_brief("p")
            self.assertEqual(brief["nextAction"],"RECOMMEND_AGAIN")
            self.assertEqual(brief["scenes"][0]["modificationNotes"],"use a comparison")
    def test_publish_storyboard_and_output_feedback(self):
        """AI publishes a local JSON and receives file-specific workbench feedback on continuation."""
        import importlib.util,json
        from types import SimpleNamespace
        from backend.app.routers.projects import save_output_review,OutputFeedback,list_outputs
        spec=importlib.util.spec_from_file_location("handoff_cli",Path(__file__).resolve().parents[1]/"scripts/motion_studio.py")
        cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)/"projects"):
            source=Path(temp)/"incoming.json"
            source.write_text(json.dumps({"projectId":"p","scenes":[{"sceneId":"S1","narration":"hello","startMs":0,"endMs":1000,"visualIntent":"text"}]}),encoding="utf-8")
            args=SimpleNamespace(project="p",input=str(source),expected_revision=0)
            self.assertEqual(cli.cmd_publish_storyboard(args),0)
            self.assertEqual(cli.cmd_publish_storyboard(args),2)
            proj.output_dir("p").mkdir()
            proj.output_dir("p").joinpath("v1.mp4").write_bytes(b"test filename only")
            save_output_review("p",OutputFeedback(file="v1.mp4",notes="revise at 00:12"))
            self.assertEqual(list_outputs("p")["outputs"][0]["notes"],"revise at 00:12")
            self.assertEqual(proj.review_brief("p")["outputReviews"][0]["notes"],"revise at 00:12")

if __name__=="__main__":unittest.main()
