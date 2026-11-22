"""
render_lineup.py
Renders broll_lineup_animated.mp4 (6.0s, 30fps, 1080x1920)
Features:
- Dark luxury mesh background + floating glowing bokeh particles
- Staggered overshoot slide-in of 3 model cards:
  * Top: HYDROGEN (Blue/Cyan theme, 'Fast & Lightweight')
  * Center: NEON (Electric Gold/Yellow pulsing neon border, 'BENCHMARK LEADER' spring pop-in badge, floating shine light sweep)
  * Bottom: CARBON (Violet theme, 'Heavyweight Reasoning')
- Bottom interactive spectrum indicator
"""

import math
import sys
import os
import cairo

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from motion_core import (
    VideoRenderer, ParticleSystem, draw_luxury_dark_bg,
    round_rect, draw_glow_rect, draw_pill, draw_text,
    draw_lightning, draw_star, clamp, ease_out_cubic,
    ease_out_back, spring_pop, lerp
)

OUTPUT_FILE = "/tmp/video_assets/broll_lineup_animated.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 6.0
TOTAL_FRAMES = int(FPS * DURATION)

def render():
    print(f"Rendering Lineup Animation: {TOTAL_FRAMES} frames @ {FPS} fps -> {OUTPUT_FILE}")
    renderer = VideoRenderer(OUTPUT_FILE, WIDTH, HEIGHT, FPS, crf=18)
    ctx = renderer.ctx
    particles = ParticleSystem(count=50, width=WIDTH, height=HEIGHT, seed=101)

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)
        
        # 1. Background
        draw_luxury_dark_bg(ctx, WIDTH, HEIGHT, t=t, primary_aura=(0.0, 0.4, 0.9), secondary_aura=(0.6, 0.1, 0.8))
        particles.draw(ctx, t)

        # 2. Header Animation (Fade & Slide down: t=0.0 -> 0.6)
        h_prog = clamp(t / 0.6)
        h_ease = ease_out_cubic(h_prog)
        h_alpha = h_prog
        h_offset = (1.0 - h_ease) * -60.0
        
        ctx.save()
        ctx.translate(0, h_offset)
        
        # Header Badge Pill
        draw_pill(ctx, WIDTH/2 - 190, 150, 380, 44, (1, 1, 1, 0.07 * h_alpha), (0.0, 0.9, 1.0, 0.4 * h_alpha), 1.5)
        # Glowing dot inside pill
        ctx.arc(WIDTH/2 - 160, 172, 5, 0, 2 * math.pi)
        ctx.set_source_rgba(0.0, 0.9, 1.0, 0.9 * h_alpha)
        ctx.fill()
        draw_text(ctx, "NEXT-GEN ARCHITECTURE", WIDTH/2 - 145, 172, font_size=20, color=(0.7, 0.9, 1.0, 0.95 * h_alpha), align='left')
        
        # Main Title
        draw_text(ctx, "GEMINI 2.0 FAMILY", WIDTH/2, 235, font_size=62, color=(1.0, 1.0, 1.0, 1.0 * h_alpha), align='center')
        
        # Subtitle
        draw_text(ctx, "Tailored for every latency and compute budget", WIDTH/2, 295, font_size=30, color=(0.58, 0.64, 0.72, 0.9 * h_alpha), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
        ctx.restore()

        # ----------------- CARD 1: HYDROGEN (Top) -----------------
        # Start t = 0.25, duration = 0.60
        c1_t = clamp((t - 0.25) / 0.60)
        if c1_t > 0:
            c1_ease = ease_out_back(c1_t, s=1.4)
            c1_x = -960.0 + c1_ease * 1040.0 # slides from left to X=80
            c1_alpha = clamp(c1_t * 2.0)
            c1_hover = 4.0 * math.sin(t * 2.4)
            c1_y = 380 + c1_hover
            c1_w = 920
            c1_h = 280

            ctx.save()
            # Drop shadow
            round_rect(ctx, c1_x + 6, c1_y + 12, c1_w, c1_h, 24)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.45 * c1_alpha)
            ctx.fill()

            # Glass card body
            round_rect(ctx, c1_x, c1_y, c1_w, c1_h, 24)
            pat1 = cairo.LinearGradient(c1_x, c1_y, c1_x + c1_w, c1_y + c1_h)
            pat1.add_color_stop_rgba(0.0, 0.06, 0.12, 0.22, 0.94 * c1_alpha)
            pat1.add_color_stop_rgba(1.0, 0.04, 0.08, 0.16, 0.96 * c1_alpha)
            ctx.set_source(pat1)
            ctx.fill_preserve()

            # Border
            ctx.set_source_rgba(0.0, 0.85, 1.0, 0.45 * c1_alpha)
            ctx.set_line_width(2.5)
            ctx.stroke()
            
            # Subtle cyan glow
            draw_glow_rect(ctx, c1_x, c1_y, c1_w, c1_h, 24, (0.0, 0.85, 1.0), intensity=0.45 * c1_alpha, max_spread=18, steps=4)

            # Icon Pill (Top-Right)
            draw_pill(ctx, c1_x + c1_w - 230, c1_y + 36, 190, 42, (0.0, 0.8, 1.0, 0.15 * c1_alpha), (0.0, 0.85, 1.0, 0.5 * c1_alpha), 1.5)
            draw_lightning(ctx, c1_x + c1_w - 210, c1_y + 57, 18, (0.0, 0.95, 1.0, c1_alpha))
            draw_text(ctx, "ULTRA FAST", c1_x + c1_w - 195, c1_y + 57, font_size=20, color=(0.0, 0.95, 1.0, c1_alpha), align='left')

            # Title & Subtitle
            draw_text(ctx, "HYDROGEN", c1_x + 50, c1_y + 65, font_size=52, color=(1.0, 1.0, 1.0, c1_alpha))
            draw_text(ctx, "Fast & Lightweight", c1_x + 50, c1_y + 115, font_size=30, color=(0.4, 0.85, 1.0, 0.95 * c1_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Spec Pills
            specs_c1 = ["⚡ Realtime Voice", "0.8B Active Params", "Sub-20ms Latency"]
            px = c1_x + 50
            for spec in specs_c1:
                ctx.save()
                ctx.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(20)
                ext = ctx.text_extents(spec)
                pw = ext.width + 36
                draw_pill(ctx, px, c1_y + 185, pw, 46, (1, 1, 1, 0.06 * c1_alpha), (1, 1, 1, 0.15 * c1_alpha), 1.2)
                draw_text(ctx, spec, px + pw/2, c1_y + 208, font_size=20, color=(0.85, 0.92, 1.0, 0.9 * c1_alpha), align='center')
                px += pw + 18
                ctx.restore()

            ctx.restore()

        # ----------------- CARD 2: NEON (Center - Hero Feature) -----------------
        # Start t = 0.55, duration = 0.65
        c2_t = clamp((t - 0.55) / 0.65)
        if c2_t > 0:
            c2_ease = ease_out_back(c2_t, s=1.4)
            c2_x = WIDTH + 40.0 - c2_ease * (WIDTH - 40.0) # slides from right to X=80
            c2_alpha = clamp(c2_t * 2.0)
            c2_hover = 5.0 * math.cos(t * 2.0)
            c2_y = 710 + c2_hover
            c2_w = 920
            c2_h = 330 # taller hero card

            ctx.save()
            # Drop shadow
            round_rect(ctx, c2_x + 8, c2_y + 16, c2_w, c2_h, 28)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.65 * c2_alpha)
            ctx.fill()

            # Glass card body with warm gold tint
            round_rect(ctx, c2_x, c2_y, c2_w, c2_h, 28)
            pat2 = cairo.LinearGradient(c2_x, c2_y, c2_x + c2_w, c2_y + c2_h)
            pat2.add_color_stop_rgba(0.0, 0.14, 0.12, 0.04, 0.95 * c2_alpha)
            pat2.add_color_stop_rgba(1.0, 0.08, 0.07, 0.02, 0.98 * c2_alpha)
            ctx.set_source(pat2)
            ctx.fill_preserve()

            # Active Pulsing Neon Glow Border
            pulse = 0.5 + 0.5 * math.sin(t * 5.0)
            glow_intensity = (0.85 + 0.35 * pulse) * c2_alpha
            border_w = 3.5 + 1.8 * pulse
            
            # Gold stroke
            ctx.set_source_rgba(1.0, 0.88, 0.15, 0.95 * c2_alpha)
            ctx.set_line_width(border_w)
            ctx.stroke()
            
            # Multi-layer laser neon glow
            draw_glow_rect(ctx, c2_x, c2_y, c2_w, c2_h, 28, (1.0, 0.85, 0.1), intensity=glow_intensity, max_spread=32, steps=6)

            # Specular Shine Light Sweep across the card!
            # Sweep 1: t=1.8 -> 2.8, Sweep 2: t=4.2 -> 5.2
            for s_start, s_end in [(1.8, 2.8), (4.2, 5.2)]:
                if s_start <= t <= s_end:
                    prog_shine = (t - s_start) / (s_end - s_start)
                    # Sweep X from -200 to c2_w + 200
                    shine_x = c2_x - 200.0 + prog_shine * (c2_w + 400.0)
                    
                    ctx.save()
                    # Clip to rounded card
                    round_rect(ctx, c2_x, c2_y, c2_w, c2_h, 28)
                    ctx.clip()
                    
                    # Angled light band
                    band = cairo.LinearGradient(shine_x, c2_y, shine_x + 180, c2_y + c2_h)
                    band.add_color_stop_rgba(0.0, 1.0, 0.95, 0.5, 0.0)
                    band.add_color_stop_rgba(0.4, 1.0, 0.95, 0.6, 0.12)
                    band.add_color_stop_rgba(0.5, 1.0, 1.0, 0.9, 0.45)
                    band.add_color_stop_rgba(0.6, 1.0, 0.95, 0.6, 0.12)
                    band.add_color_stop_rgba(1.0, 1.0, 0.95, 0.5, 0.0)
                    ctx.set_source(band)
                    ctx.paint()
                    ctx.restore()

            # Title: NEON
            draw_text(ctx, "NEON", c2_x + 50, c2_y + 75, font_size=62, color=(1.0, 0.94, 0.35, c2_alpha))
            draw_text(ctx, "The Mid-Weight Beast - Featured", c2_x + 50, c2_y + 130, font_size=32, color=(1.0, 0.92, 0.65, 0.95 * c2_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Pop-in Badge: 'BENCHMARK LEADER' (t = 1.30 -> 1.75)
            badge_t = clamp((t - 1.30) / 0.45)
            if badge_t > 0:
                b_scale = spring_pop(badge_t, damping=5.5, freq=14.0)
                bx = c2_x + c2_w - 200
                by = c2_y + 55
                bw = 340
                bh = 50
                
                ctx.save()
                ctx.translate(bx, by)
                ctx.scale(b_scale, b_scale)
                
                # Badge pill
                draw_pill(ctx, -bw/2, -bh/2, bw, bh, (0.28, 0.20, 0.02, 0.95), (1.0, 0.88, 0.2, 0.95), 2.2)
                draw_glow_rect(ctx, -bw/2, -bh/2, bw, bh, bh/2, (1.0, 0.85, 0.1), intensity=0.8, max_spread=16, steps=4)
                
                # Sparkle stars
                draw_star(ctx, -bw/2 + 25, 0, 10, 4, (1.0, 0.92, 0.3, 1.0))
                draw_star(ctx, bw/2 - 25, 0, 10, 4, (1.0, 0.92, 0.3, 1.0))
                
                draw_text(ctx, "BENCHMARK LEADER", 0, 0, font_size=20, color=(1.0, 0.95, 0.4, 1.0), align='center')
                ctx.restore()

            # Spec Pills (Center card)
            specs_c2 = ["👑 Best Price/Perf", "🔥 90% Parity with Frontier", "High Throughput"]
            px = c2_x + 50
            for spec in specs_c2:
                ctx.save()
                ctx.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(21)
                ext = ctx.text_extents(spec)
                pw = ext.width + 40
                draw_pill(ctx, px, c2_y + 215, pw, 52, (1.0, 0.85, 0.0, 0.12 * c2_alpha), (1.0, 0.85, 0.0, 0.4 * c2_alpha), 1.5)
                draw_text(ctx, spec, px + pw/2, c2_y + 241, font_size=21, color=(1.0, 0.95, 0.65, 0.98 * c2_alpha), align='center')
                px += pw + 18
                ctx.restore()

            ctx.restore()

        # ----------------- CARD 3: CARBON (Bottom) -----------------
        # Start t = 0.85, duration = 0.60
        c3_t = clamp((t - 0.85) / 0.60)
        if c3_t > 0:
            c3_ease = ease_out_back(c3_t, s=1.4)
            c3_x = -960.0 + c3_ease * 1040.0 # slides from left to X=80
            c3_alpha = clamp(c3_t * 2.0)
            c3_hover = 4.0 * math.sin(t * 2.2 + 1.2)
            c3_y = 1090 + c3_hover
            c3_w = 920
            c3_h = 280

            ctx.save()
            # Drop shadow
            round_rect(ctx, c3_x + 6, c3_y + 12, c3_w, c3_h, 24)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.45 * c3_alpha)
            ctx.fill()

            # Glass card body with violet tint
            round_rect(ctx, c3_x, c3_y, c3_w, c3_h, 24)
            pat3 = cairo.LinearGradient(c3_x, c3_y, c3_x + c3_w, c3_y + c3_h)
            pat3.add_color_stop_rgba(0.0, 0.12, 0.07, 0.22, 0.94 * c3_alpha)
            pat3.add_color_stop_rgba(1.0, 0.07, 0.04, 0.15, 0.96 * c3_alpha)
            ctx.set_source(pat3)
            ctx.fill_preserve()

            # Border
            ctx.set_source_rgba(0.65, 0.35, 0.98, 0.45 * c3_alpha)
            ctx.set_line_width(2.5)
            ctx.stroke()
            
            # Subtle violet glow
            draw_glow_rect(ctx, c3_x, c3_y, c3_w, c3_h, 24, (0.65, 0.35, 0.98), intensity=0.45 * c3_alpha, max_spread=18, steps=4)

            # Icon Pill (Top-Right)
            draw_pill(ctx, c3_x + c3_w - 240, c3_y + 36, 200, 42, (0.65, 0.35, 0.98, 0.15 * c3_alpha), (0.65, 0.35, 0.98, 0.5 * c3_alpha), 1.5)
            draw_text(ctx, "DEEP THINKING", c3_x + c3_w - 140, c3_y + 57, font_size=19, color=(0.85, 0.65, 1.0, c3_alpha), align='center')

            # Title & Subtitle
            draw_text(ctx, "CARBON", c3_x + 50, c3_y + 65, font_size=52, color=(1.0, 1.0, 1.0, c3_alpha))
            draw_text(ctx, "Heavyweight Reasoning", c3_x + 50, c3_y + 115, font_size=30, color=(0.8, 0.6, 1.0, 0.95 * c3_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Spec Pills
            specs_c3 = ["🧠 Complex Code & Math", "Full Context Depth", "Extended CoT"]
            px = c3_x + 50
            for spec in specs_c3:
                ctx.save()
                ctx.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(20)
                ext = ctx.text_extents(spec)
                pw = ext.width + 36
                draw_pill(ctx, px, c3_y + 185, pw, 46, (1, 1, 1, 0.06 * c3_alpha), (1, 1, 1, 0.15 * c3_alpha), 1.2)
                draw_text(ctx, spec, px + pw/2, c3_y + 208, font_size=20, color=(0.92, 0.85, 1.0, 0.9 * c3_alpha), align='center')
                px += pw + 18
                ctx.restore()

            ctx.restore()

        # ----------------- BOTTOM SPECTRUM / TICKER -----------------
        # Fades in smoothly at t = 1.6
        f_prog = clamp((t - 1.6) / 0.6)
        if f_prog > 0:
            f_ease = ease_out_cubic(f_prog)
            fy = 1530
            
            ctx.save()
            # Bar container
            draw_pill(ctx, 120, fy, 840, 72, (0.05, 0.07, 0.11, 0.85 * f_ease), (1, 1, 1, 0.12 * f_ease), 1.5)
            
            # Spectrum indicator segments
            draw_text(ctx, "SPEED", 200, fy + 36, font_size=22, color=(0.0, 0.85, 1.0, 0.85 * f_ease), align='center')
            draw_text(ctx, "•", 320, fy + 36, font_size=24, color=(1, 1, 1, 0.3 * f_ease), align='center')
            
            # Highlighted NEON pill in center
            draw_pill(ctx, 390, fy + 12, 300, 48, (1.0, 0.85, 0.1, 0.18 * f_ease), (1.0, 0.85, 0.1, 0.7 * f_ease), 1.8)
            draw_text(ctx, "⭐ NEON (SWEET SPOT)", 540, fy + 36, font_size=21, color=(1.0, 0.92, 0.3, f_ease), align='center')
            
            draw_text(ctx, "•", 760, fy + 36, font_size=24, color=(1, 1, 1, 0.3 * f_ease), align='center')
            draw_text(ctx, "REASONING", 870, fy + 36, font_size=22, color=(0.75, 0.45, 1.0, 0.85 * f_ease), align='center')
            
            # Sub-footer brand note
            draw_text(ctx, "Google DeepMind • Production Grade Intelligence", WIDTH/2, 1660, font_size=26, color=(0.45, 0.52, 0.62, 0.85 * f_ease), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
            ctx.restore()

        renderer.write_frame()

    renderer.close()

if __name__ == "__main__":
    render()
