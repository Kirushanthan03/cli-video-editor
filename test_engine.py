"""
test_engine.py
Verifies the new Antigravity Motion Engine (synthesizing manim, anidoodle, brag, and huashu).
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine.theme import THEMES
from engine.sfx import build_default_sfx_library
from engine.manifest import MotionScene
from engine.renderer import render_scene

print("1. Testing SFX Audio Synthesis...")
sfx_paths = build_default_sfx_library("/tmp/video_assets/sfx")
for name, p in sfx_paths.items():
    print(f"   Generated {name}: {p} ({os.path.getsize(p)} bytes)")

print("\n2. Testing Declarative Motion Scene Rendering...")
test_manifest = {
    "scene_id": "gemini_pareto_demo",
    "duration": 4.0,
    "theme": "cyber_neon",
    "has_background": True,
    "elements": [
        # Animated Keynote Card
        {
            "type": "card",
            "start": 0.2,
            "duration": 0.8,
            "props": {
                "x": 90, "y": 280, "w": 900, "h": 220,
                "title": "GEMINI 4 NEON",
                "subtitle": "Pareto Frontier Benchmark Leader"
            }
        },
        # 3b1b Manim-style Pareto Curve
        {
            "type": "pareto_curve",
            "start": 0.8,
            "duration": 1.5,
            "props": {
                "origin_x": 140, "origin_y": 1150, "w": 800, "h": 500,
                "points": [
                    (0.12, 0.25, "Claude 3.5"),
                    (0.45, 0.58, "GPT-4o"),
                    (0.72, 0.78, "Claude Opus"),
                    (0.92, 0.94, "Neon #3")
                ],
                "highlight_idx": 3
            }
        },
        # alexgreensh Anidoodle-style Hand-Drawn Oval Circling the Winner
        {
            "type": "doodle_oval",
            "start": 2.2,
            "duration": 0.8,
            "props": {
                "cx": 876, "cy": 680, "rx": 90, "ry": 60, "width": 6.0
            }
        },
        # alexgreensh Anidoodle-style Kinetic Arrow
        {
            "type": "doodle_arrow",
            "start": 2.5,
            "duration": 0.6,
            "props": {
                "x1": 700, "y1": 560, "x2": 820, "y2": 640, "curvature": -30.0
            }
        },
        # Dynamic Circular Gauge
        {
            "type": "gauge",
            "start": 1.2,
            "duration": 1.2,
            "props": {
                "cx": 540, "cy": 1420, "radius": 120, "value": 89.4, "max": 100.0,
                "label": "OVERALL SCORE"
            }
        }
    ]
}

scene = MotionScene.from_dict(test_manifest)
output_file = "/tmp/video_assets/test_advanced_motion.mp4"
print(f"   Rendering test scene to {output_file}...")
render_scene(scene, output_file, width=1080, height=1920, fps=30)
print(f"   Render Complete! File size: {os.path.getsize(output_file)} bytes")
