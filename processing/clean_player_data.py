# processing/clean_player_data.py
# processing/clean_player_data.py
import pandas as pd


def clean_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    meta_cols = ["Team", "Opponent", "Player", "Position"]

    # ── Replace dashes with 0 — used for missing stats ────────────────
    # Must happen before any numeric conversion
    df = df.replace("-", 0)

    # ── Time columns → minutes as decimal ────────────────────────────────
    time_cols = ["Mins Played", "Stint One", "Stint Two"]

    def time_to_minutes(val):
        try:
            val = str(val).strip()
            if ":" in val:
                parts = val.split(":")
                return round(int(parts[0]) + int(parts[1]) / 60, 2)
            return round(float(val), 2)
        except:
            return 0.0

    for col in time_cols:
        if col in df.columns:
            df[col] = df[col].apply(time_to_minutes)

    # ── Percentage columns → strip % ─────────────────────────────────
    pct_cols = [
        "Goal Conversion Rate", "Tackle Efficiency"
    ]
    for col in pct_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace("%", "", regex=False).str.strip(),
                errors="coerce"
            ).fillna(0)

    # ── Play the ball speed → strip 's' ──────────────────────────────
    if "Average Play The Ball Speed" in df.columns:
        df["Average Play The Ball Speed"] = pd.to_numeric(
            df["Average Play The Ball Speed"]
            .astype(str)
            .str.replace("s", "", regex=False)
            .str.strip(),
            errors="coerce"
        ).fillna(0)

    # ── Comma formatted numbers ───────────────────────────────────────
    comma_cols = [
        "All Run Metres", "Kicking Metres",
        "Dummy Half Run Metres", "Post Contact Metres"
    ]
    for col in comma_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            ).fillna(0)

    # ── Remaining object columns → numeric ────────────────────────────
    for col in df.columns:
        if col not in meta_cols and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df