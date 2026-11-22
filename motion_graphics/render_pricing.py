"""
render_pricing.py
Renders broll_pricing_animated.mp4 (5.0s, 30fps, 1080x1920)
Features:
- Header: 'GOOGLE AI STUDIO PRICING'
- Two large animated stat cards with numbers counting up:
  * Card 1: '$3.00' (Sub: 'per 1M Input Tokens', counter counts from $0.00 to $3.00)
  * Card 2: '$50.00' (Sub: 'per 1M Output Tokens', counter counts from $0.00 to $50.00)
- Animated badge: '⚡ Extreme Speed + Low Cost' with glowing border.
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

OUTPUT_FILE = "/tmp/video_assets/broll_pricing_animated.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 5.0
TOTAL_FRAMES = int(FPS * DURATION)

def render():
    print(f"Rendering Pricing Animation: {TOTAL_FRAMES} frames @ {FPS} fps -> {OUTPUT_FILE}")
    renderer = VideoRenderer(OUTPUT_FILE, WIDTH, HEIGHT, FPS, crf=18)
    ctx = renderer.ctx
    particles = ParticleSystem(count=50, width=WIDTH, height=HEIGHT, seed=303)

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)

        # 1. Background
        draw_luxury_dark_bg(ctx, WIDTH, HEIGHT, t=t, primary_aura=(0.0, 0.45, 0.8), secondary_aura=(0.7, 0.5, 0.1))
        particles.draw(ctx, t)

        # 2. Header Animation (Fade & Slide down: t=0.0 -> 0.55)
        h_prog = clamp(t / 0.55)
        h_ease = ease_out_cubic(h_prog)
        h_alpha = h_prog
        h_offset = (1.0 - h_ease) * -50.0

        ctx.save()
        ctx.translate(0, h_offset)

        # Category Pill
        draw_pill(ctx, WIDTH/2 - 210, 140, 420, 44, (1, 1, 1, 0.08 * h_alpha), (0.0, 0.85, 1.0, 0.45 * h_alpha), 1.5)
        ctx.arc(WIDTH/2 - 180, 162, 5, 0, 2 * math.pi)
        ctx.set_source_rgba(0.0, 0.9, 1.0, 0.95 * h_alpha)
        ctx.fill()
        draw_text(ctx, "DISRUPTIVE DEVELOPER ECONOMICS", WIDTH/2 - 165, 162, font_size=19, color=(0.75, 0.92, 1.0, 0.95 * h_alpha), align='left')

        # Main Header: GOOGLE AI STUDIO PRICING
        draw_text(ctx, "GOOGLE AI STUDIO PRICING", WIDTH/2, 225, font_size=58, color=(1.0, 1.0, 1.0, h_alpha), align='center')

        # Subtitle
        draw_text(ctx, "Unrivaled Performance at Unbeatable Cost", WIDTH/2, 285, font_size=32, color=(0.4, 0.85, 1.0, 0.95 * h_alpha), weight=cairo.FONT_WEIGHT_BOLD, align='center')

        # Sub-note
        draw_text(ctx, "Pay-as-you-go API • Zero Platform Markup", WIDTH/2, 335, font_size=23, color=(0.55, 0.62, 0.72, 0.85 * h_alpha), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
        ctx.restore()

        # ----------------- CARD 1: INPUT PRICING ($3.00) -----------------
        # Entrance: t = 0.25s -> 0.80s
        c1_t = clamp((t - 0.25) / 0.55)
        if c1_t > 0:
            c1_ease = ease_out_back(c1_t, s=1.3)
            c1_y = 420 + (1.0 - c1_ease) * 70.0
            c1_alpha = clamp(c1_t * 2.0)
            c1_hover = 3.5 * math.sin(t * 2.3)
            curr_c1_y = c1_y + c1_hover
            c1_w = 920
            c1_h = 340

            # Number Counter: counts smoothly from $0.00 to $3.00
            # Timing: t = 0.4s to 2.0s
            c1_count_prog = ease_out_cubic(clamp((t - 0.4) / 1.6))
            c1_val = lerp(0.00, 3.00, c1_count_prog)

            ctx.save()
            # Drop shadow
            round_rect(ctx, 88, curr_c1_y + 12, c1_w, c1_h, 26)
            ctx.set_source_rgba(0, 0, 0, 0.5 * c1_alpha)
            ctx.fill()

            # Glass card body
            round_rect(ctx, 80, curr_c1_y, c1_w, c1_h, 26)
            pat1 = cairo.LinearGradient(80, curr_c1_y, 80 + c1_w, curr_c1_y + c1_h)
            pat1.add_color_stop_rgba(0.0, 0.05, 0.11, 0.19, 0.95 * c1_alpha)
            pat1.add_color_stop_rgba(1.0, 0.03, 0.07, 0.14, 0.98 * c1_alpha)
            ctx.set_source(pat1)
            ctx.fill_preserve()

            # Cyan border
            ctx.set_source_rgba(0.0, 0.85, 1.0, 0.65 * c1_alpha)
            ctx.set_line_width(2.8)
            ctx.stroke()

            # Subtle cyan outer glow
            draw_glow_rect(ctx, 80, curr_c1_y, c1_w, c1_h, 26, (0.0, 0.85, 1.0), intensity=0.6 * c1_alpha, max_spread=22, steps=4)

            # Top Pill Badge
            draw_pill(ctx, 120, curr_c1_y + 35, 170, 40, (0.0, 0.8, 1.0, 0.15 * c1_alpha), (0.0, 0.85, 1.0, 0.6 * c1_alpha), 1.5)
            draw_text(ctx, "INPUT TOKENS", 205, curr_c1_y + 55, font_size=19, color=(0.0, 0.95, 1.0, c1_alpha), align='center')

            # Right tag: '⚡ FAST INGESTION'
            draw_pill(ctx, 770, curr_c1_y + 35, 190, 40, (1, 1, 1, 0.06 * c1_alpha), (1, 1, 1, 0.15 * c1_alpha), 1.2)
            draw_text(ctx, "1M+ Context", 865, curr_c1_y + 55, font_size=19, color=(0.8, 0.9, 1.0, 0.85 * c1_alpha), align='center')

            # Huge Number Counter: $3.00
            val_str1 = f"${c1_val:.2f}"
            draw_text(ctx, val_str1, 120, curr_c1_y + 145, font_size=96, color=(1.0, 1.0, 1.0, c1_alpha))

            # Subtitle: 'per 1M Input Tokens'
            draw_text(ctx, "per 1M Input Tokens", 120, curr_c1_y + 225, font_size=32, color=(0.4, 0.85, 1.0, 0.95 * c1_alpha), weight=cairo.FONT_WEIGHT_BOLD)

            # Bottom Perk Pill
            draw_pill(ctx, 120, curr_c1_y + 265, 480, 46, (1, 1, 1, 0.06 * c1_alpha), (0.0, 0.85, 1.0, 0.3 * c1_alpha), 1.2)
            draw_lightning(ctx, 145, curr_c1_y + 288, 18, (0.0, 0.95, 1.0, c1_alpha))
            draw_text(ctx, "80% Cheaper than Frontier Competitors", 168, curr_c1_y + 288, font_size=20, color=(0.85, 0.95, 1.0, 0.95 * c1_alpha), align='left')

            ctx.restore()

        # ----------------- CARD 2: OUTPUT PRICING ($50.00) -----------------
        # Entrance: t = 0.55s -> 1.10s
        c2_t = clamp((t - 0.55) / 0.55)
        if c2_t > 0:
            c2_ease = ease_out_back(c2_t, s=1.3)
            c2_y = 800 + (1.0 - c2_ease) * 70.0
            c2_alpha = clamp(c2_t * 2.0)
            c2_hover = 3.5 * math.cos(t * 2.1)
            curr_c2_y = c2_y + c2_hover
            c2_w = 920
            c2_h = 340

            # Number Counter: counts smoothly from $0.00 to $50.00
            # Timing: t = 0.7s to 2.4s
            c2_count_prog = ease_out_cubic(clamp((t - 0.7) / 1.7))
            c2_val = lerp(0.00, 50.00, c2_count_prog)

            ctx.save()
            # Drop shadow
            round_rect(ctx, 88, curr_c2_y + 12, c2_w, c2_h, 26)
            ctx.set_source_rgba(0, 0, 0, 0.5 * c2_alpha)
            ctx.fill()

            # Glass card body with warm gold tint
            round_rect(ctx, 80, curr_c2_y, c2_w, c2_h, 26)
            pat2 = cairo.LinearGradient(80, curr_c2_y, 80 + c2_w, curr_c2_y + c2_h)
            pat2.add_color_stop_rgba(0.0, 0.13, 0.10, 0.03, 0.95 * c2_alpha)
            pat2.add_color_stop_rgba(1.0, 0.08, 0.06, 0.02, 0.98 * c2_alpha)
            ctx.set_source(pat2)
            ctx.fill_preserve()

            # Gold pulsing border
            pulse2 = 0.5 + 0.5 * math.sin(t * 4.5)
            ctx.set_source_rgba(1.0, 0.85, 0.15, 0.85 * c2_alpha)
            ctx.set_line_width(2.8 + 1.0 * pulse2)
            ctx.stroke()

            # Gold outer glow
            draw_glow_rect(ctx, 80, curr_c2_y, c2_w, c2_h, 26, (1.0, 0.85, 0.1), intensity=0.75 * c2_alpha, max_spread=24, steps=4)

            # Top Pill Badge
            draw_pill(ctx, 120, curr_c2_y + 35, 190, 40, (1.0, 0.85, 0.1, 0.15 * c2_alpha), (1.0, 0.85, 0.1, 0.6 * c2_alpha), 1.5)
            draw_text(ctx, "OUTPUT TOKENS", 215, curr_c2_y + 55, font_size=19, color=(1.0, 0.9, 0.3, c1_alpha), align='center')

            # Right tag: '🧠 FULL REASONING'
            draw_pill(ctx, 730, curr_c2_y + 35, 230, 40, (1, 1, 1, 0.06 * c2_alpha), (1, 1, 1, 0.15 * c2_alpha), 1.2)
            draw_text(ctx, "High Throughput", 845, curr_c2_y + 55, font_size=19, color=(1.0, 0.92, 0.6, 0.85 * c2_alpha), align='center')

            # Huge Number Counter: $50.00
            val_str2 = f"${c2_val:.2f}"
            draw_text(ctx, val_str2, 120, curr_c2_y + 145, font_size=96, color=(1.0, 0.94, 0.4, c2_alpha))

            # Subtitle: 'per 1M Output Tokens'
            draw_text(ctx, "per 1M Output Tokens", 120, curr_c2_y + 225, font_size=32, color=(1.0, 0.90, 0.6, 0.95 * c2_alpha), weight=cairo.FONT_WEIGHT_BOLD)

            # Bottom Perk Pill
            draw_pill(ctx, 120, curr_c2_y + 265, 520, 46, (1, 1, 1, 0.06 * c2_alpha), (1.0, 0.85, 0.1, 0.3 * c2_alpha), 1.2)
            draw_star(ctx, 145, curr_c2_y + 288, 9, 3.5, (1.0, 0.88, 0.25, c2_alpha))
            draw_text(ctx, "Unrestricted Reasoning & Code Generation", 168, curr_c2_y + 288, font_size=20, color=(1.0, 0.95, 0.75, 0.95 * c2_alpha), align='left')

            ctx.restore()

        # ----------------- ANIMATED BADGE: '⚡ Extreme Speed + Low Cost' -----------------
        # Prompt: "Animated badge: '⚡ Extreme Speed + Low Cost' with glowing border."
        # Pops in at t = 2.2s -> 2.8s
        badge_t = clamp((t - 2.2) / 0.55)
        if badge_t > 0:
            b_scale = spring_pop(badge_t, damping=5.2, freq=13.0)
            bcx = WIDTH / 2
            bcy = 1240
            bw = 880
            bh = 120

            ctx.save()
            ctx.translate(bcx, bcy)
            ctx.scale(b_scale, b_scale)

            # Dark glass background
            round_rect(ctx, -bw/2, -bh/2, bw, bh, 30)
            pat_b = cairo.LinearGradient(-bw/2, -bh/2, bw/2, bh/2)
            pat_b.add_color_stop_rgba(0.0, 0.04, 0.12, 0.18, 0.96)
            pat_b.add_color_stop_rgba(0.5, 0.15, 0.13, 0.04, 0.97)
            pat_b.add_color_stop_rgba(1.0, 0.04, 0.14, 0.10, 0.96)
            ctx.set_source(pat_b)
            ctx.fill_preserve()

            # Glowing Animated Border (breathing gold/cyan glow)
            b_pulse = 0.5 + 0.5 * math.sin(t * 5.0)
            pat_border = cairo.LinearGradient(-bw/2, 0, bw/2, 0)
            pat_border.add_color_stop_rgba(0.0, 0.0, 0.9, 1.0, 0.95)
            pat_border.add_color_stop_rgba(0.5, 1.0, 0.88, 0.2, 1.0)
            pat_border.add_color_stop_rgba(1.0, 0.2, 0.9, 0.5, 0.95)
            ctx.set_source(pat_border)
            ctx.set_line_width(3.5 + 1.5 * b_pulse)
            ctx.stroke()

            # Multi-layer laser outer glow
            draw_glow_rect(ctx, -bw/2, -bh/2, bw, bh, 30, (1.0, 0.85, 0.1), intensity=0.9 + 0.4 * b_pulse, max_spread=28, steps=5)

            # Left Vector Lightning
            draw_lightning(ctx, -bw/2 + 65, 0, 32, (1.0, 0.9, 0.2, 1.0))

            # Main Badge Text: '⚡ Extreme Speed + Low Cost'
            draw_text(ctx, "⚡ Extreme Speed + Low Cost", 15, -12, font_size=42, color=(1.0, 1.0, 1.0, 1.0), align='center')
            draw_text(ctx, "Lowest Latency-per-Dollar in the AI Industry Today", 15, 28, font_size=23, color=(0.4, 0.9, 1.0, 0.95), weight=cairo.FONT_WEIGHT_NORMAL, align='center')

            ctx.restore()

        # ----------------- BOTTOM COMPARISON / CALLOUT -----------------
        # Fades in at t = 2.8s
        comp_t = clamp((t - 2.8) / 0.6)
        if comp_t > 0:
            c_alpha = ease_out_cubic(comp_t)
            cy = 1430

            ctx.save()
            # Comparison banner
            draw_pill(ctx, 90, cy, 900, 76, (0.05, 0.07, 0.12, 0.88 * c_alpha), (1, 1, 1, 0.12 * c_alpha), 1.5)

            # Model 1
            draw_text(ctx, "Gemini 2.0 / Neon", 180, cy + 38, font_size=23, color=(1.0, 0.88, 0.2, c_alpha), align='center')
            draw_text(ctx, "$3.00", 300, cy + 38, font_size=24, color=(1.0, 1.0, 1.0, c_alpha), align='center')

            draw_text(ctx, "vs", 380, cy + 38, font_size=20, color=(1, 1, 1, 0.3 * c_alpha), align='center')

            # Model 2
            draw_text(ctx, "Claude 3.5", 480, cy + 38, font_size=23, color=(0.7, 0.75, 0.85, 0.9 * c_alpha), align='center')
            draw_text(ctx, "$3.00", 590, cy + 38, font_size=24, color=(0.85, 0.85, 0.85, c_alpha), align='center')

            draw_text(ctx, "vs", 670, cy + 38, font_size=20, color=(1, 1, 1, 0.3 * c_alpha), align='center')

            # Model 3
            draw_text(ctx, "GPT-4o", 760, cy + 38, font_size=23, color=(0.7, 0.75, 0.85, 0.9 * c_alpha), align='center')
            draw_text(ctx, "$5.00", 860, cy + 38, font_size=24, color=(0.85, 0.85, 0.85, c_alpha), align='center')

            # Bottom note
            draw_text(ctx, "Google AI Studio • Rate Limits: Up to 2,000 RPM Production Scale", WIDTH/2, 1560, font_size=24, color=(0.45, 0.52, 0.62, 0.85 * c_alpha), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
            ctx.restore()

        renderer.write_frame()

    renderer.close()

if __name__ == "__main__":
    render()
