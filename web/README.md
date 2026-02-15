# Justice Index — Same Crime. Different Time.

A scrollytelling data journalism site exploring racial disparities in federal sentencing.

**Live:** [samecrimedifferenttime.org](https://samecrimedifferenttime.org)

## Tech Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS** — dark-mode-first styling
- **Framer Motion** — scroll-triggered animations
- **Recharts** — data visualizations

## Sections

1. **Hero** — Core stat: Black defendants get +3.85 months
2. **The Comparison** — Interactive offense-by-offense racial breakdown
3. **The Trend** — 22-year line chart of the racial gap
4. **The Geographic Lottery** — District-level sentencing variation
5. **The Calculator** — Predict your sentence based on demographics & offense
6. **The Human Cost** — 108,000+ extra prison-years animated counter
7. **The Evidence** — Regression coefficients, R², significance
8. **Take Action** — Share buttons, senator contact, reform organizations
9. **About/Methodology** — Data source, limitations, citation

## Development

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # Production build
```

## Data

All data is pre-computed from 1.3M USSC federal sentencing records (FY2002–2024) and stored in `src/data/precomputed.json`. No API calls needed.

## License

MIT — [github.com/brunobossgang/justice-index](https://github.com/brunobossgang/justice-index)
