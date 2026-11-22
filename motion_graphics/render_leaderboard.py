"""
render_leaderboard.py
Renders broll_leaderboard_animated.mp4 (6.0s, 30fps, 1080x1920)
Features:
- Header: 'ARTIFICIAL ANALYSIS' with subtitle 'Intelligence vs Speed'
- Animated horizontal ranking bars that smoothly grow from 0 to target width with ease-out:
  * Bar 1: Claude 3.5 Sonnet (Score counter ticking up to 88.2)
  * Bar 2: GPT-4o (Score counter ticking up to 87.5)
  * Bar 3: GEMINI 4 NEON (Highlight bar in glowing cyan/gold, score counter ticking up to 89.1, '#3 OVERALL' badge popping in)
- Below it: animated pop-in tag: 'Beats Claude Opus 5.5 & GPT-6.2' with green glow.
"""

import math
import sys
import os
import cairo

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from motion_core import (
    VideoRenderer, ParticleSystem, draw_luxury_dark_bg,
    round_rect, draw_glow_rect, draw_pill, draw_text,
    draw_lightning, draw_star, draw_check_badge, clamp,
    ease_out_cubic, ease_out_back, spring_pop, lerp
)

OUTPUT_FILE = "/tmp/video_assets/broll_leaderboard_animated.mp4"
WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 6.0
TOTAL_FRAMES = int(FPS * DURATION)

def render():
    print(f"Rendering Leaderboard Animation: {TOTAL_FRAMES} frames @ {FPS} fps -> {OUTPUT_FILE}")
    renderer = VideoRenderer(OUTPUT_FILE, WIDTH, HEIGHT, FPS, crf=18)
    ctx = renderer.ctx
    particles = ParticleSystem(count=50, width=WIDTH, height=HEIGHT, seed=202)

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)

        # 1. Background
        draw_luxury_dark_bg(ctx, WIDTH, HEIGHT, t=t, primary_aura=(0.0, 0.4, 0.7), secondary_aura=(0.1, 0.6, 0.4))
        particles.draw(ctx, t)

        # Subtle benchmark vertical guide lines in background
        ctx.save()
        guide_xs = [400, 550, 700, 850, 960]
        guide_labels = ["60", "70", "80", "90", "100"]
        for gx, gl in zip(guide_xs, guide_labels):
            ctx.set_source_rgba(1, 1, 1, 0.05)
            ctx.set_line_width(1.0)
            ctx.move_to(gx, 440)
            ctx.line_to(gx, 1160)
            ctx.stroke()
            draw_text(ctx, gl, gx, 425, font_size=18, color=(1, 1, 1, 0.25), align='center')
        ctx.restore()

        # 2. Header Animation (Fade & Slide down: t=0.0 -> 0.6)
        h_prog = clamp(t / 0.6)
        h_ease = ease_out_cubic(h_prog)
        h_alpha = h_prog
        h_offset = (1.0 - h_ease) * -50.0

        ctx.save()
        ctx.translate(0, h_offset)

        # Pill badge
        draw_pill(ctx, WIDTH/2 - 210, 140, 420, 44, (1, 1, 1, 0.07 * h_alpha), (0.1, 0.8, 0.5, 0.45 * h_alpha), 1.5)
        # Glowing dot inside pill
        ctx.arc(WIDTH/2 - 180, 162, 5, 0, 2 * math.pi)
        ctx.set_source_rgba(0.2, 0.9, 0.6, 0.95 * h_alpha)
        ctx.fill()
        draw_text(ctx, "OFFICIAL QUALITY BENCHMARK", WIDTH/2 - 165, 162, font_size=20, color=(0.7, 0.95, 0.8, 0.95 * h_alpha), align='left')

        # Main Title: ARTIFICIAL ANALYSIS
        draw_text(ctx, "ARTIFICIAL ANALYSIS", WIDTH/2, 225, font_size=62, color=(1.0, 1.0, 1.0, h_alpha), align='center')

        # Subtitle: Intelligence vs Speed
        draw_text(ctx, "Intelligence vs Speed", WIDTH/2, 285, font_size=34, color=(0.4, 0.85, 1.0, 0.95 * h_alpha), weight=cairo.FONT_WEIGHT_BOLD, align='center')

        # Metric Description
        draw_text(ctx, "Comprehensive Coding, Math & Reasoning Index (MMLU-Pro / HumanEval)", WIDTH/2, 335, font_size=23, color=(0.55, 0.62, 0.72, 0.85 * h_alpha), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
        ctx.restore()

        # ----------------- RANKING BARS -----------------
        # Common track geometry
        track_x = 400
        track_w = 460
        track_h = 28
        max_score = 100.0

        # --- BAR 1: Claude 3.5 Sonnet ---
        # Entrance: t = 0.3s -> 0.8s
        b1_ent = clamp((t - 0.3) / 0.5)
        if b1_ent > 0:
            b1_ease = ease_out_back(b1_ent, s=1.2)
            b1_y = 480 + (1.0 - b1_ease) * 40.0
            b1_alpha = clamp(b1_ent * 2.0)

            # Score counter animation: t = 0.4s -> 1.9s
            b1_score_prog = ease_out_cubic(clamp((t - 0.4) / 1.5))
            b1_score = lerp(0.0, 88.2, b1_score_prog)
            b1_bar_w = track_w * (b1_score / max_score)

            ctx.save()
            # Card background
            round_rect(ctx, 80, b1_y, 920, 140, 20)
            ctx.set_source_rgba(0.07, 0.08, 0.12, 0.88 * b1_alpha)
            ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, 0.10 * b1_alpha)
            ctx.set_line_width(1.5)
            ctx.stroke()

            # Model Label
            draw_text(ctx, "Claude 3.5 Sonnet", 120, b1_y + 50, font_size=32, color=(1.0, 1.0, 1.0, b1_alpha))
            draw_text(ctx, "Anthropic • Frontier Reasoning", 120, b1_y + 90, font_size=22, color=(0.6, 0.65, 0.75, 0.9 * b1_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Bar Track
            round_rect(ctx, track_x, b1_y + 56, track_w, track_h, track_h/2.0)
            ctx.set_source_rgba(1, 1, 1, 0.08 * b1_alpha)
            ctx.fill()

            # Animated Bar Fill (Terracotta / Orange)
            if b1_bar_w > 8:
                round_rect(ctx, track_x, b1_y + 56, b1_bar_w, track_h, track_h/2.0)
                pat_b1 = cairo.LinearGradient(track_x, b1_y + 56, track_x + b1_bar_w, b1_y + 56)
                pat_b1.add_color_stop_rgba(0.0, 0.95, 0.45, 0.15, 0.95 * b1_alpha)
                pat_b1.add_color_stop_rgba(1.0, 1.00, 0.60, 0.25, 1.0 * b1_alpha)
                ctx.set_source(pat_b1)
                ctx.fill()

            # Score Counter Number
            draw_text(ctx, f"{b1_score:.1f}", 930, b1_y + 70, font_size=38, color=(1.0, 0.75, 0.4, b1_alpha), align='right')
            ctx.restore()

        # --- BAR 2: GPT-4o ---
        # Entrance: t = 0.5s -> 1.0s
        b2_ent = clamp((t - 0.5) / 0.5)
        if b2_ent > 0:
            b2_ease = ease_out_back(b2_ent, s=1.2)
            b2_y = 650 + (1.0 - b2_ease) * 40.0
            b2_alpha = clamp(b2_ent * 2.0)

            # Score counter animation: t = 0.6s -> 2.1s
            b2_score_prog = ease_out_cubic(clamp((t - 0.6) / 1.5))
            b2_score = lerp(0.0, 87.5, b2_score_prog)
            b2_bar_w = track_w * (b2_score / max_score)

            ctx.save()
            # Card background
            round_rect(ctx, 80, b2_y, 920, 140, 20)
            ctx.set_source_rgba(0.07, 0.08, 0.12, 0.88 * b2_alpha)
            ctx.fill_preserve()
            ctx.set_source_rgba(1, 1, 1, 0.10 * b2_alpha)
            ctx.set_line_width(1.5)
            ctx.stroke()

            # Model Label
            draw_text(ctx, "GPT-4o", 120, b2_y + 50, font_size=32, color=(1.0, 1.0, 1.0, b2_alpha))
            draw_text(ctx, "OpenAI • Omni Flagship", 120, b2_y + 90, font_size=22, color=(0.6, 0.65, 0.75, 0.9 * b2_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Bar Track
            round_rect(ctx, track_x, b2_y + 56, track_w, track_h, track_h/2.0)
            ctx.set_source_rgba(1, 1, 1, 0.08 * b2_alpha)
            ctx.fill()

            # Animated Bar Fill (Emerald / Teal)
            if b2_bar_w > 8:
                round_rect(ctx, track_x, b2_y + 56, b2_bar_w, track_h, track_h/2.0)
                pat_b2 = cairo.LinearGradient(track_x, b2_y + 56, track_x + b2_bar_w, b2_y + 56)
                pat_b2.add_color_stop_rgba(0.0, 0.08, 0.72, 0.50, 0.95 * b2_alpha)
                pat_b2.add_color_stop_rgba(1.0, 0.15, 0.90, 0.65, 1.0 * b2_alpha)
                ctx.set_source(pat_b2)
                ctx.fill()

            # Score Counter Number
            draw_text(ctx, f"{b2_score:.1f}", 930, b2_y + 70, font_size=38, color=(0.4, 0.95, 0.7, b2_alpha), align='right')
            ctx.restore()

        # --- BAR 3: GEMINI 4 NEON (HERO ROW - HIGHLIGHT) ---
        # Entrance: t = 0.7s -> 1.2s
        b3_ent = clamp((t - 0.7) / 0.5)
        if b3_ent > 0:
            b3_ease = ease_out_back(b3_ent, s=1.2)
            b3_y = 820 + (1.0 - b3_ease) * 45.0
            b3_alpha = clamp(b3_ent * 2.0)

            # Score counter animation: t = 0.8s -> 2.5s
            # Counts up smoothly and passes both 87.5 and 88.2, hitting 89.1!
            b3_score_prog = ease_out_cubic(clamp((t - 0.8) / 1.7))
            b3_score = lerp(0.0, 89.1, b3_score_prog)
            b3_bar_w = track_w * (b3_score / max_score)

            ctx.save()
            # Elevated Hero Card with glowing cyan/gold border
            round_rect(ctx, 80, b3_y, 920, 180, 24)
            pat_card = cairo.LinearGradient(80, b3_y, 1000, b3_y + 180)
            pat_card.add_color_stop_rgba(0.0, 0.08, 0.12, 0.20, 0.95 * b3_alpha)
            pat_card.add_color_stop_rgba(1.0, 0.15, 0.12, 0.03, 0.98 * b3_alpha)
            ctx.set_source(pat_card)
            ctx.fill_preserve()

            # Active pulsing hero border
            pulse_b3 = 0.5 + 0.5 * math.sin(t * 5.0)
            b3_border_w = 3.2 + 1.5 * pulse_b3
            ctx.set_source_rgba(0.0, 0.95, 1.0, 0.9 * b3_alpha)
            ctx.set_line_width(b3_border_w)
            ctx.stroke()

            # Glowing Cyan/Gold aura around hero card
            draw_glow_rect(ctx, 80, b3_y, 920, 180, 24, (0.0, 0.9, 1.0), intensity=0.8 * b3_alpha, max_spread=24, steps=5)

            # Model Label (Large & Radiant)
            draw_lightning(ctx, 120, b3_y + 48, 22, (0.0, 0.95, 1.0, b3_alpha))
            draw_text(ctx, "GEMINI 4 NEON", 145, b3_y + 48, font_size=36, color=(1.0, 0.96, 0.6, b3_alpha))
            draw_text(ctx, "Google DeepMind • Mid-Weight Champion", 120, b3_y + 88, font_size=23, color=(0.4, 0.9, 1.0, 0.95 * b3_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Pop-in Badge: '#3 OVERALL'
            # Pops in at t = 2.2s -> 2.7s right beside the title!
            badge3_t = clamp((t - 2.2) / 0.45)
            if badge3_t > 0:
                b3_scale = spring_pop(badge3_t, damping=5.5, freq=14.0)
                bx = 550
                by = b3_y + 48
                bw = 190
                bh = 40

                ctx.save()
                ctx.translate(bx, by)
                ctx.scale(b3_scale, b3_scale)
                
                # Metallic gold badge
                draw_pill(ctx, -bw/2, -bh/2, bw, bh, (0.35, 0.25, 0.02, 0.95), (1.0, 0.88, 0.2, 0.95), 2.0)
                draw_glow_rect(ctx, -bw/2, -bh/2, bw, bh, bh/2, (1.0, 0.85, 0.1), intensity=0.9, max_spread=14, steps=3)
                draw_star(ctx, -bw/2 + 20, 0, 8, 3.5, (1.0, 0.95, 0.4, 1.0))
                draw_text(ctx, "#3 OVERALL", 8, 0, font_size=20, color=(1.0, 0.95, 0.4, 1.0), align='center')
                ctx.restore()

            # Hero Bar Track (slightly thicker)
            hero_track_h = 34
            round_rect(ctx, track_x, b3_y + 115, track_w, hero_track_h, hero_track_h/2.0)
            ctx.set_source_rgba(1, 1, 1, 0.10 * b3_alpha)
            ctx.fill()

            # Glowing Cyan-to-Gold animated bar fill
            if b3_bar_w > 8:
                round_rect(ctx, track_x, b3_y + 115, b3_bar_w, hero_track_h, hero_track_h/2.0)
                pat_hero = cairo.LinearGradient(track_x, b3_y + 115, track_x + b3_bar_w, b3_y + 115)
                pat_hero.add_color_stop_rgba(0.0, 0.0, 0.85, 1.0, 0.95 * b3_alpha)
                pat_hero.add_color_stop_rgba(0.7, 1.0, 0.85, 0.1, 1.0 * b3_alpha)
                pat_hero.add_color_stop_rgba(1.0, 1.0, 0.95, 0.4, 1.0 * b3_alpha)
                ctx.set_source(pat_hero)
                ctx.fill()

                # Laser glow on tip of bar
                tip_x = track_x + b3_bar_w
                ctx.arc(tip_x, b3_y + 115 + hero_track_h/2.0, 8, 0, 2 * math.pi)
                ctx.set_source_rgba(1.0, 0.95, 0.5, 0.9 * b3_alpha)
                ctx.fill()

            # Score Counter Number (Large glowing hero score)
            draw_text(ctx, f"{b3_score:.1f}", 930, b3_y + 132, font_size=46, color=(1.0, 0.92, 0.35, b3_alpha), align='right')
            ctx.restore()

        # ----------------- POP-IN CALLOUT TAG (GREEN GLOW) -----------------
        # Prompt: "Below it: animated pop-in tag: 'Beats Claude Opus 5.5 & GPT-6.2' with green glow."
        # Pops in at t = 2.8s -> 3.4s
        tag_t = clamp((t - 2.8) / 0.55)
        if tag_t > 0:
            tag_scale = spring_pop(tag_t, damping=5.2, freq=12.0)
            tag_cx = WIDTH / 2
            tag_cy = 1120
            tag_w = 880
            tag_h = 110

            ctx.save()
            ctx.translate(tag_cx, tag_cy)
            ctx.scale(tag_scale, tag_scale)

            # Emerald Green glowing card
            round_rect(ctx, -tag_w/2, -tag_h/2, tag_w, tag_h, 28)
            pat_tag = cairo.LinearGradient(-tag_w/2, 0, tag_w/2, 0)
            pat_tag.add_color_stop_rgba(0.0, 0.02, 0.18, 0.08, 0.96)
            pat_tag.add_color_stop_rgba(1.0, 0.04, 0.25, 0.12, 0.98)
            ctx.set_source(pat_tag)
            ctx.fill_preserve()

            # Pulsing Green Border
            green_pulse = 0.5 + 0.5 * math.sin(t * 4.5)
            ctx.set_source_rgba(0.2, 0.95, 0.45, 0.95)
            ctx.set_line_width(3.2 + 1.2 * green_pulse)
            ctx.stroke()

            # Green Glow
            draw_glow_rect(ctx, -tag_w/2, -tag_h/2, tag_w, tag_h, 28, (0.2, 0.9, 0.4), intensity=1.0 + 0.3 * green_pulse, max_spread=30, steps=5)

            # Checkmark badge icon
            draw_check_badge(ctx, -tag_w/2 + 55, 0, 24, (0.1, 0.85, 0.35, 1.0), (1.0, 1.0, 1.0, 1.0))

            # Tag text: 'Beats Claude Opus 5.5 & GPT-6.2'
            draw_text(ctx, "Beats Claude Opus 5.5 & GPT-6.2", -tag_w/2 + 95, -10, font_size=33, color=(1.0, 1.0, 1.0, 1.0), align='left')
            draw_text(ctx, "Verified on Artificial Analysis Benchmark Suite • 2026", -tag_w/2 + 95, 26, font_size=21, color=(0.45, 0.95, 0.65, 0.95), weight=cairo.FONT_WEIGHT_NORMAL, align='left')

            ctx.restore()

        # ----------------- BOTTOM BENCHMARK STATS / FOOTER -----------------
        # Fades in smoothly at t = 3.3s
        b_prog = clamp((t - 3.3) / 0.6)
        if b_prog > 0:
            b_alpha = ease_out_cubic(b_prog)
            by = 1320

            ctx.save()
            # 2 Sub-metric cards
            card_w = 430
            card_h = 180

            # Metric Card 1: Speed Advantage
            round_rect(ctx, 90, by, card_w, card_h, 20)
            ctx.set_source_rgba(0.05, 0.07, 0.12, 0.88 * b_alpha)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.0, 0.8, 1.0, 0.35 * b_alpha)
            ctx.set_line_width(1.5)
            ctx.stroke()

            draw_lightning(ctx, 130, by + 40, 20, (0.0, 0.9, 1.0, b_alpha))
            draw_text(ctx, "THROUGHPUT", 155, by + 40, font_size=20, color=(0.0, 0.9, 1.0, b_alpha))
            draw_text(ctx, "185 tps", 130, by + 95, font_size=44, color=(1.0, 1.0, 1.0, b_alpha))
            draw_text(ctx, "2.4x Faster than GPT-4o", 130, by + 140, font_size=21, color=(0.6, 0.7, 0.85, 0.9 * b_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Metric Card 2: Cost Efficiency
            round_rect(ctx, 560, by, card_w, card_h, 20)
            ctx.set_source_rgba(0.05, 0.07, 0.12, 0.88 * b_alpha)
            ctx.fill_preserve()
            ctx.set_source_rgba(1.0, 0.85, 0.1, 0.35 * b_alpha)
            ctx.set_line_width(1.5)
            ctx.stroke()

            draw_star(ctx, 600, by + 40, 10, 4, (1.0, 0.85, 0.2, b_alpha))
            draw_text(ctx, "COST EFFICIENCY", 625, by + 40, font_size=20, color=(1.0, 0.85, 0.2, b_alpha))
            draw_text(ctx, "80% Less", 600, by + 95, font_size=44, color=(1.0, 0.92, 0.4, b_alpha))
            draw_text(ctx, "Compared to Frontier Titans", 600, by + 140, font_size=21, color=(0.8, 0.75, 0.6, 0.9 * b_alpha), weight=cairo.FONT_WEIGHT_NORMAL)

            # Footer label
            draw_text(ctx, "Source: artificialanalysis.ai • Independent AI Quality Index", WIDTH/2, 1620, font_size=24, color=(0.45, 0.52, 0.62, 0.85 * b_alpha), weight=cairo.FONT_WEIGHT_NORMAL, align='center')
            ctx.restore()

        renderer.write_frame()

    renderer.close()

if __name__ == "__main__":
    render()
