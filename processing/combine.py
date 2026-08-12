# processing/combine.py
# Combines all scraped CSVs into master files for player and team stats.
#
# Expected folder structure:
#   data/raw/{year}/round_{n}/player_stats/*.csv
#   data/raw/{year}/round_{n}/team_stats/*.csv
#
# Output:
#   data/processed/player_stats_{year}.csv
#   data/processed/team_stats_{year}.csv

import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import YEAR, OUTPUT_DIR

# ── Only thing you need to change ────────────────────────────────────────────
COMBINE_YEAR = 2026

# ─────────────────────────────────────────────────────────────────────────────


def combine_season(year: int) -> pd.DataFrame:
    """Combine all player stat CSVs into one master file."""
    season_path = PROJECT_ROOT / OUTPUT_DIR / str(year)

    if not season_path.exists():
        print(f"[ERROR] No data found at {season_path}")
        return pd.DataFrame()

    round_dirs = sorted(
        [d for d in season_path.iterdir() if d.is_dir()],
        key=lambda d: int(d.name.replace("round_", ""))
        if d.name.replace("round_", "").isdigit()
        else 999,
    )

    if not round_dirs:
        print(f"[ERROR] No round folders found in {season_path}")
        return pd.DataFrame()

    print(f"Combining player stats — season {year}...")
    print(f"Found {len(round_dirs)} round folders\n")

    all_dfs = []
    for round_dir in round_dirs:
        player_dir = round_dir / "player_stats"
        if not player_dir.exists():
            print(f"  {round_dir.name}: no player_stats folder — skipping")
            continue

        csv_files = list(player_dir.glob("*.csv"))
        if not csv_files:
            continue

        round_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    round_dfs.append(df)
                else:
                    print(f"  [WARN] Empty: {csv_file.name}")
            except Exception as e:
                print(f"  [WARN] Could not read {csv_file.name}: {e}")

        if round_dfs:
            combined = pd.concat(round_dfs, ignore_index=True)
            all_dfs.append(combined)
            print(f"  {round_dir.name}: {len(csv_files)} files — {len(combined)} rows")

    if not all_dfs:
        print("[ERROR] No player data collected")
        return pd.DataFrame()

    master = pd.concat(all_dfs, ignore_index=True)

    before = len(master)
    master = master.drop_duplicates(subset=["Year", "Round", "Team", "Player"])
    removed = before - len(master)
    if removed:
        print(f"\n  Removed {removed} duplicate rows")

    master["Round"] = pd.to_numeric(master["Round"], errors="coerce")
    master = master.sort_values(["Round", "Team", "Player"]).reset_index(drop=True)

    out_dir = PROJECT_ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"player_stats_{year}.csv"
    master.to_csv(out_path, index=False)

    print(f"\n{'='*45}")
    print(f"Player stats saved → {out_path}")
    print(f"  Rows:    {len(master)}")
    print(f"  Players: {master['Player'].nunique()}")
    print(f"  Rounds:  {sorted(master['Round'].dropna().astype(int).unique().tolist())}")
    print(f"  Teams:   {len(master['Team'].unique())}")

    return master


def combine_team_stats(year: int) -> pd.DataFrame:
    """Combine all team stat CSVs into one master file."""
    season_path = PROJECT_ROOT / OUTPUT_DIR / str(year)

    if not season_path.exists():
        print(f"[ERROR] No data found at {season_path}")
        return pd.DataFrame()

    round_dirs = sorted(
        [d for d in season_path.iterdir() if d.is_dir()],
        key=lambda d: int(d.name.replace("round_", ""))
        if d.name.replace("round_", "").isdigit()
        else 999,
    )

    print(f"\nCombining team stats — season {year}...")

    all_dfs = []
    for round_dir in round_dirs:
        team_dir = round_dir / "team_stats"
        if not team_dir.exists():
            print(f"  {round_dir.name}: no team_stats folder — skipping")
            continue

        csv_files = list(team_dir.glob("*.csv"))
        if not csv_files:
            continue

        round_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    round_dfs.append(df)
                else:
                    print(f"  [WARN] Empty: {csv_file.name}")
            except Exception as e:
                print(f"  [WARN] Could not read {csv_file.name}: {e}")

        if round_dfs:
            combined = pd.concat(round_dfs, ignore_index=True)
            all_dfs.append(combined)
            print(f"  {round_dir.name}: {len(csv_files)} files — {len(combined)} rows")

    if not all_dfs:
        print("[ERROR] No team data collected")
        return pd.DataFrame()

    master = pd.concat(all_dfs, ignore_index=True)

    before = len(master)
    master = master.drop_duplicates(subset=["Year", "Round", "Team"])
    removed = before - len(master)
    if removed:
        print(f"\n  Removed {removed} duplicate rows")

    master["Round"] = pd.to_numeric(master["Round"], errors="coerce")
    master = master.sort_values(["Round", "Team"]).reset_index(drop=True)

    out_dir = PROJECT_ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"team_stats_{year}.csv"
    master.to_csv(out_path, index=False)

    print(f"\n{'='*45}")
    print(f"Team stats saved → {out_path}")
    print(f"  Rows:   {len(master)}")
    print(f"  Rounds: {sorted(master['Round'].dropna().astype(int).unique().tolist())}")
    print(f"  Teams:  {len(master['Team'].unique())}")

    return master


if __name__ == "__main__":
    combine_season(COMBINE_YEAR)
    combine_team_stats(COMBINE_YEAR)