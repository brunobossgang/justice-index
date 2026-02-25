# ⚖️ Same Crime, Different Time

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live](https://img.shields.io/badge/Live-samecrimedifferenttime.org-blue)](https://samecrimedifferenttime.org)

**Do people who commit the same crime get the same sentence? An analysis of 1,294,673 federal criminal cases reveals systemic racial disparities in US sentencing.**

🔗 **Live:** [samecrimedifferenttime.org](https://samecrimedifferenttime.org)

---

## Key Findings

After controlling for offense type, guideline minimum, criminal history, age, sex, citizenship status, and weapon involvement:

- **Black defendants receive +3.85 months** longer sentences than white defendants
- This disparity translates to **108,157 extra years** of incarceration across the dataset
- OLS regression with robust standard errors (HC1) yields **R² = 0.74**

## Data

- **Source:** [US Sentencing Commission](https://www.ussc.gov/) Individual Offender datafiles
- **Scope:** 1,294,673 cases across fiscal years 2002–2024 (23 years)
- **Unit of analysis:** Individual sentenced defendant in federal court

## Methodology

Ordinary Least Squares (OLS) regression with heteroskedasticity-robust standard errors (HC1).

**Controls:**
- Offense type (primary guideline)
- Guideline minimum sentence
- Criminal history category
- Age at sentencing
- Sex
- Citizenship status
- Weapon involvement

**Limitations:** Observational data cannot establish causation. Unmeasured confounders (e.g., quality of legal representation, plea bargain details) may affect results. The model explains 74% of variance — meaningful but not complete.

## Tech Stack

- **Frontend:** React / Next.js, deployed on Vercel
- **Analysis:** Python (statsmodels, pandas)
- **Previous version:** Streamlit app (tagged as [`v1-streamlit`](https://github.com/brunobossgang/justice-index/releases/tag/v1-streamlit))

## Part of the Justice Index Project

**[Justice Index](https://justice-index.org)** analyzes racial bias across American institutions. This is one of three live investigations:

| Investigation | Focus | Data |
|---|---|---|
| **[Same Crime, Different Time](https://samecrimedifferenttime.org)** | Federal sentencing | 1.3M cases |
| **[Same Stop, Different Outcome](https://samestopdifferentoutcome.org)** | Traffic policing | 8.6M stops |
| **[Same Loan, Different Rate](https://sameloandifferentrate.org)** | Mortgage lending | 1.9M applications |

## License

MIT — see [LICENSE](LICENSE).

## Author

**Bruno Beckman** · [justice-index.org](https://justice-index.org)
