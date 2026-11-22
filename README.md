# CLI Video Editor

An automated command-line video editing workstation that converts raw video footage into vertical 9:16 social reels (1080x1920 Full HD @ 30fps) with frame-accurate subtitles, procedural vector motion graphics, and mastered dialogue audio.

> 📖 **Beginner-Friendly Visual Guide**: Open [`docs/index.html`](docs/index.html) in your browser for a visual interactive walkthrough of the pipeline, theme previews, and CLI options.

## Features

- **Automated Silence Detection**: Detects dead air at start/end and trims automatically.
- **Multilingual Speech-to-Text**: Built on `faster-whisper` with word-level alignment (supports Tamil, English, Hindi, and 90+ languages).
- **Speed-Preserved Timing**: Configurable playback speed (e.g. 1.15x - 1.25x) using pitch-preserved `atempo` and timestamp compensation.
- **Stylized ASS Subtitles**: 4-tier color hierarchy with deep black outlines and vertical safe zones.
- **Procedural Motion Graphics**: High-performance vector overlays (kinetic cards, hand-drawn circling doodles, animated arrows, and gauges) rendered via PyCairo with alpha transparency.
- **Mathematical Foley Audio**: Procedural generation of UI sound effects (whooshes, pops, chimes) without external audio files.
- **Clean Dialogue Mastering**: Audio leveled to broadcast EBU R128 standard (-14 LUFS).

## Requirements

- Python 3.10+
- FFmpeg 6.0+ with `libass` and `libx264`
- Cairo graphics library (`libcairo2-dev`)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run Automated Pipeline

#### Single Video Mode:
```bash
python3 pipeline/auto_editor.py --raw raw/input_video.mp4 --theme cyber_neon --speed 1.18
```

#### Multi-Reference Mode (B-roll + Speaker PiP):
Drop any number of reference videos into `reference/` (auto-detected), or pass them explicitly:
```bash
python3 pipeline/auto_editor.py \
  --raw raw/my_talk.mp4 \
  --ref reference/app_demo.mp4 reference/benchmark.mp4 reference/screencast.mp4 \
  --theme cyber_neon \
  --speed 1.18
```

### CLI Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `--raw`, `-i` | Path to raw input video | Required |
| `--ref`, `-r` | One or more reference video paths for PiP B-roll | Auto-detects `reference/*` |
| `--output`, `-o` | Output file path | `exports/<basename>_master.mp4` |
| `--speed`, `-s` | Playback speed multiplier | `1.18` |
| `--theme`, `-t` | Visual style (`cyber_neon`, `apple_keynote`, `vox_editorial`, `fintech_emerald`) | `cyber_neon` |
| `--no-overlays` | Render subtitles and clean audio only | `False` |
| `--dry-run` | Run speech analysis and cue planning without rendering | `False` |

## Project Structure

```
├── engine/              # Procedural motion graphics and Foley sound synthesis
│   ├── charts.py        # Coordinate grids and animated curves
│   ├── doodle.py        # Hand-drawn animated vector doodles
│   ├── manifest.py      # Declarative motion scene schemas
│   ├── renderer.py      # PyCairo transparent video renderer
│   ├── sfx.py           # Procedural sound effect synthesizer
│   └── theme.py         # Visual color palettes and typography
├── pipeline/            # End-to-end orchestration
│   ├── auto_editor.py   # Main CLI runner
│   ├── speech_analyzer.py # Silence detection and faster-whisper transcription
│   ├── visual_director.py # Semantic cue planning
│   └── reference_matcher.py # Multi-reference scene slicing & PiP camera
├── presets/
│   └── subtitles/       # Reusable ASS subtitle formatting
├── docs/                # Architecture and workflow documentation
│   ├── index.html       # Visual beginner-friendly user guide
│   └── GENERALIZED_WORKFLOW.md
└── requirements.txt
```

## License
MIT
