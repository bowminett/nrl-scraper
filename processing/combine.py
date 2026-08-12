# Walks through data/raw/{year}/round_*/ and combines every team CSV
# into one master file at data/processed/player_stats_{year}.csv
#
# Usage:
#   python processing/combine.py           # combines current year from config
#   python processing/combine.py --year 2025

import pandas as pd
from pathlib import Path
import argparse
import sys

# Add project root to path so config can be imported
sys.path.append(str(Path(__file__).parent.parent))
from config import YEAR, OUTPUT_DIR


def combine_season(year: int, raw_dir: str = OUTPUT_DIR) -> pd.DataFrame:
    season_path = Path(raw_dir) / str(year)

    if not season_path.exists():
        print(f"[ERROR] No data found at {season_path}")
        return pd.DataFrame()

    all_dfs = []
    round_dirs = sorted(
        [d for d in season_path.iterdir() if d.is_dir()],
        key=lambda d: int(d.name.replace("round_", "")) if d.name.replace("round_", "").isdigit() else 999
    )

    if not round_dirs:
        print(f"[ERROR] No round folders found in {season_path}")
        return pd.DataFrame()

    print(f"Combining season {year}...")
    print(f"Found {len(round_dirs)} round folders\n")

    for round_dir in round_dirs:
        csv_files = list(round_dir.glob("*.csv"))
        if not csv_files:
            continue

        round_dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if df.empty:
                    print(f"  [WARN] Empty file: {csv_file.name}")
                    continue
                round_dfs.append(df)
            except Exception as e:
                print(f"  [WARN] Could not read {csv_file}: {e}")
                continue

        if round_dfs:
            round_combined = pd.concat(round_dfs, ignore_index=True)
            all_dfs.append(round_combined)
            print(f"  {round_dir.name}: {len(csv_files)} teams, {len(round_combined)} player rows")

    if not all_dfs:
        print("[ERROR] No data collected — check your raw data folder")
        return pd.DataFrame()

    master = pd.concat(all_dfs, ignore_index=True)

    # Remove duplicates — if a match was scraped twice
    before = len(master)
    master = master.drop_duplicates(subset=["Year", "Round", "Team", "Player"])
    dupes = before - len(master)
    if dupes > 0:
        print(f"\n  Removed {dupes} duplicate rows")

    # Sort chronologically
    master["Round"] = pd.to_numeric(master["Round"], errors="coerce")
    master = master.sort_values(["Round", "Team", "Player"]).reset_index(drop=True)

    # Save
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"player_stats_{year}.csv"
    master.to_csv(out_path, index=False)

    print(f"\n{'='*40}")
    print(f"Master CSV saved → {out_path}")
    print(f"  Total rows:    {len(master)}")
    print(f"  Unique players: {master['Player'].nunique()}")
    print(f"  Rounds covered: {sorted(master['Round'].dropna().unique().astype(int).tolist())}")
    print(f"  Teams:         {sorted(master['Team'].unique().tolist())}")

    return master


def combine_team_stats(year: int, raw_dir: str = OUTPUT_DIR) -> pd.DataFrame:
    season_path = Path(raw_dir) / str(year)
    all_dfs = []

    for round_dir in sorted(season_path.iterdir()):
        team_stats_dir = round_dir / "team_stats"
        if not team_stats_dir.exists():
            continue
        for csv_file in team_stats_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                print(f"  [WARN] {csv_file}: {e}")

    if not all_dfs:
        print(f"No team stats found for {year}")
        return pd.DataFrame()

    master = pd.concat(all_dfs, ignore_index=True)
    master = master.drop_duplicates(subset=["Year", "Round", "Team"])
    master["Round"] = pd.to_numeric(master["Round"], errors="coerce")
    master = master.sort_values(["Round", "Team"]).reset_index(drop=True)

    out_path = Path("data/processed") / f"team_stats_{year}.csv"
    master.to_csv(out_path, index=False)
    print(f"Team stats saved → {out_path} ({len(master)} rows)")
    return master


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine NRL player stat CSVs into master file")
    parser.add_argument("--year", type=int, default=int(YEAR), help="Season year to combine")
    args = parser.parse_args()

    combine_season(year=args.year)
    combine_team_stats(year=args.year)