# Preview and production

`main` represents production. `preview` is the integration and verification branch. All changes must pass through preview, then a preview-to-main PR, before production use.

1. Start work on preview or create a feature branch from preview.
2. Merge any feature PR into preview.
3. Validate the preview version. When a preview deployment exists, verify it there using separate runtime settings and ports.
4. Open a PR from this repository's preview branch into main. Include the PR template's Summary, Why, Validation, Next, Agent, Task, and Risk fields.
5. Require successful branch-policy and metadata checks, then merge the PR with a merge commit. Preserve preview; merge main back into preview as needed.
6. Deploy production only from main. No automatic deployment exists in the starter yet, and neither the branch nor a passing check proves a live preview has been deployed.

Main protection requires pull requests, prevents deletion and force pushes, and has no bypass actors. Required checks enforce the preview source and metadata footer. These checks establish the promotion route; actual functional preview testing must be recorded in the PR.

The PR template and metadata convention follow the Automations/Website repositories, adapted so a homelab task does not require a business task tracker.
