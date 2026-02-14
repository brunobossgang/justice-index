"""
Justice Index — USSC FY2024 Data Explorer
First look at the Individual Offender Datafile.
"""
import pandas as pd
import sys

DATA_PATH = "data/individual_fy24/opafy24nid.csv"

# Key columns we care about for Justice Index
KEY_COLS = [
    "POESSION",   # Probation office session (case ID proxy)
    "DISTRICT",   # Federal district
    "CIRCDIST",   # Circuit
    "OFFGUIDE",   # Primary offense guideline
    "SENTTOT",    # Total sentence (months)
    "SENTTCAP",   # Sentence capped
    "SENTIMP",    # Sentence imposed type
    "SENTRNGE",   # Sentencing range
    "XMINSOR",    # Guideline minimum (months)
    "XMAXSOR",    # Guideline maximum (months)
    "MONRACE",    # Race (detailed)
    "NEWRACE",    # Race (collapsed)
    "AGE",        # Age at sentencing
    "AGECAT",     # Age category
    "MONSEX",     # Sex
    "CITIZEN",    # Citizenship status
    "EDUCATN",    # Education level
    "NEWEDUC",    # Education (collapsed)
    "CRIMHIST",   # Criminal history category
    "CRIMPTS",    # Criminal history points
    "WEAPON",     # Weapon involvement
    "IS924C",     # 924(c) conviction
    "BOOTEFCT",   # Booker/departure info
    "DEPARTEFCT", # Departure direction
    "REAS1",      # Departure reason 1
]

def find_cols(df, patterns):
    """Find columns matching patterns (case-insensitive)."""
    found = []
    for p in patterns:
        matches = [c for c in df.columns if p.upper() in c.upper()]
        found.extend(matches)
    return list(dict.fromkeys(found))  # dedupe preserving order

def main():
    print(f"Loading {DATA_PATH}...")
    print("(This is a 1.6GB file, may take a moment)\n")
    
    # First pass: just read headers to find our columns
    headers = pd.read_csv(DATA_PATH, nrows=0).columns.tolist()
    print(f"Total columns: {len(headers)}")
    
    # Find which of our key columns actually exist
    available = [c for c in KEY_COLS if c in headers]
    missing = [c for c in KEY_COLS if c not in headers]
    
    # Also search for related columns we might have missed
    extra = find_cols(pd.DataFrame(columns=headers), 
                      ["RACE", "SENT", "JUDGE", "DEPART", "GUIDE", "OFFENSE", "SEX", "GENDER"])
    extra = [c for c in extra if c not in available]
    
    print(f"\nKey columns found ({len(available)}):")
    for c in available:
        print(f"  ✅ {c}")
    
    if missing:
        print(f"\nKey columns NOT found ({len(missing)}):")
        for c in missing:
            print(f"  ❌ {c}")
    
    if extra:
        print(f"\nOther potentially relevant columns ({len(extra)}):")
        for c in extra[:30]:
            print(f"  🔍 {c}")
    
    # Now load just the columns we want
    load_cols = available + [c for c in extra[:20] if c not in available]
    print(f"\nLoading {len(load_cols)} columns...")
    df = pd.read_csv(DATA_PATH, usecols=load_cols, low_memory=False)
    
    print(f"Rows: {len(df):,}")
    print(f"\n{'='*60}")
    print("BASIC STATS")
    print(f"{'='*60}")
    
    # Sentence stats
    if "SENTTOT" in df.columns:
        sent = df["SENTTOT"].dropna()
        sent = sent[sent >= 0]  # Filter out codes for life/missing
        print(f"\nSentence (SENTTOT) — months:")
        print(f"  Mean:   {sent.mean():.1f}")
        print(f"  Median: {sent.median():.1f}")
        print(f"  Min:    {sent.min():.0f}")
        print(f"  Max:    {sent.max():.0f}")
        print(f"  Std:    {sent.std():.1f}")
    
    # Race breakdown
    if "NEWRACE" in df.columns:
        print(f"\nRace (NEWRACE) distribution:")
        race_map = {1: "White", 2: "Black", 3: "Hispanic", 4: "Other", 7: "Multiracial"}
        race_counts = df["NEWRACE"].value_counts().sort_index()
        total = race_counts.sum()
        for code, count in race_counts.items():
            label = race_map.get(int(code), f"Code {code}")
            print(f"  {label}: {count:,} ({count/total*100:.1f}%)")
    
    # Sex breakdown
    if "MONSEX" in df.columns:
        print(f"\nSex (MONSEX) distribution:")
        sex_map = {0: "Male", 1: "Female"}
        sex_counts = df["MONSEX"].value_counts().sort_index()
        total = sex_counts.sum()
        for code, count in sex_counts.items():
            label = sex_map.get(int(code), f"Code {code}")
            print(f"  {label}: {count:,} ({count/total*100:.1f}%)")
    
    # Criminal history
    if "CRIMHIST" in df.columns:
        print(f"\nCriminal History Category (CRIMHIST):")
        ch_counts = df["CRIMHIST"].value_counts().sort_index()
        for code, count in ch_counts.items():
            if code >= 1 and code <= 6:
                print(f"  Category {int(code)}: {count:,}")
    
    # Offense guideline
    if "OFFGUIDE" in df.columns:
        print(f"\nTop 15 Offense Guidelines (OFFGUIDE):")
        top = df["OFFGUIDE"].value_counts().head(15)
        for code, count in top.items():
            print(f"  {code}: {count:,}")
    
    # District
    if "DISTRICT" in df.columns:
        print(f"\nTop 15 Districts by case count:")
        top = df["DISTRICT"].value_counts().head(15)
        for code, count in top.items():
            print(f"  District {code}: {count:,}")
    
    # The key analysis: sentence by race (controlling for nothing yet — just raw)
    if "SENTTOT" in df.columns and "NEWRACE" in df.columns:
        print(f"\n{'='*60}")
        print("RAW SENTENCE BY RACE (no controls — just a first look)")
        print(f"{'='*60}")
        race_map = {1: "White", 2: "Black", 3: "Hispanic", 4: "Other", 7: "Multiracial"}
        valid = df[(df["SENTTOT"] >= 0) & (df["NEWRACE"].isin(race_map.keys()))].copy()
        valid["race_label"] = valid["NEWRACE"].map(race_map)
        grouped = valid.groupby("race_label")["SENTTOT"].agg(["mean", "median", "count"])
        grouped = grouped.sort_values("mean", ascending=False)
        for race, row in grouped.iterrows():
            print(f"  {race:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")
    
    # Guideline range vs actual sentence
    if all(c in df.columns for c in ["SENTTOT", "XMINSOR", "XMAXSOR"]):
        print(f"\n{'='*60}")
        print("GUIDELINE RANGE vs ACTUAL SENTENCE")
        print(f"{'='*60}")
        valid = df[(df["SENTTOT"] >= 0) & (df["XMINSOR"] >= 0) & (df["XMAXSOR"] >= 0)].copy()
        valid["departure"] = valid["SENTTOT"] - valid["XMINSOR"]
        print(f"  Cases with valid guideline range: {len(valid):,}")
        below = (valid["SENTTOT"] < valid["XMINSOR"]).sum()
        within = ((valid["SENTTOT"] >= valid["XMINSOR"]) & (valid["SENTTOT"] <= valid["XMAXSOR"])).sum()
        above = (valid["SENTTOT"] > valid["XMAXSOR"]).sum()
        total = len(valid)
        print(f"  Below range: {below:,} ({below/total*100:.1f}%)")
        print(f"  Within range: {within:,} ({within/total*100:.1f}%)")
        print(f"  Above range: {above:,} ({above/total*100:.1f}%)")
        print(f"\n  Mean departure from minimum: {valid['departure'].mean():.1f} months")
    
    # Departure by race
    if all(c in df.columns for c in ["SENTTOT", "XMINSOR", "NEWRACE"]):
        print(f"\n{'='*60}")
        print("DEPARTURE FROM GUIDELINE MINIMUM — BY RACE")
        print(f"{'='*60}")
        race_map = {1: "White", 2: "Black", 3: "Hispanic", 4: "Other", 7: "Multiracial"}
        valid = df[(df["SENTTOT"] >= 0) & (df["XMINSOR"] >= 0) & (df["NEWRACE"].isin(race_map.keys()))].copy()
        valid["departure"] = valid["SENTTOT"] - valid["XMINSOR"]
        valid["race_label"] = valid["NEWRACE"].map(race_map)
        grouped = valid.groupby("race_label")["departure"].agg(["mean", "median", "count"])
        grouped = grouped.sort_values("mean", ascending=False)
        for race, row in grouped.iterrows():
            sign = "+" if row["mean"] >= 0 else ""
            print(f"  {race:15s}  mean={sign}{row['mean']:6.1f}mo  median={sign}{row['median']:5.1f}mo  n={int(row['count']):,}")
        print("\n  (Positive = sentenced ABOVE guideline minimum)")
        print("  (Negative = sentenced BELOW guideline minimum)")
    
    print(f"\n{'='*60}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nData saved reference: {DATA_PATH}")
    print("Next: design schema, load into Postgres, build comparison engine")

if __name__ == "__main__":
    main()
