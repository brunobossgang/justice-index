# ⚖️ Justice Index

**Analyzing racial, gender, and geographic bias in US federal sentencing.**

388,334 federal criminal cases · FY2019–2024 · US Sentencing Commission data

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.54+-red)
![License](https://img.shields.io/badge/license-MIT-green)

## Key Findings

- **After controlling for offense, guidelines, criminal history, age, sex, and citizenship**, being Black adds ~4-5 extra months to your federal prison sentence
- This racial penalty is **getting worse** — growing year over year from 2019 to 2024
- The drug trafficking racial gap **tripled** over this period
- Black defendants are **25% less likely** to receive below-guideline sentences
- **Geographic lottery**: ~100 month spread between harshest and most lenient districts for the same crime
- The **trial penalty** falls harder on Black defendants

## Live Dashboard

🔗 **[justiceindex.org](https://justiceindex.org)** (coming soon)

8 interactive pages:
1. **Same Crime, Different Time** — Side-by-side sentencing comparisons by race
2. **The Trend** — Year-over-year controlled regression results
3. **The Geographic Lottery** — Interactive bubble map of district disparities
4. **Your District** — Look up any federal district and see how it compares
5. **The Evidence** — Full regression results (OLS + logistic)
6. **The Gender Gap** — Men vs women sentencing disparities
7. **Plea vs Trial** — How the trial penalty varies by race
8. **About** — Methodology, data sources, limitations

## Data

All data comes from the [US Sentencing Commission](https://www.ussc.gov/research/datafiles/commission-datafiles) Individual Offender datafiles.

- **FY2019–2023**: Parsed from SAS fixed-width `.dat` files using column positions from `.sas` syntax files
- **FY2024**: Parsed from the full CSV release
- **Combined dataset**: 388,334 cases, 18 variables

## Methodology

**OLS Regression** with robust standard errors (HC1), controlling for:
- Offense type (dummy variables for 12 major categories)
- Guideline minimum sentence range
- Criminal history points
- Age, sex, citizenship
- Weapon involvement

**Logistic Regression** for below-guideline sentence probability with the same controls.

R² ≈ 0.74 on 322,000+ cases.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
├── app.py                  # Streamlit dashboard (main)
├── regression_utils.py     # Live regression computation module
├── districts.py            # Federal district code → name mapping
├── district_coords.py      # District lat/lon for bubble map
├── data/
│   ├── combined_fy19_fy24.csv   # Combined 6-year dataset (24MB)
│   └── individual_fy24/slim.csv # FY2024 slim extract
├── parse_dat.py            # SAS .dat fixed-width file parser
├── build_multiyear.py      # Multi-year dataset builder
├── analyze.py              # Controlled comparison analysis
├── regression.py           # Standalone regression analysis
├── trends.py               # Multi-year trend analysis
├── blog/                   # Blog post and Twitter thread drafts
└── outreach/               # Journalist outreach materials
```

## Author

**Bruno Beckman** — [GitHub](https://github.com/brunobossgang)

## License

MIT — use this data and code however you want. Attribution appreciated.
