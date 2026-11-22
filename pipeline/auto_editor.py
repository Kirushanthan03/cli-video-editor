"""
pipeline/auto_editor.py
Autonomous Master Video Editor Pipeline
Supports:
1. Raw video input (single talking-head or screencast)
2. Single or Multiple reference videos (auto-detected from reference/ or passed via --ref)
3. Speech Boundary & Dead Air Trimming
4. Multi-Language Faster-Whisper Transcription & Alignment (TA/EN/HI...)
5. Speed-Preserved ASS Subtitle Generation (social_reel_preset.ass)
6. Dynamic Multi-Reference B-roll & Floating Picture-in-Picture (PiP) Speaker Bubble
7. Procedural Kinetic Motion Graphics Overlays (Anidoodle sketches, Manim curves, Stat Badges)
8. Procedural Foley Sound Effects Synthesis (Whoosh, Pop, Chime)
9. Broadcast-Grade Master Audio (EBU R128 -14 LUFS) with 100% Zero Phantom Voice Contamination
"""

import argparse
import os
import sys
import json
import glob
import subprocess
from typing import Dict, Any, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.speech_analyzer import detect_speech_boundaries, transcribe_audio
from pipeline.visual_director import plan_visual_scenes
from pipeline.reference_matcher import process_multiple_references
from presets.subtitles.subtitle_styler import generate_synced_ass
from engine.renderer import render_scene
from engine.theme import get_theme
from engine.sfx import build_default_sfx_library

def find_all_references() -> List[str]:
    """Finds all video files in the reference/ folder."""
    ref_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference")
    refs = []
    if os.path.exists(ref_dir):
        files = sorted(glob.glob(os.path.join(ref_dir, "*.*")))
        for f in files:
            if f.lower().endswith((".mp4", ".mov", ".mkv", ".webm")) and not f.endswith(".gitkeep"):
                refs.append(f)
    return refs

def run_auto_editor(
    raw_path: str,
    ref_paths: Optional[List[str]] = None,
    output_path: Optional[str] = None,
    speed: float = 1.18,
    theme: str = "cyber_neon",
    enable_overlays: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    raw_path = os.path.abspath(raw_path)
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw video not found: {raw_path}")
        
    # Auto-detect reference videos if not explicitly specified
    if ref_paths is None or len(ref_paths) == 0:
        ref_paths = find_all_references()
    else:
        ref_paths = [os.path.abspath(p) for p in ref_paths if os.path.exists(p)]
        
    base_name = os.path.splitext(os.path.basename(raw_path))[0]
    work_dir = f"/tmp/auto_editor_{base_name}"
    os.makedirs(work_dir, exist_ok=True)
    
    theme_obj = get_theme(theme)
    
    if output_path is None:
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        output_path = os.path.join(exports_dir, f"{base_name}_master.mp4")
    else:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
    print(f"\n=======================================================")
    print(f"🎬 AUTONOMOUS VIDEO EDITOR PIPELINE (MULTI-REF ENABLED)")
    print(f"Raw Input:        {raw_path}")
    print(f"Reference Videos: {len(ref_paths)} video(s) found")
    for r_idx, rp in enumerate(ref_paths, 1):
        print(f"   [{r_idx}] {rp}")
    print(f"Output Master:    {output_path}")
    print(f"Visual Theme:     {theme}")
    print(f"Speed Multiplier: {speed}x")
    print(f"Work Directory:   {work_dir}")
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
    # STEP 4: Semantic Visual Director (Kinetic Overlays)
    # -----------------------------------------------------------------
    print("▶ Step 4: Semantic Visual Director planning kinetic motion graphics...")
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
    
    # -----------------------------------------------------------------
    # STEP 5: Multiple Reference Video Ingestion & PiP Scheduling
    # -----------------------------------------------------------------
    scheduled_brolls = []
    pip_assets = None
    if ref_paths:
        print(f"▶ Step 5: Slicing B-roll from {len(ref_paths)} reference video(s) and scheduling PiP camera...")
        ref_data = process_multiple_references(
            ref_paths=ref_paths,
            total_reel_duration=final_duration,
            work_dir=os.path.join(work_dir, "ref_processing"),
            border_color=theme_obj.glow_color
        )
        pip_assets = ref_data["pip_assets"]
        scheduled_brolls = ref_data["scheduled_brolls"]
        print(f"   Scheduled {len(scheduled_brolls)} B-roll scene(s) with speaker PiP bubble:")
        for b_idx, b in enumerate(scheduled_brolls, 1):
            print(f"     [{b_idx}] {b['start']:.2f}s - {b['start']+b['duration']:.2f}s ({b['duration']}s) from '{b['source_ref']}'")
        print()
    else:
        print("▶ Step 5: No reference videos supplied. Proceeding in pure kinetic motion graphics mode.\n")
        
    if dry_run:
        print("💡 Dry run complete. Exiting before render.")
        return {
            "status": "dry_run_complete",
            "duration": final_duration,
            "language": detected_lang,
            "segments": len(segments),
            "scenes": len(planned_scenes),
            "broll_cuts": len(scheduled_brolls)
        }
        
    # -----------------------------------------------------------------
    # STEP 6: Procedural SFX & Motion Overlays Rendering
    # -----------------------------------------------------------------
    print("▶ Step 6: Synthesizing Foley SFX and rendering transparent motion clips...")
    sfx_paths = build_default_sfx_library(os.path.join(work_dir, "sfx"))
    
    rendered_overlays = []
    for sc in planned_scenes:
        mov_path = os.path.join(work_dir, f"{sc['id']}.mov")
        print(f"   Rendering overlay {sc['id']} ({sc['duration']}s) -> {mov_path}...")
        render_scene(sc["scene"], mov_path, width=1080, height=1920, fps=30)
        sc["mov_path"] = mov_path
        rendered_overlays.append(sc)
        
    # -----------------------------------------------------------------
    # STEP 7: Multi-Layer Master Assembly (FFmpeg Compositor)
    # -----------------------------------------------------------------
    print("\n▶ Step 7: Assembling multi-track master with broadcast audio leveling...")
    
    # Input Mapping:
    # 0: Raw video
    inputs = ["-i", raw_path]
    
    # If PiP is used:
    pip_mask_idx = None
    pip_border_idx = None
    if pip_assets and scheduled_brolls:
        pip_mask_idx = len(inputs) // 2
        inputs.extend(["-i", pip_assets["mask"]])
        pip_border_idx = len(inputs) // 2
        inputs.extend(["-i", pip_assets["border"]])
        
    # B-roll inputs
    broll_indices = []
    for b in scheduled_brolls:
        broll_indices.append(len(inputs) // 2)
        inputs.extend(["-i", b["clip_path"]])
        
    # Overlay inputs
    overlay_indices = []
    for sc in rendered_overlays:
        overlay_indices.append(len(inputs) // 2)
        inputs.extend(["-i", sc["mov_path"]])
        
    # SFX inputs
    sfx_start_idx = len(inputs) // 2
    inputs.extend(["-i", sfx_paths["whoosh"]])   # sfx_start_idx + 0
    inputs.extend(["-i", sfx_paths["pop"]])      # sfx_start_idx + 1
    inputs.extend(["-i", sfx_paths["chime"]])    # sfx_start_idx + 2
    
    filter_lines = []
    
    # Video Base:
    # If B-rolls exist, split raw video into base and face crop for PiP
    if scheduled_brolls and pip_assets:
        filter_lines.append(
            f"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS,setpts=PTS/{speed},"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,split=2[v_base_full][v_base_crop]"
        )
        # Face crop & masked glowing PiP bubble
        filter_lines.append(
            f"[v_base_crop]crop=720:960:180:320,scale=360:480[speaker_face]"
        )
        filter_lines.append(
            f"[speaker_face][{pip_mask_idx}:v]alphamerge[pip_masked]"
        )
        
        num_brolls = len(scheduled_brolls)
        filter_lines.append(
            f"[pip_masked][{pip_border_idx}:v]overlay=0:0,split={num_brolls}" + "".join([f"[pb_{i+1}]" for i in range(num_brolls)])
        )
        
        curr_v = "v_base_full"
        for i, b in enumerate(scheduled_brolls):
            in_broll_idx = broll_indices[i]
            t_in = b["start"]
            t_out = b["start"] + b["duration"]
            next_bg = f"bg_broll_{i+1}"
            next_v = f"v_pip_{i+1}"
            
            # Overlay B-roll
            filter_lines.append(
                f"[{curr_v}][{in_broll_idx}:v]overlay=0:0:enable='between(t,{t_in:.2f},{t_out:.2f})'[{next_bg}]"
            )
            # Overlay floating speaker bubble at bottom right (670, 1060)
            filter_lines.append(
                f"[{next_bg}][pb_{i+1}]overlay=670:1060:enable='between(t,{t_in:.2f},{t_out:.2f})'[{next_v}]"
            )
            curr_v = next_v
    else:
        # No B-rolls: straight talking head base
        filter_lines.append(
            f"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS,setpts=PTS/{speed},"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[v_base]"
        )
        curr_v = "v_base"
        
    # Overlay kinetic cards / doodles
    for i, sc in enumerate(rendered_overlays):
        in_ov_idx = overlay_indices[i]
        next_v = f"v_ov_{i+1}"
        t_in = sc["start"]
        t_out = sc["start"] + sc["duration"]
        filter_lines.append(
            f"[{curr_v}][{in_ov_idx}:v]overlay=0:0:enable='between(t,{t_in:.2f},{t_out:.2f})'[{next_v}]"
        )
        curr_v = next_v
        
    # Subtitles
    filter_lines.append(
        f"[{curr_v}]subtitles='{captions_file}':fontsdir=/usr/share/fonts/truetype/msttcorefonts[v_final]"
    )
    
    # Audio Chain: 100% clean speech with zero reference background noise
    filter_lines.append(
        f"[0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS,atempo={speed}[a_voice_clean]"
    )
    
    # Mix Foley SFX
    sfx_audio_pads = ["[a_voice_clean]"]
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
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ COMPOSITION COMPLETE!")
    print(f"Exported: {output_path} ({file_size_mb:.2f} MB)")
    print(f"Reel Duration: {final_duration:.2f}s | Format: 1080x1920 30fps Full HD")
    print(f"B-roll Cuts: {len(scheduled_brolls)} (Muted reference B-roll + floating PiP camera)")
    print(f"Kinetic Overlays: {len(rendered_overlays)} scenes")
    print(f"Voice Quality: EBU R128 (-14 LUFS) Studio Master with Synchronized ASS Subtitles\n")
    
    return {
        "output_path": output_path,
        "duration": final_duration,
        "language": detected_lang,
        "file_size_mb": file_size_mb,
        "overlays": len(rendered_overlays),
        "broll_cuts": len(scheduled_brolls),
        "transcript_file": transcript_file,
        "captions_file": captions_file
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Autonomous Video Editor Pipeline")
    parser.add_argument("--raw", "--input", "-i", dest="raw", required=True, help="Path to raw video")
    parser.add_argument("--ref", "--reference", "-r", dest="ref", nargs="*", default=None, help="One or more reference video paths (or auto-detect from reference/ folder)")
    parser.add_argument("--output", "-o", dest="output", default=None, help="Path to output video")
    parser.add_argument("--speed", "-s", type=float, default=1.18, help="Playback speed multiplier (e.g. 1.18)")
    parser.add_argument("--theme", "-t", default="cyber_neon", choices=["cyber_neon", "apple_keynote", "vox_editorial", "fintech_emerald"])
    parser.add_argument("--no-overlays", action="store_true", help="Disable kinetic motion overlays")
    parser.add_argument("--dry-run", action="store_true", help="Run analysis and cue planning without rendering")
    
    args = parser.parse_args()
    run_auto_editor(
        raw_path=args.raw,
        ref_paths=args.ref,
        output_path=args.output,
        speed=args.speed,
        theme=args.theme,
        enable_overlays=not args.no_overlays,
        dry_run=args.dry_run
    )
