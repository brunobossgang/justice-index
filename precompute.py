"""
Precompute all regression results and heavy aggregations → data/precomputed.json
Run locally before deploying to Render (which has limited RAM).
"""
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm

# ── same helpers from regression_utils.py ──
_OFFENSE_DUMMIES = [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]

def _prepare_features(df, include_offense_dummies=True):
    cols = ['SENTTOT', 'NEWRACE', 'MONSEX', 'AGE', 'XMINSOR', 'CRIMPTS', 'CITIZEN', 'WEAPON']
    if include_offense_dummies:
        cols.append('OFFGUIDE')
    data = df[cols].copy()
    data['Black'] = (data['NEWRACE'] == 2).astype(int)
    data['Hispanic'] = (data['NEWRACE'] == 3).astype(int)
    data['Female'] = (data['MONSEX'] == 1).astype(int)
    data['IllegalAlien'] = (data['CITIZEN'] == 3).astype(int)
    data = data.dropna()
    predictors = ['Black', 'Hispanic', 'Female', 'XMINSOR', 'CRIMPTS', 'AGE', 'IllegalAlien', 'WEAPON']
    if include_offense_dummies:
        for code in _OFFENSE_DUMMIES:
            col = f'off_{code}'
            data[col] = (data['OFFGUIDE'] == code).astype(int)
            predictors.append(col)
    X = sm.add_constant(data[predictors])
    y = data['SENTTOT']
    return X, y

_VAR_NAMES = {
    'Black': 'Black (vs White)', 'Hispanic': 'Hispanic (vs White)',
    'Female': 'Female (vs Male)', 'XMINSOR': 'Guideline Minimum',
    'CRIMPTS': 'Criminal History Points', 'AGE': 'Age',
    'IllegalAlien': 'Non-Citizen (Illegal)', 'WEAPON': 'Weapon Involved',
}

OFFENSE_MAP = {
    1: "Admin of Justice", 2: "Antitrust", 3: "Arson",
    4: "Assault", 5: "Bribery/Corruption", 6: "Burglary/Trespass",
    7: "Child Pornography", 8: "Commercialized Vice",
    9: "Drug Possession", 10: "Drug Trafficking",
    11: "Environmental", 12: "Extortion/Racketeering", 13: "Firearms",
    14: "Food & Drug", 15: "Forgery/Counterfeiting", 16: "Fraud/Theft/Embezzlement",
    17: "Immigration", 18: "Individual Rights", 19: "Kidnapping",
    20: "Manslaughter", 21: "Money Laundering", 22: "Murder",
    23: "National Defense", 24: "Obscenity/Sex Offenses", 25: "Prison Offenses",
    26: "Robbery", 27: "Sexual Abuse", 28: "Stalking/Harassment",
    29: "Tax", 30: "Other"
}

def main():
    print("Loading data...")
    raw = pd.read_csv("data/combined_fy19_fy24.csv", low_memory=False)
    df = raw[
        (raw["SENTTOT"] >= 0) & (raw["SENTTOT"] < 470) &
        (raw["NEWRACE"].isin([1, 2, 3])) &
        (raw["XMINSOR"] >= 0) & (raw["XMINSOR"] < 9996) &
        (raw["OFFGUIDE"].notna()) &
        (raw["CRIMPTS"].notna()) & (raw["CRIMPTS"] >= 0) &
        (raw["AGE"].notna()) & (raw["AGE"] > 0)
    ].copy()
    for col in ["NEWRACE", "MONSEX", "CRIMHIST", "WEAPON", "CITIZEN", "NEWEDUC", "INOUT", "PRESENT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            mask = df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].astype(int)

    df["Race"] = df["NEWRACE"].map({1: "White", 2: "Black", 3: "Hispanic"})
    df["Offense"] = df["OFFGUIDE"].map(OFFENSE_MAP).fillna("Other")
    df["Year"] = df["FISCAL_YEAR"].astype(int)
    df["Below Guideline"] = df["SENTTOT"] < df["XMINSOR"]

    results = {}

    # 1) Overall regression
    print("Running overall regression...")
    X, y = _prepare_features(df)
    model = sm.OLS(y, X).fit(cov_type='HC1')
    coefficients = []
    for var in ['Black', 'Hispanic', 'Female', 'XMINSOR', 'CRIMPTS', 'AGE', 'IllegalAlien', 'WEAPON']:
        coefficients.append({
            'variable': _VAR_NAMES.get(var, var),
            'effect': round(model.params[var], 2),
            'pvalue': round(float(model.pvalues[var]), 6),
            'significant': bool(model.pvalues[var] < 0.05),
        })
    results['overall'] = {
        'r_squared': round(model.rsquared, 4),
        'n_obs': int(model.nobs),
        'coefficients': coefficients,
    }

    # 2) Fitted model params (for predict_sentence)
    print("Saving model params...")
    results['model_params'] = {k: round(float(v), 6) for k, v in model.params.items()}
    results['model_columns'] = list(X.columns)

    # 3) Yearly regression
    print("Running yearly regressions...")
    yearly_rows = []
    for year in sorted(df['Year'].unique()):
        sub = df[df['Year'] == year]
        try:
            X2, y2 = _prepare_features(sub)
            if len(y2) < 50:
                continue
            m = sm.OLS(y2, X2).fit(cov_type='HC1')
            yearly_rows.append({
                'Year': int(year),
                'Black_Effect': round(float(m.params['Black']), 2),
                'Black_pvalue': round(float(m.pvalues['Black']), 6),
                'Female_Effect': round(float(m.params['Female']), 2),
                'Hispanic_Effect': round(float(m.params['Hispanic']), 2),
                'R2': round(float(m.rsquared), 4),
                'N': int(m.nobs),
            })
        except Exception as e:
            print(f"  Year {year} failed: {e}")
    results['yearly'] = yearly_rows

    # 4) By-offense regressions
    print("Running offense regressions...")
    offense_rows = []
    for offense in df['Offense'].unique():
        sub = df[df['Offense'] == offense]
        if len(sub) < 200:
            continue
        try:
            X2, y2 = _prepare_features(sub, include_offense_dummies=False)
            if len(y2) < 200:
                continue
            m = sm.OLS(y2, X2).fit(cov_type='HC1')
            p = float(m.pvalues['Black'])
            stars = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            offense_rows.append({
                'Offense': offense,
                'Black_Effect': round(float(m.params['Black']), 2),
                'Black_pvalue': round(p, 6),
                'Significance_Stars': stars,
                'N': int(m.nobs),
            })
        except Exception as e:
            print(f"  Offense {offense} failed: {e}")
    offense_rows.sort(key=lambda r: r['Black_Effect'], reverse=True)
    results['by_offense'] = offense_rows

    # 5) Leniency regression
    print("Running leniency regression...")
    data_l = df[['Below Guideline', 'NEWRACE', 'MONSEX', 'AGE', 'XMINSOR', 'CRIMPTS', 'CITIZEN', 'WEAPON']].copy()
    data_l['Black'] = (data_l['NEWRACE'] == 2).astype(int)
    data_l['Hispanic'] = (data_l['NEWRACE'] == 3).astype(int)
    data_l['Female'] = (data_l['MONSEX'] == 1).astype(int)
    data_l['IllegalAlien'] = (data_l['CITIZEN'] == 3).astype(int)
    data_l['Below_Guideline'] = data_l['Below Guideline'].astype(int)
    data_l = data_l.dropna()
    predictors = ['Black', 'Hispanic', 'Female', 'XMINSOR', 'CRIMPTS', 'AGE', 'IllegalAlien', 'WEAPON']
    X_l = sm.add_constant(data_l[predictors])
    y_l = data_l['Below_Guideline']
    m_l = sm.Logit(y_l, X_l).fit(disp=0)
    leniency_results = []
    for var in predictors:
        leniency_results.append({
            'variable': _VAR_NAMES.get(var, var),
            'odds_ratio': round(float(np.exp(m_l.params[var])), 4),
            'pvalue': round(float(m_l.pvalues[var]), 6),
            'significant': bool(m_l.pvalues[var] < 0.05),
        })
    results['leniency'] = leniency_results

    # 6) Offense trends (Drug Trafficking, Firearms, Robbery)
    print("Running offense trend regressions...")
    offense_trends = {}
    for offense in ["Drug Trafficking", "Firearms", "Robbery"]:
        years_data = []
        for year in sorted(df['Year'].unique()):
            sub = df[(df['Offense'] == offense) & (df['Year'] == year)]
            if len(sub) < 100:
                continue
            try:
                X2, y2 = _prepare_features(sub, include_offense_dummies=False)
                if len(y2) < 50:
                    continue
                m = sm.OLS(y2, X2).fit(cov_type='HC1')
                years_data.append({"Year": int(year), "Effect": round(float(m.params["Black"]), 1)})
            except Exception:
                continue
        offense_trends[offense] = years_data
    results['offense_trends'] = offense_trends

    # 7) Human cost
    print("Computing human cost...")
    total_extra_months = 0
    offense_costs = []
    for row in results['by_offense']:
        if row['Black_Effect'] <= 0:
            continue
        n_black = len(df[(df['Offense'] == row['Offense']) & (df['Race'] == 'Black')])
        extra = row['Black_Effect'] * n_black
        total_extra_months += extra
        offense_costs.append({
            'Offense': row['Offense'],
            'Black_Effect_Mo': row['Black_Effect'],
            'N_Black': n_black,
            'Extra_Months': round(extra),
            'Extra_Years': round(extra / 12, 1),
        })
    offense_costs.sort(key=lambda r: r['Extra_Months'], reverse=True)
    results['human_cost'] = {
        'total_extra_months': round(total_extra_months),
        'total_extra_years': round(total_extra_months / 12),
        'by_offense': offense_costs,
    }

    # Write
    out = "data/precomputed.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Done! Wrote {out} ({len(json.dumps(results))//1024}KB)")

if __name__ == "__main__":
    main()
