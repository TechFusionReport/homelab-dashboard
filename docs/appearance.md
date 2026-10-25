# Homelab appearance

The homelab uses an independent palette rather than the TechFusion Report brand colors:

- **Night Circuit** (default): violet, mint, and warm amber on graphite.
- **Afterglow**: rose, lavender, and sand on plum charcoal.
- **Phosphor**: soft green, amber, and lilac on deep forest graphite.

The palette bar remembers the selection in this browser only. It does not change another device, alter live service data, or require a server restart.

The service card interaction follows the TFR website category cards: translateY(-8px), scale(1.015), a 3px accent outline, and the same 180ms transition/deep shadow. Keyboard focus gets the same treatment. Reduced-motion preferences keep the outline while disabling the lift and animation. Touch devices do not get a persistent hover lift.

Copy both config/custom.css and config/custom.js into the runtime Homepage configuration folder when updating. The local bootstrap also includes them.
