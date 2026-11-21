"""Author: Codex | Created: 2026-11-21 15:00:00 +08:00 | Verify selected candidate parameters reach rendering."""
import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
spec = importlib.util.spec_from_file_location("motion_cli", Path(__file__).resolve().parents[1] / "scripts/motion_studio.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
class ScenePropsTest(unittest.TestCase):
    """Protect the planning-to-render parameter contract."""
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
