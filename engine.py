import argparse
import json
import os
import random
import hashlib
from textwrap import dedent

# Default arc data used when no matching JSON file exists.
DEFAULT_ARCS = {
    "emberfall": {
        "world": "a volcanic island chain where storms are alive",
        "tone": "urgent mystery",
        "creatures": [
            "flare creature",
            "ashwing creature",
            "obsidian crawler creature",
            "stormfin creature",
            "emberhorn creature",
            "magma veil creature",
        ],
        "objectives": [
            "find the source of the red lightning",
            "protect the sky-port before dawn",
            "recover the fractured ember core",
        ],
        "enemy_hint": "a giant horned creature shape",
    },
    "tideveil": {
        "world": "flooded ruins beneath glowing moonwater",
        "tone": "haunting adventure",
        "creatures": [
            "reef strider creature",
            "mistscale creature",
            "lumen eel creature",
            "tideglass creature",
            "depth stalker creature",
            "pearlback creature",
        ],
        "objectives": [
            "decode the drowned signal",
            "seal the broken moon gate",
            "rescue the drifting city scouts",
        ],
        "enemy_hint": "a many-eyed creature silhouette",
    },
}


def load_arc_data(arc_name: str) -> dict:
    """Load arc data from arcs/{arc_name}.json if present, else use defaults."""
    # Normalize arc name so lookups are consistent.
    arc_key = arc_name.strip().lower()

    # Try loading a custom arc file first.
    arc_path = os.path.join("arcs", f"{arc_key}.json")
    if os.path.exists(arc_path):
        with open(arc_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fall back to built-in data if no file exists.
    if arc_key in DEFAULT_ARCS:
        return DEFAULT_ARCS[arc_key]

    # Last-resort generic arc so generation still works.
    return {
        "world": "an unstable frontier where strange energy leaks into every biome",
        "tone": "cinematic suspense",
        "creatures": [
            "shadow crest creature",
            "ion drifter creature",
            "crystal mane creature",
            "dusk burrower creature",
            "rift glider creature",
            "aurora shell creature",
        ],
        "objectives": [
            "trace the source of the anomaly",
            "stabilize the failing beacon",
            "escort the explorers to safety",
        ],
        "enemy_hint": "an unknown titan creature silhouette",
    }


def select_main_creatures(arc_data: dict, seed_value: int) -> list:
    """Select 2-3 core creatures that will lead this episode."""
    # Use a seeded random generator so the same episode is reproducible.
    rng = random.Random(seed_value)
    available = arc_data.get("creatures", [])

    # Always return at least two creatures when possible.
    if len(available) >= 3:
        return rng.sample(available, k=3)
    if len(available) == 2:
        return available[:]
    if len(available) == 1:
        return [available[0], available[0]]
    return ["frontier creature", "guardian creature"]


def build_title_and_thumbnail(arc_name: str, episode_number: int, arc_data: dict, creatures: list) -> tuple:
    """Generate an episode title and thumbnail concept line."""
    # Build a dramatic title from arc, episode number, and objective.
    objective = arc_data.get("objectives", ["survive the incoming storm"])[0]
    title = f"{arc_name.title()} Episode {episode_number}: {objective.title()}"

    # Keep the thumbnail concept concise for production handoff.
    thumbnail = (
        f"Wide cinematic shot in {arc_data.get('world', 'a wild frontier')}, "
        f"{creatures[0]} in foreground, {creatures[1]} mid-action, "
        f"red energy crack in sky, bold text '{arc_name.upper()} #{episode_number}'."
    )
    return title, thumbnail


def build_scene_blueprints(arc_data: dict, creatures: list) -> list:
    """Create the 6 locked scene beats with 10-second intent each."""
    world = arc_data.get("world", "an unstable wilderness")
    objective = random.choice(arc_data.get("objectives", ["stop the anomaly"]))
    enemy_hint = arc_data.get("enemy_hint", "an unknown creature silhouette")

    # Locked scene structure requested by spec.
    return [
        ("strong hook", f"A sudden shockwave splits the horizon in {world} as {creatures[0]} sprints toward danger."),
        ("developing tension", f"The team tracks unstable signs while {creatures[1]} senses a hidden trap tied to {objective}."),
        ("energy escalation", f"Crackling light erupts around {creatures[2]} and the ground starts pulsing like a heartbeat."),
        ("disturbance event", f"A violent rupture opens, throwing debris and separating allies across a collapsing path."),
        ("near chaos", f"All creatures scramble as storms, fire, and falling ruins collide in a near-total breakdown."),
        ("cliffhanger with enemy silhouette hint", f"In smoke and lightning, only the outline of {enemy_hint} appears before total blackout."),
    ]


def build_narration_line(scene_index: int, beat_name: str, description: str, tone: str) -> str:
    """Create a short narrator line that matches scene tone and beat."""
    return (
        f"Scene {scene_index} narration ({beat_name}, {tone}): "
        f"{description} This is only the beginning."
    )


def build_safe_image_prompt(scene_index: int, description: str) -> str:
    """Create safe image prompts and always use the word 'creature'."""
    # Explicitly include "creature" for safety requirement.
    return (
        f"Scene {scene_index} image prompt: cinematic fantasy environment, creature-focused action, "
        f"{description}, dynamic lighting, high detail, no gore, family-safe"
    )


def build_video_prompt(scene_index: int, beat_name: str, description: str) -> str:
    """Create video generation prompts with motion and camera guidance."""
    return (
        f"Scene {scene_index} video prompt (10s): {beat_name}; {description}; "
        f"camera: sweeping dolly + quick push-in; pacing: escalating; style: cinematic adventure"
    )


def generate_episode(arc_name: str, episode_number: int) -> str:
    """
    Generate a full, production-ready episode package and save it to /output.

    Required flow:
    1) load arc data
    2) select main creatures
    3) generate title and thumbnail concept
    4) create 6 scenes (10 seconds each)
    5) generate narration lines
    6) generate safe image prompts using 'creature'
    7) generate video prompts
    """
    # Make generation deterministic for the same arc + episode.
    seed_input = f"{arc_name.lower()}::{episode_number}"
    seed_value = int(hashlib.sha256(seed_input.encode("utf-8")).hexdigest()[:8], 16)

    # 1) Load arc data.
    arc_data = load_arc_data(arc_name)

    # 2) Select main creatures.
    main_creatures = select_main_creatures(arc_data, seed_value)

    # 3) Build title and thumbnail concept.
    title, thumbnail = build_title_and_thumbnail(arc_name, episode_number, arc_data, main_creatures)

    # 4) Build 6 locked scenes.
    scenes = build_scene_blueprints(arc_data, main_creatures)

    # 5-7) Build narration + image + video prompts for each scene.
    tone = arc_data.get("tone", "cinematic suspense")
    scene_blocks = []
    for idx, (beat_name, description) in enumerate(scenes, start=1):
        narration = build_narration_line(idx, beat_name, description, tone)
        image_prompt = build_safe_image_prompt(idx, description)
        video_prompt = build_video_prompt(idx, beat_name, description)
        scene_blocks.append(
            dedent(
                f"""
                --- Scene {idx} (10s) ---
                Beat: {beat_name}
                Scene Description: {description}
                Narration: {narration}
                Image Prompt: {image_prompt}
                Video Prompt: {video_prompt}
                """
            ).strip()
        )

    # Assemble clean production-ready text.
    scenes_text = "\n\n".join(scene_blocks)
    header_lines = [
        f"ARC: {arc_name}",
        f"EPISODE: {episode_number}",
        f"TITLE: {title}",
        f"THUMBNAIL CONCEPT: {thumbnail}",
        f"MAIN CREATURES: {', ' .join(main_creatures)}",
        "",
    ]
    episode_text = "\n".join(header_lines) + scenes_text + "\n"
    # Save to the requested absolute output pattern.
    os.makedirs("/output", exist_ok=True)
    out_path = f"/output/arc_{arc_name}_episode_{episode_number}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(episode_text)

    return out_path


def main() -> None:
    """CLI entrypoint for one-command episode generation."""
    parser = argparse.ArgumentParser(description="Generate a Fireverse episode package.")
    parser.add_argument("arc_name", help="Arc name, for example: emberfall")
    parser.add_argument("episode_number", type=int, help="Episode number, for example: 1")
    args = parser.parse_args()

    output_path = generate_episode(args.arc_name, args.episode_number)
    print(f"Episode generated: {output_path}")


if __name__ == "__main__":
    main()
