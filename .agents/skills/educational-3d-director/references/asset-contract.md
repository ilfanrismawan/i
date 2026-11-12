# Asset contract / interfaces

## Source preservation
Keep source files read-only in workflow; output phase versions. Prefer library linking or append + copied instancing for preview. Record original filename and sha256 if computed. Never pretend source geometry quality is validated unless opened/rendered.

## Coordinates
Use meters unless source establishes different units. Read actual transforms; do not assume world Z is screen/ground normal. Use `Object.matrix_world` and inverse transforms for world ↔ local. Anchor empties with clear names, e.g. `ASSET_Root`, `ANCHOR_Contact`, `ANCHOR_Input`, `ANCHOR_Output`, `CAM_Target`.

## Manifests
Root `asset_manifest.json` includes `project`, `schema_version`, `assets` entries. Each asset entry has `id`, `path`, `phase`, `status`, `collection`, `dependencies`, optional `anchors`, `controls`, and `source_sha256`. Never delete unrelated manifest records. Check with `scripts/validate_manifest.py`.

## Animation controls
Named, keyframeable properties should be visible in Blender. Document exact control type, range, unit, default, and what it affects; scripts must manipulate actual scene data, not unconnected Python variables. Headless deterministic evaluations required. Events should have source IDs, frames, states, positions and validity.

## Validation
Geometry scale, normals, overlap, materials, bounding boxes; camera framing, screenshot; event coordination, backward timeline scrub, reopen file, headless render, existence and dimensions of preview images. Tests should be explicit and reproducible.

## Scientific honesty
If physical dimensions have been enlarged for visibility, record scale exaggeration and do not present as measured. If a proprietary stack is reconstructed, use label `conceptual illustration`.
