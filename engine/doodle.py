"""
engine/doodle.py
Procedural hand-drawn vector doodle generator inspired by alexgreensh/anidoodle.
Creates organic, sketch-to-life vector animations (circling ovals, kinetic arrows,
highlighter underlines, and hand-drawn callout badges) using procedural Bezier jitter.
"""

import math
import cairo

def _noise(seed: int, i: float) -> float:
    """Deterministic pseudo-random organic wobble."""
    x = math.sin(seed * 12.9898 + i * 78.233) * 43758.5453
    return (x - math.floor(x)) * 2.0 - 1.0

def draw_hand_drawn_oval(
    ctx: cairo.Context,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    progress: float,
    seed: int = 42,
    color: tuple = (1.0, 0.9, 0.1, 0.95),
    line_width: float = 6.0,
    wobble: float = 6.0
):
    """
    Draws a dynamic hand-drawn animated ellipse circling a focal point.
    Progress 0.0 -> 1.0 completes up to ~1.15 loops (with overlapping tail).
    """
    if progress <= 0.01:
        return
        
    ctx.save()
    ctx.set_source_rgba(*color)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    
    # Animate from -pi/2 up to -pi/2 + 2.3*pi
    total_angle = 2.0 * math.pi * 1.15
    current_angle = progress * total_angle
    
    steps = int(max(10, current_angle / (math.pi / 24)))
    dt = current_angle / steps
    
    points = []
    for s in range(steps + 1):
        theta = -math.pi / 2.0 + s * dt
        # Organic jitter based on angle
        r_jitter_x = rx + _noise(seed, s * 0.4) * wobble
        r_jitter_y = ry + _noise(seed + 10, s * 0.4) * wobble
        
        # Spiral expansion slightly on the overlapping tail
        if theta > math.pi * 1.5:
            overlap = (theta - math.pi * 1.5) / (math.pi * 0.5)
            r_jitter_x += overlap * 8.0
            r_jitter_y += overlap * 6.0
            
        px = cx + math.cos(theta) * r_jitter_x
        py = cy + math.sin(theta) * r_jitter_y
        points.append((px, py))
        
    if len(points) >= 2:
        ctx.move_to(points[0][0], points[0][1])
        for i in range(1, len(points)):
            ctx.line_to(points[i][0], points[i][1])
        ctx.stroke()
        
    ctx.restore()

def draw_hand_drawn_arrow(
    ctx: cairo.Context,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    progress: float,
    seed: int = 101,
    color: tuple = (1.0, 0.85, 0.0, 0.95),
    line_width: float = 6.0,
    curvature: float = 40.0
):
    """
    Draws a kinetic hand-drawn arrow that arcs from (x1, y1) towards (x2, y2).
    Progress 0.0 -> 0.8 draws the shaft; 0.8 -> 1.0 pops the arrow head wings.
    """
    if progress <= 0.01:
        return
        
    ctx.save()
    ctx.set_source_rgba(*color)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    
    # Quadratic bezier control point for curvature
    mid_x = (x1 + x2) / 2.0
    mid_y = (y1 + y2) / 2.0
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 1.0:
        ctx.restore()
        return
        
    # Perpendicular vector
    nx = -dy / dist
    ny = dx / dist
    ctrl_x = mid_x + nx * curvature + _noise(seed, 1.0) * 8.0
    ctrl_y = mid_y + ny * curvature + _noise(seed, 2.0) * 8.0
    
    # Shaft progress: 0.0 -> 0.85
    shaft_prog = min(1.0, progress / 0.85)
    steps = int(max(8, shaft_prog * 25))
    
    shaft_pts = []
    for s in range(steps + 1):
        t = (s / steps) * shaft_prog if steps > 0 else 0
        omt = 1.0 - t
        # Quadratic formula: (1-t)^2 * P0 + 2*(1-t)*t*P1 + t^2*P2
        px = omt * omt * x1 + 2 * omt * t * ctrl_x + t * t * x2
        py = omt * omt * y1 + 2 * omt * t * ctrl_y + t * t * y2
        
        # Add subtle hand-jitter
        px += _noise(seed + s, 3.5) * 2.5
        py += _noise(seed + s, 4.5) * 2.5
        shaft_pts.append((px, py))
        
    if len(shaft_pts) >= 2:
        ctx.move_to(shaft_pts[0][0], shaft_pts[0][1])
        for p in shaft_pts[1:]:
            ctx.line_to(p[0], p[1])
        ctx.stroke()
        
    # Arrow head wings: 0.75 -> 1.0
    if progress >= 0.75 and len(shaft_pts) >= 2:
        head_prog = (progress - 0.75) / 0.25
        tip_x, tip_y = shaft_pts[-1]
        
        # Direction at tip
        prev_x, prev_y = shaft_pts[-2]
        vx = tip_x - prev_x
        vy = tip_y - prev_y
        vlen = math.hypot(vx, vy) or 1.0
        ux = vx / vlen
        uy = vy / vlen
        
        angle = math.atan2(uy, ux)
        head_len = 34.0 * head_prog
        
        # Wing 1
        a1 = angle + math.pi - 0.55
        w1_x = tip_x + math.cos(a1) * head_len
        w1_y = tip_y + math.sin(a1) * head_len
        ctx.move_to(tip_x, tip_y)
        ctx.line_to(w1_x, w1_y)
        ctx.stroke()
        
        # Wing 2
        a2 = angle + math.pi + 0.55
        w2_x = tip_x + math.cos(a2) * head_len
        w2_y = tip_y + math.sin(a2) * head_len
        ctx.move_to(tip_x, tip_y)
        ctx.line_to(w2_x, w2_y)
        ctx.stroke()
        
    ctx.restore()

def draw_hand_drawn_underline(
    ctx: cairo.Context,
    x1: float,
    y: float,
    x2: float,
    progress: float,
    seed: int = 55,
    color: tuple = (1.0, 0.85, 0.0, 0.9),
    line_width: float = 7.0
):
    """
    Draws a double-pass kinetic highlighter / marker underline.
    """
    if progress <= 0.01:
        return
        
    ctx.save()
    ctx.set_source_rgba(*color)
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    
    cur_x = x1 + (x2 - x1) * progress
    steps = max(6, int(20 * progress))
    
    # Pass 1: Primary stroke
    ctx.move_to(x1, y)
    for s in range(1, steps + 1):
        px = x1 + (cur_x - x1) * (s / steps)
        py = y + math.sin(s * 0.8) * 3.0 + _noise(seed, s) * 2.0
        ctx.line_to(px, py)
    ctx.stroke()
    
    # Pass 2: Energetic secondary stroke if progress > 0.5
    if progress > 0.5:
        p2_prog = (progress - 0.5) * 2.0
        p2_cur_x = x1 + (x2 - x1) * 0.85 * p2_prog
        ctx.set_line_width(line_width * 0.6)
        ctx.set_source_rgba(color[0], color[1], color[2], color[3] * 0.7)
        ctx.move_to(x1 + 10, y + 6)
        for s in range(1, steps + 1):
            px = x1 + 10 + (p2_cur_x - x1) * (s / steps)
            py = y + 6 + math.cos(s * 0.9) * 2.5
            ctx.line_to(px, py)
        ctx.stroke()
        
    ctx.restore()
