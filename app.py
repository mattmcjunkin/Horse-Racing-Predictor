from __future__ import annotations

import pandas as pd
import streamlit as st

from horse_racing_predictor.database import HorseDatabase
from horse_racing_predictor.parsing import parse_uploaded_file
from horse_racing_predictor.scoring import analyze_track_trends, calculate_speed_figures
from horse_racing_predictor.tracks import US_TRACKS

st.set_page_config(page_title="Horse Racing Predictor", layout="wide")

st.title("Horse Racing Predictor")
st.caption("Upload Brisnet files to generate proprietary speed figures and track trends.")

col1, col2 = st.columns(2)

with col1:
    card_files = st.file_uploader(
        "Upload race card files (CSV, DRF, DRF2, DRF3, DRF4)",
        accept_multiple_files=True,
        type=["csv", "drf", "drf2", "drf3", "drf4"],
    )

with col2:
    results_files = st.file_uploader(
        "Upload historical result files",
        accept_multiple_files=True,
        type=["csv", "drf", "drf2", "drf3", "drf4"],
    )

track_selection = st.selectbox("Track analyzer", US_TRACKS)

db = HorseDatabase()

def _parse_files(uploaded_files: list) -> pd.DataFrame:
    frames = []
    for uploaded in uploaded_files:
        frames.append(parse_uploaded_file(uploaded.name, uploaded.getvalue()))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

if st.button("Run Analysis", type="primary"):
    if not card_files:
        st.error("Please upload at least one race card file.")
    else:
        cards_frame = _parse_files(card_files)
        scored = calculate_speed_figures(cards_frame)
        db.upsert_figures(scored)

        st.subheader("Top Horses by Proprietary Speed Figure")
        top = scored[["track", "race", "horse", "proprietary_speed_figure", "source_type"]].head(100)
        st.dataframe(top, use_container_width=True)

        csv = scored.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download full scored card",
            data=csv,
            file_name="scored_race_card.csv",
            mime="text/csv",
        )

        results_frame = _parse_files(results_files) if results_files else pd.DataFrame()
        if not results_frame.empty:
            merged = pd.concat([results_frame, scored], ignore_index=True, sort=False)
            trends = analyze_track_trends(merged, track_selection)
        else:
            trends = analyze_track_trends(scored, track_selection)

        st.subheader(f"Track Trends: {track_selection}")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        metrics_col1.metric("Sample size", trends["sample_size"])
        metrics_col2.metric("Inside post win rate", trends["inside_post_win_rate"])
        metrics_col3.metric("Front-running win rate", trends["front_running_win_rate"])
        st.metric("Avg winning figure", trends["avg_winning_figure"])

st.divider()
st.subheader("Horse Database")
known_horses = db.list_horses()
if known_horses:
    horse = st.selectbox("Select horse", known_horses)
    history = db.horse_history(horse)
    st.dataframe(history, use_container_width=True)
else:
    st.info("No horses stored yet. Run analysis first.")
