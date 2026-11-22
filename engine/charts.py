"""
engine/charts.py
Mathematical and precision vector chart visualizations inspired by 3b1b/manim.
Supports animated Pareto frontiers, dynamic ranking bars with counting numbers,
coordinate grids, and circular metrics with spring easing.
"""

import math
import cairo

def draw_coordinate_grid(
    ctx: cairo.Context,
    x: float,
    y: float,
    w: float,
    h: float,
    x_steps: int = 5,
    y_steps: int = 4,
    color: tuple = (1.0, 1.0, 1.0, 0.08)
):
    """Draws a subtle mathematical coordinate grid background."""
    ctx.save()
    ctx.set_source_rgba(*color)
    ctx.set_line_width(1.0)
    
    # Vertical grid lines
    for i in range(x_steps + 1):
        gx = x + (w / x_steps) * i
        ctx.move_to(gx, y)
        ctx.line_to(gx, y + h)
        ctx.stroke()
        
    # Horizontal grid lines
    for j in range(y_steps + 1):
        gy = y + (h / y_steps) * j
        ctx.move_to(x, gy)
        ctx.line_to(x + w, gy)
        ctx.stroke()
        
    ctx.restore()

def draw_animated_pareto_curve(
    ctx: cairo.Context,
    origin_x: float,
    origin_y: float,
    width: float,
    height: float,
    points: list,
    progress: float,
    curve_color: tuple = (0.0, 0.85, 1.0, 0.95),
    highlight_idx: int = -1,
    time_val: float = 0.0
):
    """
    Plots a mathematical curve (e.g., Latency vs Intelligence Pareto frontier)
    drawn dynamically with Bezier smoothing and pulsing data points.
    points: List of (norm_x, norm_y, label) where norm_x, norm_y in [0.0, 1.0]
    """
    if progress <= 0.01 or not points:
        return
        
    ctx.save()
    
    # 1. Draw Axes
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
    ctx.set_line_width(2.0)
    # X axis
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x + width * min(1.0, progress * 1.5), origin_y)
    ctx.stroke()
    # Y axis
    ctx.move_to(origin_x, origin_y)
    ctx.line_to(origin_x, origin_y - height * min(1.0, progress * 1.5))
    ctx.stroke()
    
    # Map points to pixel coordinates
    # Note: y goes upward (inverted)
    coords = []
    for nx, ny, lbl in points:
        px = origin_x + nx * width
        py = origin_y - ny * height
        coords.append((px, py, lbl))
        
    # 2. Draw Smooth Spline up to progress
    sorted_pts = sorted(coords, key=lambda p: p[0])
    total_len = len(sorted_pts)
    drawn_count = max(1, int(total_len * progress))
    
    ctx.set_source_rgba(*curve_color)
    ctx.set_line_width(4.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    
    ctx.move_to(sorted_pts[0][0], sorted_pts[0][1])
    for i in range(1, drawn_count):
        p0 = sorted_pts[i - 1]
        p1 = sorted_pts[i]
        # Midpoint cubic curve
        mx = (p0[0] + p1[0]) / 2.0
        ctx.curve_to(mx, p0[1], mx, p1[1], p1[0], p1[1])
    ctx.stroke()
    
    # 3. Draw Points & Pulses
    for idx, (px, py, lbl) in enumerate(sorted_pts[:drawn_count]):
        is_highlight = (idx == highlight_idx)
        
        # Point dot
        ctx.save()
        if is_highlight:
            # Pulsing aura
            pulse = 1.0 + 0.25 * math.sin(time_val * 6.0)
            ctx.arc(px, py, 14.0 * pulse, 0, 2 * math.pi)
            ctx.set_source_rgba(1.0, 0.85, 0.0, 0.35)
            ctx.fill()
            
            ctx.arc(px, py, 8.0, 0, 2 * math.pi)
            ctx.set_source_rgba(1.0, 0.9, 0.1, 1.0)
            ctx.fill()
        else:
            ctx.arc(px, py, 6.0, 0, 2 * math.pi)
            ctx.set_source_rgba(0.0, 0.85, 1.0, 0.9)
            ctx.fill()
            
        # Label
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24 if not is_highlight else 28)
        if is_highlight:
            ctx.set_source_rgba(1.0, 0.9, 0.1, 1.0)
        else:
            ctx.set_source_rgba(0.8, 0.85, 0.9, 0.9)
            
        ctx.move_to(px - 30, py - 18)
        ctx.show_text(lbl)
        ctx.restore()
        
    ctx.restore()

def draw_circular_gauge(
    ctx: cairo.Context,
    cx: float,
    cy: float,
    radius: float,
    value: float,
    max_value: float,
    progress: float,
    label: str = "",
    unit: str = "%",
    accent_color: tuple = (0.0, 0.9, 1.0, 1.0)
):
    """
    Renders an animated circular radial speedometer gauge.
    """
    ctx.save()
    start_angle = math.pi * 0.75
    total_angle = math.pi * 1.5
    
    # Background Track
    ctx.set_line_width(14.0)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.arc(cx, cy, radius, start_angle, start_angle + total_angle)
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
    ctx.stroke()
    
    # Active Arc
    norm_val = min(1.0, value / max_value) if max_value > 0 else 0
    active_angle = start_angle + total_angle * norm_val * progress
    
    if progress > 0.01:
        ctx.arc(cx, cy, radius, start_angle, active_angle)
        ctx.set_source_rgba(*accent_color)
        ctx.stroke()
        
    # Readout text
    curr_val = norm_val * max_value * progress
    val_str = f"{curr_val:.1f}" if max_value <= 100 else f"{int(curr_val)}"
    
    ctx.select_font_face("Arial Black", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(radius * 0.52)
    ctx.set_source_rgba(1, 1, 1, 1)
    
    ext = ctx.text_extents(val_str)
    ctx.move_to(cx - (ext.x_bearing + ext.width / 2.0), cy + 10)
    ctx.show_text(val_str)
    
    # Sub label
    if label:
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(radius * 0.22)
        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.9)
        l_ext = ctx.text_extents(label)
        ctx.move_to(cx - (l_ext.x_bearing + l_ext.width / 2.0), cy + radius * 0.55)
        ctx.show_text(label)
        
    ctx.restore()
