"""Episode generation utilities for Fireverse World Engine.

This module extends the engine with an auto-arc evolution system. The progression
model is deterministic and derived from episode position in an arc, which means the
same input state always produces the same progression outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

STAGE_ORDER = ("intro", "buildup", "escalation", "instability", "finale")


@dataclass(slots=True)
class ArcMemory:
    """Persisted memory for a story arc.

    Attributes:
        arc_id: Unique arc identifier.
        total_episodes: Planned number of episodes in the arc.
        completed_episodes: Number of episodes already generated/finished.
        current_progress_stage: Current stage label computed from position.
        escalation_level: Rolling intensity indicator (0.0 to 1.0).
    """

    arc_id: str
    total_episodes: int
    completed_episodes: int = 0
    current_progress_stage: str = "intro"
    escalation_level: float = 0.0


@dataclass(slots=True)
class ArcProgression:
    """Computed progression values used to influence episode generation."""

    stage: str
    position_ratio: float
    scene_intensity: float
    narration_tension: float
    disturbance_frequency: float
    cliffhanger_strength: float
    silhouette_presence: float
    escalation_level: float


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _detect_progress_stage(episode_number: int, total_episodes: int) -> tuple[str, float]:
    """Detect arc stage from episode position.

    Progression model (ratio through arc):
      - intro:       [0.00, 0.20)
      - buildup:     [0.20, 0.40)
      - escalation:  [0.40, 0.65)
      - instability: [0.65, 0.90)
      - finale:      [0.90, 1.00]
    """

    safe_total = max(total_episodes, 1)
    clamped_episode = max(1, min(episode_number, safe_total))
    position_ratio = (clamped_episode - 1) / (safe_total - 1) if safe_total > 1 else 1.0

    if position_ratio < 0.20:
        return "intro", position_ratio
    if position_ratio < 0.40:
        return "buildup", position_ratio
    if position_ratio < 0.65:
        return "escalation", position_ratio
    if position_ratio < 0.90:
        return "instability", position_ratio
    return "finale", position_ratio


def _stage_modifier(stage: str) -> float:
    """Return a monotonic stage intensity modifier."""

    modifiers = {
        "intro": 0.10,
        "buildup": 0.30,
        "escalation": 0.55,
        "instability": 0.75,
        "finale": 0.95,
    }
    return modifiers.get(stage, 0.10)


def compute_arc_progression(
    *,
    episode_number: int,
    total_episodes: int,
    director_settings: dict[str, Any] | None,
    prior_escalation: float = 0.0,
) -> ArcProgression:
    """Compute progression outputs that shape generated episode tone.

    The algorithm combines three signals:
      1. Position ratio in arc (structural progression)
      2. Stage modifier (narrative milestone weight)
      3. Prior escalation level (memory continuity)

    Silhouette presence uses `silhouette_visibility` from director settings as base,
    then increases as episodes advance and stages intensify.
    """

    settings = director_settings or {}
    stage, ratio = _detect_progress_stage(episode_number, total_episodes)
    stage_mod = _stage_modifier(stage)

    # Blend prior escalation to preserve continuity while allowing growth.
    escalation_level = _clamp((prior_escalation * 0.4) + (ratio * 0.35) + (stage_mod * 0.25))

    scene_intensity = _clamp(0.25 + (stage_mod * 0.45) + (ratio * 0.30))
    narration_tension = _clamp(0.20 + (stage_mod * 0.40) + (escalation_level * 0.25))
    disturbance_frequency = _clamp(0.15 + (ratio * 0.35) + (stage_mod * 0.30))
    cliffhanger_strength = _clamp(0.10 + (ratio * 0.45) + (stage_mod * 0.35))

    # Base silhouette is director-controlled; progression adds automatic growth.
    base_silhouette = float(settings.get("silhouette_visibility", 0.2))
    silhouette_presence = _clamp(base_silhouette + (ratio * 0.40) + (stage_mod * 0.30))

    return ArcProgression(
        stage=stage,
        position_ratio=ratio,
        scene_intensity=scene_intensity,
        narration_tension=narration_tension,
        disturbance_frequency=disturbance_frequency,
        cliffhanger_strength=cliffhanger_strength,
        silhouette_presence=silhouette_presence,
        escalation_level=escalation_level,
    )


def generate_episode(arc: ArcMemory, director_settings: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate an episode blueprint informed by auto arc progression.

    This function *extends* generation behavior by injecting progression-driven
    values into the output contract:
      - scene intensity
      - narration tension
      - disturbance frequency
      - cliffhanger strength

    It also updates in-memory arc memory so callers can persist changes to arcs.json.
    """

    next_episode = arc.completed_episodes + 1
    progression = compute_arc_progression(
        episode_number=next_episode,
        total_episodes=arc.total_episodes,
        director_settings=director_settings,
        prior_escalation=arc.escalation_level,
    )

    # Arc memory update for persistence.
    arc.completed_episodes = min(next_episode, arc.total_episodes)
    arc.current_progress_stage = progression.stage
    arc.escalation_level = progression.escalation_level

    return {
        "arc_id": arc.arc_id,
        "episode_number": next_episode,
        "progression_stage": progression.stage,
        "scene": {
            "intensity": progression.scene_intensity,
            "disturbance_frequency": progression.disturbance_frequency,
            "enemy_silhouette_presence": progression.silhouette_presence,
        },
        "narration": {
            "tension": progression.narration_tension,
        },
        "ending": {
            "cliffhanger_strength": progression.cliffhanger_strength,
        },
    }


def load_arcs(path: str | Path) -> dict[str, ArcMemory]:
    """Load arc memory records from disk."""

    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    arcs = {}
    for item in payload.get("arcs", []):
        arcs[item["arc_id"]] = ArcMemory(
            arc_id=item["arc_id"],
            total_episodes=int(item["total_episodes"]),
            completed_episodes=int(item.get("completed_episodes", 0)),
            current_progress_stage=item.get("current_progress_stage", "intro"),
            escalation_level=float(item.get("escalation_level", 0.0)),
        )
    return arcs


def save_arcs(path: str | Path, arcs: dict[str, ArcMemory]) -> None:
    """Persist arc memory records to disk, including progression metadata."""

    p = Path(path)
    payload = {
        "arcs": [
            {
                "arc_id": arc.arc_id,
                "total_episodes": arc.total_episodes,
                "completed_episodes": arc.completed_episodes,
                "current_progress_stage": arc.current_progress_stage,
                "escalation_level": round(arc.escalation_level, 4),
            }
            for arc in arcs.values()
        ]
    }
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
