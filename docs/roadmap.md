# Implementation roadmap

## 1. Starter repository — included

Public templates, local environment settings, Homepage Compose definition, media service widgets, scope rules, and non-overwriting bootstrap.

## 2. Verify inventory and connect services

Confirm host/service locations, existing monitoring instances, app versions, access paths, API credentials, and storage mount behavior. Fill private settings and verify widget compatibility. Add infrastructure, network, core service, and backup groups using confirmed data. Keep the dashboard authenticated and independent of the ops interface.

Acceptance: every configured service has a meaningful status or an explicit unknown state; no placeholder is presented as a live reading.

## 3. Functional media health

Integrate the existing storage-health script and watchdog without changing their recovery behavior. Check mount identity and capacity; distinguish local fallback directories from a mounted SMB filesystem. Collect indexer failures, download errors, import errors, last successful imports, playback reachability, and guide freshness where supported.

Acceptance: a disconnected SMB share raises a storage incident and explains affected downloads/imports even if app HTTP checks succeed. Stale collector data is explicit.

## 4. Attention and maintenance

Aggregate incidents, link to useful app/log views, add backup freshness and disk pressure, and allowlist homelab workflows in the shared n8n instance. Reuse existing alert infrastructure, with deduplication and recovery notifications. Do not create notification workflows until the delivery destination is selected.

Acceptance: the first screen answers what is broken, its personal impact, and where to investigate. Controls, if added later, are targeted and require appropriate authorization.
