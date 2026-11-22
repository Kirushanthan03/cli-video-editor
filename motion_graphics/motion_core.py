"""
motion_core.py
High-performance motion graphics and kinetic animation core using PyCairo and FFmpeg pipe.
"""

import math
import numpy as np
import cairo
import subprocess
import os

# ----------------- EASING FUNCTIONS -----------------

def clamp(val, low=0.0, high=1.0):
    return max(low, min(high, val))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out_cubic(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - math.pow(1.0 - t, 3)

def ease_out_expo(t):
    t = clamp(t)
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2.0, -10.0 * t)

def ease_out_back(t, s=1.70158):
    """Overshoot spring pop-in"""
    t = clamp(t)
    t = t - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0

def spring_pop(t, damping=6.0, freq=12.0):
    """Physics spring oscillation settling to 1.0"""
    if t <= 0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return 1.0 - math.exp(-damping * t) * math.cos(freq * t)

# ----------------- SHAPE & DRAWING HELPERS -----------------

def round_rect(ctx, x, y, w, h, r):
    r = min(r, w / 2.0, h / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def draw_glow_rect(ctx, x, y, w, h, r, rgb, intensity=1.0, max_spread=28, steps=6):
    """Draws layered smooth neon glow around a rounded rectangle"""
    for i in range(steps, 0, -1):
        spread = (i / steps) * max_spread
        # Alpha falls off quadratically with distance
        alpha = (0.22 / (i * 0.75 + 0.25)) * intensity
        alpha = min(0.9, alpha)
        ctx.save()
        round_rect(ctx, x - spread, y - spread, w + 2 * spread, h + 2 * spread, r + spread)
        ctx.set_source_rgba(rgb[0], rgb[1], rgb[2], alpha)
        ctx.set_line_width(spread * 1.2 + 1.5)
        ctx.stroke()
        ctx.restore()

def draw_pill(ctx, x, y, w, h, fill_rgba, border_rgba=None, border_width=1.5):
    r = h / 2.0
    round_rect(ctx, x, y, w, h, r)
    ctx.set_source_rgba(*fill_rgba)
    if border_rgba:
        ctx.fill_preserve()
        ctx.set_source_rgba(*border_rgba)
        ctx.set_line_width(border_width)
        ctx.stroke()
    else:
        ctx.fill()

def draw_text(ctx, text, x, y, font_face='Arial', font_size=32, color=(1,1,1,1), weight=cairo.FONT_WEIGHT_BOLD, align='left', baseline='middle'):
    ctx.save()
    ctx.select_font_face(font_face, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(font_size)
    ext = ctx.text_extents(text)
    
    # Calculate horizontal alignment
    if align == 'center':
        tx = x - (ext.x_bearing + ext.width / 2.0)
    elif align == 'right':
        tx = x - (ext.x_bearing + ext.width)
    else: # left
        tx = x - ext.x_bearing
        
    # Calculate vertical baseline
    if baseline == 'middle':
        ty = y - (ext.y_bearing + ext.height / 2.0)
    elif baseline == 'top':
        ty = y - ext.y_bearing
    elif baseline == 'bottom':
        ty = y - (ext.y_bearing + ext.height)
    else: # baseline
        ty = y
        
    ctx.move_to(tx, ty)
    ctx.set_source_rgba(*color)
    ctx.show_text(text)
    ctx.restore()
    return ext.width, ext.height

def draw_lightning(ctx, cx, cy, size, color_rgba):
    """Draw crisp vector lightning bolt icon"""
    ctx.save()
    ctx.translate(cx, cy)
    s = size / 24.0
    ctx.scale(s, s)
    ctx.new_path()
    ctx.move_to(2, -12)
    ctx.line_to(-6, 0)
    ctx.line_to(0, 0)
    ctx.line_to(-3, 12)
    ctx.line_to(7, -2)
    ctx.line_to(1, -2)
    ctx.close_path()
    ctx.set_source_rgba(*color_rgba)
    ctx.fill()
    ctx.restore()

def draw_star(ctx, cx, cy, r_outer, r_inner, color_rgba):
    """Draw crisp 4-point tech sparkle star"""
    ctx.save()
    ctx.new_path()
    for i in range(8):
        angle = i * math.pi / 4.0 - math.pi / 2.0
        r = r_outer if i % 2 == 0 else r_inner
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        if i == 0:
            ctx.move_to(px, py)
        else:
            ctx.line_to(px, py)
    ctx.close_path()
    ctx.set_source_rgba(*color_rgba)
    ctx.fill()
    ctx.restore()

def draw_check_badge(ctx, cx, cy, radius, fill_rgba, check_rgba=(1,1,1,1)):
    """Draw circle with checkmark"""
    ctx.save()
    ctx.arc(cx, cy, radius, 0, 2 * math.pi)
    ctx.set_source_rgba(*fill_rgba)
    ctx.fill()
    
    # Checkmark path
    ctx.new_path()
    ctx.move_to(cx - radius * 0.45, cy)
    ctx.line_to(cx - radius * 0.1, cy + radius * 0.35)
    ctx.line_to(cx + radius * 0.45, cy - radius * 0.35)
    ctx.set_source_rgba(*check_rgba)
    ctx.set_line_width(radius * 0.22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ctx.restore()

# ----------------- PARTICLE SYSTEM -----------------

class ParticleSystem:
    def __init__(self, count=45, width=1080, height=1920, seed=42):
        self.width = width
        self.height = height
        np.random.seed(seed)
        self.x = np.random.uniform(0, width, count)
        self.y = np.random.uniform(0, height, count)
        self.radius = np.random.uniform(2.5, 6.5, count)
        self.speed_y = np.random.uniform(25.0, 70.0, count) # pixels/sec upward
        self.drift_amp = np.random.uniform(15.0, 45.0, count)
        self.drift_freq = np.random.uniform(0.5, 1.8, count)
        self.phase = np.random.uniform(0, 2 * math.pi, count)
        
        # Color palette: cyan, electric blue, soft gold, purple
        palettes = [
            (0.0, 0.9, 1.0),   # cyan
            (0.2, 0.5, 1.0),   # electric blue
            (1.0, 0.85, 0.3),  # gold
            (0.7, 0.4, 1.0),   # purple
        ]
        chosen_p = np.random.choice(len(palettes), count)
        self.colors = [palettes[idx] for idx in chosen_p]
        self.base_alpha = np.random.uniform(0.25, 0.7, count)

    def draw(self, ctx, t):
        ctx.save()
        for i in range(len(self.x)):
            # Upward motion with wrapping
            curr_y = (self.y[i] - self.speed_y[i] * t) % self.height
            curr_x = self.x[i] + self.drift_amp[i] * math.sin(self.drift_freq[i] * t + self.phase[i])
            curr_x = curr_x % self.width
            
            # Breathing pulse
            alpha = self.base_alpha[i] * (0.65 + 0.35 * math.sin(t * 2.5 + self.phase[i]))
            rgb = self.colors[i]
            r = self.radius[i]
            
            # Outer glow
            pat = cairo.RadialGradient(curr_x, curr_y, 0.5, curr_x, curr_y, r * 3.5)
            pat.add_color_stop_rgba(0.0, rgb[0], rgb[1], rgb[2], alpha * 0.9)
            pat.add_color_stop_rgba(0.5, rgb[0], rgb[1], rgb[2], alpha * 0.3)
            pat.add_color_stop_rgba(1.0, rgb[0], rgb[1], rgb[2], 0.0)
            ctx.set_source(pat)
            ctx.arc(curr_x, curr_y, r * 3.5, 0, 2 * math.pi)
            ctx.fill()
            
            # Bright core
            ctx.arc(curr_x, curr_y, r, 0, 2 * math.pi)
            ctx.set_source_rgba(1.0, 1.0, 1.0, alpha * 0.95)
            ctx.fill()
        ctx.restore()

# ----------------- BACKGROUND MESH / GRADIENT -----------------

def draw_luxury_dark_bg(ctx, width=1080, height=1920, t=0.0, primary_aura=(0.0, 0.3, 0.8), secondary_aura=(0.5, 0.1, 0.7)):
    """Renders a cinematic dark keynote background with subtle moving light pools"""
    # Base dark gradient
    pat = cairo.LinearGradient(0, 0, 0, height)
    pat.add_color_stop_rgb(0.0, 0.04, 0.05, 0.08)
    pat.add_color_stop_rgb(0.5, 0.03, 0.04, 0.06)
    pat.add_color_stop_rgb(1.0, 0.02, 0.02, 0.04)
    ctx.set_source(pat)
    ctx.paint()
    
    # Primary top-left ambient light pool
    cx1 = 300 + 100 * math.sin(t * 0.8)
    cy1 = 400 + 80 * math.cos(t * 0.6)
    r1 = 750
    rad1 = cairo.RadialGradient(cx1, cy1, 10, cx1, cy1, r1)
    rad1.add_color_stop_rgba(0.0, primary_aura[0], primary_aura[1], primary_aura[2], 0.18)
    rad1.add_color_stop_rgba(0.5, primary_aura[0], primary_aura[1], primary_aura[2], 0.07)
    rad1.add_color_stop_rgba(1.0, primary_aura[0], primary_aura[1], primary_aura[2], 0.0)
    ctx.set_source(rad1)
    ctx.paint()

    # Secondary bottom-right ambient light pool
    cx2 = 800 + 120 * math.cos(t * 0.7)
    cy2 = 1450 + 90 * math.sin(t * 0.5)
    r2 = 850
    rad2 = cairo.RadialGradient(cx2, cy2, 10, cx2, cy2, r2)
    rad2.add_color_stop_rgba(0.0, secondary_aura[0], secondary_aura[1], secondary_aura[2], 0.15)
    rad2.add_color_stop_rgba(0.5, secondary_aura[0], secondary_aura[1], secondary_aura[2], 0.05)
    rad2.add_color_stop_rgba(1.0, secondary_aura[0], secondary_aura[1], secondary_aura[2], 0.0)
    ctx.set_source(rad2)
    ctx.paint()

# ----------------- FFmpeg VIDEO WRITER -----------------

class VideoRenderer:
    def __init__(self, output_path, width=1080, height=1920, fps=30, crf=18):
        self.output_path = output_path
        self.width = width
        self.height = height
        self.fps = fps
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # FFmpeg command for pristine x264 MP4 vertical video
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{width}x{height}',
            '-pix_fmt', 'bgra',
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            '-crf', str(crf),
            '-movflags', '+faststart',
            output_path
        ]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

    def write_frame(self):
        self.surface.flush()
        self.proc.stdin.write(self.surface.get_data())

    def close(self):
        self.proc.stdin.close()
        stderr = self.proc.stderr.read().decode('utf-8')
        self.proc.wait()
        if self.proc.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {stderr}")
        print(f"Render completed successfully: {self.output_path}")
