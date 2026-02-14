"""
Justice Index — Interactive Dashboard v3
Exploring racial and gender disparities in US federal sentencing.
388,334 cases · FY2019–2024 · US Sentencing Commission data
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from districts import DISTRICT_MAP
from district_coords import DISTRICT_COORDS
from regression_utils import (
    run_overall_regression, run_yearly_regression,
    run_offense_regressions, run_leniency_regression
)

st.set_page_config(page_title="Justice Index", page_icon="⚖️", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
    
    .big-number { font-size: 3em; font-weight: 800; line-height: 1; }
    .stat-label { font-size: 0.9em; color: #666; margin-top: 4px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white; padding: 40px 32px; border-radius: 16px; margin-bottom: 24px;
    }
    .hero-banner h1 { color: white; font-size: 2.4em; font-weight: 800; margin-bottom: 8px; }
    .hero-banner p { color: #b0b8c8; font-size: 1.1em; margin: 0; }
    
    .race-card {
        padding: 24px; border-radius: 12px; margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.15s;
    }
    .race-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    
    .gap-callout {
        background: linear-gradient(135deg, #fff5f5, #ffe8e8); border: 2px solid #E45756;
        padding: 28px; border-radius: 16px; text-align: center; margin: 20px 0;
        box-shadow: 0 4px 12px rgba(228,87,86,0.15);
    }
    .gap-callout .number { font-size: 3em; font-weight: 800; color: #E45756; margin: 8px 0; }
    .gap-callout .context { font-size: 1.15em; color: #555; }
    
    .share-box {
        background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px;
        padding: 20px; margin-top: 20px; font-size: 0.95em; color: #444;
    }
    .share-box .headline { font-weight: 700; font-size: 1.05em; color: #222; margin-bottom: 6px; }
    
    .footer {
        text-align: center; color: #999; font-size: 0.8em; padding: 24px 0 8px 0;
        border-top: 1px solid #eee; margin-top: 40px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background: #fafbfc; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 0.95em; }
    
    /* Mobile */
    @media (max-width: 768px) {
        .hero-banner { padding: 24px 16px; }
        .hero-banner h1 { font-size: 1.6em; }
        .big-number { font-size: 2.2em; }
        .gap-callout .number { font-size: 2.2em; }
    }
</style>
""", unsafe_allow_html=True)

FOOTER = '<div class="footer">⚖️ Justice Index · Data from the <a href="https://www.ussc.gov/research/datafiles/commission-datafiles">US Sentencing Commission</a> · Built by Bruno Beckman</div>'

# ── Data loading ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/combined_fy19_fy24.csv", low_memory=False)
    df = df[
        (df["SENTTOT"] >= 0) & (df["SENTTOT"] < 470) &
        (df["NEWRACE"].isin([1, 2, 3])) &
        (df["XMINSOR"] >= 0) & (df["XMINSOR"] < 9996) &
        (df["OFFGUIDE"].notna()) &
        (df["CRIMPTS"].notna()) & (df["CRIMPTS"] >= 0) &
        (df["AGE"].notna()) & (df["AGE"] > 0)
    ].copy()

    for col in ["NEWRACE", "MONSEX", "CRIMHIST", "WEAPON", "CITIZEN", "NEWEDUC", "INOUT", "PRESENT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            mask = df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].astype(int)

    race_map = {1: "White", 2: "Black", 3: "Hispanic"}
    sex_map = {0: "Male", 1: "Female"}
    offense_map = {
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

    df["Race"] = df["NEWRACE"].map(race_map)
    df["Sex"] = df["MONSEX"].map(sex_map)
    df["Offense"] = df["OFFGUIDE"].map(offense_map).fillna("Other")
    df["Year"] = df["FISCAL_YEAR"].astype(int)
    df["Below Guideline"] = df["SENTTOT"] < df["XMINSOR"]
    df["Departure"] = df["SENTTOT"] - df["XMINSOR"]
    df["District Name"] = df["DISTRICT"].astype(int).map(DISTRICT_MAP).fillna(df["DISTRICT"].astype(str))
    df["Crim History"] = pd.cut(df["CRIMPTS"], bins=[-1, 0, 3, 6, 10, 200],
                                 labels=["0 pts", "1-3 pts", "4-6 pts", "7-10 pts", "10+ pts"])

    plea_map = {1: "Plea Deal", 2: "Plea Deal", 3: "Plea Deal",
                5: "Straight Plea", 8: "Trial", 9: "Plea Deal"}
    df["Plea Type"] = df["DSPLEA"].map(plea_map)

    return df

df = load_data()

RACE_COLORS = {"White": "#4C78A8", "Black": "#E45756", "Hispanic": "#72B7B2"}
MAJOR_OFFENSES = ["Drug Trafficking", "Firearms", "Fraud/Theft/Embezzlement",
                  "Robbery", "Assault", "Money Laundering", "Immigration",
                  "Sexual Abuse", "Child Pornography", "Murder"]

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# ⚖️ Justice Index")
    st.caption(f"**{len(df):,}** federal cases analyzed  \nFY2019 – FY2024")
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Same Crime, Different Time",
        "📈 The Trend",
        "🗺️ The Lottery",
        "🔎 Your District",
        "🔬 The Evidence",
        "👤 Gender Gap",
        "⚖️ Plea vs Trial",
        "📖 About"
    ], label_visibility="collapsed")

    st.divider()
    st.caption("Data: US Sentencing Commission")
    st.caption("Built by Bruno Beckman")

# ══════════════════════════════════════════════════════════════
# PAGE 1: SAME CRIME, DIFFERENT TIME
# ══════════════════════════════════════════════════════════════
if page == "🏠 Same Crime, Different Time":
    st.markdown("""
    <div class="hero-banner">
        <h1>Same Crime. Different Time.</h1>
        <p>Select a federal offense below. See how sentencing differs by race — even when the crime, 
        criminal history, and guidelines are the same.</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        selected_offense = st.selectbox("Offense type", MAJOR_OFFENSES +
            [o for o in sorted(df["Offense"].unique()) if o not in MAJOR_OFFENSES],
            index=0, label_visibility="collapsed",
            help="Choose an offense to compare sentencing across races")
    with col_b:
        selected_ch = st.selectbox("Criminal history",
            ["All levels"] + list(df["Crim History"].cat.categories), index=0)
    with col_c:
        year_range = st.select_slider("Years",
            options=sorted(df["Year"].unique()),
            value=(2019, 2024))

    subset = df[(df["Offense"] == selected_offense) &
                (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    if selected_ch != "All levels":
        subset = subset[subset["Crim History"] == selected_ch]

    if len(subset) < 30:
        st.warning("Not enough cases for this combination. Try broadening filters.")
    else:
        race_stats = subset.groupby("Race")["SENTTOT"].agg(["mean", "median", "count", "std"]).round(1)

        cols = st.columns(3)
        for i, race in enumerate(["White", "Black", "Hispanic"]):
            if race not in race_stats.index:
                continue
            row = race_stats.loc[race]
            with cols[i]:
                color = RACE_COLORS[race]
                st.markdown(f"""
                <div class="race-card" style="background: linear-gradient(135deg, {color}12, {color}06);
                            border-left: 5px solid {color};">
                    <div style="color: {color}; font-weight: 600; font-size: 0.95em; text-transform: uppercase;
                                letter-spacing: 0.5px;">{race} Defendants</div>
                    <div class="big-number" style="color: {color};">{row['mean']:.1f}<span style="font-size:0.35em; font-weight:500;"> months</span></div>
                    <div class="stat-label">Median: {row['median']:.0f} mo · {int(row['count']):,} cases</div>
                </div>
                """, unsafe_allow_html=True)

        # The gap callout
        if "White" in race_stats.index and "Black" in race_stats.index:
            gap = race_stats.loc["Black", "mean"] - race_stats.loc["White", "mean"]
            if abs(gap) >= 1:
                who_more = "Black" if gap > 0 else "White"
                who_less = "White" if gap > 0 else "Black"
                filter_desc = f" with {selected_ch}" if selected_ch != "All levels" else ""
                st.markdown(f"""
                <div class="gap-callout">
                    <div class="context">For <b>{selected_offense}</b>{filter_desc}:</div>
                    <div class="number">{abs(gap):.1f} months</div>
                    <div class="context">
                        longer for <b>{who_more}</b> defendants vs <b>{who_less}</b> defendants
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"✅ Less than 1 month gap between Black and White defendants for {selected_offense}")

        # Charts
        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            fig = go.Figure()
            for race in ["White", "Black", "Hispanic"]:
                if race not in race_stats.index:
                    continue
                race_data = subset[subset["Race"] == race]["SENTTOT"]
                fig.add_trace(go.Violin(y=race_data, name=race,
                                       line_color=RACE_COLORS[race],
                                       fillcolor=RACE_COLORS[race],
                                       opacity=0.6, meanline_visible=True,
                                       box_visible=True))
            fig.update_layout(title="Sentence Distribution", height=420,
                            yaxis_title="Sentence (months)", showlegend=False,
                            template="plotly_white")
            st.plotly_chart(fig, width="stretch")

        with c2:
            below_rates = subset.groupby("Race")["Below Guideline"].mean() * 100
            fig2 = go.Figure()
            for race in ["White", "Black", "Hispanic"]:
                if race not in below_rates.index:
                    continue
                fig2.add_trace(go.Bar(x=[race], y=[below_rates[race]],
                                     name=race, marker_color=RACE_COLORS[race]))
            fig2.update_layout(title="% Sentenced Below Guidelines",
                             yaxis_title="Percent", height=420,
                             showlegend=False, template="plotly_white")
            fig2.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
            st.plotly_chart(fig2, width="stretch")

        # Share box
        if "White" in race_stats.index and "Black" in race_stats.index and abs(gap) >= 1:
            b_n = int(race_stats.loc["Black", "count"])
            w_n = int(race_stats.loc["White", "count"])
            st.markdown(f"""
            <div class="share-box">
                <div class="headline">📋 The Finding</div>
                For federal {selected_offense.lower()} cases (FY{year_range[0]}–{year_range[1]}), 
                Black defendants received an average of <b>{race_stats.loc['Black','mean']:.1f} months</b> 
                vs <b>{race_stats.loc['White','mean']:.1f} months</b> for White defendants — 
                a gap of <b>{abs(gap):.1f} months</b>. 
                Based on {b_n:,} Black and {w_n:,} White cases from US Sentencing Commission data.
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("⚠️ Raw averages — not controlled for criminal history, guidelines, or other factors. "
                   "See 'The Evidence' page for controlled regression results.")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2: THE TREND
# ══════════════════════════════════════════════════════════════
elif page == "📈 The Trend":
    st.markdown("""
    <div class="hero-banner">
        <h1>The Trend</h1>
        <p>Is the racial sentencing gap getting better? Six years of data tell the story.</p>
    </div>
    """, unsafe_allow_html=True)

    # Compute live from data
    yearly = run_yearly_regression(df)

    if len(yearly) > 0:
        first_year = yearly.iloc[0]
        last_year = yearly.iloc[-1]
        trend_dir = "WORSENING" if last_year["Black_Effect"] > first_year["Black_Effect"] else "IMPROVING"
        delta = last_year["Black_Effect"] - first_year["Black_Effect"]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"Black penalty ({int(first_year['Year'])})",
                      f"+{first_year['Black_Effect']:.1f} months",
                      help="Controlled for offense, guidelines, criminal history, age, sex, citizenship")
        with c2:
            st.metric(f"Black penalty ({int(last_year['Year'])})",
                      f"+{last_year['Black_Effect']:.1f} months",
                      delta=f"{delta:+.1f} mo", delta_color="inverse")
        with c3:
            st.metric("Trend", trend_dir,
                      delta=f"{'▲ growing' if delta > 0 else '▼ shrinking'} gap",
                      delta_color="inverse")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Controlled Gap", "⚖️ Leniency Gap", "🔍 By Offense"])

    with tab1:
        if len(yearly) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yearly["Year"], y=yearly["Black_Effect"],
                                    mode="lines+markers", name="Black penalty",
                                    line=dict(color="#E45756", width=3),
                                    marker=dict(size=10)))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")

            z = np.polyfit(yearly["Year"], yearly["Black_Effect"], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(x=yearly["Year"], y=p(yearly["Year"]),
                                    mode="lines", name="Trend",
                                    line=dict(color="#E45756", width=1.5, dash="dot"),
                                    opacity=0.5))

            fig.update_layout(
                title="Controlled Black Penalty Over Time<br><sub>After controlling for offense type, guidelines, criminal history, age, sex, citizenship</sub>",
                yaxis_title="Extra months (vs White defendants)",
                xaxis_title="Fiscal Year", height=500,
                template="plotly_white", showlegend=False
            )
            st.plotly_chart(fig, width="stretch")

            st.markdown(f"""
            > **What this shows:** Each year, we run a regression controlling for offense type, guideline range,
            criminal history, age, sex, and citizenship. The remaining race effect — the penalty for being Black
            that legal factors can't explain — went from **+{first_year['Black_Effect']:.1f} months** in 
            {int(first_year['Year'])} to **+{last_year['Black_Effect']:.1f} months** in {int(last_year['Year'])}.
            """)

    with tab2:
        below_data = []
        for year in sorted(df["Year"].unique()):
            for race in ["White", "Black", "Hispanic"]:
                r = df[(df["Year"] == year) & (df["Race"] == race)]
                rate = r["Below Guideline"].mean() * 100
                below_data.append({"Year": year, "Race": race, "Rate": rate})
        below_df = pd.DataFrame(below_data)

        fig = px.line(below_df, x="Year", y="Rate", color="Race",
                     color_discrete_map=RACE_COLORS, markers=True,
                     labels={"Rate": "% Below Guideline Minimum"})
        fig.update_layout(title="Who Gets Mercy?<br><sub>% sentenced below the guideline minimum by race</sub>",
                         height=500, template="plotly_white")
        st.plotly_chart(fig, width="stretch")

        # Compute actual gap
        w_rate = df[df["Race"] == "White"]["Below Guideline"].mean() * 100
        b_rate = df[df["Race"] == "Black"]["Below Guideline"].mean() * 100
        st.error(f"📌 **Steady {w_rate - b_rate:.0f}-point gap.** White defendants receive below-guideline "
                f"sentences ~{w_rate:.0f}% of the time. Black defendants: ~{b_rate:.0f}%. "
                "This gap hasn't moved in six years.")

    with tab3:
        @st.cache_data
        def compute_offense_trends(_df):
            import statsmodels.api as sm_api
            from regression_utils import _prepare_features
            results = {}
            for offense in ["Drug Trafficking", "Firearms", "Robbery"]:
                years_data = []
                for year in sorted(_df["Year"].unique()):
                    sub = _df[(_df["Offense"] == offense) & (_df["Year"] == year)]
                    if len(sub) < 100:
                        continue
                    try:
                        X, y = _prepare_features(sub, include_offense_dummies=False)
                        if len(y) < 50:
                            continue
                        m = sm_api.OLS(y, X).fit(cov_type='HC1')
                        years_data.append({"Year": year, "Effect": round(m.params["Black"], 1)})
                    except Exception:
                        continue
                results[offense] = pd.DataFrame(years_data)
            return results

        off_yearly = compute_offense_trends(df)

        off_choice = st.selectbox("Select offense", ["Drug Trafficking", "Firearms", "Robbery"])

        if off_choice in off_yearly and len(off_yearly[off_choice]) > 0:
            odf = off_yearly[off_choice]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=odf["Year"], y=odf["Effect"],
                                marker_color=["#E45756" if v > 0 else "#4C78A8" for v in odf["Effect"]]))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                title=f"{off_choice}: Black Penalty by Year (controlled)",
                yaxis_title="Extra months vs White defendants",
                height=450, template="plotly_white"
            )
            st.plotly_chart(fig, width="stretch")

            if off_choice == "Drug Trafficking" and len(odf) >= 2:
                first_v = odf.iloc[0]["Effect"]
                last_v = odf.iloc[-1]["Effect"]
                if last_v > first_v * 1.5:
                    st.error(f"📌 **The drug trafficking gap grew** — from +{first_v:.1f} months "
                            f"in {int(odf.iloc[0]['Year'])} to +{last_v:.1f} in {int(odf.iloc[-1]['Year'])}.")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3: THE LOTTERY
# ══════════════════════════════════════════════════════════════
elif page == "🗺️ The Lottery":
    st.markdown("""
    <div class="hero-banner">
        <h1>The Geographic Lottery</h1>
        <p>Where you're sentenced can matter more than what you did. Same crime, wildly different outcomes.</p>
    </div>
    """, unsafe_allow_html=True)

    offense_choice = st.selectbox("Offense type",
        ["Drug Trafficking", "Firearms", "Fraud/Theft/Embezzlement", "Robbery"])

    geo = df[df["Offense"] == offense_choice]
    dist_stats = geo.groupby(["DISTRICT", "District Name"]).agg(
        avg=("SENTTOT", "mean"), med=("SENTTOT", "median"), n=("SENTTOT", "count"),
        below=("Below Guideline", "mean")
    ).reset_index()
    dist_stats = dist_stats[dist_stats["n"] >= 50].sort_values("avg", ascending=False)
    dist_stats["avg"] = dist_stats["avg"].round(1)
    dist_stats["below"] = (dist_stats["below"] * 100).round(1)

    spread = dist_stats["avg"].max() - dist_stats["avg"].min()

    st.markdown(f"""
    <div class="gap-callout">
        <div class="context">Between harshest and most lenient districts for <b>{offense_choice}</b>:</div>
        <div class="number">{spread:.0f} months</div>
        <div class="context">That's <b>{spread/12:.1f} years</b> of someone's life, depending on geography alone.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bubble map ──
    map_data = dist_stats.copy()
    map_data["lat"] = map_data["DISTRICT"].map(lambda d: DISTRICT_COORDS.get(int(d), (None,None,None))[0])
    map_data["lon"] = map_data["DISTRICT"].map(lambda d: DISTRICT_COORDS.get(int(d), (None,None,None))[1])
    map_data = map_data.dropna(subset=["lat", "lon"])

    if len(map_data) > 10:
        fig_map = go.Figure()
        fig_map.add_trace(go.Scattergeo(
            lat=map_data["lat"], lon=map_data["lon"],
            text=map_data.apply(lambda r: f"<b>{r['District Name']}</b><br>"
                                          f"Avg: {r['avg']:.1f} mo<br>"
                                          f"Cases: {int(r['n']):,}<br>"
                                          f"Below guideline: {r['below']:.0f}%", axis=1),
            hoverinfo="text",
            marker=dict(
                size=map_data["n"] ** 0.4 * 3,  # scale by case count
                color=map_data["avg"],
                colorscale="RdYlBu_r",
                colorbar=dict(title="Avg Sentence<br>(months)"),
                line=dict(width=0.5, color="white"),
                sizemin=5,
            ),
        ))
        fig_map.update_layout(
            title=f"Federal Districts: Average {offense_choice} Sentence",
            geo=dict(
                scope="usa", projection_type="albers usa",
                showland=True, landcolor="#f0f0f0",
                showlakes=True, lakecolor="white",
                showcountries=False,
            ),
            height=500, template="plotly_white", margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_map, width="stretch")

    # ── Harshest vs lenient tables ──
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔴 Harshest Districts")
        harsh = dist_stats.head(10)[["District Name", "avg", "n"]].reset_index(drop=True)
        harsh.columns = ["District", "Avg Sentence (mo)", "Cases"]
        harsh.index = harsh.index + 1
        st.dataframe(harsh, width="stretch")
    with c2:
        st.subheader("🟢 Most Lenient Districts")
        lenient = dist_stats.tail(10).sort_values("avg")[["District Name", "avg", "n"]].reset_index(drop=True)
        lenient.columns = ["District", "Avg Sentence (mo)", "Cases"]
        lenient.index = lenient.index + 1
        st.dataframe(lenient, width="stretch")

    # ── Full bar chart ──
    with st.expander(f"📊 All Districts: {offense_choice}", expanded=False):
        fig = px.bar(dist_stats.sort_values("avg"), x="avg", y="District Name",
                    orientation="h", color="avg",
                    color_continuous_scale="RdYlBu_r",
                    labels={"avg": "Average Sentence (months)", "District Name": ""},
                    title=f"All Districts: {offense_choice}")
        fig.update_layout(height=max(400, len(dist_stats) * 22), template="plotly_white",
                         showlegend=False, yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig, width="stretch")

    # ── Racial gap by district ──
    st.divider()
    st.markdown("### 🔍 Where Is the Racial Gap Worst?")
    st.caption("Districts with ≥20 Black and ≥20 White cases for this offense")

    race_by_dist = geo.groupby(["DISTRICT", "District Name", "Race"])["SENTTOT"].agg(["mean", "count"]).reset_index()
    bw_pivot = race_by_dist[race_by_dist["Race"].isin(["White", "Black"])].pivot_table(
        index=["DISTRICT", "District Name"], columns="Race", values=["mean", "count"]
    )
    bw_pivot.columns = [f"{c[1]}_{c[0]}" for c in bw_pivot.columns]
    bw_pivot = bw_pivot.reset_index()
    if "Black_count" in bw_pivot.columns and "White_count" in bw_pivot.columns:
        bw_pivot = bw_pivot[(bw_pivot["Black_count"] >= 20) & (bw_pivot["White_count"] >= 20)].copy()
        bw_pivot["Gap"] = (bw_pivot["Black_mean"] - bw_pivot["White_mean"]).round(1)
        bw_pivot = bw_pivot.sort_values("Gap", ascending=False)

        if len(bw_pivot) >= 5:
            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(
                y=bw_pivot["District Name"], x=bw_pivot["Gap"],
                orientation="h",
                marker_color=["#E45756" if g > 0 else "#4C78A8" for g in bw_pivot["Gap"]],
                text=[f"{g:+.1f}" for g in bw_pivot["Gap"]],
                textposition="outside"
            ))
            fig_gap.add_vline(x=0, line_color="gray")
            fig_gap.update_layout(
                title=f"Black–White Sentencing Gap by District: {offense_choice}<br><sub>Positive = Black defendants receive longer sentences</sub>",
                xaxis_title="Gap (months)", height=max(400, len(bw_pivot) * 24),
                template="plotly_white",
                yaxis=dict(tickfont=dict(size=10))
            )
            st.plotly_chart(fig_gap, width="stretch")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3B: YOUR DISTRICT
# ══════════════════════════════════════════════════════════════
elif page == "🔎 Your District":
    st.markdown("""
    <div class="hero-banner">
        <h1>Look Up Your District</h1>
        <p>See how your federal judicial district compares to the rest of the country.</p>
    </div>
    """, unsafe_allow_html=True)

    # Build district list sorted by name
    district_options = df[["DISTRICT", "District Name"]].drop_duplicates().sort_values("District Name")
    district_options = district_options[district_options["District Name"].notna()]
    dist_names = district_options["District Name"].tolist()
    dist_codes = district_options["DISTRICT"].tolist()
    name_to_code = dict(zip(dist_names, dist_codes))

    selected_dist = st.selectbox("Select your federal district", dist_names,
                                 index=dist_names.index("S.D. New York") if "S.D. New York" in dist_names else 0)
    dist_code = name_to_code[selected_dist]
    dist_df = df[df["DISTRICT"] == dist_code]
    nat_df = df  # national comparison

    st.divider()

    # Overview metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Cases", f"{len(dist_df):,}",
                  delta=f"{'above' if len(dist_df) > len(nat_df)/94 else 'below'} avg",
                  delta_color="off")
    with c2:
        dist_avg = dist_df["SENTTOT"].mean()
        nat_avg = nat_df["SENTTOT"].mean()
        st.metric("Avg Sentence", f"{dist_avg:.1f} mo",
                  delta=f"{dist_avg - nat_avg:+.1f} vs national", delta_color="inverse")
    with c3:
        dist_below = dist_df["Below Guideline"].mean() * 100
        nat_below = nat_df["Below Guideline"].mean() * 100
        st.metric("Below Guideline", f"{dist_below:.0f}%",
                  delta=f"{dist_below - nat_below:+.1f}pp vs national")
    with c4:
        dist_median = dist_df["SENTTOT"].median()
        st.metric("Median Sentence", f"{dist_median:.0f} mo")

    st.divider()

    # Racial breakdown
    st.markdown("### Racial Breakdown")
    race_stats = dist_df.groupby("Race")["SENTTOT"].agg(["mean", "median", "count"]).round(1)
    nat_race = nat_df.groupby("Race")["SENTTOT"].agg(["mean"]).round(1)

    cols = st.columns(3)
    for i, race in enumerate(["White", "Black", "Hispanic"]):
        if race not in race_stats.index:
            continue
        row = race_stats.loc[race]
        nat_mean = nat_race.loc[race, "mean"] if race in nat_race.index else 0
        color = RACE_COLORS[race]
        with cols[i]:
            st.markdown(f"""
            <div class="race-card" style="background: linear-gradient(135deg, {color}12, {color}06);
                        border-left: 5px solid {color};">
                <div style="color: {color}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{race}</div>
                <div class="big-number" style="color: {color};">{row['mean']:.1f}<span style="font-size:0.35em;"> mo</span></div>
                <div class="stat-label">
                    Median: {row['median']:.0f} mo · {int(row['count']):,} cases<br>
                    National avg: {nat_mean:.1f} mo ({row['mean'] - nat_mean:+.1f})
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Racial gap in this district
    if "White" in race_stats.index and "Black" in race_stats.index:
        local_gap = race_stats.loc["Black", "mean"] - race_stats.loc["White", "mean"]
        nat_gap = nat_race.loc["Black", "mean"] - nat_race.loc["White", "mean"]
        st.markdown(f"""
        <div class="gap-callout">
            <div class="context">In <b>{selected_dist}</b>:</div>
            <div class="number">{abs(local_gap):.1f} months</div>
            <div class="context">
                {'longer for <b>Black</b>' if local_gap > 0 else 'longer for <b>White</b>'} defendants vs 
                {abs(nat_gap):.1f} mo nationally
                {'— <b>worse</b> than average' if abs(local_gap) > abs(nat_gap) else '— <b>better</b> than average'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Top offenses in this district
    st.divider()
    st.markdown("### Top Offenses")
    off_stats = dist_df.groupby("Offense")["SENTTOT"].agg(["mean", "count"]).round(1)
    off_stats = off_stats[off_stats["count"] >= 10].sort_values("count", ascending=False).head(10)
    off_stats.columns = ["Avg Sentence (mo)", "Cases"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=off_stats.index, x=off_stats["Cases"],
        orientation="h", marker_color="#4C78A8",
        text=[f"{n:,} cases · {s:.0f} mo avg" for n, s in
              zip(off_stats["Cases"], off_stats["Avg Sentence (mo)"])],
        textposition="outside"
    ))
    fig.update_layout(title=f"Most Common Offenses in {selected_dist}",
                     height=400, template="plotly_white",
                     xaxis_title="Number of Cases")
    st.plotly_chart(fig, width="stretch")

    # Trend over time for this district
    st.divider()
    st.markdown("### Sentencing Trend")
    # Only show race lines with enough data per year
    yr_stats = dist_df.groupby(["Year", "Race"])["SENTTOT"].agg(["mean", "count"]).reset_index()
    yr_stats = yr_stats[yr_stats["count"] >= 10]  # filter noisy years

    if len(yr_stats) > 2:
        fig2 = px.line(yr_stats, x="Year", y="mean", color="Race",
                       color_discrete_map=RACE_COLORS, markers=True,
                       labels={"mean": "Average Sentence (months)"})
        fig2.update_layout(title=f"Average Sentence Over Time in {selected_dist}",
                          height=400, template="plotly_white")
        st.plotly_chart(fig2, width="stretch")
    else:
        st.info("Not enough yearly data to show a meaningful trend for this district.")

    # Ranking among all districts
    st.divider()
    st.markdown("### How Does This District Rank?")
    all_dist = nat_df.groupby("District Name")["SENTTOT"].agg(["mean", "count"]).reset_index()
    all_dist = all_dist[all_dist["count"] >= 50].sort_values("mean", ascending=False).reset_index(drop=True)
    all_dist.index = all_dist.index + 1
    rank = all_dist[all_dist["District Name"] == selected_dist].index
    if len(rank) > 0:
        rank_num = rank[0]
        total = len(all_dist)
        pctile = (total - rank_num) / total * 100
        st.markdown(f"""
        <div style="text-align: center; padding: 16px;">
            <span style="font-size: 2em; font-weight: 800; color: #1a1a2e;">#{rank_num}</span>
            <span style="font-size: 1.1em; color: #666;"> out of {total} districts (harshest → most lenient)</span>
            <br><span style="color: #888;">{'Top quartile — harsher than most' if pctile < 25 else 'Above average' if pctile < 50 else 'Below average' if pctile < 75 else 'Bottom quartile — more lenient than most'}</span>
        </div>
        """, unsafe_allow_html=True)

    # Share box
    if "White" in race_stats.index and "Black" in race_stats.index:
        st.markdown(f"""
        <div class="share-box">
            <div class="headline">📋 Share This</div>
            In {selected_dist}, Black defendants receive an average of {race_stats.loc['Black','mean']:.1f} months 
            vs {race_stats.loc['White','mean']:.1f} months for White defendants — a gap of {abs(local_gap):.1f} months. 
            Based on {int(race_stats.loc['Black','count']):,} Black and {int(race_stats.loc['White','count']):,} White 
            cases (FY2019–2024). Source: Justice Index / US Sentencing Commission data.
        </div>
        """, unsafe_allow_html=True)

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4: THE EVIDENCE (live regression)
# ══════════════════════════════════════════════════════════════
elif page == "🔬 The Evidence":
    st.markdown("""
    <div class="hero-banner">
        <h1>The Evidence</h1>
        <p>Regression analysis: what predicts your sentence after controlling for every legal factor in the data?</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 Overall Model", "📋 By Offense", "⚖️ Who Gets Leniency?"])

    with tab1:
        with st.spinner("Running regression on 322,000+ cases..."):
            overall = run_overall_regression(df)
        st.markdown(f"### Full Model: What Predicts Sentence Length?")
        st.markdown(f"OLS regression on **{overall['n_obs']:,}** cases (FY2019–2024). **R² = {overall['r_squared']:.2f}**. Robust standard errors (HC1).")

        coef_df = pd.DataFrame(overall["coefficients"])
        # Filter to main variables of interest (skip offense dummies)
        main_vars = ["Black (vs White)", "Hispanic (vs White)", "Female (vs Male)",
                     "Guideline Minimum", "Criminal History Points", "Age",
                     "Non-Citizen (Illegal)", "Weapon Involved"]
        coef_df = coef_df[coef_df["variable"].isin(main_vars)]

        fig = go.Figure()
        colors = ["#E45756" if v > 0 else "#4C78A8" for v in coef_df["effect"]]
        fig.add_trace(go.Bar(y=coef_df["variable"], x=coef_df["effect"],
                            orientation="h", marker_color=colors,
                            text=[f"{v:+.1f}" for v in coef_df["effect"]],
                            textposition="outside"))
        fig.add_vline(x=0, line_color="gray")
        fig.update_layout(title="Effect on Sentence Length (months)",
                         height=400, template="plotly_white",
                         xaxis_title="Months added/subtracted from sentence")
        st.plotly_chart(fig, width="stretch")

        # Find the Black effect for the narrative
        black_row = coef_df[coef_df["variable"] == "Black (vs White)"].iloc[0]
        female_row = coef_df[coef_df["variable"] == "Female (vs Male)"].iloc[0]
        weapon_row = coef_df[coef_df["variable"] == "Weapon Involved"].iloc[0]

        st.markdown(f"""
        **How to read this:** After accounting for offense type, guideline range, criminal history, age, sex,
        citizenship, and weapon involvement — being Black adds **+{black_row['effect']:.1f} months** to your sentence.
        Being female subtracts **{abs(female_row['effect']):.1f} months**. Having a weapon adds **+{weapon_row['effect']:.1f} months**.

        The guideline minimum coefficient shows how closely judges follow guidelines — a value of ~0.6 means
        for every 1-month increase in the guideline minimum, actual sentences increase by ~0.6 months.
        """)

    with tab2:
        st.markdown("### Race Effect by Offense Type (Controlled)")

        offense_df = run_offense_regressions(df)

        fig = go.Figure()
        colors = ["#E45756" if v > 0 else "#4C78A8" for v in offense_df["Black_Effect"]]
        fig.add_trace(go.Bar(
            y=offense_df["Offense"],
            x=offense_df["Black_Effect"],
            orientation="h", marker_color=colors,
            text=[f"{v:+.1f} {s}" for v, s in
                  zip(offense_df["Black_Effect"], offense_df["Significance_Stars"])],
            textposition="outside"
        ))
        fig.add_vline(x=0, line_color="gray")
        fig.update_layout(
            title="Extra Months for Black Defendants by Offense<br><sub>Controlling for guidelines, criminal history, age, sex, citizenship, weapon</sub>",
            xaxis_title="Extra months vs White defendants",
            height=max(400, len(offense_df) * 28), template="plotly_white"
        )
        st.plotly_chart(fig, width="stretch")

        # Count how many show positive vs negative
        pos = (offense_df["Black_Effect"] > 0).sum()
        neg = (offense_df["Black_Effect"] < 0).sum()
        sig_pos = ((offense_df["Black_Effect"] > 0) & (offense_df["Significance_Stars"] != "")).sum()

        st.markdown(f"""
        **Key patterns:**
        - **{pos} of {len(offense_df)} offense types** show longer sentences for Black defendants
        - **{sig_pos} are statistically significant** (p < 0.05)
        - **Violent crimes** tend to show the largest disparities
        - Some offenses flip — showing this isn't a simple story, and builds credibility
        - \\*\\*\\* = p<0.001, \\*\\* = p<0.01, \\* = p<0.05
        """)

    with tab3:
        st.markdown("### Logistic Regression: Who Gets Below-Guideline Sentences?")
        st.markdown("Odds ratios — values below 1.0 mean **less likely** to receive leniency.")

        leniency = run_leniency_regression(df)
        lr_df = pd.DataFrame(leniency)

        fig = go.Figure()
        colors = ["#E45756" if v < 1 else "#4C78A8" if v > 1.05 else "#999" for v in lr_df["odds_ratio"]]
        fig.add_trace(go.Bar(y=lr_df["variable"], x=lr_df["odds_ratio"],
                            orientation="h", marker_color=colors,
                            text=[f"{v:.2f}x" for v in lr_df["odds_ratio"]],
                            textposition="outside"))
        fig.add_vline(x=1, line_color="gray", line_dash="dash")
        fig.update_layout(title="Odds of Receiving Below-Guideline Sentence",
                         xaxis_title="Odds Ratio (1.0 = equal chance)",
                         height=380, template="plotly_white",
                         xaxis=dict(range=[0.4, 1.7]))
        st.plotly_chart(fig, width="stretch")

        black_or = [l for l in leniency if "Black" in l["variable"]][0]["odds_ratio"]
        female_or = [l for l in leniency if "Female" in l["variable"]][0]["odds_ratio"]
        st.error(f"📌 **Black defendants are {(1-black_or)*100:.0f}% less likely** to receive a below-guideline "
                f"sentence compared to White defendants with the same offense, criminal history, and demographics. "
                f"Women are **{(female_or-1)*100:.0f}% more likely** to receive leniency.")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 5: GENDER GAP
# ══════════════════════════════════════════════════════════════
elif page == "👤 Gender Gap":
    st.markdown("""
    <div class="hero-banner">
        <h1>The Gender Gap</h1>
        <p>Men receive dramatically longer sentences than women for the same crimes.</p>
    </div>
    """, unsafe_allow_html=True)

    gender_df = df[df["Sex"].notna()]

    c1, c2 = st.columns(2)
    with c1:
        m_avg = gender_df[gender_df["Sex"] == "Male"]["SENTTOT"].mean()
        st.metric("Male Average Sentence", f"{m_avg:.1f} months")
    with c2:
        f_avg = gender_df[gender_df["Sex"] == "Female"]["SENTTOT"].mean()
        st.metric("Female Average Sentence", f"{f_avg:.1f} months")

    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <span style="font-size: 2.5em; font-weight: 800; color: #E45756;">{m_avg/f_avg:.1f}x</span>
        <span style="font-size: 1.1em; color: #666;"> longer for men overall</span>
    </div>
    """, unsafe_allow_html=True)

    gender_by_off = gender_df.groupby(["Offense", "Sex"])["SENTTOT"].mean().unstack("Sex")
    counts = gender_df.groupby(["Offense", "Sex"])["SENTTOT"].count().unstack("Sex")
    mask = (counts["Male"] >= 50) & (counts["Female"] >= 50)
    gender_by_off = gender_by_off[mask]
    gender_by_off["Gap"] = gender_by_off["Male"] - gender_by_off["Female"]
    gender_by_off = gender_by_off.sort_values("Gap", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=gender_by_off.index, x=gender_by_off["Male"],
                        name="Male", marker_color="#4C78A8", orientation="h"))
    fig.add_trace(go.Bar(y=gender_by_off.index, x=gender_by_off["Female"],
                        name="Female", marker_color="#E45756", orientation="h"))
    fig.update_layout(title="Average Sentence by Gender and Offense",
                     xaxis_title="Average Sentence (months)",
                     height=500, template="plotly_white", barmode="group")
    st.plotly_chart(fig, width="stretch")

    # Get controlled female effect from regression
    overall = run_overall_regression(df)
    female_effect = [c for c in overall["coefficients"] if "Female" in c["variable"]]
    if female_effect:
        fe = abs(female_effect[0]["effect"])
        st.info(f"📌 The gender gap exists across **every major offense type**. "
                f"The controlled regression shows women receive **{fe:.1f} fewer months** "
                "after accounting for offense severity, criminal history, and other factors.")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 6: PLEA VS TRIAL
# ══════════════════════════════════════════════════════════════
elif page == "⚖️ Plea vs Trial":
    st.markdown("""
    <div class="hero-banner">
        <h1>Plea vs Trial</h1>
        <p>The 6th Amendment guarantees the right to trial. But exercising it comes at a cost — and that cost isn't equal.</p>
    </div>
    """, unsafe_allow_html=True)

    plea_df = df[df["Plea Type"].notna() & df["Race"].notna()].copy()

    trial_b = plea_df[(plea_df["Plea Type"] == "Trial") & (plea_df["Race"] == "Black")]["SENTTOT"].mean()
    trial_w = plea_df[(plea_df["Plea Type"] == "Trial") & (plea_df["Race"] == "White")]["SENTTOT"].mean()
    plea_b = plea_df[(plea_df["Plea Type"] == "Plea Deal") & (plea_df["Race"] == "Black")]["SENTTOT"].mean()
    plea_w = plea_df[(plea_df["Plea Type"] == "Plea Deal") & (plea_df["Race"] == "White")]["SENTTOT"].mean()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Plea Deal: B-W Gap", f"{plea_b - plea_w:+.1f} months",
                  help="Black - White average sentence for plea deals")
    with c2:
        st.metric("Trial: B-W Gap", f"{trial_b - trial_w:+.1f} months",
                  delta=f"{(trial_b-trial_w)-(plea_b-plea_w):+.0f} mo wider", delta_color="inverse")
    with c3:
        trial_pct = len(plea_df[plea_df["Plea Type"] == "Trial"]) / len(plea_df) * 100
        st.metric("Cases Going to Trial", f"{trial_pct:.1f}%")

    st.divider()

    plea_stats = plea_df.groupby(["Plea Type", "Race"])["SENTTOT"].agg(["mean", "count"]).reset_index()

    fig = px.bar(plea_stats, x="Plea Type", y="mean", color="Race",
                color_discrete_map=RACE_COLORS, barmode="group",
                labels={"mean": "Average Sentence (months)", "Plea Type": ""},
                title="Average Sentence by Plea Type and Race")
    fig.update_layout(height=500, template="plotly_white")
    st.plotly_chart(fig, width="stretch")

    st.error(f"""📌 **The trial penalty is racially unequal.** When cases go to trial, Black defendants
    receive **{trial_b - trial_w:.0f} months more** than White defendants. For plea deals, the gap
    is smaller. This suggests the disparity may be concentrated in how trials are conducted,
    how juries decide, or how judges sentence after conviction.""")

    st.markdown("### Who Goes to Trial?")
    trial_rates = plea_df.groupby("Race")["Plea Type"].apply(
        lambda x: (x == "Trial").mean() * 100).reset_index()
    trial_rates.columns = ["Race", "Trial Rate %"]

    fig2 = px.bar(trial_rates, x="Race", y="Trial Rate %", color="Race",
                 color_discrete_map=RACE_COLORS,
                 title="% of Cases Going to Trial by Race")
    fig2.update_layout(height=350, template="plotly_white", showlegend=False)
    st.plotly_chart(fig2, width="stretch")

    st.markdown("### Trial Penalty by Offense")
    off_choice = st.selectbox("Select offense",
        ["Drug Trafficking", "Firearms", "Fraud/Theft/Embezzlement", "Robbery"],
        key="plea_offense")

    off_plea = plea_df[plea_df["Offense"] == off_choice]
    off_stats = off_plea.groupby(["Plea Type", "Race"])["SENTTOT"].agg(["mean", "count"]).reset_index()
    off_stats = off_stats[off_stats["count"] >= 10]

    fig3 = px.bar(off_stats, x="Plea Type", y="mean", color="Race",
                 color_discrete_map=RACE_COLORS, barmode="group",
                 labels={"mean": "Average Sentence (months)"},
                 title=f"{off_choice}: Sentence by Plea Type and Race")
    fig3.update_layout(height=450, template="plotly_white")
    st.plotly_chart(fig3, width="stretch")

    st.info("""💡 **Why this matters:** The 6th Amendment guarantees the right to trial. But exercising that right
    comes with a massive "trial penalty" — and that penalty falls harder on Black defendants. This creates
    pressure to accept plea deals, even for those who may be innocent.""")

    st.markdown(FOOTER, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 7: ABOUT
# ══════════════════════════════════════════════════════════════
elif page == "📖 About":
    st.markdown("""
    <div class="hero-banner">
        <h1>About Justice Index</h1>
        <p>Methodology, data sources, limitations, and how to cite this work.</p>
    </div>
    """, unsafe_allow_html=True)

    overall = run_overall_regression(df)
    black_effect = [c for c in overall["coefficients"] if "Black" in c["variable"]][0]["effect"]

    st.markdown(f"""
    ## The Question

    Is the American federal justice system fair? When two people commit the same crime
    with similar backgrounds, do they receive similar sentences — or does race tip the scales?

    ## The Data

    We analyzed **{len(df):,} federal criminal cases** from the
    [US Sentencing Commission](https://www.ussc.gov/research/datafiles/commission-datafiles)
    spanning fiscal years 2019–2024. This is official government data covering every federal
    case sentenced under the US Sentencing Guidelines.

    ## The Method

    **Descriptive comparisons** — Side-by-side average sentences by race, controlling for
    offense type and criminal history level.

    **OLS Regression** — Predicting sentence length while controlling for: offense type (dummy variables),
    guideline range, criminal history points, age, sex, citizenship, and weapon involvement.
    Uses robust standard errors (HC1). R² = {overall['r_squared']:.2f} on {overall['n_obs']:,} cases.

    **Logistic Regression** — Predicting who receives below-guideline sentences (judicial mercy)
    with the same controls.

    ## The Finding

    > After controlling for every legal factor available in the data, **being Black predicts
    > approximately +{black_effect:.1f} extra months** of prison time compared to White defendants.
    > This effect is statistically significant (p < 0.0001) every year from 2019–2024
    > and is **getting worse, not better**.

    ## What We Can't Control For

    - **Attorney quality** — Public defenders vs. expensive private attorneys
    - **Plea deal specifics** — Most cases are plea bargains; the deal terms matter enormously
    - **Judge identity** — Individual judges vary enormously in sentencing patterns
    - **Case circumstances** — Specific details not captured in USSC structured data
    - **Prosecutorial discretion** — Which charges are filed, which are dropped, what deals are offered

    These unmeasured factors mean our estimates could go either way. Some may inflate the gap;
    others may explain part of it. But the consistency across years, offenses, and methods
    makes a strong case that race independently affects federal sentencing outcomes.

    ## How to Cite

    > Beckman, B. (2026). *Justice Index: Racial and Gender Disparities in US Federal Sentencing.*
    > Analysis of US Sentencing Commission Individual Offender data, FY2019–2024.
    > Available at: [justiceindex.org](https://justiceindex.org)

    ## Open Source

    All analysis code is available on [GitHub](https://github.com/brunobossgang/justice-index).
    Data is publicly available from the [US Sentencing Commission](https://www.ussc.gov/research/datafiles/commission-datafiles).

    ---

    *Built by Bruno Beckman. Data from the US Sentencing Commission.*
    """)

    st.markdown(FOOTER, unsafe_allow_html=True)
