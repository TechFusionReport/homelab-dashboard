import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bootstrap', Path(__file__).parents[1] / 'scripts' / 'bootstrap.py')
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)
ROOT = Path(__file__).parents[1]


class BootstrapTests(unittest.TestCase):
    def build(self, target):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'config').mkdir()
        for name in ('settings.yaml', 'widgets.yaml'):
            (root / 'config' / name).write_bytes((ROOT / 'config' / name).read_bytes())
        (root / '.env.example').write_text('')
        bootstrap.bootstrap(root, target)
        return root / bootstrap.TARGETS[target]['runtime']

    def test_preview_runtime_is_labeled(self):
        runtime = self.build('preview')
        self.assertIn('title: Area J Homelab · Preview', (runtime / 'settings.yaml').read_text(encoding='utf-8'))
        widgets = (runtime / 'widgets.yaml').read_text(encoding='utf-8')
        self.assertLess(widgets.index('- logo:'), widgets.index('- greeting:'))
        self.assertLess(widgets.index('- greeting:'), widgets.index('- datetime:'))

    def test_production_runtime_has_no_preview_labels(self):
        runtime = self.build('production')
        for name in ('settings.yaml', 'widgets.yaml'):
            self.assertNotIn('preview', (runtime / name).read_text(encoding='utf-8').lower())


if __name__ == '__main__':
    unittest.main()
