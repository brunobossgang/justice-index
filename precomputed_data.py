"""
Precomputed data access layer for Justice Index.
Loads from data/precomputed.json and provides helper functions so app.py
never needs to touch the raw CSV/parquet on Render.
"""
import json
import os
import pandas as pd

_PRECOMPUTED_PATH = os.path.join(os.path.dirname(__file__), "data", "precomputed.json")
_CACHE = None


def _load():
    global _CACHE
    if _CACHE is None:
        if os.path.exists(_PRECOMPUTED_PATH):
            with open(_PRECOMPUTED_PATH) as f:
                _CACHE = json.load(f)
    return _CACHE


def is_available():
    """Check if precomputed data exists and has descriptive stats."""
    pc = _load()
    return pc is not None and 'same_crime' in pc


def get_summary():
    """Return summary stats dict."""
    return _load()['summary']


def get_offense_race_stats(offense, crim_history="All levels", year_range=None):
    """
    Return race_stats, below_rates, total_count for Same Crime Different Time page.
    If year_range is provided as (min_year, max_year), aggregates from yearly data.
    Returns: (race_stats_dict, below_rates_dict, total_count)
    """
    pc = _load()
    sc = pc['same_crime']

    if offense not in sc:
        return {}, {}, 0

    ch_data = sc[offense].get(crim_history)
    if ch_data is None:
        return {}, {}, 0

    if year_range is None or (year_range[0] == pc['summary']['year_min'] and
                               year_range[1] == pc['summary']['year_max']):
        return ch_data['race_stats'], ch_data['below_rates'], ch_data['total_count']

    # Aggregate from yearly data for the requested year range
    yearly = ch_data['yearly']
    race_agg = {}  # race -> list of (mean, count, below_rate)
    for yr_str, yr_data in yearly.items():
        yr = int(yr_str)
        if yr < year_range[0] or yr > year_range[1]:
            continue
        for race, stats in yr_data.items():
            if race not in race_agg:
                race_agg[race] = []
            race_agg[race].append(stats)

    race_stats = {}
    below_rates = {}
    total_count = 0
    for race, entries in race_agg.items():
        total_n = sum(e['count'] for e in entries)
        if total_n == 0:
            continue
        weighted_mean = sum(e['mean'] * e['count'] for e in entries) / total_n
        # Weighted median approximation: use weighted mean (exact median not available from yearly)
        weighted_below = sum(e.get('below_rate', 0) * e['count'] for e in entries) / total_n
        race_stats[race] = {
            'mean': round(weighted_mean, 1),
            'median': round(weighted_mean, 0),  # approximation
            'count': total_n,
            'std': None,  # not available for filtered years
        }
        below_rates[race] = round(weighted_below, 1)
        total_count += total_n

    return race_stats, below_rates, total_count


def get_all_offenses():
    """Return list of all offense names."""
    return _load()['summary']['all_offenses']


def get_district_list():
    """Return list of {'code': int, 'name': str} sorted by name."""
    return _load()['summary']['all_districts']


def get_lottery_stats(offense):
    """Return district stats and BW gaps for The Lottery page."""
    pc = _load()
    lot = pc.get('lottery', {}).get(offense, {})
    districts = lot.get('districts', [])
    bw_gaps = lot.get('bw_gaps', [])
    return districts, bw_gaps


def get_district_detail(district_name):
    """Return full detail dict for a district, or None."""
    pc = _load()
    return pc.get('your_district', {}).get(district_name)


def get_district_meta():
    """Return national comparison stats for Your District page."""
    return _load().get('your_district_meta', {})


def get_gender_stats():
    """Return gender stats dict with 'overall' and 'by_offense'."""
    return _load()['gender']


def get_plea_stats(offense=None):
    """Return plea stats. If offense given, return that offense's drill-down."""
    pc = _load()
    plea = pc['plea']
    if offense:
        return {
            'plea_race': plea.get('by_offense', {}).get(offense, []),
            'trial_rates': plea['trial_rates'],
            'trial_pct': plea['trial_pct'],
        }
    return plea


def get_below_guideline_trend():
    """Return list of {year, race, rate} for leniency gap tab."""
    return _load()['below_guideline_trend']
