# Justice Index — Game Plan

## Vision
Compare similar US federal court cases with different outcomes to detect bias/corruption in the American justice system.

## Phase 1: Data Foundation
- [ ] Download USSC FY2024 Individual Offender Datafile (CSV) + Codebook
- [ ] Download USSC Criminal History datafile (FY2024 CSV)
- [ ] Explore the data — understand fields, coverage, quality
- [ ] Design a Postgres schema that combines: offense, sentence, demographics, judge, district, criminal history
- [ ] Build ingestion pipeline (CSV → Postgres)
- [ ] Set up Docker Compose (pgvector + any services we need)

## Phase 2: Similarity & Comparison Engine
- [ ] Define "similar cases" — same primary offense + similar criminal history + similar guidelines range
- [ ] Build query: given a case, find its closest peers
- [ ] Calculate outcome variance (actual sentence vs guideline range, sentence differences between peers)
- [ ] Flag outlier pairs — similar inputs, drastically different outcomes
- [ ] Enrich with CourtListener opinion text (link via docket/case ID if possible)

## Phase 3: Bias Detection
- [ ] Statistical analysis: what predicts sentencing variance after controlling for legal factors?
- [ ] Key variables to test: race, gender, district/circuit, judge, representation type, citizenship
- [ ] Regression models — what's the residual variance that legal factors can't explain?
- [ ] Visualize disparities (by district, by demographic, over time)

## Phase 4: Frontend / Dashboard
- [ ] Searchable case comparison tool
- [ ] "Case pairs" viewer — side-by-side similar cases with different outcomes
- [ ] District/judge scorecards
- [ ] Trend charts over time
- [ ] Public-facing, shareable

## Data Sources
| Source | What it gives us | Format | Status |
|--------|-----------------|--------|--------|
| USSC Individual Offender Files | Structured sentencing data (offense, sentence, demographics, district) | CSV/SAS | Not yet downloaded |
| USSC Criminal History Files | Prior offenses, criminal history points | CSV/SAS | Not yet downloaded |
| CourtListener | Opinion text, case metadata | API (JSON) | Existing pipeline (old repo) |
| USSC Report Datafiles | Specialized datasets (drugs, robbery, etc.) | CSV/SAS | Available if needed |

## Tech Stack
- **Python** (data pipeline + API)
- **PostgreSQL + pgvector** (storage + semantic search)
- **FastAPI** (backend API)
- **Docker Compose** (local dev)
- **Frontend TBD** (React? Streamlit for v1?)

## Open Questions
- Scope: start federal only, expand to state later?
- Can we link USSC records to CourtListener cases? (Would let us pair structured data with full opinion text)
- Frontend choice — quick Streamlit prototype or proper React app?
- How far back do we go? (Data available from ~2002)

## Tomorrow's First Steps
1. Download FY2024 Individual Offender CSV + codebook
2. Load into a notebook/script and explore the fields
3. Start designing the schema
