# Read-only health collector

`health.py` runs on the Linux media host and exposes sanitized JSON only on loopback. It gathers app health, queues, host resources, SMB capacity, playback mount consistency, and existing watchdog state. It never initiates downloads or controls media containers.

Configure services and storage under ignored `local/health.json`. App API keys are read directly from existing local XML configuration; credentials and paths never enter responses. qBittorrent transfer stats require existing API authorization. Backup freshness and authenticated playback stats are explicitly unconnected until integrated.

The collector caches observations for fast HTTP responses. Observations older than 90 seconds become unknown/stale. Filesystem commands have bounded timeouts. See [preview deployment](../docs/preview.md) for installation and tests.
