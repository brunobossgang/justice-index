"""
Precompute all regression results and descriptive stats → data/precomputed.json
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

from districts import DISTRICT_MAP


def _safe(v):
    """Convert numpy types to JSON-safe Python types."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 4)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if pd.isna(v):
        return None
    return v


def main():
    import os
    print("Loading data...")
    pq = os.path.join(os.path.dirname(__file__), "data", "combined_fy19_fy24.parquet")
    if os.path.exists(pq):
        raw = pd.read_parquet(pq)
    else:
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
    df["Sex"] = df["MONSEX"].map({0: "Male", 1: "Female"})
    df["Offense"] = df["OFFGUIDE"].map(OFFENSE_MAP).fillna("Other")
    df["Year"] = df["FISCAL_YEAR"].astype(int)
    df["Below Guideline"] = df["SENTTOT"] < df["XMINSOR"]
    df["Departure"] = df["SENTTOT"] - df["XMINSOR"]
    df["District Name"] = df["DISTRICT"].astype(int).map(DISTRICT_MAP).fillna(df["DISTRICT"].astype(str))
    df["Crim History"] = pd.cut(df["CRIMPTS"], bins=[-1, 0, 3, 6, 10, 200],
                                 labels=["0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"])

    plea_map = {1: "Plea Deal", 2: "Plea Deal", 3: "Plea Deal",
                5: "Straight Plea", 8: "Trial", 9: "Plea Deal"}
    df["Plea Type"] = df["DSPLEA"].map(plea_map)

    results = {}

    # ════════════════════════════════════════════════════════
    # REGRESSION RESULTS (existing)
    # ════════════════════════════════════════════════════════

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

    # ════════════════════════════════════════════════════════
    # DESCRIPTIVE STATS (new — for all pages)
    # ════════════════════════════════════════════════════════

    # ── Summary stats ──
    print("Computing summary stats...")
    results['summary'] = {
        'total_cases': int(len(df)),
        'year_min': int(df['Year'].min()),
        'year_max': int(df['Year'].max()),
        'years': sorted([int(y) for y in df['Year'].unique()]),
        'all_offenses': sorted(df['Offense'].unique().tolist()),
        'all_districts': sorted([
            {'code': int(code), 'name': name}
            for code, name in sorted(
                df[['DISTRICT', 'District Name']].drop_duplicates().values.tolist(),
                key=lambda x: str(x[1])
            )
            if name and str(name) != 'nan'
        ], key=lambda x: x['name']),
        'crim_history_levels': ["0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"],
        'national_avg_sentence': _safe(df['SENTTOT'].mean()),
        'national_median_sentence': _safe(df['SENTTOT'].median()),
        'national_below_guideline': _safe(df['Below Guideline'].mean() * 100),
        'national_race_avg': {
            race: _safe(df[df['Race'] == race]['SENTTOT'].mean())
            for race in ['White', 'Black', 'Hispanic']
        },
        'n_black': int(len(df[df['Race'] == 'Black'])),
    }

    # ── Page: Same Crime Different Time ──
    # Precompute offense × race × crim_history stats, with yearly breakdown
    print("Computing Same Crime Different Time stats...")
    same_crime = {}
    ch_levels = ["All levels", "0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"]

    for offense in df['Offense'].unique():
        off_data = df[df['Offense'] == offense]
        same_crime[offense] = {}

        for ch in ch_levels:
            if ch == "All levels":
                subset = off_data
            else:
                subset = off_data[off_data['Crim History'] == ch]

            # Overall stats by race (all years combined)
            race_stats = {}
            below_rates = {}
            for race in ['White', 'Black', 'Hispanic']:
                rdata = subset[subset['Race'] == race]['SENTTOT']
                if len(rdata) == 0:
                    continue
                race_stats[race] = {
                    'mean': _safe(rdata.mean()),
                    'median': _safe(rdata.median()),
                    'count': int(len(rdata)),
                    'std': _safe(rdata.std()),
                }
                br = subset[subset['Race'] == race]['Below Guideline'].mean()
                below_rates[race] = _safe(br * 100) if not pd.isna(br) else None

            # Yearly breakdown for year-range filtering
            yearly = {}
            for year in sorted(subset['Year'].unique()):
                ysub = subset[subset['Year'] == year]
                yearly[str(int(year))] = {}
                for race in ['White', 'Black', 'Hispanic']:
                    rdata = ysub[ysub['Race'] == race]['SENTTOT']
                    if len(rdata) == 0:
                        continue
                    yearly[str(int(year))][race] = {
                        'mean': _safe(rdata.mean()),
                        'median': _safe(rdata.median()),
                        'count': int(len(rdata)),
                        'std': _safe(rdata.std()),
                        'below_rate': _safe(ysub[ysub['Race'] == race]['Below Guideline'].mean() * 100),
                    }

            same_crime[offense][ch] = {
                'race_stats': race_stats,
                'below_rates': below_rates,
                'yearly': yearly,
                'total_count': int(len(subset)),
            }

    results['same_crime'] = same_crime

    # ── Page: The Lottery ──
    print("Computing Lottery (district) stats...")
    lottery = {}
    for offense in ["Drug Trafficking", "Firearms", "Fraud/Theft/Embezzlement", "Robbery"]:
        geo = df[df['Offense'] == offense]

        # District-level stats
        dist_list = []
        for (dist_code, dist_name), grp in geo.groupby(['DISTRICT', 'District Name']):
            if len(grp) < 10:
                continue
            dist_list.append({
                'district_code': int(dist_code),
                'district_name': str(dist_name),
                'avg': _safe(grp['SENTTOT'].mean()),
                'med': _safe(grp['SENTTOT'].median()),
                'n': int(len(grp)),
                'below': _safe(grp['Below Guideline'].mean() * 100),
            })
        dist_list.sort(key=lambda x: x['avg'], reverse=True)

        # Black-White gap by district
        bw_gaps = []
        race_dist = geo.groupby(['DISTRICT', 'District Name', 'Race'])['SENTTOT'].agg(['mean', 'count']).reset_index()
        for (dist_code, dist_name), grp in race_dist.groupby(['DISTRICT', 'District Name']):
            b_rows = grp[grp['Race'] == 'Black']
            w_rows = grp[grp['Race'] == 'White']
            if len(b_rows) == 0 or len(w_rows) == 0:
                continue
            b_mean, b_count = b_rows.iloc[0]['mean'], int(b_rows.iloc[0]['count'])
            w_mean, w_count = w_rows.iloc[0]['mean'], int(w_rows.iloc[0]['count'])
            if b_count < 20 or w_count < 20:
                continue
            bw_gaps.append({
                'district_code': int(dist_code),
                'district_name': str(dist_name),
                'black_mean': _safe(b_mean),
                'white_mean': _safe(w_mean),
                'black_count': b_count,
                'white_count': w_count,
                'gap': _safe(b_mean - w_mean),
            })
        bw_gaps.sort(key=lambda x: x['gap'], reverse=True)

        lottery[offense] = {
            'districts': dist_list,
            'bw_gaps': bw_gaps,
        }

    results['lottery'] = lottery

    # ── Page: Your District ──
    print("Computing Your District stats...")
    # National stats for comparison
    nat_avg = _safe(df['SENTTOT'].mean())
    nat_median = _safe(df['SENTTOT'].median())
    nat_below = _safe(df['Below Guideline'].mean() * 100)
    nat_race_avg = {
        race: _safe(df[df['Race'] == race]['SENTTOT'].mean())
        for race in ['White', 'Black', 'Hispanic']
    }
    n_districts = df['DISTRICT'].nunique()

    # All-district ranking
    all_dist_rank = df.groupby('District Name')['SENTTOT'].agg(['mean', 'count']).reset_index()
    all_dist_rank = all_dist_rank[all_dist_rank['count'] >= 50].sort_values('mean', ascending=False).reset_index(drop=True)
    all_dist_rank.index = all_dist_rank.index + 1
    rank_lookup = {row['District Name']: idx for idx, row in all_dist_rank.iterrows()}
    total_ranked = len(all_dist_rank)

    your_district = {}
    for (dist_code, dist_name), dist_df_grp in df.groupby(['DISTRICT', 'District Name']):
        dist_code = int(dist_code)
        dist_name = str(dist_name)
        if dist_name == 'nan' or len(dist_df_grp) < 10:
            continue

        # Basic stats
        d = {
            'district_code': dist_code,
            'total_cases': int(len(dist_df_grp)),
            'avg_sentence': _safe(dist_df_grp['SENTTOT'].mean()),
            'median_sentence': _safe(dist_df_grp['SENTTOT'].median()),
            'below_guideline_pct': _safe(dist_df_grp['Below Guideline'].mean() * 100),
        }

        # Racial breakdown
        race_breakdown = {}
        for race in ['White', 'Black', 'Hispanic']:
            rdata = dist_df_grp[dist_df_grp['Race'] == race]
            if len(rdata) == 0:
                continue
            race_breakdown[race] = {
                'mean': _safe(rdata['SENTTOT'].mean()),
                'median': _safe(rdata['SENTTOT'].median()),
                'count': int(len(rdata)),
            }
        d['race_breakdown'] = race_breakdown

        # Top offenses
        off_stats = dist_df_grp.groupby('Offense')['SENTTOT'].agg(['mean', 'count'])
        off_stats = off_stats[off_stats['count'] >= 10].sort_values('count', ascending=False).head(10)
        d['top_offenses'] = [
            {'offense': off, 'mean': _safe(row['mean']), 'count': int(row['count'])}
            for off, row in off_stats.iterrows()
        ]

        # Yearly trend by race
        yr_race = dist_df_grp.groupby(['Year', 'Race'])['SENTTOT'].agg(['mean', 'count']).reset_index()
        yr_race = yr_race[yr_race['count'] >= 10]
        yearly_trend = []
        for _, row in yr_race.iterrows():
            yearly_trend.append({
                'year': int(row['Year']),
                'race': row['Race'],
                'mean': _safe(row['mean']),
                'count': int(row['count']),
            })
        d['yearly_trend'] = yearly_trend

        # Ranking
        rank = rank_lookup.get(dist_name)
        if rank:
            d['rank'] = int(rank)
            d['rank_total'] = total_ranked
            pctile = (total_ranked - rank) / total_ranked * 100
            d['percentile'] = _safe(pctile)
        else:
            d['rank'] = None
            d['rank_total'] = total_ranked

        your_district[dist_name] = d

    results['your_district'] = your_district
    results['your_district_meta'] = {
        'national_avg': nat_avg,
        'national_median': nat_median,
        'national_below': nat_below,
        'national_race_avg': nat_race_avg,
        'n_districts': n_districts,
    }

    # ── Page: Gender Gap ──
    print("Computing Gender Gap stats...")
    gender_df = df[df['Sex'].notna()]
    gender_overall = {
        'male_avg': _safe(gender_df[gender_df['Sex'] == 'Male']['SENTTOT'].mean()),
        'female_avg': _safe(gender_df[gender_df['Sex'] == 'Female']['SENTTOT'].mean()),
    }
    # By offense × sex
    gender_by_offense = []
    g_stats = gender_df.groupby(['Offense', 'Sex'])['SENTTOT'].agg(['mean', 'count']).reset_index()
    # Pivot to get both sexes per offense
    for offense in g_stats['Offense'].unique():
        off_data = g_stats[g_stats['Offense'] == offense]
        m_row = off_data[off_data['Sex'] == 'Male']
        f_row = off_data[off_data['Sex'] == 'Female']
        m_mean = _safe(m_row.iloc[0]['mean']) if len(m_row) > 0 else None
        f_mean = _safe(f_row.iloc[0]['mean']) if len(f_row) > 0 else None
        m_count = int(m_row.iloc[0]['count']) if len(m_row) > 0 else 0
        f_count = int(f_row.iloc[0]['count']) if len(f_row) > 0 else 0
        gender_by_offense.append({
            'offense': offense,
            'male_mean': m_mean,
            'female_mean': f_mean,
            'male_count': m_count,
            'female_count': f_count,
        })

    results['gender'] = {
        'overall': gender_overall,
        'by_offense': gender_by_offense,
    }

    # ── Page: Plea vs Trial ──
    print("Computing Plea vs Trial stats...")
    plea_df = df[df['Plea Type'].notna() & df['Race'].notna()].copy()

    # Overall plea × race stats
    plea_race = plea_df.groupby(['Plea Type', 'Race'])['SENTTOT'].agg(['mean', 'count']).reset_index()
    plea_race_list = [
        {'plea_type': row['Plea Type'], 'race': row['Race'],
         'mean': _safe(row['mean']), 'count': int(row['count'])}
        for _, row in plea_race.iterrows()
    ]

    # Trial rates by race
    trial_rates = []
    for race in ['White', 'Black', 'Hispanic']:
        rdata = plea_df[plea_df['Race'] == race]
        rate = (rdata['Plea Type'] == 'Trial').mean() * 100
        trial_rates.append({'race': race, 'trial_rate': _safe(rate)})

    # Overall trial pct
    trial_pct = _safe(len(plea_df[plea_df['Plea Type'] == 'Trial']) / len(plea_df) * 100)

    # By offense drill-down
    plea_by_offense = {}
    for offense in ["Drug Trafficking", "Firearms", "Fraud/Theft/Embezzlement", "Robbery"]:
        off_plea = plea_df[plea_df['Offense'] == offense]
        off_stats = off_plea.groupby(['Plea Type', 'Race'])['SENTTOT'].agg(['mean', 'count']).reset_index()
        off_stats = off_stats[off_stats['count'] >= 10]
        plea_by_offense[offense] = [
            {'plea_type': row['Plea Type'], 'race': row['Race'],
             'mean': _safe(row['mean']), 'count': int(row['count'])}
            for _, row in off_stats.iterrows()
        ]

    results['plea'] = {
        'plea_race': plea_race_list,
        'trial_rates': trial_rates,
        'trial_pct': trial_pct,
        'by_offense': plea_by_offense,
    }

    # ── Page: The Trend (leniency gap tab) ──
    print("Computing below-guideline rates by year × race...")
    below_by_year_race = []
    for year in sorted(df['Year'].unique()):
        for race in ['White', 'Black', 'Hispanic']:
            r = df[(df['Year'] == year) & (df['Race'] == race)]
            rate = r['Below Guideline'].mean() * 100
            below_by_year_race.append({
                'year': int(year), 'race': race, 'rate': _safe(rate),
            })
    results['below_guideline_trend'] = below_by_year_race

    # Write
    out = "data/precomputed.json"
    json_str = json.dumps(results, indent=2)
    with open(out, "w") as f:
        f.write(json_str)
    print(f"Done! Wrote {out} ({len(json_str)//1024}KB)")

if __name__ == "__main__":
    main()
