# Homelab Dashboard

A personal dashboard for home systems, media services, storage, and the shared infrastructure they depend on.

This project is separate from TechFusion ops. n8n and Oracle are included only for their homelab functions. Business workflows, publishing pipelines, analytics, and unrelated workloads are outside its scope.

## Status

Homepage preview with a read-only host health collector, media API health and queues, SMB mount verification, watchdog observation, and dependency reachability. See [preview deployment](docs/preview.md). Backup freshness, authenticated playback statistics, and per-workflow n8n monitoring are not connected yet.

## Start locally

Requires Python 3 and Docker Compose.

`preview` is for development and verification; `main` is production. Changes reach main only through a preview-to-main pull request. See [release rules](docs/releases.md). The starter has no automatic deployment yet.

```sh
python scripts/bootstrap.py
# Edit .env locally with your service URLs and credentials.
docker compose config --quiet
docker compose up -d
```

Open http://localhost:3000. The default port binding is loopback only. Homepage does not supply authentication: put an authenticated reverse proxy in front of it before making it accessible beyond the host. Allowed hostnames are request validation, not authentication.

The example image is pinned to Homepage v2.7.0. Test image updates in preview before production promotion.

## Layout

- `config/`: public Homepage templates using environment variable placeholders.
- `local/`: ignored runtime configuration, initialized by bootstrap.
- `.env.example`: placeholder settings; `.env` is private and ignored.
- `docs/scope.md`: inclusion rules and monitoring behavior.
- `docs/roadmap.md`: implementation sequence and acceptance criteria.
- `collectors/README.md`: contract for future local health collectors.

## Media services

The starter includes Prowlarr, Radarr, Sonarr, qBittorrent, Jellyfin, Plex, and Threadfin links. The host collector supplies app health and queue metrics through Homepage Custom API widgets; playback services begin with reachability checks. qBittorrent transfer metrics require API authorization. Populate the private URLs and credentials before expecting valid readings. An HTTP response alone does not prove the media pipeline is healthy.

The full design follows discovery ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ download ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ import ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ library ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ playback/live TV, with SMB storage and its watchdog treated as first-class dependencies.

## Public source, private deployment

Commit reusable code and placeholder templates only. Keep credentials, real host addresses, personal inventory, SMB details, logs, download titles, and viewing activity out of Git. Do not copy existing workflow exports into this repository. Local configuration changes belong under `local/` or in `.env`, not in public templates.

No open-source license is selected yet.

## Upstream references

- [Homepage Docker setup](https://gethomepage.dev/installation/docker/)
- [Environment variable substitution](https://gethomepage.dev/installation/)
- [Service widgets](https://gethomepage.dev/widgets/services/)
- [Custom API widget](https://gethomepage.dev/widgets/services/customapi/)
