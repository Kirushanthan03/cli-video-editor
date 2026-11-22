# Generalized AI Video Editor Workstation: User Guide & Architecture

## Overview
This workstation is designed as an autonomous, end-to-end AI video editing engine. It accepts **any raw video** (talking head, tutorial, product review, screencast) in any language and produces a broadcast-ready 9:16 vertical social reel (1080x1920 Full HD @ 30fps) with frame-accurate subtitles, procedural motion graphics, and studio-mastered audio.

---

## 1. How to Edit Any New Video

### Method A: Single Command Execution
Drop any raw video into `raw/` (or anywhere on disk) and execute:
```bash
python3 pipeline/auto_editor.py --raw raw/<your_video>.mp4
```

#### Available CLI Flags:
| Flag | Description | Default | Options |
| :--- | :--- | :--- | :--- |
| `--raw`, `-i` | Path to raw input footage (Required) | — | Any MP4/MOV file |
| `--output`, `-o` | Output file path | `exports/<basename>_master.mp4` | Any MP4 path |
| `--speed`, `-s` | Speech-preserved playback speed multiplier | `1.18` | e.g. `1.0` (normal) to `1.25` |
| `--theme`, `-t` | Visual motion graphics theme | `cyber_neon` | `cyber_neon`, `apple_keynote`, `fintech_emerald`, `vox_editorial` |
| `--no-overlays` | Renders clean subtitles + voice master without cards | False | Flag |
| `--dry-run` | Audits speech, generates transcript & scenes without rendering | False | Flag |

---

### Method B: Autonomous Subagent Delegation
You can instruct Antigravity or invoke the subagent directly:
> *"Edit the new footage in `raw/episode_2.mp4` using the `apple_keynote` theme at 1.15x speed."*

The `video-editor` subagent autonomously:
1. Detects start/stop speech boundaries to cut leading dead air and trailing camera reach.
2. Transcribes multi-language audio with word-level timestamps (`faster-whisper`).
3. Compiles speed-compensated, highlighted subtitles ([social_reel_preset.ass](file:///mnt/hdd/Antigravity%20Video%20Editor/presets/subtitles/social_reel_preset.ass)).
4. Analyzes semantic beats to plan kinetic overlays (Anidoodle sketches, benchmark counters, badges).
5. Renders transparent ProRes alpha motion clips.
6. Masters speech audio (EBU R128 -14 LUFS, zero background chatter, pitch-preserved `atempo`).
7. Mixes Foley sound effects and exports the final master into `exports/`.

---

## 2. Audio Architecture & Zero-Contamination Guarantee
- **Root Cause of Past Audio Issue**: In earlier versions, background music sampled from `reference/Video-57475.mp4` contained the reference video's English narrator speaking quietly over the music track, causing an overlapping voice issue.
- **The Generalized Fix**:
  - Raw dialogue is processed through a dedicated vocal chain:
    `atrim -> asetpts -> atempo -> loudnorm=I=-14:TP=-1:LRA=11`.
  - No external reference video audio is mixed in unless pure instrumental audio is explicitly provided.
  - UI sound effects (whoosh, pop, chime) are mathematically synthesized procedurally via `engine/sfx.py` so they are 100% clean, royalty-free, and perfectly timed to visual entrances.

---

## 3. Motion Graphics Architecture
Inspired by modern viral video techniques and top open-source creative coding frameworks:
- **`alexgreensh/anidoodle`**: Organic hand-drawn procedural vector doodles (circling ovals, kinetic arrows, double-pass underlines with Bezier jitter) that highlight key phrases directly on screen.
- **`3b1b/manim`**: Dynamic Pareto curves, animated metric speedometers, and smooth mathematical easing (`spring_pop`, `ease_out_back`).
- **`latent-spaces/brag`**: Declarative scene orchestration with synthesized UI Foley sound effects on entrances.
- **`alchaincyf/huashu-art-motion`**: Multi-theme palettes (`cyber_neon`, `apple_keynote`, `vox_editorial`, `fintech_emerald`) rendered with transparent alpha channels (`yuva444p10le`) overlaid directly over speaker footage.

---

## 4. Subtitle Styling Preset
All subtitles adhere to [social_reel_preset.ass](file:///mnt/hdd/Antigravity%20Video%20Editor/presets/subtitles/social_reel_preset.ass):
- **Resolution**: 1080x1920 PlayRes
- **Font**: Arial Black / Heavy Gothic, 54–58pt
- **Outline & Shadow**: 5.5px deep black outline with `ScaledBorderAndShadow = yes`
- **Color Hierarchy**:
  - `Default`: Pure White (`&H00FFFFFF`)
  - `Accent`: Electric Yellow (`&H0018EAFF`)
  - `GreenAccent`: Emerald Green (`&H0030FF80`)
  - `RedAccent`: Coral Warning (`&H003030FF`)
- **Safe Zone**: `MarginV = 280` (avoids TikTok/Instagram Reel UI buttons and captions).
