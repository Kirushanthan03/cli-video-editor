"""
build_full_video_v2.py
Compiles the complete raw video (keeping 100% of speech, sped up 1.18x)
with real animated motion graphics, 3D demo b-roll, synced subtitles, and mastered audio.
"""

import subprocess
import os

OUTPUT_VIDEO = "/mnt/hdd/Antigravity Video Editor/exports/gemini_4_neon_tamil_full_reel.mp4"
RAW_VIDEO = "/mnt/hdd/Antigravity Video Editor/raw/20261119_181852.mp4"
BROLL_LINEUP = "/tmp/video_assets/broll_lineup_animated.mp4"
BROLL_LEADERBOARD = "/tmp/video_assets/broll_leaderboard_animated.mp4"
BROLL_SKI = "/tmp/video_assets/ski_sim_full.mp4"
BROLL_PRICING = "/tmp/video_assets/broll_pricing_animated.mp4"
BGM = "/tmp/video_assets/ducked_bgm.wav"
CAPTIONS = "/tmp/video_assets/captions_sync.ass"

SPEED = 1.18
START_TIME = 1.0
END_TIME = 119.2
RAW_DURATION = END_TIME - START_TIME  # 118.2s
FINAL_DURATION = RAW_DURATION / SPEED  # ~100.17s

print(f"Building Full Reel: {FINAL_DURATION:.2f}s (Speed {SPEED}x from {RAW_DURATION:.2f}s raw)")

# Overlay timeline in sped-up time:
# Lineup: 3.0s -> 9.0s (6s)
# Leaderboard: 10.0s -> 16.0s (6s)
# Ski Sim: 58.0s -> 68.0s (10s)
# Pricing: 84.0s -> 89.0s (5s)

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
[a_voice][a_bgm]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:TP=-1:LRA=11[a_final]
"""

cmd = [
    "ffmpeg", "-y",
    "-i", RAW_VIDEO,
    "-i", BROLL_LINEUP,
    "-i", BROLL_LEADERBOARD,
    "-i", BROLL_SKI,
    "-i", BROLL_PRICING,
    "-i", BGM,
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

print("Executing FFmpeg composite command...")
subprocess.run(cmd, check=True)
print(f"Export successful -> {OUTPUT_VIDEO}")
