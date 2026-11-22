"""
build_hybrid_master.py
Compiles the Hybrid Master Cut:
- Real UI screen-recordings (Artificial Analysis website, Google AI Studio, 3D Ski Sim)
- Speaker in glowing Picture-in-Picture (PiP) floating camera bubble during UI screencasts
- Sleek keynote motion graphics for the model lineup & pricing
- 100% speech preservation at 1.18x speed
- Frame-accurate synchronized subtitles from preset
- Foley UI sound effects (whooshes, pops, chimes)
"""

import subprocess
import os

OUTPUT_VIDEO = "/mnt/hdd/Antigravity Video Editor/exports/gemini_4_neon_tamil_hybrid_master.mp4"
RAW_VIDEO = "/mnt/hdd/Antigravity Video Editor/raw/20261119_181852.mp4"

# Visual Assets
BROLL_LINEUP = "/tmp/video_assets/broll_lineup_animated.mp4"
UI_LEADERBOARD = "/tmp/video_assets/ref_ui_leaderboard.mp4"
UI_SKI = "/tmp/video_assets/ski_sim_full.mp4"
UI_STUDIO = "/tmp/video_assets/ref_ui_studio_pricing.mp4"
BROLL_PRICING = "/tmp/video_assets/broll_pricing_animated.mp4"

PIP_MASK = "/tmp/pip_mask.png"
PIP_BORDER = "/tmp/pip_border.png"

# Audio Assets
BGM = "/tmp/video_assets/ducked_bgm.wav"
SFX_WHOOSH = "/tmp/video_assets/sfx/ui_whoosh.wav"
SFX_CHIME = "/tmp/video_assets/sfx/ui_chime.wav"
SFX_POP = "/tmp/video_assets/sfx/ui_pop.wav"
CAPTIONS = "/tmp/video_assets/captions_sync.ass"

SPEED = 1.18
START_TIME = 1.0
END_TIME = 119.2
RAW_DURATION = END_TIME - START_TIME
FINAL_DURATION = RAW_DURATION / SPEED  # 100.17s

print(f"Building Hybrid Master Reel: {FINAL_DURATION:.2f}s (Speed {SPEED}x)")

filter_complex = f"""
[0:v]trim=start={START_TIME}:end={END_TIME},setpts=PTS-STARTPTS,setpts=PTS/{SPEED},
scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
fps=30,split=2[v_base_bg][v_base_crop];

[v_base_crop]crop=720:960:180:320,scale=360:480[speaker_face];
[speaker_face][6:v]alphamerge[pip_masked];
[pip_masked][7:v]overlay=0:0,split=5[pb1][pb2][pb3][pb4][pb5];

[1:v]fps=30,scale=1080:1920[v_lineup];
[2:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v_lb];
[3:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v_ski];
[4:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v_studio];
[5:v]fps=30,scale=1080:1920[v_price];

[v_base_bg][v_lineup]overlay=0:0:enable='between(t,3.0,9.0)'[bg1];
[bg1][pb1]overlay=670:1060:enable='between(t,3.0,9.0)'[c1];

[c1][v_lb]overlay=0:0:enable='between(t,9.0,16.0)'[bg2];
[bg2][pb2]overlay=670:1060:enable='between(t,9.0,16.0)'[c2];

[c2][v_ski]overlay=0:0:enable='between(t,58.0,68.0)'[bg3];
[bg3][pb3]overlay=670:1060:enable='between(t,58.0,68.0)'[c3];

[c3][v_studio]overlay=0:0:enable='between(t,68.0,78.0)'[bg4];
[bg4][pb4]overlay=670:1060:enable='between(t,68.0,78.0)'[c4];

[c4][v_price]overlay=0:0:enable='between(t,84.0,89.0)'[bg5];
[bg5][pb5]overlay=670:1060:enable='between(t,84.0,89.0)'[c5];

[c5]subtitles='{CAPTIONS}':fontsdir=/usr/share/fonts/truetype/msttcorefonts[v_final];

[0:a]atrim=start={START_TIME}:end={END_TIME},asetpts=PTS-STARTPTS,atempo={SPEED}[a_voice];
[8:a]aloop=loop=-1:size=2e+09,atrim=0:{FINAL_DURATION},volume=0.07[a_bgm];

[9:a]asplit=2[sfx_w1_in][sfx_w2_in];
[sfx_w1_in]adelay=3000|3000,volume=0.35[sfx_w1];
[sfx_w2_in]adelay=84000|84000,volume=0.35[sfx_w2];

[10:a]adelay=11000|11000,volume=0.40[sfx_chime];
[11:a]adelay=58000|58000,volume=0.35[sfx_pop];

[a_voice][a_bgm][sfx_w1][sfx_chime][sfx_pop][sfx_w2]amix=inputs=6:duration=first:dropout_transition=2,
loudnorm=I=-14:TP=-1:LRA=11[a_final]
"""

cmd = [
    "ffmpeg", "-y",
    "-i", RAW_VIDEO,           # 0
    "-i", BROLL_LINEUP,        # 1
    "-i", UI_LEADERBOARD,      # 2
    "-i", UI_SKI,              # 3
    "-i", UI_STUDIO,           # 4
    "-i", BROLL_PRICING,       # 5
    "-i", PIP_MASK,            # 6
    "-i", PIP_BORDER,          # 7
    "-i", BGM,                 # 8
    "-i", SFX_WHOOSH,          # 9
    "-i", SFX_CHIME,           # 10
    "-i", SFX_POP,             # 11
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

print("Executing Hybrid Master Composite...")
subprocess.run(cmd, check=True)
print(f"Hybrid Master successfully compiled -> {OUTPUT_VIDEO}")
