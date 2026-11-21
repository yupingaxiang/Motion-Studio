"""Author: Codex | Modified: 2026-11-21 23:00:00 +08:00 | Versioned scene editor persistence and lock regressions."""
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
    def test_element_offsets_persist_and_reject_invalid_values(self):
        """Individual offsets survive the AI handoff; malformed IDs and nonfinite values are rejected."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=4000,visualIntent="x")]))
            base={"templateId":"TEXT-001","templateVersion":"1.1.0","props":{"keyword":"ok"},"endMs":3000,"elements":{"keyword":{"x":123,"y":-45}}}
            result=proj.save_scene_edit("p","S1",base,0)
            self.assertEqual(result["scenes"]["S1"]["elements"]["keyword"],{"x":123,"y":-45})
            self.assertEqual(proj.review_brief("p")["sceneEdits"]["scenes"]["S1"]["elements"],base["elements"])
            for offsets in ({"bad]id":{"x":0,"y":0}},{"keyword":{"x":float("nan"),"y":0}},{"keyword":{"x":9999,"y":0}}):
                with self.assertRaises(ValueError):proj.save_scene_edit("p","S1",{**base,"elements":offsets},1)

    def test_locked_scene_rejects_changes(self):
        """Confirmed scenes require explicit unlock before any visual edit."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=4000,visualIntent="x")]))
            proj._save_approvals(Approvals(projectId="p",approvals=[SceneApproval(sceneId="S1",locked=True,approvalStatus="APPROVED")]))
            with self.assertRaises(PermissionError):proj.save_scene_edit("p","S1",{},0)
    def test_editor_props_override_ai_proposal(self):
        """A selected matching candidate renders the user's edits instead of stale AI values."""
        import importlib.util
        from types import SimpleNamespace
        from backend.app.models import Recommendations,SceneRecommendation,Candidate
        spec=importlib.util.spec_from_file_location("editor_cli",Path(__file__).resolve().parents[1]/"scripts/motion_studio.py")
        cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        rec=Recommendations(projectId="p",scenes=[SceneRecommendation(sceneId="S1",candidates=[Candidate(templateId="TEXT-001",templateVersion="1.1.0",previewPath="real.mp4",recommendationReason="text",proposedProps={"keyword":"old"})])])
        saved={"scenes":{"S1":{"templateId":"TEXT-001","templateVersion":"1.1.0","props":{"keyword":"manual"},"startMs":500,"endMs":3000,"elements":{"keyword":{"x":120,"y":10}},"layout":{"x":80,"y":0,"scale":.8,"transparent":True}}}}
        with patch.object(proj,"read_recommendations",return_value=rec),patch.object(proj,"read_scene_edits",return_value=saved):
            result=cli._selected_candidate_props("p","S1",SimpleNamespace(selectedTemplateId="TEXT-001",selectedTemplateVersion="1.1.0"))
            self.assertEqual(result["keyword"],"manual")
            self.assertEqual(result["_editor"]["startMs"],500)
            self.assertEqual(result["_editor"]["elements"]["keyword"]["x"],120)
            saved["scenes"]["S1"]["templateVersion"]="changed"
            with self.assertRaises(ValueError):cli._selected_candidate_props("p","S1",SimpleNamespace(selectedTemplateId="TEXT-001",selectedTemplateVersion="1.1.0"))

    def test_out_of_bounds_and_undeclared_parameters_rejected(self):
        """Invalid editable payloads never reach components or persisted files."""
        with tempfile.TemporaryDirectory() as temp,patch.object(proj,"projects_root",return_value=Path(temp)):
            proj.write_storyboard(Storyboard(projectId="p",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=4000,visualIntent="x")]))
            base={"templateId":"TEXT-001","templateVersion":"1.1.0","props":{"keyword":"ok"},"startMs":0,"endMs":5000}
            with self.assertRaises(ValueError):proj.save_scene_edit("p","S1",base,0)
            base["endMs"]=3000;base["props"]={"keyword":["wrong type"]}
            with self.assertRaises(ValueError):proj.save_scene_edit("p","S1",base,0)
            base["props"]={"arbitrary":"value"}
            with self.assertRaises(ValueError):proj.save_scene_edit("p","S1",base,0)

if __name__=="__main__":unittest.main()
