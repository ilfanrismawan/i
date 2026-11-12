# Accuracy and visual-story guidance

## Evidence tiers
- **Verified:** sourced general mechanism with reliable documentation, model-specific constraints where known.
- **Conceptual:** known class of mechanism, details/geometry approximate.
- **Illustrative:** colors, particles, beams, motion exaggerations for explanation only.
- **Unknown:** proprietary, disputed, or unavailable. Never invent definitive details.

For each explanatory overlay, record what is metaphor. Example: color-coded electric field arcs are visual aids, not visible light; pulsing circuit traces represent signal timing, not electrons racing along wires; biophysical pathways often involve distributed processes, not a single visible stream.

## Mechanical processes
Show constraints, forces and contacts. Avoid intersecting solids, impossible motion and unstated scale exaggeration. Sequence should reflect actual causal order.

## Electrical/electronic
Don't show arcing or electrical contact unless appropriate. Distinguish field, current, voltage, capacitance, digital computation, and interface response. No fake real-world V/pF readings or undocumented chip schematics.

## Biological/medical
Not medical advice; for anatomy and physiology show typical processes without making unjustified diagnosis claims. Prefer authoritative references; label schematic cross-sections.

## Historical/manufacturing
Avoid claiming access to proprietary factory processes or uncertain historical reconstructions. Clearly label illustrative machine stages.

## Claims register
Maintain `claims.json` optional array: `claim`, `tier`, `source`, `visual_shot`, `visual_metaphor`, `caveat`. Review before final render.
