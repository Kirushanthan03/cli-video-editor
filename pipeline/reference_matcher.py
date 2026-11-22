"""
pipeline/reference_matcher.py
Analyzes reference video, detects high-motion / UI screencast scenes,
and prepares B-roll segments for Picture-in-Picture (PiP) compositing.
Ensures reference audio is 100% stripped to avoid phantom voice contamination.
"""

import subprocess
import os
import re
import cairo
from typing import List, Dict, Any, Optional

def generate_pip_assets(output_dir: str = "/tmp", width: int = 360, height: int = 480, corner_radius: int = 36, border_color: tuple = (0.0, 0.94, 1.0)) -> Dict[str, str]:
    """
    Procedurally generates pip_mask.png and pip_border.png with glowing rounded corners.
    """
    os.makedirs(output_dir, exist_ok=True)
    mask_path = os.path.join(output_dir, "pip_mask.png")
    border_path = os.path.join(output_dir, "pip_border.png")
    
    # 1. Mask (solid white rounded rectangle on transparent background)
    surface_mask = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx_m = cairo.Context(surface_mask)
    ctx_m.set_operator(cairo.OPERATOR_CLEAR)
    ctx_m.paint()
    ctx_m.set_operator(cairo.OPERATOR_OVER)
    
    # Rounded rect path
    _draw_round_rect_path(ctx_m, 0, 0, width, height, corner_radius)
    ctx_m.set_source_rgba(1.0, 1.0, 1.0, 1.0)
    ctx_m.fill()
    surface_mask.write_to_png(mask_path)
    
    # 2. Glowing Border
    surface_border = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx_b = cairo.Context(surface_border)
    ctx_b.set_operator(cairo.OPERATOR_CLEAR)
    ctx_b.paint()
    ctx_b.set_operator(cairo.OPERATOR_OVER)
    
    # Glow passes
    r, g, b = border_color[:3]
    for p in range(6, 0, -1):
        ctx_b.save()
        _draw_round_rect_path(ctx_b, 0, 0, width, height, corner_radius)
        ctx_b.set_source_rgba(r, g, b, 0.12 / p)
        ctx_b.set_line_width(p * 3.5)
        ctx_b.stroke()
        ctx_b.restore()
        
    # Main crisp stroke
    _draw_round_rect_path(ctx_b, 0, 0, width, height, corner_radius)
    ctx_b.set_source_rgba(r, g, b, 0.95)
    ctx_b.set_line_width(5.0)
    ctx_b.stroke()
    surface_border.write_to_png(border_path)
    
    return {"mask": mask_path, "border": border_path}

def _draw_round_rect_path(ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -1.5707963, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 1.5707963)
    ctx.arc(x + r, y + h - r, r, 1.5707963, 3.1415926)
    ctx.arc(x + r, y + r, r, 3.1415926, 4.7123889)
    ctx.close_path()

def detect_reference_scenes(ref_path: str, max_cuts: int = 4) -> List[Dict[str, float]]:
    """
    Detects scene changes in the reference video using FFmpeg.
    Returns: [{'start': float, 'duration': float}]
    """
    # Probe duration
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        ref_path
    ]
    res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, text=True, check=True)
    total_dur = float(res.stdout.strip())
    
    # Run showinfo scene detector
    cmd = [
        "ffmpeg", "-i", ref_path,
        "-filter:v", "select='gt(scene,0.30)',showinfo",
        "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    pts_matches = re.findall(r"pts_time:\s*([0-9.]+)", proc.stderr)
    timestamps = [float(t) for t in pts_matches if float(t) < total_dur - 2.0]
    
    scenes = []
    if len(timestamps) >= 2:
        # Group timestamps into scene segments (min duration 3s, max 8s)
        curr_start = timestamps[0]
        for t in timestamps[1:]:
            dur = t - curr_start
            if 3.0 <= dur <= 8.5:
                scenes.append({"start": curr_start, "duration": round(dur, 2)})
                curr_start = t
                if len(scenes) >= max_cuts:
                    break
            elif dur > 8.5:
                scenes.append({"start": curr_start, "duration": 6.0})
                curr_start = t
                if len(scenes) >= max_cuts:
                    break
    
    # Fallback if few cuts detected: evenly sample 3 slices
    if len(scenes) < 2 and total_dur >= 10.0:
        slice_dur = min(6.0, total_dur / 4.0)
        scenes = [
            {"start": round(total_dur * 0.15, 2), "duration": slice_dur},
            {"start": round(total_dur * 0.50, 2), "duration": slice_dur},
            {"start": round(total_dur * 0.80, 2), "duration": slice_dur}
        ]
        
    return scenes

def extract_broll_segments(
    ref_path: str,
    scenes: List[Dict[str, float]],
    work_dir: str,
    prefix: str = "ref_broll"
) -> List[Dict[str, Any]]:
    """
    Extracts muted 1080x1920 vertical B-roll clips from reference video.
    Returns: [{'clip_path': str, 'duration': float, 'source_ref': str}]
    """
    os.makedirs(work_dir, exist_ok=True)
    broll_records = []
    
    for idx, sc in enumerate(scenes, 1):
        out_clip = os.path.join(work_dir, f"{prefix}_{idx}.mp4")
        dur = sc["duration"]
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(sc["start"]),
            "-t", str(dur),
            "-i", ref_path,
            "-an",  # ALWAYS STRIP AUDIO! Zero contamination guarantee
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "19",
            out_clip
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        broll_records.append({
            "clip_path": out_clip,
            "duration": dur,
            "source_ref": os.path.basename(ref_path)
        })
        
    return broll_records

def process_multiple_references(
    ref_paths: List[str],
    total_reel_duration: float,
    work_dir: str,
    border_color: tuple = (0.0, 0.94, 1.0)
) -> Dict[str, Any]:
    """
    Ingests multiple reference videos, extracts the best B-roll slices from each,
    and schedules them with Picture-in-Picture (PiP) timing across the reel timeline.
    """
    os.makedirs(work_dir, exist_ok=True)
    pip_assets = generate_pip_assets(
        output_dir=os.path.join(work_dir, "pip"),
        width=360,
        height=480,
        corner_radius=36,
        border_color=border_color
    )
    
    all_brolls = []
    for ref_idx, ref_p in enumerate(ref_paths, 1):
        if not os.path.exists(ref_p):
            continue
        scenes = detect_reference_scenes(ref_p, max_cuts=2)
        if scenes:
            extracted = extract_broll_segments(
                ref_path=ref_p,
                scenes=scenes[:2],
                work_dir=os.path.join(work_dir, "broll"),
                prefix=f"ref{ref_idx}_broll"
            )
            all_brolls.extend(extracted)
            
    if not all_brolls:
        return {"pip_assets": pip_assets, "scheduled_brolls": []}
        
    # Schedule B-rolls across the reel
    # Leave 8s intro on speaker, leave 6s outro on speaker
    # Distribute B-rolls with spacing in between
    avail_start = 8.0
    avail_end = max(avail_start + 10.0, total_reel_duration - 6.0)
    avail_span = avail_end - avail_start
    
    num_cuts = min(len(all_brolls), 5)
    brolls_to_schedule = all_brolls[:num_cuts]
    
    interval = avail_span / float(num_cuts + 1)
    
    scheduled = []
    curr_t = avail_start + (interval * 0.5)
    for b in brolls_to_schedule:
        dur = min(b["duration"], 6.5)
        # Cap duration to avoid overlapping next interval
        dur = min(dur, interval * 0.85)
        dur = max(2.5, round(dur, 2))
        
        scheduled.append({
            "clip_path": b["clip_path"],
            "start": round(curr_t, 2),
            "duration": dur,
            "source_ref": b["source_ref"]
        })
        curr_t += interval
        
    return {
        "pip_assets": pip_assets,
        "scheduled_brolls": scheduled
    }
