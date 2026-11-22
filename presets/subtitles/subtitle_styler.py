"""
subtitle_styler.py
Reusable module for generating synchronized, high-impact social reel ASS subtitles.
"""

import json
from typing import List, Dict, Any, Optional

HEADER_TEMPLATE = """[Script Info]
Title: {title}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,54,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,0,2,40,40,280,1
Style: Accent,Arial Black,58,&H0018EAFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.5,0,2,40,40,280,1
Style: GreenAccent,Arial Black,58,&H0030FF80,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.5,0,2,40,40,280,1
Style: RedAccent,Arial Black,58,&H003030FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.5,0,2,40,40,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(seconds: float) -> str:
    """Format float seconds to H:MM:SS.cs for ASS subtitles."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis == 100:
        secs += 1
        centis = 0
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def generate_synced_ass(
    segments: List[Dict[str, Any]],
    output_path: str,
    speed: float = 1.0,
    start_offset: float = 0.0,
    title: str = "Antigravity Reel Captions"
) -> str:
    """
    Generates an ASS subtitle file from speech segments, adjusting for playback speed
    and audio start offset.
    
    :param segments: List of dicts with 'start', 'end', 'text', and optional 'style'
    :param output_path: Destination .ass file path
    :param speed: Speed multiplier applied to the video (e.g. 1.18)
    :param start_offset: Starting cut offset in the raw video (e.g. 1.0s)
    :param title: Title in ASS header
    """
    lines = [HEADER_TEMPLATE.format(title=title)]
    for seg in segments:
        s_raw = seg['start']
        e_raw = seg['end']
        text = seg['text'].strip()
        style = seg.get('style', 'Default')
        
        # Calculate speed-adjusted timestamps
        s_adj = max(0.0, (s_raw - start_offset) / speed)
        e_adj = max(0.0, (e_raw - start_offset) / speed)
        
        if e_adj <= s_adj:
            continue
            
        start_str = format_ass_time(s_adj)
        end_str = format_ass_time(e_adj)
        lines.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{text}\n")
        
    content = "".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return output_path
