"""Proprietary speed figure computation and trend analyzers."""

from __future__ import annotations

import numpy as np
import pandas as pd

SOURCE_WEIGHTS = {
    "csv": 0.9,
    "drf": 1.0,
    "drf2": 1.05,
    "drf3": 1.1,
    "drf4": 1.15,
}

METRIC_WEIGHTS = {
    "speed": 0.45,
    "pace": 0.25,
    "class": 0.2,
    "weight": -0.1,
}


def _zscore(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    std = series.std(ddof=0)
    if std == 0 or np.isnan(std):
        return series.fillna(series.mean()).mul(0)
    return (series - series.mean()) / std


def calculate_speed_figures(frame: pd.DataFrame) -> pd.DataFrame:
    """Generate proprietary speed figure per horse/race row."""
    scored = frame.copy()
    for metric in ["speed", "pace", "class", "weight"]:
        if metric not in scored:
            scored[metric] = 0
        scored[f"z_{metric}"] = _zscore(scored[metric])

    composite = sum(scored[f"z_{metric}"] * weight for metric, weight in METRIC_WEIGHTS.items())
    scored["base_figure"] = 100 + (composite * 12)

    source_multiplier = scored.get("source_type", "unknown").astype(str).str.lower().map(SOURCE_WEIGHTS).fillna(1.0)
    scored["proprietary_speed_figure"] = (scored["base_figure"] * source_multiplier).round(2)

    return scored.sort_values(["track", "race", "proprietary_speed_figure"], ascending=[True, True, False])


def analyze_track_trends(results: pd.DataFrame, track_name: str) -> dict:
    """Summarize historical trends for a selected track."""
    subset = results[results["track"].astype(str).str.lower() == track_name.lower()].copy()
    if subset.empty:
        return {
            "sample_size": 0,
            "inside_post_win_rate": None,
            "front_running_win_rate": None,
            "avg_winning_figure": None,
        }

    if "finish" in subset:
        winners = subset[subset["finish"] == 1]
    else:
        winners = subset.iloc[0:0]

    inside = subset[subset.get("post", 99) <= 3]
    front = subset[subset.get("style", "").astype(str).str.upper().str.startswith("E")]

    return {
        "sample_size": int(len(subset)),
        "inside_post_win_rate": round(len(inside[inside.get("finish", 0) == 1]) / max(len(inside), 1), 3),
        "front_running_win_rate": round(len(front[front.get("finish", 0) == 1]) / max(len(front), 1), 3),
        "avg_winning_figure": round(float(winners.get("proprietary_speed_figure", pd.Series(dtype=float)).mean()), 2)
        if not winners.empty
        else None,
    }
