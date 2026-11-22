# Antigravity Social Reel Subtitle Preset

This preset captures the typography, color hierarchy, vertical margins, and sync formulas tested and validated on 9:16 vertical short-form video reels.

## Style Specifications
* **Screen Resolution Base:** `1080 x 1920` (Vertical 9:16)
* **Font Family:** `Arial Black` / `Montserrat Black` (heavy geometric weight for instant readability)
* **Margins:** `MarginV = 280` (positioned in the lower third, comfortably clear of TikTok/Instagram/YouTube Reels bottom controls and action buttons)
* **Outline / Stroke:** 5.0 - 5.5px solid black border with subtle alpha drop-shadow (ensures 100% contrast against bright B-rolls and dark footage)

## Available Color Hierarchy
1. **`Default`** (`#FFFFFF` pure white, 54pt): Standard narrative and explanatory speech.
2. **`Accent`** (`#18EAFF` bright neon yellow/gold, 58pt): Key model names, product releases, hooks, and crucial keywords.
3. **`GreenAccent`** (`#30FF80` neon emerald, 58pt): Performance benchmarks, cost savings, positive metrics, and speed boosts.
4. **`RedAccent`** (`#3030FF` coral/red, 58pt): Friction points, problem statements, high costs, and alerts.

## Synchronization Formula
When video playback is sped up by speed factor $S$ and trimmed at start offset $T_0$:
$$T_{\text{subtitle}} = \frac{T_{\text{raw\_whisper}} - T_0}{S}$$

Use `presets/subtitles/subtitle_styler.py` to compile Whisper transcripts directly into this preset.
