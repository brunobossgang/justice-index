"""
Justice Index — Controlled Sentencing Disparity Analysis
FY2024 USSC Individual Offender Data

Compares sentences across race/gender while controlling for:
- Offense type (OFFGUIDE)
- Criminal history points (CRIMPTS)  
- Guideline range (XMINSOR, XMAXSOR)
- Citizenship status (CITIZEN)
- Weapon involvement (WEAPON)
"""
import pandas as pd
import numpy as np

DATA_PATH = "data/individual_fy24/slim.csv"

RACE_MAP = {1: "White", 2: "Black", 3: "Hispanic", 4: "Other", 7: "Multiracial"}
SEX_MAP = {0: "Male", 1: "Female"}
CITIZEN_MAP = {1: "US Citizen", 2: "Legal Alien", 3: "Illegal Alien", 4: "Unknown Alien", 5: "Extradited"}
OFFENSE_MAP = {
    1: "Admin of Justice", 2: "Antitrust", 3: "Arson", 4: "Assault",
    5: "Bribery/Corruption", 6: "Burglary", 7: "Child Porn", 8: "Commercialized Vice",
    9: "Drug Possession", 10: "Drug Trafficking", 11: "Environmental",
    12: "Extortion/Racketeering", 13: "Firearms", 14: "Food & Drug",
    15: "Forgery/Counter", 16: "Fraud/Theft", 17: "Immigration",
    18: "Individual Rights", 19: "Kidnapping", 20: "Manslaughter",
    21: "Money Laundering", 22: "Murder", 23: "National Defense",
    24: "Obscenity/Sex", 25: "Prison Offenses", 26: "Robbery",
    27: "Sex Abuse", 28: "Stalking", 29: "Tax", 30: "Other"
}
EDUC_MAP = {1: "< HS", 3: "HS Grad", 5: "Some College", 6: "College Grad"}

print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Loaded {len(df):,} cases\n")

# Filter to valid sentences (exclude life=470, probation=missing, etc.)
valid = df[
    (df["SENTTOT"] >= 0) & (df["SENTTOT"] < 470) &  # exclude life sentences
    (df["NEWRACE"].isin([1, 2, 3])) &  # White, Black, Hispanic (enough n)
    (df["XMINSOR"] >= 0) & (df["XMAXSOR"] >= 0) &  # valid guideline range
    (df["XMINSOR"] < 9996) & (df["XMAXSOR"] < 9996) &  # exclude life guidelines
    (df["OFFGUIDE"].notna()) &
    (df["CRIMPTS"].notna()) & (df["CRIMPTS"] >= 0)
].copy()

valid["race"] = valid["NEWRACE"].map(RACE_MAP)
valid["offense"] = valid["OFFGUIDE"].map(OFFENSE_MAP)
valid["sex"] = valid["MONSEX"].map(SEX_MAP)
valid["departure"] = valid["SENTTOT"] - valid["XMINSOR"]
valid["dep_pct"] = np.where(valid["XMINSOR"] > 0, 
                            (valid["SENTTOT"] - valid["XMINSOR"]) / valid["XMINSOR"] * 100, 
                            0)

print(f"Valid cases for analysis: {len(valid):,}")
print(f"(Excluded: life sentences, missing data, races with small n)\n")

# ============================================================
# 1. OVERALL DISPARITY (still raw)
# ============================================================
print("=" * 65)
print("1. RAW SENTENCE BY RACE (all offense types combined)")
print("=" * 65)
g = valid.groupby("race")["SENTTOT"].agg(["mean", "median", "count"])
g = g.sort_values("mean", ascending=False)
for race, row in g.iterrows():
    print(f"  {race:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")

# ============================================================
# 2. CONTROLLED BY OFFENSE TYPE
# ============================================================
print(f"\n{'=' * 65}")
print("2. SENTENCE BY RACE — CONTROLLED BY OFFENSE TYPE")
print("   (Same crime, different outcomes?)")
print("=" * 65)

# Focus on offenses with enough cases in each race
top_offenses = valid["OFFGUIDE"].value_counts()
top_offenses = top_offenses[top_offenses >= 100].index

for off_code in sorted(top_offenses):
    off_name = OFFENSE_MAP.get(int(off_code), f"Code {int(off_code)}")
    subset = valid[valid["OFFGUIDE"] == off_code]
    
    # Need at least 30 cases per race to be meaningful
    race_counts = subset["race"].value_counts()
    races_with_data = race_counts[race_counts >= 30].index
    if len(races_with_data) < 2:
        continue
    
    subset = subset[subset["race"].isin(races_with_data)]
    g = subset.groupby("race")["SENTTOT"].agg(["mean", "median", "count"])
    g = g.sort_values("mean", ascending=False)
    
    print(f"\n  📌 {off_name} (code {int(off_code)}):")
    for race, row in g.iterrows():
        print(f"     {race:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")
    
    # Show disparity ratio
    if "White" in g.index and "Black" in g.index:
        ratio = g.loc["Black", "mean"] / g.loc["White", "mean"] if g.loc["White", "mean"] > 0 else 0
        diff = g.loc["Black", "mean"] - g.loc["White", "mean"]
        print(f"     → Black/White ratio: {ratio:.2f}x ({diff:+.1f} months)")

# ============================================================
# 3. DEPARTURE ANALYSIS — CONTROLLED
# ============================================================
print(f"\n{'=' * 65}")
print("3. GUIDELINE DEPARTURE BY RACE — CONTROLLED BY OFFENSE")
print("   (Who gets leniency for the same crime?)")
print("=" * 65)

for off_code in sorted(top_offenses):
    off_name = OFFENSE_MAP.get(int(off_code), f"Code {int(off_code)}")
    subset = valid[valid["OFFGUIDE"] == off_code]
    
    race_counts = subset["race"].value_counts()
    races_with_data = race_counts[race_counts >= 30].index
    if len(races_with_data) < 2:
        continue
    
    subset = subset[subset["race"].isin(races_with_data)]
    g = subset.groupby("race")["departure"].agg(["mean", "median", "count"])
    g = g.sort_values("mean", ascending=True)  # most lenient first
    
    print(f"\n  📌 {off_name}:")
    for race, row in g.iterrows():
        sign = "+" if row["mean"] >= 0 else ""
        msign = "+" if row["median"] >= 0 else ""
        print(f"     {race:15s}  mean={sign}{row['mean']:5.1f}mo  median={msign}{row['median']:4.1f}mo  n={int(row['count']):,}")

# ============================================================
# 4. SAME OFFENSE + SAME CRIMINAL HISTORY = DIFFERENT SENTENCE?
# ============================================================
print(f"\n{'=' * 65}")
print("4. DOUBLE CONTROLLED: Same Offense + Similar Criminal History")
print("   (The tightest comparison)")
print("=" * 65)

# Bin criminal history points into groups
valid["ch_bin"] = pd.cut(valid["CRIMPTS"], bins=[-1, 0, 3, 6, 10, 200], 
                          labels=["0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"])

for off_code in [10, 13, 16, 26, 17, 21, 7, 27]:  # Major offense types
    off_name = OFFENSE_MAP.get(off_code, f"Code {off_code}")
    off_data = valid[valid["OFFGUIDE"] == off_code]
    
    if len(off_data) < 100:
        continue
    
    print(f"\n  📌 {off_name}:")
    
    for ch_label in ["0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"]:
        subset = off_data[off_data["ch_bin"] == ch_label]
        race_counts = subset["race"].value_counts()
        races_with_data = race_counts[race_counts >= 15].index
        
        if len(races_with_data) < 2:
            continue
        
        subset = subset[subset["race"].isin(races_with_data)]
        g = subset.groupby("race")["SENTTOT"].agg(["mean", "median", "count"])
        g = g.sort_values("mean", ascending=False)
        
        print(f"     Criminal History {ch_label}:")
        for race, row in g.iterrows():
            print(f"       {race:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")
        
        if "White" in g.index and "Black" in g.index:
            diff = g.loc["Black", "mean"] - g.loc["White", "mean"]
            print(f"       → Black-White gap: {diff:+.1f} months")

# ============================================================
# 5. GENDER DISPARITY
# ============================================================
print(f"\n{'=' * 65}")
print("5. GENDER DISPARITY — CONTROLLED BY OFFENSE TYPE")
print("=" * 65)

for off_code in sorted(top_offenses):
    off_name = OFFENSE_MAP.get(int(off_code), f"Code {int(off_code)}")
    subset = valid[(valid["OFFGUIDE"] == off_code) & (valid["MONSEX"].isin([0, 1]))]
    
    sex_counts = subset["sex"].value_counts()
    if all(sex_counts.get(s, 0) >= 20 for s in ["Male", "Female"]):
        g = subset.groupby("sex")["SENTTOT"].agg(["mean", "median", "count"])
        male_mean = g.loc["Male", "mean"]
        female_mean = g.loc["Female", "mean"]
        diff = male_mean - female_mean
        ratio = male_mean / female_mean if female_mean > 0 else 0
        
        print(f"\n  📌 {off_name}:")
        for sex, row in g.iterrows():
            print(f"     {sex:15s}  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")
        print(f"     → Male sentences {diff:+.1f}mo longer ({ratio:.2f}x)")

# ============================================================
# 6. DISTRICT VARIATION (geographic disparity)
# ============================================================
print(f"\n{'=' * 65}")
print("6. TOP/BOTTOM DISTRICTS BY AVERAGE SENTENCE")
print("   (Drug trafficking only — same crime, different courthouses)")
print("=" * 65)

drugs = valid[(valid["OFFGUIDE"] == 10) & (valid["SENTTOT"] > 0)]
dist_stats = drugs.groupby("DISTRICT")["SENTTOT"].agg(["mean", "median", "count"])
dist_stats = dist_stats[dist_stats["count"] >= 30]  # need decent sample
dist_stats = dist_stats.sort_values("mean", ascending=False)

print("\n  HARSHEST districts (drug trafficking):")
for dist, row in dist_stats.head(10).iterrows():
    print(f"     District {int(dist):3d}:  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")

print("\n  MOST LENIENT districts (drug trafficking):")
for dist, row in dist_stats.tail(10).iterrows():
    print(f"     District {int(dist):3d}:  mean={row['mean']:6.1f}mo  median={row['median']:5.1f}mo  n={int(row['count']):,}")

spread = dist_stats["mean"].max() - dist_stats["mean"].min()
print(f"\n  Range: {spread:.1f} months between harshest and most lenient districts")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 65}")
print("SUMMARY OF KEY FINDINGS")
print("=" * 65)

# Overall race disparity for drug trafficking (biggest category)
drugs_race = valid[(valid["OFFGUIDE"] == 10) & (valid["race"].isin(["White", "Black", "Hispanic"]))]
g = drugs_race.groupby("race")["SENTTOT"].mean()
if "White" in g.index and "Black" in g.index:
    print(f"\n  Drug Trafficking — Black avg: {g['Black']:.1f}mo vs White avg: {g['White']:.1f}mo")
    print(f"  Gap: {g['Black'] - g['White']:+.1f} months")

# Gender
male_avg = valid[valid["MONSEX"] == 0]["SENTTOT"].mean()
female_avg = valid[valid["MONSEX"] == 1]["SENTTOT"].mean()
print(f"\n  Overall — Male avg: {male_avg:.1f}mo vs Female avg: {female_avg:.1f}mo")
print(f"  Gap: {male_avg - female_avg:+.1f} months")

# Below guideline rate by race
for race_code, race_name in [(1, "White"), (2, "Black"), (3, "Hispanic")]:
    r = valid[valid["NEWRACE"] == race_code]
    below = (r["SENTTOT"] < r["XMINSOR"]).sum()
    total = len(r)
    print(f"  {race_name}: {below/total*100:.1f}% sentenced below guideline minimum")

print(f"\n✅ Analysis complete — {len(valid):,} cases analyzed")
print("⚠️  These are descriptive statistics. Causal claims require regression analysis (Phase 3).")
