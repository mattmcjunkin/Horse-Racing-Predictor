"""SQLite persistence layer for horse-level speed figures."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


class HorseDatabase:
    def __init__(self, db_path: str = "data/horse_racing.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS horse_figures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    horse TEXT NOT NULL,
                    track TEXT,
                    race INTEGER,
                    source_type TEXT,
                    proprietary_speed_figure REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert_figures(self, scored: pd.DataFrame) -> None:
        columns = ["horse", "track", "race", "source_type", "proprietary_speed_figure"]
        existing_cols = [col for col in columns if col in scored.columns]
        to_store = scored[existing_cols].copy()
        with self._connect() as con:
            to_store.to_sql("horse_figures", con, if_exists="append", index=False)

    def horse_history(self, horse_name: str) -> pd.DataFrame:
        with self._connect() as con:
            return pd.read_sql_query(
                """
                SELECT horse, track, race, source_type, proprietary_speed_figure, created_at
                FROM horse_figures
                WHERE lower(horse) = lower(?)
                ORDER BY created_at DESC
                """,
                con,
                params=(horse_name,),
            )

    def list_horses(self) -> list[str]:
        with self._connect() as con:
            rows = con.execute("SELECT DISTINCT horse FROM horse_figures ORDER BY horse").fetchall()
        return [row[0] for row in rows]
