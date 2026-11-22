"""
pipeline/auto_editor.py
Autonomous Master Video Editor Pipeline
Generalizes the entire editing workstation for ANY raw video:
1. Speech Boundary & Silence Detection
2. Automatic Whisper Transcription & Alignment (Multi-language)
3. Speed-Adjusted, Color-Coded ASS Subtitle Generation
4. Visual Director: Semantic Cue Planning (Anidoodle, Manim, Keynote elements)
5. Transparent Motion Graphic Rendering (Alpha Channel ProRes / MOV)
6. Procedural Foley Sound Effects Synthesis (Whoosh, Pop, Chime)
7. Broadcast-Grade Master Audio & Video Multi-Track Assembly
"""

import argparse
import os
import sys
import json
import subprocess
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.speech_analyzer import detect_speech_boundaries, transcribe_audio
from pipeline.visual_director import plan_visual_scenes
from presets.subtitles.subtitle_styler import generate_synced_ass
from engine.renderer import render_scene
from engine.sfx import build_default_sfx_library

def run_auto_editor(
    raw_path: str,
    output_path: str = None,
    speed: float = 1.18,
    theme: str = "cyber_neon",
    enable_overlays: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    raw_path = os.path.abspath(raw_path)
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw video not found: {raw_path}")
        
    base_name = os.path.splitext(os.path.basename(raw_path))[0]
    work_dir = f"/tmp/auto_editor_{base_name}"
    os.makedirs(work_dir, exist_ok=True)
    
    if output_path is None:
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        output_path = os.path.join(exports_dir, f"{base_name}_master.mp4")
    else:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
    print(f"\n=======================================================")
    print(f"🎬 AUTONOMOUS VIDEO EDITOR PIPELINE")
    print(f"Input:       {raw_path}")
    print(f"Output:      {output_path}")
    print(f"Theme:       {theme}")
    print(f"Speed:       {speed}x")
    print(f"Work Dir:    {work_dir}")
    print(f"=======================================================\n")
    
    # -----------------------------------------------------------------
    # STEP 1: Silence & Speech Boundary Detection
    # -----------------------------------------------------------------
    print("▶ Step 1: Detecting speech boundaries and trimming dead air...")
    start_time, end_time, raw_duration = detect_speech_boundaries(raw_path)
    speech_duration = end_time - start_time
    final_duration = speech_duration / speed
    print(f"   Raw duration: {raw_duration:.2f}s | Speech window: {start_time:.2f}s -> {end_time:.2f}s")
    print(f"   Preserved Speech: {speech_duration:.2f}s (100%) -> Final Reel: {final_duration:.2f}s at {speed}x\n")
    
    # -----------------------------------------------------------------
    # STEP 2: Multi-Language Transcription & Alignment
    # -----------------------------------------------------------------
    print("▶ Step 2: Running faster-whisper transcription and timestamp alignment...")
    transcription = transcribe_audio(raw_path, start_time=start_time, end_time=end_time)
    detected_lang = transcription["language"]
    lang_prob = transcription["language_probability"]
    segments = transcription["segments"]
    print(f"   Detected Language: {detected_lang.upper()} (Confidence: {lang_prob*100:.1f}%)")
    print(f"   Transcribed {len(segments)} spoken segments.\n")
    
    # Save transcription transcript
    transcript_file = os.path.join(work_dir, "transcript.json")
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(transcription, f, indent=2, ensure_ascii=False)
        
    # -----------------------------------------------------------------
    # STEP 3: Subtitle Generation (social_reel_preset.ass)
    # -----------------------------------------------------------------
    print("▶ Step 3: Compiling frame-accurate speed-compensated subtitles...")
    captions_file = os.path.join(work_dir, "captions.ass")
    generate_synced_ass(
        segments=segments,
        output_path=captions_file,
        speed=speed,
        start_offset=start_time,
        title=f"Reel Subtitles - {base_name}"
    )
    print(f"   Subtitles generated -> {captions_file}\n")
    
    # -----------------------------------------------------------------
    # STEP 4: Visual Director & Semantic Cue Planning
    # -----------------------------------------------------------------
    print("▶ Step 4: Semantic Visual Director planning motion graphics...")
    planned_scenes = []
    if enable_overlays:
        planned_scenes = plan_visual_scenes(
            segments=segments,
            speed=speed,
            start_offset=start_time,
            theme_name=theme
        )
    print(f"   Planned {len(planned_scenes)} kinetic overlay scenes.")
    for idx, sc in enumerate(planned_scenes, 1):
        print(f"     [{idx}] {sc['start']:.2f}s - {sc['start']+sc['duration']:.2f}s | SFX: {sc['sfx']}")
    print()
    
    if dry_run:
        print("💡 Dry run complete. Exiting before render.")
        return {
            "status": "dry_run_complete",
            "duration": final_duration,
            "language": detected_lang,
            "segments": len(segments),
            "scenes": len(planned_scenes)
        }
        
    # -----------------------------------------------------------------
    # STEP 5: Procedural SFX & Motion Overlays Rendering
    # -----------------------------------------------------------------
    print("▶ Step 5: Synthesizing Foley SFX and rendering transparent motion clips...")
    sfx_paths = build_default_sfx_library(os.path.join(work_dir, "sfx"))
    
    rendered_overlays = []
    for sc in planned_scenes:
        mov_path = os.path.join(work_dir, f"{sc['id']}.mov")
        print(f"   Rendering overlay {sc['id']} ({sc['duration']}s) -> {mov_path}...")
        render_scene(sc["scene"], mov_path, width=1080, height=1920, fps=30)
        sc["mov_path"] = mov_path
        rendered_overlays.append(sc)
        
    # -----------------------------------------------------------------
    # STEP 6: Multi-Layer Master Assembly (FFmpeg Compositor)
    # -----------------------------------------------------------------
    print("\n▶ Step 6: Assembling master reel with broadcast audio leveling...")
    
    # Build filter complex
    # Inputs:
    # 0: Raw video
    # 1..N: Overlay .mov files
    # N+1: whoosh SFX
    # N+2: pop SFX
    # N+3: chime SFX
    
    inputs = ["-i", raw_path]
    for sc in rendered_overlays:
        inputs.extend(["-i", sc["mov_path"]])
        
    sfx_start_idx = 1 + len(rendered_overlays)
    inputs.extend(["-i", sfx_paths["whoosh"]])   # sfx_start_idx + 0
    inputs.extend(["-i", sfx_paths["pop"]])      # sfx_start_idx + 1
    inputs.extend(["-i", sfx_paths["chime"]])    # sfx_start_idx + 2
    
    filter_lines = []
    # Video base: trim, speedup, vertical crop 1080x1920
    filter_lines.append(
        f"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS,setpts=PTS/{speed},"
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[v_base]"
    )
    
    curr_v = "v_base"
    for i, sc in enumerate(rendered_overlays):
        in_idx = 1 + i
        next_v = f"v_ov_{i+1}"
        t_in = sc["start"]
        t_out = sc["start"] + sc["duration"]
        filter_lines.append(
            f"[{curr_v}][{in_idx}:v]overlay=0:0:enable='between(t,{t_in:.2f},{t_out:.2f})'[{next_v}]"
        )
        curr_v = next_v
        
    # Subtitles
    filter_lines.append(
        f"[{curr_v}]subtitles='{captions_file}':fontsdir=/usr/share/fonts/truetype/msttcorefonts[v_final]"
    )
    
    # Audio master: voice speedup + loudnorm
    filter_lines.append(
        f"[0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS,atempo={speed}[a_voice_clean]"
    )
    
    # Mix Foley SFX
    sfx_audio_pads = ["[a_voice_clean]"]
    sfx_split_counts = {"whoosh": 0, "pop": 0, "chime": 0}
    for sc in rendered_overlays:
        sfx_split_counts[sc["sfx"]] += 1
        
    # Setup delays for each overlay sfx
    sfx_indices = {"whoosh": sfx_start_idx, "pop": sfx_start_idx + 1, "chime": sfx_start_idx + 2}
    
    for idx, sc in enumerate(rendered_overlays):
        sfx_type = sc["sfx"]
        stream_idx = sfx_indices[sfx_type]
        delay_ms = int(sc["start"] * 1000)
        pad_name = f"sfx_{idx}"
        filter_lines.append(
            f"[{stream_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.35[{pad_name}]"
        )
        sfx_audio_pads.append(f"[{pad_name}]")
        
    num_audio_inputs = len(sfx_audio_pads)
    audio_pads_str = "".join(sfx_audio_pads)
    filter_lines.append(
        f"{audio_pads_str}amix=inputs={num_audio_inputs}:duration=first:dropout_transition=2,"
        f"loudnorm=I=-14:TP=-1:LRA=11[a_final]"
    )
    
    filter_complex = ";\n".join(filter_lines)
    
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex.replace("\n", " ").strip(),
        "-map", "[v_final]",
        "-map", "[a_final]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{final_duration:.2f}",
        output_path
    ]
    
    proc = subprocess.run(cmd, check=True)
    
    # Check file size
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ COMPOSITION COMPLETE!")
    print(f"Exported: {output_path} ({file_size_mb:.2f} MB)")
    print(f"Reel Duration: {final_duration:.2f}s | Format: 1080x1920 30fps Full HD")
    print(f"Voice Quality: EBU R128 (-14 LUFS) Studio Master with Synchronized ASS Subtitles\n")
    
    return {
        "output_path": output_path,
        "duration": final_duration,
        "language": detected_lang,
        "file_size_mb": file_size_mb,
        "overlays": len(rendered_overlays),
        "transcript_file": transcript_file,
        "captions_file": captions_file
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Autonomous Video Editor Pipeline")
    parser.add_argument("--raw", "--input", "-i", dest="raw", required=True, help="Path to raw video")
    parser.add_argument("--output", "-o", dest="output", default=None, help="Path to output video")
    parser.add_argument("--speed", "-s", type=float, default=1.18, help="Playback speed multiplier (e.g. 1.18)")
    parser.add_argument("--theme", "-t", default="cyber_neon", choices=["cyber_neon", "apple_keynote", "vox_editorial", "fintech_emerald"])
    parser.add_argument("--no-overlays", action="store_true", help="Disable kinetic motion overlays")
    parser.add_argument("--dry-run", action="store_true", help="Run analysis and cue planning without rendering")
    
    args = parser.parse_args()
    run_auto_editor(
        raw_path=args.raw,
        output_path=args.output,
        speed=args.speed,
        theme=args.theme,
        enable_overlays=not args.no_overlays,
        dry_run=args.dry_run
    )
