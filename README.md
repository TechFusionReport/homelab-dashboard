# Homelab Dashboard

A personal dashboard for home systems, media services, storage, and the shared infrastructure they depend on.

This project is separate from TechFusion ops. n8n and Oracle are included only for their homelab functions. Business workflows, publishing pipelines, analytics, and unrelated workloads are outside its scope.

## Status

Initial Homepage scaffold. It is not deployed or connected to live systems yet. Storage checks, watchdog integration, incident aggregation, and workflow filtering are planned; the starter does not claim to provide them.

## Start locally

Requires Python 3 and Docker Compose.

```sh
python scripts/bootstrap.py
# Edit .env locally with your service URLs and credentials.
docker compose config --quiet
docker compose up -d
```

Open http://localhost:3000. The default port binding is loopback only. Homepage does not supply authentication: put an authenticated reverse proxy in front of it before making it accessible beyond the host. Allowed hostnames are request validation, not authentication.

The example image uses the upstream latest tag for initial evaluation. Set HOMEPAGE_IMAGE to a tested release tag or digest before production use.

## Layout

- `config/`: public Homepage templates using environment variable placeholders.
- `local/`: ignored runtime configuration, initialized by bootstrap.
- `.env.example`: placeholder settings; `.env` is private and ignored.
- `docs/scope.md`: inclusion rules and monitoring behavior.
- `docs/roadmap.md`: implementation sequence and acceptance criteria.
- `collectors/README.md`: contract for future local health collectors.

## Media services

The starter includes Prowlarr, Radarr, Sonarr, qBittorrent, Jellyfin, Plex, and Threadfin links. Native metrics are configured for the first five; Plex and Threadfin begin as links and HTTP availability checks. Populate the private URLs and credentials before expecting valid readings. An HTTP response alone does not prove the media pipeline is healthy.

The full design follows discovery → download → import → library → playback/live TV, with SMB storage and its watchdog treated as first-class dependencies.

## Public source, private deployment

Commit reusable code and placeholder templates only. Keep credentials, real host addresses, personal inventory, SMB details, logs, download titles, and viewing activity out of Git. Do not copy existing workflow exports into this repository. Local configuration changes belong under `local/` or in `.env`, not in public templates.

No open-source license is selected yet.

## Upstream references

- [Homepage Docker setup](https://gethomepage.dev/installation/docker/)
- [Environment variable substitution](https://gethomepage.dev/installation/)
- [Service widgets](https://gethomepage.dev/widgets/services/)
- [Custom API widget](https://gethomepage.dev/widgets/services/customapi/)
