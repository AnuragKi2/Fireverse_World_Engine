"""Fireverse World Engine core episode generation.

Director Control Mode adds a light-weight configuration layer so creators can
shape tone and escalation without changing core scene flow.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


DIRECTOR_SETTINGS_PATH = Path("data/director_settings.json")
DEFAULT_DIRECTOR_SETTINGS: Dict[str, Any] = {
    "pacing_style": "cinematic",
    "hook_intensity": "medium",
    "mystery_level": "medium",
    "chaos_scaling": True,
    "warning_light_style": "default red cinematic",
    "silhouette_visibility": "medium",
}


def load_director_settings(path: Path = DIRECTOR_SETTINGS_PATH) -> Dict[str, Any]:
    """Load Director Control Mode settings with sane defaults.

    Creator note:
    - To tune show feel globally, edit /data/director_settings.json.
    - Keys here are merged with defaults, so creators can override only what they need.
    """

    settings = DEFAULT_DIRECTOR_SETTINGS.copy()

    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            settings.update(raw)

    return settings


def _pace_descriptor(pacing_style: str) -> str:
    return {
        "fast": "rapid cuts and short beats",
        "cinematic": "sweeping camera movement and dramatic pauses",
        "slow": "lingering details and deliberate progression",
    }.get(pacing_style, "balanced pacing")


def _mystery_descriptor(mystery_level: str) -> str:
    return {
        "low": "most motives are visible from the outset",
        "medium": "motives are partially obscured",
        "high": "clues are fragmented and the truth is withheld",
    }.get(mystery_level, "motives are partially obscured")


def _silhouette_hint(silhouette_visibility: str) -> str:
    return {
        "subtle": "a barely-there silhouette flickers at the edge of frame",
        "medium": "a distinct shadowed figure appears briefly in reflective surfaces",
        "strong": "the enemy silhouette dominates the scene transition before vanishing",
    }.get(silhouette_visibility, "a distinct shadowed figure appears briefly")


def generate_episode(title: str, scene_count: int = 3) -> Dict[str, Any]:
    """Generate a Fireverse episode package.

    Director layer integration:
    1) Reads Director settings.
    2) Adapts each scene to pacing/mystery/warning-light style.
    3) Applies hook intensity to Scene 1.
    4) Scales chaos across scenes when enabled.
    5) Tunes enemy hint strength using silhouette visibility.

    Creator note:
    - Change `scene_count` for longer or shorter episodes.
    - Change director presets in /data/director_settings.json to retone output.
    """

    director = load_director_settings()

    pace = _pace_descriptor(director["pacing_style"])
    mystery = _mystery_descriptor(director["mystery_level"])
    silhouette_hint = _silhouette_hint(director["silhouette_visibility"])

    scenes: List[Dict[str, Any]] = []
    for index in range(scene_count):
        scene_no = index + 1

        # Chaos scaling raises tension per scene when enabled.
        if director["chaos_scaling"]:
            tension = min(10, 4 + index * 2)
        else:
            tension = 5

        opening_hook = ""
        if scene_no == 1:
            # Hook intensity directly controls the force of Scene 1's inciting beat.
            opening_hook = {
                "medium": "An uneasy signal interrupts routine operations.",
                "hard": "A catastrophic anomaly tears open the calm in seconds.",
            }.get(director["hook_intensity"], "An uneasy signal interrupts routine operations.")

        narrative = (
            f"Scene {scene_no} uses {pace}. "
            f"The warning lights pulse in {director['warning_light_style']} style. "
            f"Narrative mystery: {mystery}. "
            f"Tension level: {tension}/10."
        )

        if scene_no == 1 and opening_hook:
            narrative = f"{opening_hook} {narrative}"

        # Enemy hint is always present but weighted by silhouette_visibility strength.
        enemy_hint = silhouette_hint

        scenes.append(
            {
                "scene_number": scene_no,
                "narrative": narrative,
                "enemy_hint": enemy_hint,
                "tension": tension,
            }
        )

    return {
        "title": title,
        "director_settings": director,
        "scenes": scenes,
    }
