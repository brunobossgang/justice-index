"""
Justice Index — USSC FY2024 Data Explorer (lightweight)
Only loads the columns we need to avoid choking on 27k cols.
"""
import pandas as pd

DATA_PATH = "data/individual_fy24/opafy24nid.csv"

# Only the columns we care about
COLS = [
    "DISTRICT", "OFFGUIDE", "SENTTOT", "SENTIMP",
    "XMINSOR", "XMAXSOR", "NEWRACE", "MONSEX", "AGE",
    "CITIZEN", "NEWEDUC", "CRIMHIST", "CRIMPTS",
    "WEAPON", "BOOTEFCT",
]

print("Loading selected columns from FY2024 data...")

# First check which columns exist
headers = pd.read_csv(DATA_PATH, nrows=0).columns.tolist()
available = [c for c in COLS if c in headers]
missing = [c for c in COLS if c not in headers]

print(f"Found {len(available)}/{len(COLS)} target columns")
if missing:
    print(f"Missing: {missing}")

df = pd.read_csv(DATA_PATH, usecols=available, low_memory=False)
print(f"Loaded {len(df):,} cases\n")

# --- Sentence stats ---
if "SENTTOT" in df.columns:
    s = df["SENTTOT"].dropna()
    s = s[(s >= 0) & (s < 9000)]  # filter out special codes
    print(f"SENTENCES (months):")
    print(f"  Mean: {s.mean():.1f}  Median: {s.median():.1f}  Max: {s.max():.0f}  Std: {s.std():.1f}\n")

# --- Race ---
race_map = {1: "White", 2: "Black", 3: "Hispanic", 4: "Other", 7: "Multiracial"}
if "NEWRACE" in df.columns:
    print("RACE DISTRIBUTION:")
    rc = df["NEWRACE"].value_counts().sort_index()
    tot = rc.sum()
    for code, n in rc.items():
        label = race_map.get(int(code), f"Code {code}")
        print(f"  {label:15s} {n:>7,}  ({n/tot*100:.1f}%)")
    print()

# --- Sex ---
if "MONSEX" in df.columns:
    print("SEX DISTRIBUTION:")
    sex_map = {0: "Male", 1: "Female"}
    sc = df["MONSEX"].value_counts().sort_index()
    tot = sc.sum()
    for code, n in sc.items():
        label = sex_map.get(int(code), f"Code {code}")
        print(f"  {label:15s} {n:>7,}  ({n/tot*100:.1f}%)")
    print()

# --- Criminal History ---
if "CRIMHIST" in df.columns:
    print("CRIMINAL HISTORY CATEGORY:")
    ch = df["CRIMHIST"].value_counts().sort_index()
    for code, n in ch.items():
        if 1 <= code <= 6:
            print(f"  Cat {int(code)}: {n:>7,}")
    print()

# --- Top offenses ---
if "OFFGUIDE" in df.columns:
    print("TOP 10 OFFENSE GUIDELINES:")
    for code, n in df["OFFGUIDE"].value_counts().head(10).items():
        print(f"  {code}: {n:,}")
    print()

# --- RAW sentence by race ---
if "SENTTOT" in df.columns and "NEWRACE" in df.columns:
    print("=" * 55)
    print("RAW AVERAGE SENTENCE BY RACE (no controls)")
    print("=" * 55)
    v = df[(df["SENTTOT"] >= 0) & (df["SENTTOT"] < 9000) & (df["NEWRACE"].isin(race_map))].copy()
    v["race"] = v["NEWRACE"].map(race_map)
    g = v.groupby("race")["SENTTOT"].agg(["mean", "median", "count"])
    g = g.sort_values("mean", ascending=False)
    for race, row in g.iterrows():
        print(f"  {race:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")
    print()

# --- Guideline range vs actual ---
if all(c in df.columns for c in ["SENTTOT", "XMINSOR", "XMAXSOR"]):
    print("=" * 55)
    print("GUIDELINE RANGE vs ACTUAL SENTENCE")
    print("=" * 55)
    v = df[(df["SENTTOT"] >= 0) & (df["SENTTOT"] < 9000) & 
           (df["XMINSOR"] >= 0) & (df["XMAXSOR"] >= 0)].copy()
    below = (v["SENTTOT"] < v["XMINSOR"]).sum()
    within = ((v["SENTTOT"] >= v["XMINSOR"]) & (v["SENTTOT"] <= v["XMAXSOR"])).sum()
    above = (v["SENTTOT"] > v["XMAXSOR"]).sum()
    t = len(v)
    print(f"  Below range:  {below:>6,} ({below/t*100:.1f}%)")
    print(f"  Within range: {within:>6,} ({within/t*100:.1f}%)")
    print(f"  Above range:  {above:>6,} ({above/t*100:.1f}%)")
    
    v["dep"] = v["SENTTOT"] - v["XMINSOR"]
    print(f"  Mean departure from min: {v['dep'].mean():+.1f} months\n")

# --- Departure by race ---
if all(c in df.columns for c in ["SENTTOT", "XMINSOR", "NEWRACE"]):
    print("=" * 55)
    print("DEPARTURE FROM GUIDELINE MIN — BY RACE")
    print("=" * 55)
    v = df[(df["SENTTOT"] >= 0) & (df["SENTTOT"] < 9000) & 
           (df["XMINSOR"] >= 0) & (df["NEWRACE"].isin(race_map))].copy()
    v["dep"] = v["SENTTOT"] - v["XMINSOR"]
    v["race"] = v["NEWRACE"].map(race_map)
    g = v.groupby("race")["dep"].agg(["mean", "median", "count"])
    g = g.sort_values("mean", ascending=False)
    for race, row in g.iterrows():
        print(f"  {race:15s}  mean={row['mean']:+6.1f}mo  median={row['median']:+5.1f}mo  n={int(row['count']):,}")
    print("  (+ = above guideline min, - = below)")

print("\n✅ Exploration complete!")
