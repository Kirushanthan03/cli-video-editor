"""
engine/manifest.py
Declarative motion scene definition schema and validator.
Inspired by alchaincyf/huashu-art-motion's declarative scene grammars.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ElementSpec:
    element_type: str                  # 'card', 'doodle_oval', 'doodle_arrow', 'pareto_curve', 'gauge', 'badge'
    start_time: float
    duration: float
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MotionScene:
    scene_id: str
    duration: float
    theme_name: str = "cyber_neon"
    has_background: bool = True       # If False, renders as transparent alpha overlay!
    elements: List[ElementSpec] = field(default_factory=list)
    sfx_cues: List[Dict[str, Any]] = field(default_factory=list)  # [{'time': 0.5, 'sound': 'whoosh'}]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotionScene":
        elements = [
            ElementSpec(
                element_type=el.get("type", "card"),
                start_time=float(el.get("start", 0.0)),
                duration=float(el.get("duration", 1.0)),
                properties=el.get("props", {})
            )
            for el in data.get("elements", [])
        ]
        return cls(
            scene_id=data.get("scene_id", "scene_default"),
            duration=float(data.get("duration", 5.0)),
            theme_name=data.get("theme", "cyber_neon"),
            has_background=bool(data.get("has_background", True)),
            elements=elements,
            sfx_cues=data.get("sfx_cues", [])
        )
