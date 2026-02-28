# Fireverse_World_Engine

Fireverse_World_Engine is an intelligent content generation engine for cinematic creature containment stories.

## Project Goal

This project provides a structured foundation for generating episodic content across multiple story arcs while enforcing persistent world rules:

- Each **arc** represents a unique environment (ice, fire, volcano, modern, ancient, etc.).
- Each arc has one hidden **enemy silhouette** seeded subtly across episodes.
- Each **episode** contains exactly 3 main creatures.
- Each arc tracks about 15–20 creatures in total.
- The universe supports multiple lores (anime, fantasy, and beyond).
- A future compilation arc can merge enemies and heroes from prior arcs.

## Starter Architecture

```text
/data
  arcs.json
  creature_tracker.json
  enemy_silhouettes.json
/templates
  episode_template.txt
  scene_template.txt
  prompt_template.txt
engine.py
README.md
```

## File Responsibilities

- `data/arcs.json` - Defines arc-level metadata, episode lineup, and fixed main creatures per episode.
- `data/creature_tracker.json` - Tracks creature usage across arcs and episodes to preserve continuity.
- `data/enemy_silhouettes.json` - Stores hidden enemy silhouette details for each arc.
- `templates/episode_template.txt` - Blueprint for full episode output fields.
- `templates/scene_template.txt` - Blueprint for 6 scene blocks (10 seconds each).
- `templates/prompt_template.txt` - Safe prompt style guide for image/video generation using the word "creature".
- `engine.py` - Starter orchestrator that loads data, validates world constraints, and builds episode output.

## Quick Start

1. Edit JSON files in `/data` to define your arcs, creatures, and silhouette hints.
2. Update templates in `/templates` to tune narrative style.
3. Run:

```bash
python3 engine.py
```

The starter run prints a sample generated episode package using template-backed placeholders.
