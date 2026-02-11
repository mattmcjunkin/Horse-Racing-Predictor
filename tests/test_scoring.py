import pandas as pd

from horse_racing_predictor.scoring import analyze_track_trends, calculate_speed_figures


def test_calculate_speed_figures_adds_column():
    frame = pd.DataFrame(
        {
            "horse": ["A", "B", "C"],
            "track": ["Aqueduct", "Aqueduct", "Aqueduct"],
            "race": [1, 1, 1],
            "speed": [80, 90, 85],
            "pace": [78, 88, 84],
            "class": [70, 75, 72],
            "weight": [120, 122, 121],
            "source_type": ["drf", "drf4", "csv"],
        }
    )

    scored = calculate_speed_figures(frame)

    assert "proprietary_speed_figure" in scored.columns
    assert scored["proprietary_speed_figure"].notna().all()


def test_track_trends_sample_size():
    frame = pd.DataFrame(
        {
            "horse": ["A", "B"],
            "track": ["Saratoga", "Saratoga"],
            "finish": [1, 2],
            "post": [1, 8],
            "style": ["E", "C"],
            "proprietary_speed_figure": [110.0, 95.0],
        }
    )

    trends = analyze_track_trends(frame, "Saratoga")
    assert trends["sample_size"] == 2
    assert trends["inside_post_win_rate"] == 1.0
