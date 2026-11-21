"""Author: Codex | Modified: 2026-11-21 23:55:00 +08:00 | Verify selected candidate parameters reach rendering."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
spec = importlib.util.spec_from_file_location("motion_cli", Path(__file__).resolve().parents[1] / "scripts/motion_studio.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
class ScenePropsTest(unittest.TestCase):
    """Protect the planning-to-render parameter contract."""
    def test_bound_background_uses_shared_scene_renderer_for_every_template(self):
        """Background-only scenes must use the editor composition even without manual overrides."""
        scene=SimpleNamespace(narration="x",visualIntent="x",styleId="x",startMs=0,endMs=4200)
        for template in ("TEXT-001","FRED-STACK","NUMBER-001"):
            with patch.object(cli,"_scene_media_props",return_value={"backgroundImage":"scene-assets/test.png"}):
                result=cli._build_scene_props(scene,SimpleNamespace(templateId=template,params=[]))
            self.assertEqual(result["_editor"]["endMs"],4200)
            self.assertEqual(result["backgroundImage"],"scene-assets/test.png")

    def test_presenter_requires_real_source_in_project_renders(self):
        """Stand-ins are library demos only; project renders need a real source video."""
        scene=SimpleNamespace(narration="x",visualIntent="x",styleId="x",startMs=0,endMs=6000)
        with self.assertRaises(ValueError):cli._build_scene_props(scene,SimpleNamespace(templateId="PRESENTER-OUT",params=[]))

    def test_selected_props_override_demo_defaults(self):
        """Use real candidate content while retaining the scene style."""
        scene = SimpleNamespace(narration="真实流程", visualIntent="流程", styleId="minimal-tech")
        meta = SimpleNamespace(templateId="FLOW-001", params=[])
        result = cli._build_scene_props(scene, meta, {"nodes": ["检索", "验证"], "title": "真实内容"})
        self.assertEqual(result["nodes"], ["检索", "验证"])
        self.assertEqual(result["title"], "真实内容")
        self.assertEqual(result["styleId"], "minimal-tech")
if __name__ == "__main__":
    unittest.main()
