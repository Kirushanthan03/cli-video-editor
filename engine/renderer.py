"""
engine/renderer.py
Core rendering pipeline for the Antigravity Motion Engine.
Executes declarative MotionScenes using PyCairo, drawing layers, doodle accents,
and charts, piping uncompressed BGRA frames directly to FFmpeg at 30/60 fps.
Supports full alpha-transparency (ProRes 4444 / PNG) or solid MP4 output.
"""

import math
import subprocess
import os
import sys
import cairo

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.theme import get_theme, Theme
from engine.manifest import MotionScene, ElementSpec
from engine.doodle import draw_hand_drawn_oval, draw_hand_drawn_arrow, draw_hand_drawn_underline
from engine.charts import draw_coordinate_grid, draw_animated_pareto_curve, draw_circular_gauge
from motion_graphics.motion_core import (
    clamp, lerp, ease_out_cubic, ease_out_back, spring_pop,
    round_rect, draw_glow_rect, draw_pill, draw_text,
    ParticleSystem, draw_luxury_dark_bg
)

def render_scene(
    scene: MotionScene,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    crf: int = 18
) -> str:
    """
    Renders a MotionScene into an MP4 (or MOV with alpha).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    theme = get_theme(scene.theme_name)
    total_frames = int(scene.duration * fps)
    
    is_alpha = not scene.has_background or output_path.endswith(".mov")
    
    if is_alpha:
        # ProRes 4444 with alpha channel for overlays
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgra",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "prores_ks",
            "-profile:v", "4444",
            "-pix_fmt", "yuva444p10le",
            output_path
        ]
    else:
        # Standard H.264 MP4
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgra",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", str(crf),
            output_path
        ]
        
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    particles = ParticleSystem(count=45, width=width, height=height, seed=77)
    
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        
        # 1. Background
        if scene.has_background:
            draw_luxury_dark_bg(ctx, width, height, t=t, primary_aura=theme.bg_secondary, secondary_aura=theme.glow_color)
            particles.draw(ctx, t)
        else:
            # Clear transparent
            ctx.save()
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.paint()
            ctx.restore()
            
        # 2. Render Scene Elements
        for elem in scene.elements:
            e_t = t - elem.start_time
            if e_t < 0:
                continue
                
            e_prog = clamp(e_t / elem.duration) if elem.duration > 0 else 1.0
            p = elem.properties
            
            # --- CARD ELEMENT ---
            if elem.element_type == "card":
                x = p.get("x", 80)
                y = p.get("y", 600)
                w = p.get("w", 920)
                h = p.get("h", 300)
                title = p.get("title", "")
                subtitle = p.get("subtitle", "")
                
                # Spring pop in
                scale = max(0.0001, spring_pop(e_prog * 1.4))
                alpha = clamp(e_prog * 2.5)
                
                ctx.save()
                cx, cy = x + w / 2.0, y + h / 2.0
                ctx.translate(cx, cy)
                ctx.scale(scale, scale)
                ctx.translate(-cx, -cy)
                
                # Glow
                if p.get("glow", True):
                    draw_glow_rect(ctx, x, y, w, h, 24, theme.glow_color, intensity=alpha * 0.9)
                # Card base
                round_rect(ctx, x, y, w, h, 24)
                ctx.set_source_rgba(theme.card_bg[0], theme.card_bg[1], theme.card_bg[2], theme.card_bg[3] * alpha)
                ctx.fill_preserve()
                ctx.set_line_width(3.0)
                ctx.set_source_rgba(theme.card_border[0], theme.card_border[1], theme.card_border[2], theme.card_border[3] * alpha)
                ctx.stroke()
                
                # Text
                if title:
                    draw_text(ctx, title, x + 40, y + 80, font_size=52, color=(1, 1, 1, alpha))
                if subtitle:
                    draw_text(ctx, subtitle, x + 40, y + 130, font_size=28, color=(theme.text_secondary[0], theme.text_secondary[1], theme.text_secondary[2], alpha), weight=cairo.FONT_WEIGHT_NORMAL)
                ctx.restore()

            # --- DOODLE OVAL ELEMENT (anidoodle) ---
            elif elem.element_type == "doodle_oval":
                cx = p.get("cx", width / 2.0)
                cy = p.get("cy", height / 2.0)
                rx = p.get("rx", 200)
                ry = p.get("ry", 100)
                draw_hand_drawn_oval(ctx, cx, cy, rx, ry, progress=e_prog, seed=p.get("seed", 42), color=theme.doodle_color, line_width=p.get("width", 6.0))

            # --- DOODLE ARROW ELEMENT (anidoodle) ---
            elif elem.element_type == "doodle_arrow":
                x1 = p.get("x1", 200)
                y1 = p.get("y1", 400)
                x2 = p.get("x2", 400)
                y2 = p.get("y2", 500)
                draw_hand_drawn_arrow(ctx, x1, y1, x2, y2, progress=e_prog, seed=p.get("seed", 101), color=theme.doodle_color, line_width=p.get("width", 6.0), curvature=p.get("curvature", 40.0))

            # --- DOODLE UNDERLINE (anidoodle) ---
            elif elem.element_type == "doodle_underline":
                x1 = p.get("x1", 200)
                y = p.get("y", 500)
                x2 = p.get("x2", 800)
                draw_hand_drawn_underline(ctx, x1, y, x2, progress=e_prog, seed=p.get("seed", 55), color=theme.doodle_color, line_width=p.get("width", 7.0))

            # --- PARETO CURVE ELEMENT (manim) ---
            elif elem.element_type == "pareto_curve":
                ox = p.get("origin_x", 140)
                oy = p.get("origin_y", 1100)
                pw = p.get("w", 800)
                ph = p.get("h", 500)
                pts = p.get("points", [(0.1, 0.2, "GPT-3"), (0.4, 0.5, "GPT-4"), (0.85, 0.92, "Neon")])
                draw_coordinate_grid(ctx, ox, oy - ph, pw, ph, x_steps=4, y_steps=4)
                draw_animated_pareto_curve(ctx, ox, oy, pw, ph, pts, progress=e_prog, curve_color=theme.accent_secondary, highlight_idx=p.get("highlight_idx", 2), time_val=t)

            # --- CIRCULAR GAUGE ELEMENT (manim) ---
            elif elem.element_type == "gauge":
                cx = p.get("cx", width / 2.0)
                cy = p.get("cy", 850)
                r = p.get("radius", 140)
                val = p.get("value", 89.4)
                max_v = p.get("max", 100.0)
                draw_circular_gauge(ctx, cx, cy, r, val, max_v, progress=e_prog, label=p.get("label", "BENCHMARK"), accent_color=theme.accent_primary)

        # Write frame to pipe
        proc.stdin.write(surface.get_data())
        
    proc.stdin.close()
    proc.wait()
    return output_path
