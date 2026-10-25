# Repository rules

- This repository is personal homelab only. Shared services are included only for their personal functions. Keep it independent of TechFusion ops.
- `main` is production. Never push changes directly to `main` or bypass its rules.
- All changes must land on `preview` before promotion. Develop on `preview` or a `codex/` branch based on it; feature PRs target `preview`.
- Production promotion is a PR from this repository's `preview` branch into `main`. No other source branch may merge into `main`.
- Keep `preview` after promotion. Use a merge commit for preview-to-main promotion to preserve branch ancestry. Merge `main` back into `preview` as needed; never reset or force-push either branch.
- Include Summary, Why, Validation, Next, and real Agent/Task/Risk metadata in PR descriptions. Personal tasks may use `N/A — homelab setup` rather than require a business tracker.
- Run relevant validation before promotion. Check both the branch-policy and PR metadata jobs.
- Keep credentials, personal addresses/inventory, live logs, and media activity in ignored local configuration. Do not commit existing automation exports.
- `main` is the only production deployment source. Preview and production must use separate runtime folders, ports, and settings. This starter has no automated deployment configured; a merge does not deploy it yet.

- Push preview changes and open promotion PRs without asking for permission. The user reviews and merges production PRs. Do not merge into main on their behalf.
