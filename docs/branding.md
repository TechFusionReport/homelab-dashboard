# Area J Homelab

The selected identity is the violet/amber AJ monogram with the wide AREA J wordmark and HOMELAB descriptor. It belongs to the personal homelab, independently of TechFusion Report.

- `assets/area-j-logo.png` is the user-approved original artwork, preserved byte-for-byte. The header uses CSS framing to remove excess visual margins; no generated replacement or glow export is used.
- `assets/area-j-icon.png` is the standalone AJ extraction used as the favicon.
- Assets are mounted read-only at `/app/public/images` in both Compose definitions. No image-generation directory is needed at runtime.

## Image provenance

Created with the built-in image-generation tool. The approved image was generated from the Area J concept sheet by retaining the top-right AJ monogram and stacked layout, adopting the bottom-right lettering style, and keeping off-white AREA J and amber HOMELAB text on graphite. The favicon was generated with: "Output ONLY the exact intertwined angular AJ monogram from above the AREA J wordmark, on a genuinely transparent square background. Preserve the original geometry, violet A, warm amber J, relative stroke thickness and negative space. Remove both text lines and the graphite background. Center it with about 10% transparent padding."

The browser title and favicon identify Area J; the preview badge remains explicit. Color palette choices stay browser-local. Production still follows preview-to-main PR review.
