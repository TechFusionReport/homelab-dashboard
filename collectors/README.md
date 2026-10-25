# Planned local collectors

No collector is implemented in this starter. Reuse existing monitoring before adding agents.

The first adapter should expose sanitized results from the media storage health script and watchdog. It should run on the host with the real mount namespace, rather than mistake a container's filesystem for the SMB mount.

Suggested JSON fields: `observed_at`, `status`, `mount_present`, `expected_source_matches`, `writable`, `free_bytes`, `total_bytes`, `watchdog_last_check`, `watchdog_last_result`, and `reason`.

Use `unknown` when checks cannot run. Require bounded timeouts, handle stale data, avoid returning credentials, real share paths, media titles, or raw logs. A writable check requires a controlled temporary probe in an approved directory; it is not a read-only check. Do not remount storage, restart apps, or initiate downloads as a side effect of monitoring.

Expose collector output only to the private dashboard/monitoring network. Homepage's Custom API widget can consume the sanitized endpoint once implemented.
