# Live preview deployment

The Linux preview uses a separate Compose project and a loopback-only host health API. It does not replace an existing Homepage installation or modify media container configuration.

Generate config/services.yaml with `python scripts/render_services.py`. Copy config templates, including custom.css, to local/preview-homepage. Store runtime environment settings in local/preview.env and collector configuration in local/health.json. These paths are ignored by Git. Pin HOMEPAGE_IMAGE to a tested release or digest.

The collector reads local app API keys from the apps' XML configuration. Keys never enter its JSON responses. HTTP checks indicate reachability, while Radarr/Sonarr/Prowlarr health is checked through their APIs. qBittorrent transfer metrics require existing API authorization; an authorization gap is explicit. Playback session counts and Threadfin guide freshness are not implemented yet.

The storage collector verifies the exact SMB mount before reading capacity. It invokes the configured existing read-only health script, observes the watchdog service, and compares playback library mounts to the same share. It never remounts storage, restarts media apps, or initiates downloads. Filesystem probes use bounded subprocesses so an unresponsive SMB mount does not hang HTTP requests. Data older than 90 seconds becomes unknown/stale.

Run the collector under a dedicated systemd unit using deploy/homelab-preview-health.service.example, replacing the user and checkout path. It requires the existing user's read access to app config and Docker listing permission for the container count. Do not grant access to the Docker socket to Homepage.

```sh
docker compose --env-file local/preview.env -f deploy/preview.compose.yaml up -d
```

Homepage binds only to 127.0.0.1:3080; the collector binds to 127.0.0.1:3081. Use SSH forwarding for local review:

```sh
ssh -N -L 3080:127.0.0.1:3080 YOUR_MEDIA_HOST
```

Then open http://localhost:3080. This is a preview, not production. The production deployment must use main and separate runtime configuration. An authenticated remote-access policy must be established before publishing beyond loopback.

Validate with `python -m unittest discover -s tests` and Docker Compose config validation. Backup freshness, per-workflow n8n health, authenticated playback metrics, and guide freshness remain explicit follow-up integrations rather than fabricated healthy states.
