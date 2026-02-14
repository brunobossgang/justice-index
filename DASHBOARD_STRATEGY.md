# Justice Index — Dashboard Strategy

## Reflections on What the Data Tells Us

After exploring 50,322 federal cases from FY2024, here's what shapes the dashboard:

### What hits hardest
1. **The same-crime comparison is the killer feature.** When you say "Black defendants get 53 more months for assault than White defendants," people can argue about confounding factors. But when you say "same crime, same criminal history, same guideline range — and there's STILL a gap," that's undeniable. The double-controlled analysis (offense + criminal history) is our strongest weapon.

2. **Geography as lottery is viscerally unfair.** A 100-month spread for the same drug crime depending on which courthouse you walk into. This is something everyone can understand — justice shouldn't depend on your zip code.

3. **The leniency gap matters more than the sentence gap.** The fact that White defendants get sentenced below guidelines 60% of the time vs 48% for Black defendants — that's about discretion. Judges CHOOSE to be lenient more often for some people. That's the story.

4. **Not everything is one-directional.** Child porn and sex abuse sentences are actually longer for White defendants. Intellectual honesty here builds credibility. We're not cherry-picking — we're showing the full picture.

### What the dashboard needs to DO

The goal isn't just "show data." It's to make the unfairness *felt*. Data alone doesn't change minds — comparisons do.

## Dashboard Design

### Page 1: "The Comparison" (Hero Feature)
**A side-by-side case comparator.**

User picks an offense type. We show two composite profiles:
- Same crime, same criminal history tier, same guideline range
- Different race (or gender, or district)
- Show the average sentence for each

Visual: Two human silhouettes, one with a shorter bar (sentence), one longer. The gap highlighted. Simple, emotional, irrefutable.

This is the thing people will screenshot and share.

### Page 2: "The Map" 
**Geographic justice lottery.**

US map, color-coded by average sentence for a given crime. User can toggle crime type. Click a district to see its stats vs national average.

The insight: "Where you're tried matters more than what you did."

### Page 3: "The Numbers"
**Deep-dive statistical dashboard.**

- Filterable by: offense type, race, gender, criminal history, district, year
- Charts: sentence distributions (histograms), departure rates, trend lines
- Tables: the controlled comparisons from our analysis
- Regression results: "after controlling for X, Y, Z — race still predicts N months of difference"

This is for journalists, researchers, lawyers. The credibility layer.

### Page 4: "The Methodology"
**Full transparency.**

- Data sources (USSC, with links)
- What we control for and what we can't
- Limitations (federal only, no private attorney quality data, no plea deal details)
- Code is open source

This prevents "but you didn't account for..." criticism.

## Design Principles

1. **Lead with the comparison, not the chart.** People remember stories, not statistics. "Same crime, different time" is the narrative.

2. **Make it shareable.** Every comparison should generate a unique URL. Social media cards with the key stat.

3. **Intellectual honesty = credibility.** Show where the gaps DON'T exist too. Show limitations. This isn't advocacy — it's evidence.

4. **Progressive disclosure.** Landing page = one powerful comparison. Scroll = more depth. Click through = full data. Don't overwhelm.

5. **Mobile-first.** Most sharing happens on phones. The hero comparison MUST work on a small screen.

## Tech Considerations

- **Frontend:** React + D3 for the map/charts. Or simpler: Next.js + Recharts.
- **v1 prototype:** Streamlit. Fast to build, good enough to validate the concept and get feedback.
- **Backend:** FastAPI serving pre-computed statistics from Postgres. No heavy computation on request.
- **Pre-compute everything:** The controlled comparisons, regression coefficients, district rankings — all computed offline and served as JSON. Dashboard is just a display layer.

## Data Pipeline for Dashboard

```
USSC CSV → Python ingestion → Postgres → 
  → Pre-compute: controlled comparisons per offense/race/ch_bin
  → Pre-compute: district rankings per offense
  → Pre-compute: regression coefficients
  → Export as JSON → Serve via API or static files
  → Frontend renders
```

## What We're Missing (for later)
- State court data (this is federal only — most criminal cases are state)
- Attorney quality (public defender vs private — huge confounder we can't control yet)
- Plea deal data (most cases never go to trial)
- Victim demographics
- Multi-year trends (we have FY2024 only so far, but USSC has data back to 2002)
- Judge-level analysis (not in this dataset directly, but could link via district + date)

## Priority Order
1. Regression analysis (make findings statistically rigorous) ← DOING NOW
2. Multi-year data (download FY2020-2023, show trends)
3. Streamlit prototype (get it visual fast)
4. Proper React dashboard
5. State data integration
