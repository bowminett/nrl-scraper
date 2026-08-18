# processing/clean_teams.py
import pandas as pd

def clean_team_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ── Split fraction columns into MADE and PCT ──────────────────────
    # e.g. CONVERSIONS "2/3" → CONVERSIONS_MADE = 2, CONVERSIONS_PCT = 66.7
    fraction_cols = [
        "CONVERSIONS",
        "1 POINT FIELD GOALS",
        "2 POINT FIELD GOALS",
        "PENALTY GOALS",
    ]

    for col in fraction_cols:
        if col not in df.columns:
            continue

        def extract_made(val):
            val = str(val).strip()
            if "/" in val:
                return int(val.split("/")[0])
            try:
                return int(float(val))
            except:
                return 0

        def extract_pct(val):
            val = str(val).strip()
            if "/" in val:
                parts = val.split("/")
                made = int(parts[0])
                attempted = int(parts[1])
                if attempted == 0:
                    return 0.0
                return round((made / attempted) * 100, 1)
            # If it's just 0 (default) — no attempts, return 0
            return 0.0

        df[f"{col}_MADE"] = df[col].apply(extract_made)
        df[f"{col}_PCT"] = df[col].apply(extract_pct)

        # Drop original fraction column
        df = df.drop(columns=[col])

    # ── Percentage columns → strip % ─────────────────────────────────
    pct_cols = [
        "POSSESSION %", "COMPLETION RATE",
        "KICK DEFUSAL %", "EFFECTIVE TACKLE %"
    ]
    for col in pct_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace("%", "", regex=False).str.strip(),
                errors="coerce"
            ).fillna(0)

    # ── Comma formatted numbers ───────────────────────────────────────
    comma_cols = ["ALL RUN METRES", "KICKING METRES"]
    for col in comma_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            ).fillna(0)

    # ── Time in possession → total seconds ───────────────────────────
    if "TIME IN POSSESSION" in df.columns:
        def time_to_seconds(val):
            try:
                parts = str(val).split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except:
                return 0
        df["TIME IN POSSESSION"] = df["TIME IN POSSESSION"].apply(time_to_seconds)

    # ── Play the ball speed → strip 's' ──────────────────────────────
    if "AVERAGE PLAY THE BALL SPEED" in df.columns:
        df["AVERAGE PLAY THE BALL SPEED"] = pd.to_numeric(
            df["AVERAGE PLAY THE BALL SPEED"]
            .astype(str)
            .str.replace("s", "", regex=False)
            .str.strip(),
            errors="coerce"
        ).fillna(0)

    # ── Remaining object columns → numeric ────────────────────────────
    meta_cols = ["Team", "Opponent", "Is_Home", "Result", "RESULT"]
    for col in df.columns:
        if col not in meta_cols and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Fill remaining nulls with 0 ───────────────────────────────────
    fill_zero_cols = [
        "FORCED DROP OUTS", "INTERCEPTS", "INSIDE 10 METRES",
        "HEAD INJURY ASSESSMENT", "ON REPORTS", "40/20", "SENT OFF"
    ]
    for col in fill_zero_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    return df