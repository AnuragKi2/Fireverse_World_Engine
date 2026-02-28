"""Fireverse_World_Engine starter orchestrator.

This script demonstrates the initial architecture for generating episode packages
for cinematic creature containment stories.

What this file does:
1. Loads structured world data from /data JSON files.
2. Validates core world rules (e.g., 3 main creatures, one silhouette per arc).
3. Builds a starter episode output dictionary with required fields:
   - Viral title
   - Thumbnail concept
   - 6-scene plan (10 seconds each)
   - Safe image prompts (contains the word "creature")
   - Video prompts
   - Narration lines
4. Prints a readable sample payload for extension into future pipelines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"


@dataclass
class EngineData:
    """Container for loaded world data files."""

    arcs: dict[str, Any]
    creature_tracker: dict[str, Any]
    enemy_silhouettes: dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file into a Python dictionary."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_engine_data() -> EngineData:
    """Load all required data files from /data."""
    return EngineData(
        arcs=load_json(DATA_DIR / "arcs.json"),
        creature_tracker=load_json(DATA_DIR / "creature_tracker.json"),
        enemy_silhouettes=load_json(DATA_DIR / "enemy_silhouettes.json"),
    )


def validate_world_rules(data: EngineData) -> None:
    """Validate core constraints defined by the Fireverse world rules.

    Raises:
        ValueError: If any rule is violated.
    """
    silhouettes_by_arc = {
        entry["arc_id"]: entry for entry in data.enemy_silhouettes.get("silhouettes", [])
    }

    for arc in data.arcs.get("arcs", []):
        arc_id = arc["arc_id"]

        # Rule: each arc should map to exactly one hidden enemy silhouette.
        if arc_id not in silhouettes_by_arc:
            raise ValueError(f"Arc '{arc_id}' has no silhouette definition.")

        # Rule: each arc should maintain about 15-20 creatures.
        pool_size = len(arc.get("creature_pool", []))
        if not 15 <= pool_size <= 20:
            raise ValueError(
                f"Arc '{arc_id}' creature_pool size must be 15-20; got {pool_size}."
            )

        # Rule: each episode contains exactly 3 main creatures.
        for episode in arc.get("episodes", []):
            mains = episode.get("main_creatures", [])
            if len(mains) != 3:
                raise ValueError(
                    f"Episode '{episode.get('episode_id')}' must have 3 main creatures."
                )


def build_episode_output(arc: dict[str, Any], episode: dict[str, Any]) -> dict[str, Any]:
    """Build a starter episode payload matching output requirements.

    Note:
        This is intentionally template-based placeholder logic for iteration.
    """
    main_creatures = episode["main_creatures"]

    scenes = []
    for i in range(1, 7):
        start_second = (i - 1) * 10
        end_second = i * 10
        scenes.append(
            {
                "scene_number": i,
                "time_window": f"00:{start_second:02d}-00:{end_second:02d}",
                "focus_creature": main_creatures[(i - 1) % 3],
                "objective": f"Escalate containment tension in scene {i}.",
            }
        )

    safe_image_prompts = [
        f"Cinematic shot of a {name} creature in a {arc['environment']} containment lab, dramatic lighting, no gore."
        for name in main_creatures
    ]

    video_prompts = [
        f"10-second sequence featuring the {name} creature navigating security corridors in the {arc['environment']} arc setting."
        for name in main_creatures
    ]

    narration_lines = [
        f"Scene {scene['scene_number']}: The {scene['focus_creature']} creature tests the limits of containment."
        for scene in scenes
    ]

    return {
        "arc_id": arc["arc_id"],
        "episode_id": episode["episode_id"],
        "viral_title": f"{episode['title_seed']} | 3 Creature Lockdown Goes Wrong",
        "thumbnail_concept": (
            "Split-frame: three featured creatures in alarm-lit chambers, with a faint"
            " hidden silhouette reflected in frosted glass."
        ),
        "scene_plan": scenes,
        "safe_image_prompts": safe_image_prompts,
        "video_prompts": video_prompts,
        "narration_lines": narration_lines,
    }


def main() -> None:
    """Run starter engine flow and print one sample episode output."""
    data = load_engine_data()
    validate_world_rules(data)

    first_arc = data.arcs["arcs"][0]
    first_episode = first_arc["episodes"][0]
    result = build_episode_output(first_arc, first_episode)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
