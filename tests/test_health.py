import importlib.util
from pathlib import Path
import time
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('health', Path(__file__).parents[1] / 'collectors' / 'health.py')
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class HealthTests(unittest.TestCase):
    def test_stale_data_cannot_claim_healthy(self):
        result = health.response_view({'storage': {'status': 'Healthy'}}, time.time()-91, '/storage')
        self.assertIn('stale', result['status'])

    def test_missing_mount_never_reports_local_disk_capacity(self):
        with patch.object(health, 'command', side_effect=RuntimeError('missing')):
            result = health.check_storage({'mount': '/not-mounted', 'expected_source': '//example.invalid/media', 'watchdog_service': 'test'})
        self.assertEqual(result['status'], 'Down')
        self.assertEqual(result['free_gib'], '—')

    def test_wrong_share_is_rejected(self):
        with patch.object(health, 'command', return_value='//example.invalid/wrong'):
            result = health.check_storage({'mount': '/media', 'expected_source': '//example.invalid/media'})
        self.assertEqual(result['mount'], 'Unexpected filesystem')

    def test_unavailable_api_does_not_expose_url_or_credentials(self):
        with patch.object(health, 'urlopen', side_effect=OSError('secret-url-and-key')):
            result = health.check_service({'id': 'radarr', 'url': 'http://example.invalid', 'kind': 'radarr'})
        self.assertEqual(result['status'], 'Down')
        self.assertNotIn('secret', str(result))

    def test_unknown_backup_is_explicit(self):
        with patch.object(health, 'check_host', return_value={'status': 'Healthy'}):
            result = health.collect({'services': []})
        self.assertEqual(result['backups']['last_success'], 'Unknown')
        self.assertIn('pending', result['summary']['coverage'])


if __name__ == '__main__':
    unittest.main()
