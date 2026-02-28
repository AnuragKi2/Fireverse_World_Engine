from fireverse_engine.episode_engine import ArcMemory, compute_arc_progression, generate_episode


def test_progression_stage_ordering():
    arc = ArcMemory(arc_id="a", total_episodes=10)
    seen = []
    for _ in range(10):
        ep = generate_episode(arc, director_settings={"silhouette_visibility": 0.1})
        seen.append(ep["progression_stage"])

    assert "intro" in seen
    assert "buildup" in seen
    assert "escalation" in seen
    assert "instability" in seen
    assert seen[-1] == "finale"


def test_silhouette_presence_scales_with_progress():
    early = compute_arc_progression(
        episode_number=1,
        total_episodes=10,
        director_settings={"silhouette_visibility": 0.2},
    )
    late = compute_arc_progression(
        episode_number=10,
        total_episodes=10,
        director_settings={"silhouette_visibility": 0.2},
    )
    assert late.silhouette_presence > early.silhouette_presence
