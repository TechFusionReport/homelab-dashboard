# Live preview deployment

The Linux preview uses a separate Compose project and a loopback-only host health API. It does not replace an existing Homepage installation or modify media container configuration.

Generate config/services.yaml with `python scripts/render_services.py`. Create the preview runtime with `python scripts/bootstrap.py --target preview`. It writes local/preview-homepage (config templates plus custom.css and custom.js) and local/preview.env, and adds the preview title suffix and badge. Production templates in config/ carry no preview labels; CI rejects them. Existing runtime files are kept; pass `--overwrite` to refresh them from config/ after a template change. Store collector configuration in local/health.json. These paths are ignored by Git. Pin HOMEPAGE_IMAGE to a tested release or digest.

The collector reads local app API keys from the apps' XML configuration. Keys never enter its JSON responses. HTTP checks indicate reachability, while Radarr/Sonarr/Prowlarr health is checked through their APIs. qBittorrent transfer metrics require existing API authorization; an authorization gap is explicit. Playback session counts and Threadfin guide freshness are not implemented yet.

The storage collector verifies the exact SMB mount before reading capacity. It invokes the configured existing read-only health script, observes the watchdog service, and compares playback library mounts to the same share. A failing health script marks storage Degraded without discarding the mount and capacity results. It never remounts storage, restarts media apps, or initiates downloads. Filesystem probes use bounded subprocesses so an unresponsive SMB mount does not hang HTTP requests. Data older than 90 seconds becomes unknown/stale.

Run the collector under a dedicated systemd unit using deploy/homelab-preview-health.service.example, replacing the user and checkout path. The service user needs read access to app config only. The container count comes from a container-list-only Docker API proxy (`docker_api` in local/health.json, for example `http://127.0.0.1:2375`); do not add the service user to the `docker` group, and do not give Homepage the Docker socket. Without `docker_api` the count shows as unavailable.

```sh
docker compose --env-file local/preview.env -f deploy/preview.compose.yaml up -d
```

Homepage binds only to 127.0.0.1:3080; the collector binds to 127.0.0.1:3081.

## Remote access

The preview is published at https://homelab-preview.techfusionreport.com through the existing homelab-pi Cloudflare Tunnel, which forwards to 127.0.0.1:3080. A Cloudflare Access application on that hostname admits only the owner's identities; anonymous requests receive the Access login redirect. Homepage itself has no authentication, so never route a hostname to it without an Access application in front.

Add the public hostname to HOMEPAGE_ALLOWED_HOSTS in local/preview.env alongside the loopback entries. Allowed hosts are request validation, not authentication.

SSH forwarding remains available as a fallback for review without the tunnel:

```sh
ssh -N -L 3080:127.0.0.1:3080 YOUR_MEDIA_HOST
```

Then open http://localhost:3080. This is a preview, not production. The production deployment must use main, separate runtime configuration, and its own hostname and Access application.

Validate with `python scripts/check_repo.py`, `python -m unittest discover -s tests`, and Docker Compose config validation. Backup freshness, per-workflow n8n health, authenticated playback metrics, and guide freshness remain explicit follow-up integrations rather than fabricated healthy states.
