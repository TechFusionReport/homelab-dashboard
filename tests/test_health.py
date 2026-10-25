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

    def test_failed_health_script_degrades_without_discarding_readings(self):
        def fake(args, timeout=6):
            if args[0] == '/probe':
                raise RuntimeError('probe failed')
            if args[0] == 'df':
                return '      Size     Avail\n1000000000000 500000000000'
            if args[0] == 'systemctl':
                return 'active'
            return '//example.invalid/media'
        config = {'mount': '/media', 'expected_source': '//example.invalid/media', 'health_script': '/probe',
                  'library_paths': [{'label': 'Plex', 'path': '/media/movies'}], 'watchdog_service': 'test', 'minimum_free_gib': 1}
        with patch.object(health, 'command', side_effect=fake):
            result = health.check_storage(config)
        self.assertEqual(result['status'], 'Degraded')
        self.assertEqual(result['probe'], 'Failed: RuntimeError')
        self.assertEqual(result['mount'], 'Expected SMB share mounted')
        self.assertEqual(result['free_gib'], 465.7)
        self.assertEqual(result['libraries'], 'Same SMB share')

    def test_queue_warnings_count_every_page(self):
        pages = {1: [{'statusMessages': ['x']}] * 100, 2: [{'statusMessages': []}, {'statusMessages': ['y']}]}
        def fake(url, key=None):
            page = int(url.split('page=')[1].split('&')[0])
            return {'totalRecords': 102, 'records': pages[page]}
        with patch.object(health, 'json_get', side_effect=fake):
            self.assertEqual(health.queue_counts('http://example.invalid/api/v3', 'k'), (102, 101))

    def test_slow_services_check_in_parallel(self):
        def slow(item):
            time.sleep(0.3)
            return {'id': item['id'], 'status': 'Healthy'}
        services = [{'id': str(n)} for n in range(20)]
        with patch.object(health, 'check_service', side_effect=slow), patch.object(health, 'check_host', return_value={'status': 'Healthy'}):
            started = time.monotonic()
            result = health.collect({'services': services})
        # Serialized behind a small pool this would take 2s or more.
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertEqual(len(result['services']), 20)

    def test_container_count_uses_docker_api_not_docker_cli(self):
        with patch.object(health, 'json_get', return_value=[{}, {}, {}]), patch.object(health, 'command', side_effect=AssertionError('no CLI')):
            result = health.check_host('http://127.0.0.1:2375')
        self.assertEqual(result['containers'], 3)
        self.assertIn('observed_at', result)

    def test_unknown_backup_is_explicit(self):
        with patch.object(health, 'check_host', return_value={'status': 'Healthy'}):
            result = health.collect({'services': []})
        self.assertEqual(result['backups']['last_success'], 'Unknown')
        self.assertIn('pending', result['summary']['coverage'])


if __name__ == '__main__':
    unittest.main()
