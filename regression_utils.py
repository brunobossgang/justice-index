import pandas as pd
import numpy as np
import streamlit as st
import statsmodels.api as sm


_OFFENSE_DUMMIES = [1, 4, 5, 7, 13, 16, 17, 21, 22, 26, 27, 30]

def _prepare_features(df, include_offense_dummies=True):
    """Create dummy variables and return X, y with no missing values."""
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
    'Black': 'Black (vs White)',
    'Hispanic': 'Hispanic (vs White)',
    'Female': 'Female (vs Male)',
    'XMINSOR': 'Guideline Minimum',
    'CRIMPTS': 'Criminal History Points',
    'AGE': 'Age',
    'IllegalAlien': 'Non-Citizen (Illegal)',
    'WEAPON': 'Weapon Involved',
}


@st.cache_data
def run_overall_regression(df):
    X, y = _prepare_features(df)
    model = sm.OLS(y, X).fit(cov_type='HC1')
    coefficients = []
    for var in ['Black', 'Hispanic', 'Female', 'XMINSOR', 'CRIMPTS', 'AGE', 'IllegalAlien', 'WEAPON']:
        coefficients.append({
            'variable': _VAR_NAMES.get(var, var),
            'effect': round(model.params[var], 2),
            'pvalue': round(model.pvalues[var], 6),
            'significant': model.pvalues[var] < 0.05,
        })
    return {
        'r_squared': round(model.rsquared, 4),
        'n_obs': int(model.nobs),
        'coefficients': coefficients,
    }


@st.cache_data
def run_yearly_regression(df):
    rows = []
    for year in sorted(df['Year'].unique()):
        sub = df[df['Year'] == year]
        try:
            X, y = _prepare_features(sub)
            if len(y) < 50:
                continue
            model = sm.OLS(y, X).fit(cov_type='HC1')
            rows.append({
                'Year': year,
                'Black_Effect': round(model.params['Black'], 2),
                'Black_pvalue': round(model.pvalues['Black'], 6),
                'Female_Effect': round(model.params['Female'], 2),
                'Hispanic_Effect': round(model.params['Hispanic'], 2),
                'R2': round(model.rsquared, 4),
                'N': int(model.nobs),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


@st.cache_data
def run_offense_regressions(df, min_cases=200):
    rows = []
    for offense in df['Offense'].unique():
        sub = df[df['Offense'] == offense]
        if len(sub) < min_cases:
            continue
        try:
            X, y = _prepare_features(sub, include_offense_dummies=False)
            if len(y) < min_cases:
                continue
            model = sm.OLS(y, X).fit(cov_type='HC1')
            p = model.pvalues['Black']
            stars = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            rows.append({
                'Offense': offense,
                'Black_Effect': round(model.params['Black'], 2),
                'Black_pvalue': round(p, 6),
                'Significance_Stars': stars,
                'N': int(model.nobs),
            })
        except Exception:
            continue
    result = pd.DataFrame(rows).sort_values('Black_Effect', ascending=False).reset_index(drop=True)
    return result


@st.cache_data
def run_leniency_regression(df):
    data = df[['Below Guideline', 'NEWRACE', 'MONSEX', 'AGE', 'XMINSOR', 'CRIMPTS', 'CITIZEN', 'WEAPON']].copy()
    data['Black'] = (data['NEWRACE'] == 2).astype(int)
    data['Hispanic'] = (data['NEWRACE'] == 3).astype(int)
    data['Female'] = (data['MONSEX'] == 1).astype(int)
    data['IllegalAlien'] = (data['CITIZEN'] == 3).astype(int)
    data['Below_Guideline'] = data['Below Guideline'].astype(int)
    data = data.dropna()
    predictors = ['Black', 'Hispanic', 'Female', 'XMINSOR', 'CRIMPTS', 'AGE', 'IllegalAlien', 'WEAPON']
    X = sm.add_constant(data[predictors])
    y = data['Below_Guideline']
    model = sm.Logit(y, X).fit(disp=0)
    results = []
    for var in predictors:
        results.append({
            'variable': _VAR_NAMES.get(var, var),
            'odds_ratio': round(np.exp(model.params[var]), 4),
            'pvalue': round(model.pvalues[var], 6),
            'significant': model.pvalues[var] < 0.05,
        })
    return results


@st.cache_data
def get_fitted_model(df):
    """Return the fitted OLS model params for prediction use."""
    X, y = _prepare_features(df)
    model = sm.OLS(y, X).fit(cov_type='HC1')
    return dict(model.params), list(X.columns)


@st.cache_data
def predict_sentence(df, offense_code, age, crim_pts, guideline_min, is_female, is_citizen, has_weapon):
    """
    Predict sentence for White, Black, and Hispanic defendants with given characteristics.
    Returns dict: {race: predicted_months}
    """
    params, col_names = get_fitted_model(df)

    base = {col: 0.0 for col in col_names}
    base['const'] = 1.0
    base['AGE'] = age
    base['CRIMPTS'] = crim_pts
    base['XMINSOR'] = guideline_min
    base['Female'] = 1 if is_female else 0
    base['IllegalAlien'] = 0 if is_citizen else 1
    base['WEAPON'] = 1 if has_weapon else 0

    # Set offense dummy
    off_col = f'off_{offense_code}'
    if off_col in base:
        base[off_col] = 1

    results = {}
    for race, black_val, hisp_val in [("White", 0, 0), ("Black", 1, 0), ("Hispanic", 0, 1)]:
        row = base.copy()
        row['Black'] = black_val
        row['Hispanic'] = hisp_val
        pred = sum(row[col] * params.get(col, 0) for col in col_names)
        results[race] = max(0, round(pred, 1))

    return results


@st.cache_data
def compute_human_cost(df):
    """
    Compute aggregate human cost of the racial gap.
    Returns dict with total extra years, by offense, etc.
    """
    # Get per-offense Black effect
    offense_effects = run_offense_regressions(df)

    total_extra_months = 0
    offense_costs = []

    for _, row in offense_effects.iterrows():
        if row['Black_Effect'] <= 0:
            continue
        # Count Black defendants for this offense
        off_data = df[(df['Offense'] == row['Offense']) & (df['Race'] == 'Black')]
        n_black = len(off_data)
        extra = row['Black_Effect'] * n_black
        total_extra_months += extra
        offense_costs.append({
            'Offense': row['Offense'],
            'Black_Effect_Mo': row['Black_Effect'],
            'N_Black': n_black,
            'Extra_Months': round(extra),
            'Extra_Years': round(extra / 12, 1),
        })

    return {
        'total_extra_months': round(total_extra_months),
        'total_extra_years': round(total_extra_months / 12),
        'by_offense': pd.DataFrame(offense_costs).sort_values('Extra_Months', ascending=False),
    }
