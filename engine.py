"""Core world-intelligence utilities for Fireverse World Engine.

This module only builds the reusable data and memory logic.
It does not generate full episodes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

# Paths for persistent world-memory files.
ARCS_PATH = Path("arcs.json")
CREATURE_TRACKER_PATH = Path("creature_tracker.json")
ENEMY_SILHOUETTES_PATH = Path("enemy_silhouettes.json")


def _load_json(path: Path, default: Any) -> Any:
    """Load JSON from disk and return a default value when missing or invalid."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data: Any) -> None:
    """Save JSON to disk with readable formatting for long-term memory files."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_arc_data() -> List[Dict[str, Any]]:
    """Load arc definitions used to guide episode intelligence.

    Expected schema for each arc in arcs.json:
      - arc_name
      - environment_type
      - tone
      - enemy_silhouette
      - episode_count
    """
    return _load_json(ARCS_PATH, default=[])


def get_episode_creatures(
    available_creatures: List[str],
    episode_number: int,
    recent_main_window: int = 3,
) -> Dict[str, Any]:
    """Select main and background creatures while reducing repeated main usage.

    The function reads creature_tracker.json and avoids assigning the same creature
    as a main focus too frequently by using a configurable recency window.
    """
    tracker = _load_json(
        CREATURE_TRACKER_PATH,
        default={
            "creatures_used": {},
            "main_episode_assignments": {},
            "background_appearances": {},
        },
    )

    main_assignments = tracker.setdefault("main_episode_assignments", {})
    background_appearances = tracker.setdefault("background_appearances", {})

    # Exclude creatures that have been main characters in the most recent window.
    recent_threshold = max(1, episode_number - recent_main_window + 1)
    eligible_main = [
        creature
        for creature in available_creatures
        if not any(ep >= recent_threshold for ep in main_assignments.get(creature, []))
    ]

    # Fallback when all creatures were used recently.
    if not eligible_main:
        eligible_main = list(available_creatures)

    # Prefer least-used creature for main assignment to balance exposure.
    eligible_main.sort(key=lambda c: len(main_assignments.get(c, [])))
    main_creature = eligible_main[0] if eligible_main else None

    # Background creatures are all others for this lightweight planning stage.
    background_creatures = [c for c in available_creatures if c != main_creature]

    # Update tracker state for selected creatures.
    if main_creature:
        main_assignments.setdefault(main_creature, []).append(episode_number)
    for creature in background_creatures:
        background_appearances.setdefault(creature, []).append(episode_number)

    creatures_used = tracker.setdefault("creatures_used", {})
    for creature in available_creatures:
        creatures_used[creature] = creatures_used.get(creature, 0) + 1

    _save_json(CREATURE_TRACKER_PATH, tracker)

    return {
        "main_creature": main_creature,
        "background_creatures": background_creatures,
        "tracker": tracker,
    }


def generate_scene_structure(arc: Dict[str, Any], episode_number: int) -> Dict[str, Any]:
    """Build a reusable scene skeleton from arc metadata and episode position.

    This structure is intentionally abstract: it provides planning slots for
    opening, conflict escalation, and resolution hooks without creating full prose.
    """
    arc_name = arc.get("arc_name", "Unknown Arc")
    tone = arc.get("tone", "neutral")
    environment = arc.get("environment_type", "unspecified")

    return {
        "arc_name": arc_name,
        "episode_number": episode_number,
        "environment_type": environment,
        "tone": tone,
        "scenes": [
            {
                "name": "opening",
                "goal": f"Establish {environment} atmosphere with {tone} tone.",
            },
            {
                "name": "escalation",
                "goal": "Increase pressure with creature activity and silhouette hints.",
            },
            {
                "name": "turning_point",
                "goal": "Reveal strategic clue that changes character expectations.",
            },
            {
                "name": "cooldown",
                "goal": "End with unresolved tension to carry forward arc momentum.",
            },
        ],
    }


def generate_prompts(
    arc: Dict[str, Any],
    episode_number: int,
    creature_plan: Dict[str, Any],
    scene_structure: Dict[str, Any],
) -> Dict[str, str]:
    """Create compact prompt blocks for downstream generation systems.

    The prompts capture arc identity, creature roles, and scene expectations,
    but stop short of generating a complete episode script.
    """
    arc_name = arc.get("arc_name", "Unknown Arc")
    silhouette = arc.get("enemy_silhouette", "Unknown silhouette")

    system_prompt = (
        f"Arc: {arc_name}\n"
        f"Episode: {episode_number}\n"
        f"Tone: {arc.get('tone', 'neutral')}\n"
        f"Environment: {arc.get('environment_type', 'unspecified')}\n"
        f"Enemy silhouette: {silhouette}"
    )

    user_prompt = (
        f"Main creature: {creature_plan.get('main_creature')}\n"
        f"Background creatures: {', '.join(creature_plan.get('background_creatures', [])) or 'None'}\n"
        f"Scene plan: {json.dumps(scene_structure.get('scenes', []), ensure_ascii=False)}"
    )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }


def update_world_memory(
    arc_name: str,
    silhouette_name: str,
    episode_number: int,
) -> Dict[str, Any]:
    """Update enemy silhouette memory for continuity and progressive hinting.

    enemy_silhouettes.json stores per-arc visibility and hint statistics so later
    planning can reference how often an enemy shape has been teased.
    """
    memory = _load_json(ENEMY_SILHOUETTES_PATH, default=[])

    entry = next(
        (
            item
            for item in memory
            if item.get("arc_name") == arc_name
            and item.get("silhouette_name") == silhouette_name
        ),
        None,
    )

    if entry is None:
        entry = {
            "arc_name": arc_name,
            "silhouette_name": silhouette_name,
            "hint_count": 0,
            "last_episode_seen": None,
        }
        memory.append(entry)

    entry["hint_count"] = int(entry.get("hint_count", 0)) + 1
    entry["last_episode_seen"] = episode_number

    _save_json(ENEMY_SILHOUETTES_PATH, memory)
    return entry
