# processing/build_database.py
# Cleans processed CSVs and loads them into a local SQLite database.
#
# Run this after combine.py whenever you have new data.
#
# Usage: python processing/build_database.py
#
# Output: nrl.db in project root

import pandas as pd
import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import YEAR
from processing.clean_team_data import clean_team_stats
from processing.clean_player_data import clean_player_stats

DB_PATH = PROJECT_ROOT / "nrl.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ── Only thing you need to change ────────────────────────────────────────────
BUILD_YEAR = 2026

# ─────────────────────────────────────────────────────────────────────────────


def build_database(year: int):
    print(f"Building database → {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)

    # ── Player stats ──────────────────────────────────────────────────
    player_path = PROCESSED_DIR / f"player_stats_{year}.csv"
    if player_path.exists():
        print(f"Loading player stats...")
        df = pd.read_csv(player_path)
        print(f"  Raw: {len(df)} rows, {len(df.columns)} columns")

        df = clean_player_stats(df)
        print(f"  Cleaned: {len(df)} rows, {len(df.columns)} columns")

        # Check for nulls after cleaning
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            print(f"  [WARN] Nulls remaining: {nulls.to_dict()}")

        df.to_sql("player_stats", conn, if_exists="replace", index=False)
        print(f"  Loaded to database ✓")
        print(f"  Players: {df['Player'].nunique()}")
        print(f"  Rounds:  {sorted(df['Round'].unique().astype(int).tolist())}")
        print(f"  Teams:   {df['Team'].nunique()}")
    else:
        print(f"[WARN] Not found: {player_path}")

    print()

    # ── Team stats ────────────────────────────────────────────────────
    team_path = PROCESSED_DIR / f"team_stats_{year}.csv"
    if team_path.exists():
        print(f"Loading team stats...")
        df = pd.read_csv(team_path)
        print(f"  Raw: {len(df)} rows, {len(df.columns)} columns")

        df = clean_team_stats(df)
        print(f"  Cleaned: {len(df)} rows, {len(df.columns)} columns")

        # Check for nulls after cleaning
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            print(f"  [WARN] Nulls remaining: {nulls.to_dict()}")

        df.to_sql("team_stats", conn, if_exists="replace", index=False)
        print(f"  Loaded to database ✓")
        print(f"  Rounds: {sorted(df['Round'].unique().astype(int).tolist())}")
        print(f"  Teams:  {df['Team'].nunique()}")
    else:
        print(f"[WARN] Not found: {team_path}")

    # ── Verify tables ─────────────────────────────────────────────────
    print(f"\n{'='*45}")
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print(f"Tables in database: {tables['name'].tolist()}")

    for table in tables['name']:
        count = pd.read_sql(f"SELECT COUNT(*) as n FROM {table}", conn)['n'][0]
        print(f"  {table}: {count} rows")

    conn.close()
    print(f"\nDone → {DB_PATH}")


if __name__ == "__main__":
    build_database(BUILD_YEAR)