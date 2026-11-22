"""
build_full_video_v3.py
Compiles the master upgraded video incorporating:
1. Declarative motion graphics with 3b1b Manim-style Pareto curves
2. alexgreensh Anidoodle-style procedural sketch oval & kinetic arrows
3. Latent-spaces Brag-style synchronized foley UI sound effects (whoosh, pop, chime)
4. Full speech preservation at 1.18x speed
5. Frame-accurate synchronized social reel subtitles
"""

import subprocess
import os

OUTPUT_VIDEO = "/mnt/hdd/Antigravity Video Editor/exports/gemini_4_neon_tamil_v3_master.mp4"
RAW_VIDEO = "/mnt/hdd/Antigravity Video Editor/raw/20261119_181852.mp4"
BROLL_LINEUP = "/tmp/video_assets/broll_lineup_animated.mp4"
BROLL_LEADERBOARD = "/tmp/video_assets/broll_leaderboard_pareto_v2.mp4"
BROLL_SKI = "/tmp/video_assets/ski_sim_full.mp4"
BROLL_PRICING = "/tmp/video_assets/broll_pricing_animated.mp4"
BGM = "/tmp/video_assets/ducked_bgm.wav"
CAPTIONS = "/tmp/video_assets/captions_sync.ass"
SFX_WHOOSH = "/tmp/video_assets/sfx/ui_whoosh.wav"
SFX_CHIME = "/tmp/video_assets/sfx/ui_chime.wav"
SFX_POP = "/tmp/video_assets/sfx/ui_pop.wav"

SPEED = 1.18
START_TIME = 1.0
END_TIME = 119.2
RAW_DURATION = END_TIME - START_TIME
FINAL_DURATION = RAW_DURATION / SPEED  # 100.17s

print(f"Building V3 Master Reel: {FINAL_DURATION:.2f}s (Speed {SPEED}x)")

# Build multi-channel audio mix:
# Voice + ducked BGM + SFX cues (whoosh at 3.0s, chime at 12.5s, pop at 58.0s, whoosh at 84.0s)
filter_complex = f"""
[0:v]trim=start={START_TIME}:end={END_TIME},setpts=PTS-STARTPTS,setpts=PTS/{SPEED},
scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
fps=30[v_base];

[0:a]atrim=start={START_TIME}:end={END_TIME},asetpts=PTS-STARTPTS,atempo={SPEED}[a_voice];

[1:v]fps=30,scale=1080:1920[v_lineup];
[2:v]fps=30,scale=1080:1920[v_lb];
[3:v]fps=30,scale=1080:1920[v_ski];
[4:v]fps=30,scale=1080:1920[v_price];

[v_base][v_lineup]overlay=0:0:enable='between(t,3.0,9.0)'[ov1];
[ov1][v_lb]overlay=0:0:enable='between(t,10.0,16.0)'[ov2];
[ov2][v_ski]overlay=0:0:enable='between(t,58.0,68.0)'[ov3];
[ov3][v_price]overlay=0:0:enable='between(t,84.0,89.0)'[ov4];

[ov4]subtitles='{CAPTIONS}':fontsdir=/usr/share/fonts/truetype/msttcorefonts[v_final];

[5:a]aloop=loop=-1:size=2e+09,atrim=0:{FINAL_DURATION},volume=0.07[a_bgm];

[6:a]adelay=3000|3000,volume=0.35[sfx_w1];
[7:a]adelay=12500|12500,volume=0.40[sfx_chime];
[8:a]adelay=58000|58000,volume=0.35[sfx_pop];
[6:a]adelay=84000|84000,volume=0.35[sfx_w2];

[a_voice][a_bgm][sfx_w1][sfx_chime][sfx_pop][sfx_w2]amix=inputs=6:duration=first:dropout_transition=2,
loudnorm=I=-14:TP=-1:LRA=11[a_final]
"""

cmd = [
    "ffmpeg", "-y",
    "-i", RAW_VIDEO,
    "-i", BROLL_LINEUP,
    "-i", BROLL_LEADERBOARD,
    "-i", BROLL_SKI,
    "-i", BROLL_PRICING,
    "-i", BGM,
    "-i", SFX_WHOOSH,
    "-i", SFX_CHIME,
    "-i", SFX_POP,
    "-filter_complex", filter_complex.replace("\n", " ").strip(),
    "-map", "[v_final]",
    "-map", "[a_final]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-t", f"{FINAL_DURATION:.2f}",
    OUTPUT_VIDEO
]

print("Rendering Master V3 Video...")
subprocess.run(cmd, check=True)
print(f"V3 Master successfully compiled -> {OUTPUT_VIDEO}")
