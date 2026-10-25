# Scope and health rules

Include a system when it helps operate home systems or personal services.

Fully included: Jellyfin, Plex, Threadfin, Prowlarr, Radarr, Sonarr, qBittorrent, their hosts, media storage, home networking, DNS, Home Assistant, personal backups, and personal supporting services.

Shared dependencies: n8n availability plus explicitly allowed homelab workflows; Oracle host, mesh connectivity, and designated personal storage resources. Do not pull all business workflows or storage into this dashboard. Record the actual inventory and workflow/bucket allowlists privately under local/.

Keep deployment and dashboard configuration independent of TechFusion ops. Sharing a backend or a domain does not change the dashboard's personal scope.

## Target health behavior

- Healthy: a recent successful check supports normal operation.
- Degraded: reachable but a function or dependency is impaired.
- Down: checks establish unavailability.
- Unknown/stale: no trustworthy recent observation; never assume healthy.

Every custom observation must carry its timestamp. Separate HTTP reachability from functional pipeline health. Group related failures under the underlying dependency, while retaining each component's observed state. An idle torrent or a wanted episode alone is not an incident.

Planned refresh targets: transfers 15 seconds, availability 60 seconds, capacity 60 seconds, backup freshness 15 minutes. Actual schedules must be configured during monitoring integration.
