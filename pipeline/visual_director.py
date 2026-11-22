"""
pipeline/visual_director.py
Semantic Visual Director:
Scans speech transcript segments to detect key moments, metrics, comparisons,
and technical entities, and generates declarative MotionScene specifications
for transparent overlays with synchronized audio cues.
"""

import re
from typing import List, Dict, Any
from engine.manifest import MotionScene, ElementSpec

def plan_visual_scenes(
    segments: List[Dict[str, Any]],
    speed: float = 1.0,
    start_offset: float = 0.0,
    theme_name: str = "cyber_neon"
) -> List[Dict[str, Any]]:
    """
    Analyzes transcript segments to generate timed motion graphic overlays.
    Returns a list of dicts:
    [
      {
        'id': 'overlay_1',
        'start': float,          # In final speed-adjusted reel timeline
        'duration': float,
        'scene': MotionScene,
        'sfx': 'whoosh' | 'pop' | 'chime'
      }
    ]
    """
    scenes = []
    scene_counter = 1
    
    # Track used timestamps to avoid overlay collisions (min 5s between overlays)
    last_overlay_end = 0.0
    
    for seg in segments:
        text = seg["text"]
        raw_start = seg["start"]
        raw_end = seg["end"]
        
        # Calculate speed-adjusted timeline position
        t_start = max(0.0, (raw_start - start_offset) / speed)
        
        # Only place overlays if there's sufficient separation
        if t_start < last_overlay_end + 3.0:
            continue
            
        elements = []
        sfx_cue = "whoosh"
        scene_dur = 4.0
        
        # Pattern 1: High-impact numbers / benchmarks / stats (e.g. 89.1, 88.2, 50%, 2x, #1, #3)
        num_match = re.search(r"(\d+(\.\d+)?%?|\#\d+|[0-9]+x)", text)
        metric_match = re.search(r"(benchmark|score|speed|rank|fast|rate|latency|token|டோக்கன்|ஸ்கோர்|ரேங்க்)", text, re.IGNORECASE)
        
        # Pattern 2: Key AI models / tools / technology mentions (English + Tamil + Multilingual)
        ai_match = re.search(r"(gemini|ஜெமினி|claude|கிளாட்|gpt|anthropic|openai|google|கூகுள்|deepmind|llama|mistral|ai|ஏஐ|workflow|steering)", text, re.IGNORECASE)
        
        # Pattern 3: Comparisons, reasoning, performance
        comp_match = re.search(r"(better|faster|compare|pricing|cost|free|reasoning|cheap|high|மாடல்|சிறந்த|வேகம்)", text, re.IGNORECASE)
        
        if num_match and metric_match:
            stat_str = num_match.group(1)
            elements.append(ElementSpec(
                element_type="card",
                start_time=0.0,
                duration=scene_dur,
                properties={
                    "x": 80, "y": 420, "w": 920, "h": 260,
                    "title": f"BENCHMARK: {stat_str}",
                    "subtitle": text[:45] + ("..." if len(text) > 45 else ""),
                    "glow": True
                }
            ))
            elements.append(ElementSpec(
                element_type="doodle_oval",
                start_time=0.4,
                duration=scene_dur - 0.4,
                properties={
                    "cx": 540, "cy": 550, "rx": 380, "ry": 100,
                    "width": 6.0, "seed": 42 + scene_counter
                }
            ))
            sfx_cue = "chime"
            
        elif ai_match:
            keyword = ai_match.group(0).upper()
            if keyword in ["ஜெமினி", "GEMINI"]:
                card_title = "✦ GEMINI AI ✦"
                sub_label = "Next-Gen Frontier Intelligence"
            elif keyword in ["WORKFLOW", "STEERING"]:
                card_title = f"✦ {keyword} ✦"
                sub_label = "Long-Running Agentic Execution"
            else:
                card_title = f"✦ {keyword} ✦"
                sub_label = text[:50] + ("..." if len(text) > 50 else "")
                
            elements.append(ElementSpec(
                element_type="card",
                start_time=0.0,
                duration=scene_dur,
                properties={
                    "x": 100, "y": 480, "w": 880, "h": 220,
                    "title": card_title,
                    "subtitle": sub_label,
                    "glow": True
                }
            ))
            elements.append(ElementSpec(
                element_type="doodle_underline",
                start_time=0.3,
                duration=scene_dur - 0.3,
                properties={
                    "x1": 180, "y": 660, "x2": 900, "width": 8.0, "seed": 88 + scene_counter
                }
            ))
            sfx_cue = "pop"
            
        elif comp_match:
            elements.append(ElementSpec(
                element_type="card",
                start_time=0.0,
                duration=scene_dur,
                properties={
                    "x": 120, "y": 520, "w": 840, "h": 220,
                    "title": "KEY CAPABILITY",
                    "subtitle": text[:50] + ("..." if len(text) > 50 else ""),
                    "glow": True
                }
            ))
            elements.append(ElementSpec(
                element_type="doodle_arrow",
                start_time=0.2,
                duration=scene_dur - 0.2,
                properties={
                    "x1": 240, "y1": 460, "x2": 450, "y2": 520, "width": 6.0, "curvature": 30.0
                }
            ))
            sfx_cue = "whoosh"
            
        # Fallback Pacing: If no cue for 22+ seconds, add a kinetic accent beat
        elif t_start > last_overlay_end + 22.0:
            elements.append(ElementSpec(
                element_type="doodle_oval",
                start_time=0.2,
                duration=scene_dur - 0.2,
                properties={
                    "cx": 540, "cy": 580, "rx": 340, "ry": 120,
                    "width": 6.0, "seed": 77 + scene_counter
                }
            ))
            sfx_cue = "whoosh"
            
        if elements:
            motion_scene = MotionScene(
                scene_id=f"overlay_cue_{scene_counter}",
                duration=scene_dur,
                theme_name=theme_name,
                has_background=False,  # Transparent overlay directly over footage!
                elements=elements
            )
            scenes.append({
                "id": f"overlay_{scene_counter}",
                "start": round(t_start, 2),
                "duration": scene_dur,
                "scene": motion_scene,
                "sfx": sfx_cue
            })
            last_overlay_end = t_start + scene_dur
            scene_counter += 1
            
            # Limit to 5-6 well-spaced high-impact overlays per reel to avoid visual clutter
            if len(scenes) >= 6:
                break
                
    return scenes
