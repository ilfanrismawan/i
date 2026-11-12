# Bagaimana iPhone tahu mobilmu kecelakaan?

Generated cross-niche 3D explainer scaffold. **No assets or renders are created by this scaffold.**

1. Review `project_brief.json` and confirm mechanism facts.
2. Add existing asset file paths in `asset_manifest.json` and do not duplicate them.
3. Refine `shot_plan.json` and phase prompts; omit phases irrelevant to the niche.
4. Run the agent one phase at a time using prompts in `prompts/`.
5. Render blocking previews before a final frame sequence.
6. Render one Eevee shot at a time. Encode its own MP4; do not create a Blender or FFmpeg final edit.
7. Import AND edit each verified shot in the SAME CapCut Pro project before the next render (unless explicit batch permission).
8. Validate shot diversity AND virtual camera planning with scripts/validate_shot_diversity.py and scripts/validate_virtual_cinematography.py; generate camera briefs with scripts/build_camera_briefs.py. Generate editorial handoff with build_postproduction.py.

Target: 60s, 30 FPS, 1080x1920.
