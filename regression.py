"""
Justice Index — Phase 3: Regression Analysis
Answers: After controlling for legal factors, does race/gender still predict sentence length?

Model: OLS regression
  SENTTOT ~ race + sex + age + criminal_history + offense_type + guideline_min + citizenship + education + weapon

This isolates the independent effect of race on sentencing.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col

DATA_PATH = "data/individual_fy24/slim.csv"

RACE_MAP = {1: "White", 2: "Black", 3: "Hispanic"}
SEX_MAP = {0: "Male", 1: "Female"}
OFFENSE_MAP = {
    1: "Admin of Justice", 4: "Assault", 5: "Bribery", 7: "Child Porn",
    10: "Drug Trafficking", 13: "Firearms", 16: "Fraud/Theft",
    17: "Immigration", 21: "Money Laundering", 22: "Murder",
    26: "Robbery", 27: "Sex Abuse", 30: "Other"
}

print("Loading data...")
df = pd.read_csv(DATA_PATH, low_memory=False)

# Filter to clean cases
valid = df[
    (df["SENTTOT"] >= 0) & (df["SENTTOT"] < 470) &  # exclude life
    (df["NEWRACE"].isin([1, 2, 3])) &
    (df["XMINSOR"] >= 0) & (df["XMINSOR"] < 9996) &
    (df["XMAXSOR"] >= 0) & (df["XMAXSOR"] < 9996) &
    (df["OFFGUIDE"].notna()) &
    (df["CRIMPTS"].notna()) & (df["CRIMPTS"] >= 0) &
    (df["AGE"].notna()) & (df["AGE"] > 0) &
    (df["MONSEX"].isin([0, 1]))
].copy()

print(f"Valid cases: {len(valid):,}\n")

# ============================================================
# MODEL 1: ALL OFFENSES — FULL CONTROLS
# ============================================================
print("=" * 70)
print("MODEL 1: OLS REGRESSION — ALL OFFENSES COMBINED")
print("  DV: Sentence length (months)")
print("  Controls: offense type, guideline min, crim history, age, sex,")
print("            citizenship, education, weapon")
print("=" * 70)

# Create dummies
valid["is_black"] = (valid["NEWRACE"] == 2).astype(int)
valid["is_hispanic"] = (valid["NEWRACE"] == 3).astype(int)
valid["is_female"] = (valid["MONSEX"] == 1).astype(int)

# Offense dummies (reference = Drug Trafficking as largest category)
for code in [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]:
    valid[f"off_{code}"] = (valid["OFFGUIDE"] == code).astype(int)

# Citizenship dummies (reference = US citizen)
valid["is_illegal_alien"] = (valid["CITIZEN"] == 3).astype(int)
valid["is_legal_alien"] = (valid["CITIZEN"] == 2).astype(int)

# Education dummies (reference = HS grad)
valid["educ_lt_hs"] = (valid["NEWEDUC"] == 1).astype(int)
valid["educ_some_college"] = (valid["NEWEDUC"] == 5).astype(int)
valid["educ_college_grad"] = (valid["NEWEDUC"] == 6).astype(int)

# Weapon
valid["has_weapon"] = (valid["WEAPON"].notna() & (valid["WEAPON"] > 0)).astype(int)

# Build feature matrix
features = [
    "is_black", "is_hispanic", "is_female",
    "XMINSOR", "CRIMPTS", "AGE",
    "is_illegal_alien", "is_legal_alien",
    "educ_lt_hs", "educ_some_college", "educ_college_grad",
    "has_weapon",
] + [f"off_{c}" for c in [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]]

X = valid[features].fillna(0)
X = sm.add_constant(X)
y = valid["SENTTOT"]

model1 = sm.OLS(y, X).fit(cov_type='HC1')  # robust standard errors

print(f"\nR² = {model1.rsquared:.4f}")
print(f"Adjusted R² = {model1.rsquared_adj:.4f}")
print(f"N = {int(model1.nobs):,}")

print("\n--- KEY COEFFICIENTS ---")
print(f"{'Variable':<25s} {'Coef':>8s} {'Std Err':>8s} {'t':>8s} {'P>|t|':>8s} {'Sig':>5s}")
print("-" * 65)

key_vars = ["is_black", "is_hispanic", "is_female", "XMINSOR", "CRIMPTS", "AGE",
            "is_illegal_alien", "has_weapon"]
for var in key_vars:
    coef = model1.params[var]
    se = model1.bse[var]
    t = model1.tvalues[var]
    p = model1.pvalues[var]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {var:<23s} {coef:>8.2f} {se:>8.2f} {t:>8.2f} {p:>8.4f} {sig:>5s}")

print("\nInterpretation:")
b_coef = model1.params["is_black"]
b_p = model1.pvalues["is_black"]
h_coef = model1.params["is_hispanic"]
f_coef = model1.params["is_female"]
print(f"  • Being Black → {b_coef:+.1f} months vs White (p={b_p:.4f})")
print(f"  • Being Hispanic → {h_coef:+.1f} months vs White")
print(f"  • Being Female → {f_coef:+.1f} months vs Male")
print(f"  (After controlling for offense, guidelines, criminal history, age, etc.)")

# ============================================================
# MODEL 2: OFFENSE-SPECIFIC REGRESSIONS
# ============================================================
print(f"\n{'=' * 70}")
print("MODEL 2: OFFENSE-SPECIFIC REGRESSIONS")
print("  (Does the race effect hold within each crime type?)")
print("=" * 70)

results_by_offense = []

for off_code, off_name in sorted(OFFENSE_MAP.items()):
    off_data = valid[valid["OFFGUIDE"] == off_code].copy()
    
    if len(off_data) < 200:
        continue
    
    feats = ["is_black", "is_hispanic", "is_female", "XMINSOR", "CRIMPTS", "AGE",
             "is_illegal_alien", "has_weapon"]
    
    X_off = off_data[feats].fillna(0)
    X_off = sm.add_constant(X_off)
    y_off = off_data["SENTTOT"]
    
    try:
        m = sm.OLS(y_off, X_off).fit(cov_type='HC1')
    except Exception:
        continue
    
    b_coef = m.params.get("is_black", 0)
    b_p = m.pvalues.get("is_black", 1)
    h_coef = m.params.get("is_hispanic", 0)
    h_p = m.pvalues.get("is_hispanic", 1)
    f_coef = m.params.get("is_female", 0)
    f_p = m.pvalues.get("is_female", 1)
    
    b_sig = "***" if b_p < 0.001 else "**" if b_p < 0.01 else "*" if b_p < 0.05 else ""
    h_sig = "***" if h_p < 0.001 else "**" if h_p < 0.01 else "*" if h_p < 0.05 else ""
    f_sig = "***" if f_p < 0.001 else "**" if f_p < 0.01 else "*" if f_p < 0.05 else ""
    
    results_by_offense.append({
        "offense": off_name, "n": int(m.nobs), "r2": m.rsquared,
        "black_coef": b_coef, "black_p": b_p, "black_sig": b_sig,
        "hispanic_coef": h_coef, "hispanic_p": h_p, "hispanic_sig": h_sig,
        "female_coef": f_coef, "female_p": f_p, "female_sig": f_sig,
    })
    
    print(f"\n  📌 {off_name} (n={int(m.nobs):,}, R²={m.rsquared:.3f}):")
    print(f"     Black effect:    {b_coef:+6.1f} months {b_sig} (p={b_p:.4f})")
    print(f"     Hispanic effect: {h_coef:+6.1f} months {h_sig} (p={h_p:.4f})")
    print(f"     Female effect:   {f_coef:+6.1f} months {f_sig} (p={f_p:.4f})")

# ============================================================
# MODEL 3: LOGISTIC REGRESSION — WHO GETS BELOW-GUIDELINE?
# ============================================================
print(f"\n{'=' * 70}")
print("MODEL 3: LOGISTIC REGRESSION — BELOW-GUIDELINE SENTENCES")
print("  (Who is more likely to receive mercy?)")
print("=" * 70)

from statsmodels.discrete.discrete_model import Logit

valid["below_guideline"] = (valid["SENTTOT"] < valid["XMINSOR"]).astype(int)

feats_logit = ["is_black", "is_hispanic", "is_female", "CRIMPTS", "AGE",
               "is_illegal_alien", "has_weapon"]
# Add offense dummies
feats_logit += [f"off_{c}" for c in [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]]

X_logit = valid[feats_logit].fillna(0)
X_logit = sm.add_constant(X_logit)
y_logit = valid["below_guideline"]

logit_model = Logit(y_logit, X_logit).fit(disp=0, cov_type='HC1')

print(f"\nPseudo R² = {logit_model.prsquared:.4f}")
print(f"N = {int(logit_model.nobs):,}")

# Convert to odds ratios
print("\n--- ODDS RATIOS (key variables) ---")
print(f"{'Variable':<25s} {'OR':>8s} {'95% CI':>18s} {'P>|z|':>8s} {'Sig':>5s}")
print("-" * 70)

conf = logit_model.conf_int()
for var in ["is_black", "is_hispanic", "is_female", "CRIMPTS", "AGE", "is_illegal_alien", "has_weapon"]:
    coef = logit_model.params[var]
    p = logit_model.pvalues[var]
    or_val = np.exp(coef)
    ci_lo = np.exp(conf.loc[var, 0])
    ci_hi = np.exp(conf.loc[var, 1])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {var:<23s} {or_val:>8.3f} [{ci_lo:.3f} - {ci_hi:.3f}] {p:>8.4f} {sig:>5s}")

print("\nInterpretation:")
b_or = np.exp(logit_model.params["is_black"])
h_or = np.exp(logit_model.params["is_hispanic"])
f_or = np.exp(logit_model.params["is_female"])
print(f"  • Black defendants are {b_or:.2f}x as likely to get below-guideline sentence vs White")
print(f"    (OR < 1 = LESS likely to receive leniency)")
print(f"  • Hispanic defendants: OR = {h_or:.2f}")
print(f"  • Female defendants: OR = {f_or:.2f}")
print(f"  (After controlling for offense, criminal history, age, citizenship, weapon)")

# ============================================================
# SUMMARY TABLE
# ============================================================
print(f"\n{'=' * 70}")
print("SUMMARY: RACE EFFECT BY OFFENSE (controlled)")
print("  (Positive = longer sentence than White defendants, controlling for")
print("   guideline range, criminal history, age, sex, citizenship, weapon)")
print("=" * 70)

print(f"\n{'Offense':<22s} {'Black Effect':>14s} {'Sig':>4s}  {'Hispanic Effect':>16s} {'Sig':>4s}  {'N':>7s}")
print("-" * 75)
for r in sorted(results_by_offense, key=lambda x: abs(x["black_coef"]), reverse=True):
    print(f"  {r['offense']:<20s} {r['black_coef']:>+10.1f} mo {r['black_sig']:>4s}  {r['hispanic_coef']:>+12.1f} mo {r['hispanic_sig']:>4s}  {r['n']:>7,}")

print(f"\n✅ Regression analysis complete")
print(f"*** p<0.001  ** p<0.01  * p<0.05")
print(f"\n⚠️  Limitations: Cannot control for attorney quality, plea deals,")
print(f"   judge identity, or case-specific circumstances not in USSC data.")
