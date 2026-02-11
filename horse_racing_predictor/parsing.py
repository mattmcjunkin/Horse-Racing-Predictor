"""File parsing utilities for Brisnet-like card and results files."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

COLUMN_ALIASES = {
    "horse": ["horse", "horse_name", "runner", "name"],
    "track": ["track", "track_name", "course"],
    "race": ["race", "race_num", "race_number"],
    "speed": ["speed", "speed_rating", "last_speed", "bris_speed"],
    "pace": ["pace", "pace_rating", "early_pace"],
    "class": ["class", "class_rating", "class_fig"],
    "weight": ["weight", "carried_weight", "wgt"],
    "post": ["post", "post_position", "pp"],
    "style": ["style", "run_style", "running_style"],
    "finish": ["finish", "finish_position", "pos"],
    "date": ["date", "race_date"],
}


def _read_delimited(data: bytes) -> pd.DataFrame:
    """Attempt multiple delimiters to parse nonstandard files."""
    text = data.decode("utf-8", errors="ignore")
    for sep in [",", "|", "\t", ";"]:
        frame = pd.read_csv(io.StringIO(text), sep=sep)
        if frame.shape[1] > 1:
            return frame
    frame = pd.read_csv(io.StringIO(text), sep=r"\s+", engine="python")
    return frame


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize columns into model-required names."""
    frame = frame.copy()
    lower_map = {col.lower().strip(): col for col in frame.columns}

    normalized = pd.DataFrame()
    for canonical, aliases in COLUMN_ALIASES.items():
        original = next((lower_map[a] for a in aliases if a in lower_map), None)
        if original:
            normalized[canonical] = frame[original]

    if "horse" not in normalized:
        normalized["horse"] = frame.iloc[:, 0].astype(str)
    if "track" not in normalized:
        normalized["track"] = "Unknown"
    if "race" not in normalized:
        normalized["race"] = 1

    for numeric_col in ["speed", "pace", "class", "weight", "post", "finish"]:
        if numeric_col in normalized:
            normalized[numeric_col] = pd.to_numeric(normalized[numeric_col], errors="coerce")

    if "style" not in normalized:
        normalized["style"] = "Unknown"

    if "date" in normalized:
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")

    return normalized


def parse_uploaded_file(file_name: str, data: bytes) -> pd.DataFrame:
    """Parse uploaded race card or result file into normalized tabular data."""
    suffix = Path(file_name).suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(io.BytesIO(data))
    else:
        frame = _read_delimited(data)

    normalized = normalize_columns(frame)
    normalized["source_type"] = suffix.lstrip(".") or "unknown"
    return normalized
