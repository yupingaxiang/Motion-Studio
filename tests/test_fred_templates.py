"""Author: Codex | Created: 2026-11-21 18:00:00 +08:00 | Fred source provenance and executable registration."""
import json,hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.services import library
ROOT=Path(__file__).resolve().parents[1]
class FredTemplatesTest(unittest.TestCase):
    """Verify original source identity and all four concrete runtime adapters."""
    def test_source_provenance(self):
        """Keep MIT attribution and hashes for the actual vendored source."""
        folder=ROOT/'remotion/src/components/fred'
        receipt=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
        self.assertIn('MIT License',(folder/'LICENSE').read_text(encoding='utf-8'))
        for entry in receipt['files']:
            self.assertEqual(hashlib.sha256((folder/entry['file']).read_bytes()).hexdigest(),entry['localSha256'])
    def test_real_adapter_registration(self):
        """Every external record points to imported code and a registered 4:3 composition."""
        root=(ROOT/'remotion/src/Root.tsx').read_text(encoding='utf-8')
        for tid in ['FRED-V087','FRED-STACK','FRED-RETYPE','FRED-FOCUS']:
            meta=library.get_template(tid)
            self.assertIsNotNone(meta)
            self.assertEqual(meta.sourceName,'FredTalk')
            self.assertEqual(meta.aspectRatios,['4:3'])
            self.assertIn('id="'+tid+'"',root)
            self.assertTrue(library.template_source_abs(tid).is_file())
if __name__=='__main__':unittest.main()
