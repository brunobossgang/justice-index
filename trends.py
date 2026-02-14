"""
Justice Index — Multi-Year Trend Analysis (FY2019-2024)
Is the racial sentencing gap getting better or worse over time?
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

DATA_PATH = "data/combined_fy19_fy24.csv"
RACE_MAP = {1: "White", 2: "Black", 3: "Hispanic"}
OFFENSE_MAP = {
    4: "Assault", 10: "Drug Trafficking", 13: "Firearms", 
    16: "Fraud/Theft", 17: "Immigration", 21: "Money Laundering",
    26: "Robbery"
}

print("Loading 6 years of data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Total: {len(df):,} cases\n")

# Filter
valid = df[
    (df["SENTTOT"] >= 0) & (df["SENTTOT"] < 470) &
    (df["NEWRACE"].isin([1, 2, 3])) &
    (df["XMINSOR"] >= 0) & (df["XMINSOR"] < 9996) &
    (df["XMAXSOR"] >= 0) & (df["XMAXSOR"] < 9996) &
    (df["OFFGUIDE"].notna()) &
    (df["CRIMPTS"].notna()) & (df["CRIMPTS"] >= 0) &
    (df["MONSEX"].isin([0, 1])) &
    (df["AGE"].notna()) & (df["AGE"] > 0)
].copy()

valid["race"] = valid["NEWRACE"].map(RACE_MAP)
print(f"Valid cases: {len(valid):,}\n")

# ============================================================
# 1. RAW TRENDS — Average sentence by race per year
# ============================================================
print("=" * 65)
print("1. RAW AVERAGE SENTENCE BY RACE — OVER TIME")
print("=" * 65)

pivot = valid.groupby(["FISCAL_YEAR", "race"])["SENTTOT"].agg(["mean", "count"]).unstack("race")
print("\nMean sentence (months):")
print(f"{'Year':<8s} {'White':>10s} {'Black':>10s} {'Hispanic':>10s} {'B-W Gap':>10s}")
print("-" * 55)
for year in sorted(valid["FISCAL_YEAR"].unique()):
    w = pivot.loc[year, ("mean", "White")]
    b = pivot.loc[year, ("mean", "Black")]
    h = pivot.loc[year, ("mean", "Hispanic")]
    gap = b - w
    print(f"  {int(year):<6d} {w:>8.1f}mo {b:>8.1f}mo {h:>8.1f}mo {gap:>+8.1f}mo")

# ============================================================
# 2. CONTROLLED TREND — Regression per year
# ============================================================
print(f"\n{'=' * 65}")
print("2. CONTROLLED BLACK EFFECT — BY YEAR")
print("   (OLS: SENTTOT ~ race + sex + age + offense + guideline + crimhist)")
print("=" * 65)

valid["is_black"] = (valid["NEWRACE"] == 2).astype(int)
valid["is_hispanic"] = (valid["NEWRACE"] == 3).astype(int)
valid["is_female"] = (valid["MONSEX"] == 1).astype(int)
valid["is_illegal_alien"] = (valid["CITIZEN"] == 3).astype(int)

# Offense dummies
for code in [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]:
    valid[f"off_{code}"] = (valid["OFFGUIDE"] == code).astype(int)

off_cols = [f"off_{c}" for c in [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]]

print(f"\n{'Year':<8s} {'Black Effect':>14s} {'p-value':>10s} {'Sig':>5s} {'Female Effect':>15s} {'N':>8s}")
print("-" * 65)

yearly_black_effect = []
yearly_female_effect = []

for year in sorted(valid["FISCAL_YEAR"].unique()):
    ydf = valid[valid["FISCAL_YEAR"] == year]
    
    feats = ["is_black", "is_hispanic", "is_female", "XMINSOR", "CRIMPTS", "AGE", "is_illegal_alien"] + off_cols
    X = ydf[feats].fillna(0)
    X = sm.add_constant(X)
    y = ydf["SENTTOT"]
    
    m = sm.OLS(y, X).fit(cov_type='HC1')
    
    b_coef = m.params["is_black"]
    b_p = m.pvalues["is_black"]
    b_sig = "***" if b_p < 0.001 else "**" if b_p < 0.01 else "*" if b_p < 0.05 else ""
    f_coef = m.params["is_female"]
    
    yearly_black_effect.append({"year": int(year), "effect": b_coef, "p": b_p})
    yearly_female_effect.append({"year": int(year), "effect": f_coef})
    
    print(f"  {int(year):<6d} {b_coef:>+10.1f} mo {b_p:>10.4f} {b_sig:>5s} {f_coef:>+11.1f} mo {int(m.nobs):>8,}")

# ============================================================
# 3. BELOW-GUIDELINE RATE BY RACE — OVER TIME
# ============================================================
print(f"\n{'=' * 65}")
print("3. BELOW-GUIDELINE RATE BY RACE — OVER TIME")
print("   (% sentenced below guideline minimum)")
print("=" * 65)

valid["below"] = (valid["SENTTOT"] < valid["XMINSOR"]).astype(int)

print(f"\n{'Year':<8s} {'White':>10s} {'Black':>10s} {'Hispanic':>10s} {'W-B Gap':>10s}")
print("-" * 55)
for year in sorted(valid["FISCAL_YEAR"].unique()):
    ydf = valid[valid["FISCAL_YEAR"] == year]
    rates = {}
    for rc, rn in RACE_MAP.items():
        r = ydf[ydf["NEWRACE"] == rc]
        rates[rn] = r["below"].mean() * 100
    gap = rates["White"] - rates["Black"]
    print(f"  {int(year):<6d} {rates['White']:>8.1f}% {rates['Black']:>8.1f}% {rates['Hispanic']:>8.1f}% {gap:>+8.1f}pp")

# ============================================================
# 4. OFFENSE-SPECIFIC TRENDS (Drug Trafficking & Firearms)
# ============================================================
for off_code, off_name in [(10, "Drug Trafficking"), (13, "Firearms"), (26, "Robbery")]:
    print(f"\n{'=' * 65}")
    print(f"4. {off_name.upper()} — BLACK EFFECT OVER TIME (controlled)")
    print("=" * 65)
    
    off_data = valid[valid["OFFGUIDE"] == off_code]
    
    print(f"\n{'Year':<8s} {'Black Effect':>14s} {'p-value':>10s} {'Sig':>5s} {'N':>8s}")
    print("-" * 50)
    
    for year in sorted(off_data["FISCAL_YEAR"].unique()):
        ydf = off_data[off_data["FISCAL_YEAR"] == year]
        if len(ydf) < 100:
            continue
        
        feats = ["is_black", "is_hispanic", "is_female", "XMINSOR", "CRIMPTS", "AGE", "is_illegal_alien"]
        X = ydf[feats].fillna(0)
        X = sm.add_constant(X)
        y = ydf["SENTTOT"]
        
        try:
            m = sm.OLS(y, X).fit(cov_type='HC1')
            b_coef = m.params["is_black"]
            b_p = m.pvalues["is_black"]
            b_sig = "***" if b_p < 0.001 else "**" if b_p < 0.01 else "*" if b_p < 0.05 else ""
            print(f"  {int(year):<6d} {b_coef:>+10.1f} mo {b_p:>10.4f} {b_sig:>5s} {int(m.nobs):>8,}")
        except:
            print(f"  {int(year):<6d}  (insufficient data)")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 65}")
print("TREND SUMMARY")
print("=" * 65)

first = yearly_black_effect[0]
last = yearly_black_effect[-1]
print(f"\n  Black penalty (controlled):")
print(f"    FY{first['year']}: {first['effect']:+.1f} months")
print(f"    FY{last['year']}: {last['effect']:+.1f} months")
change = last['effect'] - first['effect']
print(f"    Change: {change:+.1f} months ({'WORSENING' if change > 0 else 'IMPROVING'})")

first_f = yearly_female_effect[0]
last_f = yearly_female_effect[-1]
print(f"\n  Female discount (controlled):")
print(f"    FY{first_f['year']}: {first_f['effect']:+.1f} months")
print(f"    FY{last_f['year']}: {last_f['effect']:+.1f} months")

print(f"\n✅ Trend analysis complete — {len(valid):,} cases across 6 years")
