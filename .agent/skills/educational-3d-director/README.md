# Educational 3D Director — Codex + Claude Code

A portable Agent Skill to produce cinematic, scientifically responsible Blender educational explainers for **any niche**, from a topic through reusable assets to final animation. Supports phase-by-phase prompting and real utility scripts.

## Installation

Requires Python 3.9+ for the installer/scaffold, and a separately installed Blender for actual modeling/rendering. No third-party Python packages required by helper scripts.

From within this skill folder:

```powershell
# Windows (personal install to both agents)
py -3 scripts/install_skill.py --target both --scope user
```

```bash
# macOS/Linux (personal install to both agents)
python3 scripts/install_skill.py --target both --scope user
```

For project-only install:

```powershell
py -3 scripts/install_skill.py --target both --scope project --project-dir "C:\path\to\your-project"
```

This copies the skill to `~/.agents/skills/educational-3d-director/` for Codex and `~/.claude/skills/educational-3d-director/` for Claude Code. Repo scope copies into `.agents/skills/` and `.claude/skills/` respectively. Restart the agents if necessary.

## Use

Codex: `$educational-3d-director Buat pipeline animasi 3D tentang cara kerja wireless charging, tahap demi tahap.`

Claude Code: `/educational-3d-director Buat pipeline animasi 3D tentang bagaimana ban mobil mencengkeram jalan basah.`

To create a new planning scaffold:

```powershell
py -3 scripts/plan_project.py --topic "Kenapa kaca berembun?" --niche "fisika" --duration 60 --output "D:\Projects\embun-3d"
```

The scaffold creates project brief, manifest, shot plan, and per-phase prompt files; **it does not create 3D models until a code agent runs Blender generation scripts**.

## Important behavior

- Never duplicate completed assets; inspect before generating.
- The default pipeline adapts stages by niche. Not every project needs electronic controllers or a phone UI.
- Source file materials/rigs remain untouched; changes occur in new phase outputs.
- Represent conceptual scientific effects honestly, not as proprietary exact internals.
- Generate preview stills and test animations before full 1080×1920 rendering.
- Rendering requires Blender installed and depends on local hardware.

The package is a **skill**, not an installed graphical Blender addon nor a network-service plugin. It can instruct Codex and Claude Code to drive Blender with `bpy`. See `SKILL.md` and `references/`.

## v5.0: Virtual camera freedom + CapCut-first editing

New: `references/virtual-cinematography.md`, `scripts/validate_virtual_cinematography.py`, and `scripts/build_camera_briefs.py`. The skill now plans non-physical camera reveals (through conceptual interiors, exploded assemblies, invisible-signal tracking, bullet time, and scale jumps) with explicit geometry/cutaway/scale handling. It uses **Eevee-only per-shot delivery** and does not merge the movie outside CapCut. Complex moves must communicate a new fact; do not add visual clutter just to increase shot count.

```powershell
py -3 scripts/validate_virtual_cinematography.py "D:\Projects\episode\shot_plan.json"
py -3 scripts/build_camera_briefs.py "D:\Projects\episode\shot_plan.json" --output "D:\Projects\episode\camera_briefs"
```

## v4.0: Dynamic cinematic shots + CapCut-first editing

The skill now includes two new opt-in workflows:

**Fact discovery** (requires real research access in your code agent): propose unexpected topics, preserve citations, verify the precise claims, and score visual/story potential. A score is *not* evidence. Offline utilities can rank candidate JSON and validate source metadata but **cannot verify whether a web page supports a claim**.

```powershell
py -3 scripts/rank_topics.py templates/topic_candidates.example.json
py -3 scripts/validate_research.py templates/claims.example.json
```

**FFmpeg + CapCut Pro**: Blender renders separate shot frames, FFmpeg encodes each separate shot MP4 (NEVER joins them), and CapCut Pro is the ONLY final assembly and finishing tool. The tool produces a portable shot spreadsheet, optional SRT and editing guide. It does **not** create a native CapCut project file or control the CapCut GUI.

```powershell
py -3 scripts/build_postproduction.py --shots "D:\Projects\my-3d-video\shot_plan.json" --output "D:\Projects\my-3d-video\postproduction"
# When voice-over-derived caption timing is available:
py -3 scripts/build_postproduction.py --shots "D:\Projects\my-3d-video\shot_plan.json" --captions "D:\Projects\my-3d-video\captions.json" --output "D:\Projects\my-3d-video\postproduction"
```

New references: `references/fact-research.md`, `references/creative-formats.md`, `references/postproduction.md`.

### Example new workflow

Codex: `$educational-3d-director Temukan 15 fakta unik tentang benda sehari-hari yang sumbernya dapat diverifikasi. Ranking potensinya untuk animasi 3D TikTok, jangan mulai modeling sebelum sumber dan storyboard lolos. Kemudian buat aset per tahap, render tiap shot, dan siapkan paket editing CapCut Pro.`

Claude Code: `/educational-3d-director Bangun serial edukasi tentang proses pembuatan benda sehari-hari. Gunakan Blender modular, tanpa duplikasi aset, dan buat output shot untuk CapCut Pro.`

### Upgrading an existing installation

Back up any edits you made to the installed skill, then run:

```powershell
py -3 scripts/install_skill.py --target both --scope user --force
```

`--force` **replaces** existing installations of this skill in the destination directories. It does not change your Blender project files.

## v3.0 required behavior

- **Eevee-only**, render individual shots and deliver a ready-for-import MP4 to CapCut immediately after a shot passes media QA.
- **No baked overlays** in Blender: no captions, explanation labels, arrows, HUD or debug text. Genuine 3D model parts and actual phone app UI can remain.
- **Voice-over:** Indonesian simple enough for a typical seven-year-old, short everyday sentences, no unexplained jargon; still scientifically sound.
- **CapCut Pro:** edit each incoming shot, add word-by-word captions, purposeful transitions, scene SFX, transition SFX, BGM and final color/audio polish. The skill generates an import-ready handoff, not a native CapCut project or autonomous GUI edits.
- For word-by-word subtitles, prepare audio-aligned `words.json` (example in `templates/word_captions.example.json`), then:

```powershell
py -3 scripts/build_postproduction.py --shots "D:\Projects\video\shot_plan.json" --word-captions "D:\Projects\video\words.json" --output "D:\Projects\video\postproduction"
```

For a newly finished shot, optionally use `--ready-shot <shot_id> --clip <existing.mp4>` to mark that the clip exists (NOT that full media QA passed). Inspect it and import it manually into CapCut.

## v4 Critical fix: no reassembly in Blender

1. Build the 12–20-ish shots for 60s from story and voice-over, not as a hard quota; validate variation: `python scripts/validate_shot_diversity.py path/to/shot_plan.json`.
2. Eevee renders the current shot. FFmpeg encodes only that shot to `SHOT_XX.mp4`; technical media QA with `ffprobe`.
3. **STOP** and hand off the MP4 to the SAME CapCut Pro project for timing/VO, word-by-word subtitles, transitions, scene SFX, transition SFX, and BGM. Never assemble in Blender/VSE/FFmpeg.
4. The code agent does not have native CapCut GUI access: use `scripts/capcut_shot_gate.py` to mark CapCut import/edit **only after explicit user confirmation**.
5. After edit confirmation, render the next shot. For bulk renders, user must explicitly choose batch mode; each shot still gets a separate handoff immediately.

Example (replace paths and shot IDs):

```powershell
py -3 scripts/capcut_shot_gate.py --plan shot_plan.json --status-file postproduction/editorial_status.json --shot SHOT_01 --action clip-ready --clip renders/shot_01.mp4
# User imports shot_01.mp4 into CapCut and edits it, then confirms both steps.
py -3 scripts/capcut_shot_gate.py --plan shot_plan.json --status-file postproduction/editorial_status.json --shot SHOT_01 --action mark-imported --confirmed-by-user
py -3 scripts/capcut_shot_gate.py --plan shot_plan.json --status-file postproduction/editorial_status.json --shot SHOT_01 --action mark-edited --confirmed-by-user
py -3 scripts/capcut_shot_gate.py --plan shot_plan.json --status-file postproduction/editorial_status.json --shot SHOT_02 --action can-render-next
```

**No fake automation:** CLI status marks only user-confirmed CapCut actions; the skill does not automatically click CapCut. If you have computer-use capabilities, confirm actual changes visually before updating status.
