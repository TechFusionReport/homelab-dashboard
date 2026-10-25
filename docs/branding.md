# Area J Homelab

The selected identity is the violet/amber AJ monogram with the wide AREA J wordmark and HOMELAB descriptor. It belongs to the personal homelab, independently of TechFusion Report.

- `branding/source/area-j-logo.png` is the user-approved original artwork, preserved byte-for-byte. It is not served. The header uses `assets/area-j-logo.jpg`, a 768×512 resize of it (about 26 KB instead of 1.4 MB, ample for the 372×248 CSS-pixel header at 2× density). CSS framing removes excess visual margins.
- `branding/source/area-j-icon.png` is the standalone AJ extraction. `assets/area-j-icon.png` is its 64×64 favicon export (about 2 KB).
- Only `assets/` is mounted read-only at `/app/public/images` in both Compose definitions, so the full-size originals never reach the browser. Regenerate exports from `branding/source/` when the artwork changes; never edit the originals.

## Image provenance

Created with the built-in image-generation tool. The approved image was generated from the Area J concept sheet by retaining the top-right AJ monogram and stacked layout, adopting the bottom-right lettering style, and keeping off-white AREA J and amber HOMELAB text on graphite. The favicon was generated with: "Output ONLY the exact intertwined angular AJ monogram from above the AREA J wordmark, on a genuinely transparent square background. Preserve the original geometry, violet A, warm amber J, relative stroke thickness and negative space. Remove both text lines and the graphite background. Center it with about 10% transparent padding."

The browser title and favicon identify Area J; the preview title suffix and badge are added only to the preview runtime by `scripts/bootstrap.py --target preview`. Color palette choices stay browser-local. Production still follows preview-to-main PR review.
