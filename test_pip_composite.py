"""
test_pip_composite.py
Tests the Hybrid Picture-in-Picture (PiP) composite:
Real UI screencast + Speaker in a floating masked webcam bubble + glowing border + subtitles.
"""

import subprocess

cmd = [
    "ffmpeg", "-y",
    "-ss", "10.0", "-t", "5.0", "-i", "/mnt/hdd/Antigravity Video Editor/exports/gemini_4_neon_tamil_v3_master.mp4",
    "-i", "/tmp/video_assets/ref_ui_leaderboard.mp4",
    "-i", "/tmp/pip_mask.png",
    "-i", "/tmp/pip_border.png",
    "-filter_complex",
    """
    [0:v]crop=720:960:180:360,scale=360:480[speaker_crop];
    [speaker_crop][2:v]alphamerge[speaker_pip];
    [1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[ui_bg];
    [ui_bg][speaker_pip]overlay=670:1060[with_speaker];
    [with_speaker][3:v]overlay=670:1060[v_out]
    """.replace("\n", " ").strip(),
    "-map", "[v_out]",
    "-map", "0:a",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-t", "5.0",
    "/tmp/test_pip_sample.mp4"
]

print("Rendering PiP sample...")
subprocess.run(cmd, check=True)
print("Rendered /tmp/test_pip_sample.mp4")
