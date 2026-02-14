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
