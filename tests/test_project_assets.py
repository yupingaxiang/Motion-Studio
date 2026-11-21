"""Author: Codex | Created: 2026-11-21 16:00:00 +08:00 | Isolated asset binding regressions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unittest
from unittest.mock import patch
from backend.app.services import projects as proj
from backend.app.models import Storyboard,Scene,AssetRecord,Approvals,SceneApproval
class BindingTest(unittest.TestCase):
    """Validate revision and lock checks without changing user data."""
    def test_locked_scene_rejects_binding(self):
        """Confirmed scenes must not silently change their media."""
        sb=Storyboard(projectId="test",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=1000,visualIntent="x")])
        ap=Approvals(projectId="test",approvals=[SceneApproval(sceneId="S1",locked=True,approvalStatus="APPROVED")])
        with patch.object(proj,"read_storyboard",return_value=sb),patch.object(proj,"read_approvals_safe",return_value=ap):
            with self.assertRaises(PermissionError):proj.bind_scene_asset("test","S1","a","test",1)
    def test_stale_revision_rejects_binding(self):
        """Concurrent editors cannot overwrite a newer storyboard."""
        sb=Storyboard(projectId="test",projectRevision=2,scenes=[])
        with patch.object(proj,"read_storyboard",return_value=sb):
            with self.assertRaises(ValueError):proj.bind_scene_asset("test","S1","a","test",1)
    def test_upload_bind_and_clear_project_image(self):
        """Persist uploaded image metadata, bind its real path and clear it without touching other refs."""
        import tempfile, io, asyncio
        from fastapi import UploadFile
        from backend.app.routers.assets import import_asset
        from backend.app.services import library as lib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            project=root/"projects"/"sample"
            project.mkdir(parents=True)
            with patch.object(lib,"projects_root",return_value=root/"projects"),patch.object(proj,"projects_root",return_value=root/"projects"),patch.object(lib,"library_root",return_value=root/"library"):
                sb=Storyboard(projectId="sample",scenes=[Scene(sceneId="S1",narration="x",startMs=0,endMs=1000,visualIntent="x")])
                proj.write_storyboard(sb)
                data=Path(__file__).resolve().parents[1].joinpath("library/motions/TEXT-001/poster.jpg").read_bytes()
                result=asyncio.run(import_asset(file=UploadFile(filename="test.jpg",file=io.BytesIO(data)),scope="sample",tags="test",source="local",license="test"))
                record=result["asset"]
                updated=proj.bind_scene_asset("sample","S1",record["assetId"],"sample",1)
                self.assertEqual(updated.projectRevision,2)
                ref=updated.scenes[0].assets[0]
                self.assertTrue((root/ref.localPath).is_file())
                self.assertEqual(lib.load_asset_registry("sample")[0].source,"local")
                cleared=proj.bind_scene_asset("sample","S1","","sample",2)
                self.assertEqual(cleared.scenes[0].assets,[])

    def test_invalid_scope_is_rejected(self):
        """Never traverse directories through a folder selector."""
        from backend.app.routers.assets import _validate_scope
        from fastapi import HTTPException
        with self.assertRaises(HTTPException): _validate_scope("../outside")

if __name__=="__main__":unittest.main()
