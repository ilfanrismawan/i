# Codex and Claude Code usage

Both tools can discover the same `SKILL.md` when the folder is installed in their respective locations.

- **Codex (repo):** `<repo>/.agents/skills/educational-3d-director/SKILL.md`
- **Codex (user):** `~/.agents/skills/educational-3d-director/SKILL.md`
- **Claude Code (repo):** `<repo>/.claude/skills/educational-3d-director/SKILL.md`
- **Claude Code (user):** `~/.claude/skills/educational-3d-director/SKILL.md`

Use `python scripts/install_skill.py --target both --scope user` from skill directory to install. For a project install, pass `--scope project --project-dir PATH`. A restart may be needed for discovery.

Invocations (inside a code agent workspace):
- Codex: `$educational-3d-director Plan a 60-second 3D explainer about how wireless charging works, step-by-step, using existing assets first.`
- Claude Code: `/educational-3d-director Plan a 60-second 3D explainer about how wireless charging works, step-by-step.`

Prompts:
- `Use educational-3d-director in plan mode. Topic: why does bread rise? Niche: food science. Write Indonesian narration, shot list, staged Blender asset prompts, no full render yet.`
- `Use educational-3d-director in asset mode. Only build the next required component; inspect any existing .blend and manifest. Stop after preview validation.`
- `Use educational-3d-director in integrate mode. Preserve all old assets. Link them, create deterministic event continuity and blocking renders.`
- `Use educational-3d-director in repair mode. Diagnose clipped glass and broken rotations without regenerating the phone.`

The skill does not install Blender, does not supply purchased models, and does not grant Claude/Codex GPU resources automatically. Execution depends on machine and enabled shell/filesystem permissions. A plain skill is the most portable cross-agent artifact; a host-specific plugin/MCP is only necessary for external APIs or a store-installable integration.
