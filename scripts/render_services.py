"""Generate public Homepage templates without requiring a YAML dependency."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def card(name, description, endpoint, fields, href=None):
    lines = [f'    - {name}:', f'        description: {json.dumps(description, ensure_ascii=False)}']
    if href:
        lines.append(f'        href: "{{{{HOMEPAGE_VAR_{href}_URL}}}}"')
    lines += ['        widget:', '          type: customapi', f'          url: "{{{{HOMEPAGE_VAR_HEALTH_URL}}}}/{endpoint}"', '          refreshInterval: 15000', '          mappings:']
    for field, label in fields:
        lines += [f'            - field: {field}', f'              label: {json.dumps(label)}', '              format: text']
    return '\n'.join(lines)


groups = []
def group(name, cards):
    groups.append(f'- {name}:\n' + '\n'.join(cards))

group('Overview', [card('Needs attention', 'Live checks · failures are grouped by the systems they affect', 'summary', [('status','Overall'),('details','Attention'),('checked','Last checked'),('coverage','Coverage')])])
group('Media Server', [
    card('Prowlarr', 'DISCOVER · Indexers and app health', 'services/prowlarr', [('status','Health'),('warnings','Warnings'),('version','Version')], 'PROWLARR'),
    card('Radarr', 'MOVIES · Search → download → import', 'services/radarr', [('status','Health'),('queued','Queued'),('wanted','Missing'),('blocked','Queue warnings')], 'RADARR'),
    card('Sonarr', 'TELEVISION · Search → download → import', 'services/sonarr', [('status','Health'),('queued','Queued'),('wanted','Missing'),('blocked','Queue warnings')], 'SONARR'),
    card('qBittorrent', 'TRANSFER · Download and seeding connection', 'services/qbittorrent', [('status','Service'),('connection','Transfer API'),('download','Down MiB/s'),('upload','Up MiB/s')], 'QBITTORRENT'),
    card('Jellyfin', 'PLAYBACK · Library and live TV', 'services/jellyfin', [('status','Service'),('version','Version')], 'JELLYFIN'),
    card('Plex', 'PLAYBACK · Personal media library', 'services/plex', [('status','Service'),('observed_at','Last checked')], 'PLEX'),
    card('Threadfin', 'LIVE TV · Playlist and tuner bridge', 'services/threadfin', [('status','Service'),('observed_at','Last checked')], 'THREADFIN')
])
group('Storage & Protection', [
    card('Media storage', 'Download and import dependency · expected SMB share verified', 'storage', [('mount','Mount'),('free_gib','Free GiB'),('used_percent','Used %'),('libraries','Playback mounts')]),
    card('Storage watchdog', 'Read-only observation of the existing watchdog; no recovery actions', 'storage', [('watchdog','Watchdog'),('probe','Storage probe'),('status','Storage state'),('observed_at','Last checked')]),
    card('Backups', 'No green status without evidence of a successful backup', 'backups', [('status','Monitor'),('last_success','Last success')])
])
group('Infrastructure', [
    card('Media host', 'Pi resources · sampled on the host, outside container namespaces', 'host', [('load','Load 1m'),('memory_percent','Memory %'),('temperature','Temp °C'),('containers','Running containers'),('uptime_hours','Uptime hours')]),
    card('Windows media host', 'SMB service availability; filesystem health is shown above', 'services/windows', [('status','SMB'),('observed_at','Last checked')]),
    card('Oracle cloud', 'Shared dependency · existing Glances metrics over the mesh', 'services/oracle', [('status','Health'),('cpu_percent','CPU %'),('memory_percent','Memory %')]),
    card('Hetzner', 'Shared infrastructure host · reachability only', 'services/hetzner', [('status','SSH connection'),('observed_at','Last checked')])
])
group('Network & Home', [
    card('Pi-hole', 'Home DNS interface · query-level checks are not connected yet', 'services/pihole', [('status','Web interface'),('observed_at','Last checked')], 'PIHOLE'),
    card('Home Assistant', 'Home automation availability', 'services/homeassistant', [('status','Service'),('observed_at','Last checked')], 'HOMEASSISTANT'),
    card('LAN monitor', 'Local network inventory interface', 'services/netalertx', [('status','Service'),('observed_at','Last checked')], 'NETALERTX')
])
group('Shared Dependencies', [
    card('n8n', 'Availability only · business workflows stay outside this dashboard', 'services/n8n', [('status','Service'),('observed_at','Last checked')], 'N8N'),
    card('Vaultwarden', 'Personal credential service availability', 'services/vaultwarden', [('status','Service'),('observed_at','Last checked')], 'VAULTWARDEN'),
    card('Syncthing', 'Personal sync service availability; file contents are excluded', 'services/syncthing', [('status','Service'),('observed_at','Last checked')], 'SYNCTHING')
])

if __name__ == '__main__':
    (ROOT / 'config' / 'services.yaml').write_text('\n\n'.join(groups) + '\n', encoding='utf-8')
