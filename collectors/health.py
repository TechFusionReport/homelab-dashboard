"""Read-only homelab health API. Private configuration never enters responses."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def now():
    return datetime.now(timezone.utc).isoformat()


def command(args, timeout=6):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError('Probe failed')
    return result.stdout.strip()


def json_get(url, key=None):
    request = Request(url, headers={'Accept': 'application/json', **({'X-Api-Key': key} if key else {})})
    with urlopen(request, timeout=4) as response:
        return json.loads(response.read(2_000_000))


def queue_counts(base, key, page_size=100, max_pages=10):
    """Count queue rows with status messages across pages, bounded to max_pages requests."""
    total, blocked, page = 0, 0, 1
    while page <= max_pages:
        queue = json_get(f'{base}/queue?page={page}&pageSize={page_size}', key)
        total = queue.get('totalRecords', 0)
        records = queue.get('records', [])
        blocked += sum(bool(row.get('statusMessages')) for row in records)
        if not records or page * page_size >= total:
            break
        page += 1
    return total, blocked


def check_service(item):
    result = {'id': item['id'], 'status': 'Unknown', 'version': '—', 'queued': '—', 'wanted': '—', 'warnings': '—'}
    try:
        if item.get('tcp'):
            with socket.create_connection((item['tcp']['host'], item['tcp']['port']), timeout=3):
                pass
            result['status'] = 'Reachable'
            result['observed_at'] = now()
            return result
        try:
            with urlopen(item['url'], timeout=4) as response:
                response.read(256)
            result['status'] = 'Responding'
        except HTTPError as error:
            if error.code in (401, 403):
                result['status'] = 'Responding · auth required'
            else:
                raise
        kind = item.get('kind')
        if kind == 'glances':
            base = item['url'].rstrip('/') + '/api/4'
            result['cpu_percent'] = json_get(base + '/cpu').get('total', '—')
            result['memory_percent'] = json_get(base + '/mem').get('percent', '—')
            result['status'] = 'Healthy'
        elif kind == 'jsonhealth':
            info = json_get(item['url'])
            result['status'] = 'Healthy' if info.get('status') == 'ok' else 'Degraded'
        elif kind in ('radarr', 'sonarr', 'prowlarr'):
            key = ET.parse(item['api_key_file']).getroot().findtext('ApiKey')
            if not key:
                raise ValueError('Missing key')
            base = item['url'].rstrip('/') + ('/api/v1' if kind == 'prowlarr' else '/api/v3')
            result['version'] = json_get(base + '/system/status', key).get('version', '—')
            warnings = json_get(base + '/health', key)
            result['warnings'] = len(warnings)
            result['status'] = 'Degraded' if warnings else 'Healthy'
            if kind != 'prowlarr':
                result['queued'], result['blocked'] = queue_counts(base, key)
                wanted = json_get(base + '/wanted/missing?page=1&pageSize=1', key)
                result['wanted'] = wanted.get('totalRecords', 0)
                if result['blocked']:
                    result['status'] = 'Degraded'
        elif kind == 'jellyfin':
            result['version'] = json_get(item['url'].rstrip('/') + '/System/Info/Public').get('Version', '—')
        elif kind == 'qbittorrent':
            try:
                info = json_get(item['url'].rstrip('/') + '/api/v2/transfer/info')
                result['download'] = round(info.get('dl_info_speed', 0) / 1048576, 2)
                result['upload'] = round(info.get('up_info_speed', 0) / 1048576, 2)
                result['connection'] = info.get('connection_status', 'Unknown')
            except Exception:
                result['connection'] = 'API authentication required'
    except Exception as error:
        if result['status'] != 'Unknown':
            result['status'] = 'Degraded · metrics unavailable'
        else:
            result['status'] = 'Down'
        result['error'] = type(error).__name__
    result['observed_at'] = now()
    return result


def check_storage(config):
    result = {'status': 'Unknown', 'mount': 'Unknown', 'free_gib': '—', 'used_percent': '—', 'watchdog': 'Unknown', 'probe': 'Not configured', 'libraries': 'Unknown'}
    if not config:
        return result
    try:
        source = command(['findmnt', '-rn', '-M', config['mount'], '-t', 'cifs', '-o', 'SOURCE'])
        if source != config['expected_source']:
            result.update(status='Down', mount='Unexpected filesystem', observed_at=now())
            return result
        result['mount'] = 'Expected SMB share mounted'
        lines = command(['df', '-B1', '--output=size,avail', config['mount']]).splitlines()
        total, available = map(int, lines[-1].split())
        result['free_gib'] = round(available / 1073741824, 1)
        result['used_percent'] = round((1 - available / total) * 100, 1)
        result['status'] = 'Healthy' if available >= config.get('minimum_free_gib', 30) * 1073741824 else 'Low space'
        if config.get('health_script'):
            # A failing probe degrades storage but keeps the verified mount and capacity readings.
            try:
                command([config['health_script']], timeout=25)
                result['probe'] = 'Passed (read-only)'
            except Exception as error:
                result['probe'] = 'Failed: ' + type(error).__name__
                result['status'] = 'Degraded'
        mismatches = []
        for library in config.get('library_paths', []):
            # Trigger an automount through a bounded subprocess; never touch it in the API thread.
            try:
                command(['stat', '-L', library['path']], timeout=6)
                library_source = command(['findmnt', '-rn', '-T', library['path'], '-t', 'cifs', '-o', 'SOURCE']).splitlines()[-1]
                if library_source != source:
                    mismatches.append(library['label'])
            except Exception:
                mismatches.append(library['label'])
        result['libraries'] = 'Same SMB share' if config.get('library_paths') else 'Unverified'
        if mismatches:
            result['status'] = 'Degraded'
            result['libraries'] = ', '.join(mismatches) + ': expected share not verified'
    except Exception as error:
        result['status'] = 'Down'
        result['probe'] = 'Failed: ' + type(error).__name__
    try:
        result['watchdog'] = command(['systemctl', 'is-active', config['watchdog_service']])
        if result['watchdog'] != 'active':
            result['status'] = 'Degraded'
    except Exception:
        result['watchdog'] = 'Inactive or unavailable'
        if result['status'] == 'Healthy':
            result['status'] = 'Degraded'
    result['observed_at'] = now()
    return result


def check_host(docker_api=None):
    result = {'status': 'Unknown', 'load': '—', 'memory_percent': '—', 'temperature': '—', 'containers': '—', 'uptime_hours': '—'}
    try:
        mem = {}
        for line in Path('/proc/meminfo').read_text().splitlines():
            name, value = line.split(':', 1)
            mem[name] = int(value.split()[0])
        result.update(status='Healthy', load=round(os.getloadavg()[0], 2), memory_percent=round((1-mem['MemAvailable']/mem['MemTotal'])*100, 1), uptime_hours=round(float(Path('/proc/uptime').read_text().split()[0])/3600, 1))
        thermal = Path('/sys/class/thermal/thermal_zone0/temp')
        if thermal.exists():
            result['temperature'] = round(int(thermal.read_text()) / 1000, 1)
    except Exception:
        pass
    # Count containers through a list-only Docker API proxy; the collector never needs docker group access.
    if docker_api:
        try:
            result['containers'] = len(json_get(docker_api.rstrip('/') + '/containers/json'))
        except Exception:
            pass
    result['observed_at'] = now()
    return result


def collect(config):
    # One worker per check, so a refresh takes as long as the slowest check rather than queuing behind it.
    service_configs = config.get('services', [])
    with ThreadPoolExecutor(max_workers=len(service_configs) + 2) as pool:
        service_futures = [pool.submit(check_service, item) for item in service_configs]
        storage_future = pool.submit(check_storage, config.get('storage'))
        host_future = pool.submit(check_host, config.get('docker_api'))
        services = [future.result() for future in service_futures]
        storage, host = storage_future.result(), host_future.result()
    down = [s['id'] for s in services if s['status'] == 'Down']
    degraded = [s['id'] for s in services if s['status'].startswith('Degraded')]
    issues = []
    if storage['status'] == 'Degraded' and 'expected share not verified' in storage['libraries']:
        issues.append('Playback storage: ' + storage['libraries'])
    elif storage['status'] not in ('Healthy', 'Unknown'):
        issues.append('Media storage needs attention; downloads/imports depend on it')
    if down:
        issues.append('Unavailable: ' + ', '.join(down))
    if degraded:
        issues.append('Check app health: ' + ', '.join(degraded))
    summary = {'status': 'Needs attention' if issues else 'Checks passing', 'issues': len(issues), 'details': '; '.join(issues) or 'No failures in connected checks', 'checked': now(), 'coverage': 'Backup freshness and authenticated playback metrics pending'}
    return {'summary': summary, 'storage': storage, 'host': host, 'services': {s['id']: s for s in services}, 'backups': {'status': 'Not connected', 'last_success': 'Unknown', 'detail': 'No backup monitor configured'}}


def response_view(snapshot, collected_at, path):
    """Never serve previously healthy data as current after collection stops."""
    if time.time() - collected_at > 90:
        return {'status': 'Unknown · stale data', 'details': 'No successful collection within 90 seconds', 'checked': snapshot.get('summary', {}).get('checked', 'Unknown')}
    parts = path.strip('/').split('/')
    value = snapshot
    for part in parts:
        if not part or not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def serve(config, port):
    state = {'snapshot': {}, 'collected_at': 0}
    lock = threading.Lock()
    def refresh():
        while True:
            try:
                snapshot = collect(config)
                with lock:
                    state.update(snapshot=snapshot, collected_at=time.time())
            except Exception:
                pass
            time.sleep(30)
    threading.Thread(target=refresh, daemon=True).start()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            with lock:
                value = response_view(state['snapshot'], state['collected_at'], self.path.split('?', 1)[0])
            body = json.dumps(value if value is not None else {'error': 'Not found'}).encode()
            self.send_response(200 if value is not None else 404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--port', type=int, default=3081)
    args = parser.parse_args()
    serve(json.loads(args.config.read_text()), args.port)
