"""
╔══════════════════════════════════════════════════════════════════════════╗
║        HDFC Bank: Green Finance & ESG Investment Tracker                 ║
║        Multi-Page Professional Streamlit Dashboard                       ║
║        Pages: Overview | ESG Analysis | Geography | Carbon | ROI         ║
╚══════════════════════════════════════════════════════════════════════════╝

HOW TO RUN:
    1. pip install streamlit plotly pandas numpy openpyxl
    2. Place all 5 CSV files in the SAME folder as this script
    3. streamlit run hdfc_esg_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HDFC Bank: Green Finance & ESG Tracker",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — Dark banking + green accent
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --hdfc-red:   #D32F2F;
    --eco-green:  #00C896;
    --eco-light:  #00FFB3;
    --dark-bg:    #0A0E1A;
    --card-bg:    #111827;
    --card2-bg:   #1A2235;
    --border:     rgba(0,200,150,0.18);
    --text-main:  #E8F5E9;
    --text-muted: #90A4AE;
    --gold:       #FFD700;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--dark-bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-main);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #0A1628 100%) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text-main) !important; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* KPI cards */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,200,150,0.08);
    transition: transform .2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--eco-green);
    margin: 6px 0 2px;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
.kpi-delta { font-size: 0.82rem; color: #69F0AE; margin-top: 4px; }

/* Section titles */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--eco-green);
    border-left: 4px solid var(--eco-green);
    padding-left: 12px;
    margin: 28px 0 16px;
}

/* Page header */
.page-header {
    background: linear-gradient(135deg, #0D2137 0%, #0A1628 60%, #061A14 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
}
.page-header h1 {
    font-size: 2rem;
    font-weight: 800;
    color: var(--eco-green);
    margin: 0 0 4px;
}
.page-header p { color: var(--text-muted); margin: 0; font-size: 0.92rem; }

/* Nav buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    width: 100% !important;
    text-align: left !important;
    padding: 10px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    transition: all .2s !important;
    margin-bottom: 4px !important;
}
.stButton > button:hover {
    background: rgba(0,200,150,0.12) !important;
    border-color: var(--eco-green) !important;
    color: var(--eco-green) !important;
}

/* Plotly chart background */
.js-plotly-plot { border-radius: 14px; overflow: hidden; }

/* Sidebar logo area */
.sidebar-logo {
    background: linear-gradient(135deg, var(--hdfc-red), #B71C1C);
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    margin-bottom: 20px;
}
.sidebar-logo h2 {
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem !important;
    margin: 0 !important;
}
.sidebar-logo p { color: rgba(255,255,255,.7) !important; font-size: .75rem !important; margin: 4px 0 0 !important; }

/* Ribbon / info bar */
.ribbon {
    display: flex;
    gap: 16px;
    background: var(--card2-bg);
    border-radius: 12px;
    padding: 14px 20px;
    border: 1px solid var(--border);
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.ribbon-item { text-align: center; flex: 1; min-width: 100px; }
.ribbon-val { font-weight: 700; color: var(--eco-green); font-size: 1.1rem; }
.ribbon-lbl { font-size: 0.72rem; color: var(--text-muted); }

/* Insight box */
.insight-box {
    background: rgba(0,200,150,0.07);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 10px;
}
.insight-box b { color: var(--eco-green); }

/* Hide streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY DARK TEMPLATE
# ─────────────────────────────────────────────
CHART_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(family="DM Sans", color="#E8F5E9", size=12),
        title_font=dict(family="Syne", color="#E8F5E9", size=15),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#90A4AE")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(color="#90A4AE")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", tickfont=dict(color="#90A4AE")),
        margin=dict(l=20, r=20, t=45, b=20),
    )
)

GREEN_PALETTE = [
    "#00C896","#00FFB3","#26D07C","#69F0AE","#00897B",
    "#1DE9B6","#B2DFDB","#FFD700","#FF6B6B","#A78BFA"
]

def apply_template(fig):
    fig.update_layout(CHART_TEMPLATE["layout"])
    return fig

# ─────────────────────────────────────────────
#  DATA LOADING  (cached — loads only once)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="🌿 Loading ESG data...")
def load_data():
    geo  = pd.read_csv("green_investments_geographic.csv", parse_dates=["Project_Start_Date"])
    cr   = pd.read_csv("carbon_reduction.csv")
    esg  = pd.read_csv("esg_scores_companies.csv")
    roi  = pd.read_csv("roi_returns.csv")
    sec  = pd.read_csv("sector_info.csv", header=None, names=["Sector", "Description"])

    # Merge master table
    master = geo.merge(cr,  on="Project_ID", how="left", suffixes=("","_cr"))
    master = master.merge(roi, on="Project_ID", how="left")
    master = master.merge(esg, on="Company_Name", how="left")

    # Unify Year column
    if "Year_cr" in master.columns:
        master["Year"] = master["Year"].fillna(master["Year_cr"])
        master.drop(columns=["Year_cr"], inplace=True)

    master["Year"] = master["Year"].astype(int)
    master["Investment_Cr"] = master["Investment_Amount_USD"] / 1e7  # USD → Crore (approx)
    return master, esg, sec

try:
    master, esg_df, sector_df = load_data()
    DATA_LOADED = True
except FileNotFoundError as e:
    DATA_LOADED = False
    LOAD_ERROR  = str(e)

# ─────────────────────────────────────────────
#  SIDEBAR  — Navigation + Global Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🏦 HDFC Bank</h2>
        <p>Green Finance & ESG Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📌 Navigation")
    pages = {
        "🏠 Executive Overview":      "overview",
        "🌿 ESG Analysis":            "esg",
        "🗺️ Geographic Intelligence": "geo",
        "🌍 Carbon Reduction":        "carbon",
        "💰 ROI & Returns":           "roi",
        "🔍 Sector Deep Dive":        "sector",
    }

    if "page" not in st.session_state:
        st.session_state.page = "overview"

    for label, key in pages.items():
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key

    # ── Global Slicers ──────────────────────
    if DATA_LOADED:
        st.markdown("---")
        st.markdown("### 🎛️ Global Filters")

        years = sorted(master["Year"].dropna().unique().tolist())
        sel_years = st.select_slider(
            "📅 Year Range",
            options=years,
            value=(min(years), max(years))
        )

        sectors = ["All"] + sorted(master["Sector"].dropna().unique().tolist())
        sel_sector = st.multiselect("🏭 Sector", sectors[1:], default=sectors[1:])

        regions = ["All"] + sorted(master["Region"].dropna().unique().tolist())
        sel_region = st.selectbox("📍 Region", regions)

        risk_cats = ["All", "Low", "Medium", "High"]
        sel_risk = st.selectbox("⚠️ ESG Risk", risk_cats)

        st.markdown("---")
        st.caption("📊 Dashboard v2.0 | HDFC Green Finance")
        st.caption(f"🗂️ {len(master):,} investment records loaded")

# ─────────────────────────────────────────────
#  FILTER HELPER
# ─────────────────────────────────────────────
def apply_filters(df):
    d = df.copy()
    d = d[(d["Year"] >= sel_years[0]) & (d["Year"] <= sel_years[1])]
    if sel_sector:
        d = d[d["Sector"].isin(sel_sector)]
    if sel_region != "All":
        d = d[d["Region"] == sel_region]
    if sel_risk != "All":
        d = d[d["Risk_Category"] == sel_risk]
    return d

# ─────────────────────────────────────────────
#  GUARD: Data not loaded
# ─────────────────────────────────────────────
if not DATA_LOADED:
    st.error(f"❌ CSV files not found: `{LOAD_ERROR}`\n\nPlace all 5 CSV files in the same folder as this script and restart.")
    st.stop()

# ─────────────────────────────────────────────
#  FILTERED MASTER
# ─────────────────────────────────────────────
df = apply_filters(master)

# ══════════════════════════════════════════════
#  PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════
if st.session_state.page == "overview":
    st.markdown("""
    <div class="page-header">
        <h1>🏠 Executive Overview</h1>
        <p>HDFC Bank Green Finance & ESG Investment Tracker — Consolidated Performance Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row ─────────────────────────────
    total_inv   = df["Investment_Amount_USD"].sum() / 1e9
    total_co2   = df["CO2_Reduction_Tons"].sum() / 1e6
    avg_roi     = df["ROI_Percentage"].mean()
    avg_esg     = df["ESG_Score"].mean()
    n_projects  = df["Project_ID"].nunique()
    n_states    = df["State"].nunique()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpis = [
        (c1, f"${total_inv:.2f}B",  "Total Investment",        "↑ Green Portfolio"),
        (c2, f"{total_co2:.2f}M T", "CO₂ Reduced",            "🌍 Carbon Impact"),
        (c3, f"{avg_roi:.1f}%",     "Avg ROI",                 "📈 Returns"),
        (c4, f"{avg_esg:.1f}",      "Avg ESG Score",           "🌿 ESG Health"),
        (c5, f"{n_projects:,}",     "Active Projects",         "🏗️ Initiatives"),
        (c6, f"{n_states}",         "States Covered",          "📍 Reach"),
    ]
    for col, val, lbl, delta in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-delta">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Ribbon summary bar ──────────────────
    total_sectors = df["Sector"].nunique()
    best_sector   = df.groupby("Sector")["Investment_Amount_USD"].sum().idxmax()
    top_region    = df.groupby("Region")["Investment_Amount_USD"].sum().idxmax()
    best_roi_sec  = df.groupby("Sector")["ROI_Percentage"].mean().idxmax()

    st.markdown(f"""
    <div class="ribbon">
        <div class="ribbon-item"><div class="ribbon-val">{total_sectors}</div><div class="ribbon-lbl">Sectors</div></div>
        <div class="ribbon-item"><div class="ribbon-val">{best_sector}</div><div class="ribbon-lbl">Top Invested Sector</div></div>
        <div class="ribbon-item"><div class="ribbon-val">{top_region}</div><div class="ribbon-lbl">Leading Region</div></div>
        <div class="ribbon-item"><div class="ribbon-val">{best_roi_sec}</div><div class="ribbon-lbl">Best ROI Sector</div></div>
        <div class="ribbon-item"><div class="ribbon-val">{sel_years[0]}–{sel_years[1]}</div><div class="ribbon-lbl">Period</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 1: Investment trend + Sector pie ─
    st.markdown('<div class="section-title">📊 Investment Trends & Sector Mix</div>', unsafe_allow_html=True)
    r1c1, r1c2 = st.columns([3, 2])

    with r1c1:
        trend = df.groupby(["Year","Sector"])["Investment_Amount_USD"].sum().reset_index()
        fig = px.area(trend, x="Year", y="Investment_Amount_USD", color="Sector",
                      color_discrete_sequence=GREEN_PALETTE,
                      labels={"Investment_Amount_USD":"Investment (USD)"},
                      title="📈 Annual Investment by Sector (Stacked Area)")
        fig.update_traces(line=dict(width=1.5))
        apply_template(fig)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        pie_data = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
        fig2 = px.pie(pie_data, values="Investment_Amount_USD", names="Sector",
                      color_discrete_sequence=GREEN_PALETTE,
                      hole=0.52, title="🥧 Portfolio Sector Split")
        fig2.update_traces(textinfo="label+percent", textfont_size=11,
                           marker=dict(line=dict(color="#111827", width=2)))
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: ESG dist + CO2 bar + ROI box ─
    st.markdown('<div class="section-title">🌿 ESG, Carbon & ROI Snapshot</div>', unsafe_allow_html=True)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        esg_risk = df.groupby("Risk_Category")["Investment_Amount_USD"].sum().reset_index()
        risk_order = {"Low":0,"Medium":1,"High":2}
        esg_risk["order"] = esg_risk["Risk_Category"].map(risk_order)
        esg_risk = esg_risk.sort_values("order")
        fig3 = px.bar(esg_risk, x="Risk_Category", y="Investment_Amount_USD",
                      color="Risk_Category", text_auto=".2s",
                      color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                      title="⚠️ Investment by ESG Risk Category")
        apply_template(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        co2_yr = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        fig4 = px.bar(co2_yr, x="Year", y="CO2_Reduction_Tons",
                      color="CO2_Reduction_Tons", color_continuous_scale="Greens",
                      text_auto=".2s", title="🌍 CO₂ Reduced Per Year (Tons)")
        apply_template(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    with r2c3:
        roi_sec = df.groupby("Sector")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage", ascending=True)
        fig5 = px.bar(roi_sec, x="ROI_Percentage", y="Sector", orientation="h",
                      color="ROI_Percentage", color_continuous_scale="Teal",
                      text_auto=".1f", title="💰 Avg ROI by Sector (%)")
        apply_template(fig5)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Insight strip ───────────────────────
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>AI Insight:</b> The <b>{best_sector}</b> sector has attracted the highest cumulative investment in the selected period.
    <b>{best_roi_sec}</b> leads in average ROI at <b>{df[df['Sector']==best_roi_sec]['ROI_Percentage'].mean():.1f}%</b>,
    while <b>{top_region}</b> is the dominant geographic region.
    Total CO₂ avoided: <b>{total_co2:.2f} Million Tonnes</b> — equivalent to removing ~{total_co2/4.6:.1f}M cars from roads for a year.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  PAGE 2 — ESG ANALYSIS
# ══════════════════════════════════════════════
elif st.session_state.page == "esg":
    st.markdown("""
    <div class="page-header">
        <h1>🌿 ESG Analysis</h1>
        <p>Environmental, Social & Governance deep-dive across companies and risk tiers</p>
    </div>
    """, unsafe_allow_html=True)

    # ── ESG Score distribution histogram ────
    st.markdown('<div class="section-title">📊 ESG Score Distribution</div>', unsafe_allow_html=True)
    hc1, hc2 = st.columns([3,2])

    with hc1:
        fig = px.histogram(df.dropna(subset=["ESG_Score"]), x="ESG_Score",
                           color="Risk_Category", nbins=40, barmode="overlay",
                           color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                           title="📊 ESG Score Distribution by Risk Category")
        fig.update_layout(bargap=0.05)
        apply_template(fig)
        st.plotly_chart(fig, use_container_width=True)

    with hc2:
        risk_counts = df["Risk_Category"].value_counts().reset_index()
        risk_counts.columns = ["Risk_Category","Count"]
        fig2 = px.pie(risk_counts, values="Count", names="Risk_Category",
                      color="Risk_Category", hole=0.6,
                      color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                      title="🥧 Risk Category Split")
        fig2.update_traces(textinfo="label+percent")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── ESG Score vs ROI scatter (bubble) ───
    st.markdown('<div class="section-title">🔬 ESG Score vs ROI Bubble Chart</div>', unsafe_allow_html=True)
    bubble_df = df.dropna(subset=["ESG_Score","ROI_Percentage"]).groupby("Company_Name").agg(
        ESG_Score=("ESG_Score","first"),
        ROI_Percentage=("ROI_Percentage","mean"),
        Investment=("Investment_Amount_USD","sum"),
        Risk_Category=("Risk_Category","first"),
        Sector=("Sector","first")
    ).reset_index()

    fig3 = px.scatter(bubble_df, x="ESG_Score", y="ROI_Percentage",
                      size="Investment", color="Risk_Category",
                      hover_name="Company_Name", hover_data={"Sector":True},
                      color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                      size_max=30, opacity=0.75,
                      title="🔬 ESG Score vs ROI — Bubble = Investment Size")
    fig3.add_vline(x=bubble_df["ESG_Score"].mean(), line_dash="dash", line_color="#90A4AE",
                   annotation_text="Avg ESG", annotation_position="top right")
    fig3.add_hline(y=bubble_df["ROI_Percentage"].mean(), line_dash="dash", line_color="#90A4AE",
                   annotation_text="Avg ROI", annotation_position="top right")
    apply_template(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # ── ESG by Sector violin + box ───────────
    st.markdown('<div class="section-title">🎻 ESG Score by Sector</div>', unsafe_allow_html=True)
    vc1, vc2 = st.columns(2)

    with vc1:
        fig4 = px.violin(df.dropna(subset=["ESG_Score","Sector"]), x="Sector", y="ESG_Score",
                         box=True, color="Sector", color_discrete_sequence=GREEN_PALETTE,
                         title="🎻 ESG Distribution per Sector (Violin)")
        apply_template(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    with vc2:
        esg_sec_avg = df.groupby("Sector")["ESG_Score"].mean().reset_index().sort_values("ESG_Score", ascending=False)
        fig5 = px.bar(esg_sec_avg, x="ESG_Score", y="Sector", orientation="h",
                      color="ESG_Score", color_continuous_scale="Greens",
                      text_auto=".1f", title="📊 Avg ESG Score by Sector")
        apply_template(fig5)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Decomposition Tree (ESG Risk → Sector → Region) ─
    st.markdown('<div class="section-title">🌳 Decomposition Tree: Investment by Risk → Sector → Region</div>', unsafe_allow_html=True)
    tree_df = df.groupby(["Risk_Category","Sector","Region"])["Investment_Amount_USD"].sum().reset_index()
    fig6 = px.treemap(tree_df, path=["Risk_Category","Sector","Region"],
                      values="Investment_Amount_USD",
                      color="Investment_Amount_USD", color_continuous_scale="Greens",
                      title="🌳 Decomposition Tree: Risk → Sector → Region → Investment")
    fig6.update_traces(textinfo="label+value+percent entry")
    apply_template(fig6)
    st.plotly_chart(fig6, use_container_width=True)

    # ── Top 10 companies ────────────────────
    st.markdown('<div class="section-title">🏆 Top 10 Companies by ESG Score</div>', unsafe_allow_html=True)
    top_esg = df.dropna(subset=["ESG_Score"]).groupby("Company_Name").agg(
        ESG_Score=("ESG_Score","first"),
        Investment=("Investment_Amount_USD","sum"),
        Risk=("Risk_Category","first")
    ).sort_values("ESG_Score", ascending=False).head(10).reset_index()

    fig7 = px.bar(top_esg, x="Company_Name", y="ESG_Score",
                  color="Risk", text="ESG_Score",
                  color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                  title="🏆 Top 10 Companies — ESG Score")
    fig7.update_traces(textposition="outside")
    apply_template(fig7)
    st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════
#  PAGE 3 — GEOGRAPHIC INTELLIGENCE
# ══════════════════════════════════════════════
elif st.session_state.page == "geo":
    st.markdown("""
    <div class="page-header">
        <h1>🗺️ Geographic Intelligence</h1>
        <p>Regional investment patterns, state-level breakdown & spatial analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Region Bar ──────────────────────────
    st.markdown('<div class="section-title">📍 Investment by Region</div>', unsafe_allow_html=True)
    gc1, gc2 = st.columns([3,2])

    with gc1:
        reg_inv = df.groupby(["Region","Year"])["Investment_Amount_USD"].sum().reset_index()
        fig = px.bar(reg_inv, x="Year", y="Investment_Amount_USD", color="Region",
                     barmode="group", color_discrete_sequence=GREEN_PALETTE,
                     text_auto=".2s", title="📍 Regional Investment by Year")
        apply_template(fig)
        st.plotly_chart(fig, use_container_width=True)

    with gc2:
        reg_total = df.groupby("Region")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD", ascending=False)
        fig2 = px.funnel(reg_total, x="Investment_Amount_USD", y="Region",
                         color_discrete_sequence=GREEN_PALETTE,
                         title="🏆 Region Investment Funnel")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── State level ─────────────────────────
    st.markdown('<div class="section-title">🗺️ State-Level Investment Heatmap</div>', unsafe_allow_html=True)
    state_inv = df.groupby("State")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD", ascending=False)

    fig3 = px.bar(state_inv.head(20), x="State", y="Investment_Amount_USD",
                  color="Investment_Amount_USD", color_continuous_scale="Greens",
                  text_auto=".2s", title="🗺️ Top 20 States by Green Investment")
    fig3.update_xaxes(tickangle=35)
    apply_template(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # ── Sector × Region heatmap ─────────────
    st.markdown('<div class="section-title">🔥 Sector × Region Investment Heatmap</div>', unsafe_allow_html=True)
    heat = df.groupby(["Sector","Region"])["Investment_Amount_USD"].sum().reset_index()
    heat_pivot = heat.pivot(index="Sector", columns="Region", values="Investment_Amount_USD").fillna(0)

    fig4 = go.Figure(data=go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale="Greens",
        text=heat_pivot.values.round(0),
        texttemplate="%{text:.2s}",
        hoverongaps=False,
    ))
    fig4.update_layout(title="🔥 Investment Heatmap: Sector × Region",
                       **CHART_TEMPLATE["layout"])
    st.plotly_chart(fig4, use_container_width=True)

    # ── City-level Top 15 + Quarter ─────────
    st.markdown('<div class="section-title">🏙️ City Investment & Quarterly Patterns</div>', unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)

    with cc1:
        city_inv = df.groupby("City")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(15)
        fig5 = px.bar(city_inv, x="City", y="Investment_Amount_USD",
                      color="Investment_Amount_USD", color_continuous_scale="Greens",
                      text_auto=".2s", title="🏙️ Top 15 Cities by Investment")
        fig5.update_xaxes(tickangle=35)
        apply_template(fig5)
        st.plotly_chart(fig5, use_container_width=True)

    with cc2:
        qtr_inv = df.groupby("Quarter")["Investment_Amount_USD"].sum().reset_index()
        qtr_order = {"Q1":0,"Q2":1,"Q3":2,"Q4":3}
        qtr_inv["order"] = qtr_inv["Quarter"].map(qtr_order)
        qtr_inv = qtr_inv.sort_values("order")
        fig6 = px.bar(qtr_inv, x="Quarter", y="Investment_Amount_USD",
                      color="Quarter", text_auto=".2s",
                      color_discrete_sequence=GREEN_PALETTE,
                      title="📅 Investment by Quarter")
        apply_template(fig6)
        st.plotly_chart(fig6, use_container_width=True)

    # ── Month heatmap ───────────────────────
    st.markdown('<div class="section-title">📆 Monthly Investment Heatmap</div>', unsafe_allow_html=True)
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    month_pivot = df.groupby(["Year","Month_Name"])["Investment_Amount_USD"].sum().reset_index()
    month_pivot["Month_Name"] = pd.Categorical(month_pivot["Month_Name"], categories=month_order, ordered=True)
    month_pivot = month_pivot.sort_values("Month_Name")
    m_piv = month_pivot.pivot(index="Year", columns="Month_Name", values="Investment_Amount_USD").fillna(0)

    fig7 = go.Figure(data=go.Heatmap(
        z=m_piv.values, x=m_piv.columns.tolist(), y=m_piv.index.tolist(),
        colorscale="Greens", texttemplate="%{z:.2s}", hoverongaps=False
    ))
    fig7.update_layout(title="📆 Monthly Investment Heatmap (Year × Month)", **CHART_TEMPLATE["layout"])
    st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════
#  PAGE 4 — CARBON REDUCTION
# ══════════════════════════════════════════════
elif st.session_state.page == "carbon":
    st.markdown("""
    <div class="page-header">
        <h1>🌍 Carbon Reduction Analysis</h1>
        <p>CO₂ impact tracking, sector-level emission abatement & efficiency metrics</p>
    </div>
    """, unsafe_allow_html=True)

    total_co2  = df["CO2_Reduction_Tons"].sum()
    avg_co2    = df["CO2_Reduction_Tons"].mean()
    max_co2_yr = df.groupby("Year")["CO2_Reduction_Tons"].sum().idxmax()
    eff_ratio  = df["Investment_Amount_USD"].sum() / (total_co2 + 1) 

    c1,c2,c3,c4 = st.columns(4)
    for col, val, lbl in [
        (c1, f"{total_co2/1e6:.2f}M T", "Total CO₂ Reduced"),
        (c2, f"{avg_co2:,.0f} T",       "Avg per Project"),
        (c3, str(max_co2_yr),           "Peak Year"),
        (c4, f"${eff_ratio:.0f}",       "USD per Tonne CO₂"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CO2 trend + sector ──────────────────
    st.markdown('<div class="section-title">📈 Carbon Reduction Trends</div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)

    with tc1:
        co2_yr = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=co2_yr["Year"], y=co2_yr["CO2_Reduction_Tons"],
                                 mode="lines+markers",
                                 line=dict(color="#00C896", width=3),
                                 marker=dict(size=8, color="#00FFB3"),
                                 fill="tozeroy", fillcolor="rgba(0,200,150,0.12)",
                                 name="CO₂ Reduced"))
        fig.update_layout(title="📈 Annual CO₂ Reduction Trend", **CHART_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with tc2:
        co2_sec = df.groupby("Sector")["CO2_Reduction_Tons"].sum().reset_index().sort_values("CO2_Reduction_Tons",ascending=True)
        fig2 = px.bar(co2_sec, x="CO2_Reduction_Tons", y="Sector", orientation="h",
                      color="CO2_Reduction_Tons", color_continuous_scale="Greens",
                      text_auto=".2s", title="🌱 CO₂ Reduced by Sector")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── CO2 Year × Sector heatmap ───────────
    st.markdown('<div class="section-title">🔥 Carbon Heatmap: Year × Sector</div>', unsafe_allow_html=True)
    co2_pivot = df.groupby(["Year","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    co2_piv = co2_pivot.pivot(index="Sector", columns="Year", values="CO2_Reduction_Tons").fillna(0)
    fig3 = go.Figure(go.Heatmap(
        z=co2_piv.values, x=co2_piv.columns.tolist(), y=co2_piv.index.tolist(),
        colorscale="Greens", texttemplate="%{z:.2s}"
    ))
    fig3.update_layout(title="🔥 Carbon Reduction Heatmap (Sector × Year)", **CHART_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    # ── CO2 per $M invested (efficiency) ────
    st.markdown('<div class="section-title">⚡ Carbon Efficiency: CO₂ per $M Invested</div>', unsafe_allow_html=True)
    eff_df = df.groupby("Sector").agg(
        CO2=("CO2_Reduction_Tons","sum"),
        Inv=("Investment_Amount_USD","sum")
    ).reset_index()
    eff_df["CO2_per_M"] = eff_df["CO2"] / (eff_df["Inv"] / 1e6)
    fig4 = px.bar(eff_df.sort_values("CO2_per_M",ascending=False),
                  x="Sector", y="CO2_per_M",
                  color="CO2_per_M", color_continuous_scale="Greens",
                  text_auto=".1f",
                  title="⚡ CO₂ Reduced per $1M Invested (Sector Efficiency)")
    apply_template(fig4)
    st.plotly_chart(fig4, use_container_width=True)

    # ── Region + CO2 sunburst ───────────────
    st.markdown('<div class="section-title">☀️ Carbon Sunburst: Region → Sector</div>', unsafe_allow_html=True)
    sun_df = df.groupby(["Region","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    fig5 = px.sunburst(sun_df, path=["Region","Sector"], values="CO2_Reduction_Tons",
                       color="CO2_Reduction_Tons", color_continuous_scale="Greens",
                       title="☀️ CO₂ Sunburst: Region → Sector")
    apply_template(fig5)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Carbon Insight:</b> The portfolio has collectively avoided <b>{total_co2/1e6:.2f} Million Tonnes</b> of CO₂.
    Cost efficiency stands at <b>${eff_ratio:.0f} per tonne</b> — compared to the global carbon credit average of ~$50–80/tonne,
    HDFC's green portfolio shows <b>strong environmental leverage</b>.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  PAGE 5 — ROI & RETURNS
# ══════════════════════════════════════════════
elif st.session_state.page == "roi":
    st.markdown("""
    <div class="page-header">
        <h1>💰 ROI & Returns Analysis</h1>
        <p>Return on investment deep-dive, risk-adjusted performance & portfolio optimization signals</p>
    </div>
    """, unsafe_allow_html=True)

    avg_roi  = df["ROI_Percentage"].mean()
    med_roi  = df["ROI_Percentage"].median()
    max_roi  = df["ROI_Percentage"].max()
    roi_std  = df["ROI_Percentage"].std()
    sharpe   = avg_roi / (roi_std + 0.001)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, val, lbl in [
        (c1, f"{avg_roi:.2f}%", "Avg ROI"),
        (c2, f"{med_roi:.2f}%", "Median ROI"),
        (c3, f"{max_roi:.2f}%", "Max ROI"),
        (c4, f"{roi_std:.2f}%", "Volatility (σ)"),
        (c5, f"{sharpe:.2f}",   "Sharpe-Like Ratio"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROI trend + sector box ───────────────
    st.markdown('<div class="section-title">📈 ROI Trends & Distribution</div>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)

    with rc1:
        roi_yr = df.groupby("Year")["ROI_Percentage"].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=roi_yr["Year"], y=roi_yr["ROI_Percentage"],
                                 mode="lines+markers",
                                 line=dict(color="#FFD700", width=3),
                                 marker=dict(size=8, color="#FFD700"),
                                 fill="tozeroy", fillcolor="rgba(255,215,0,0.1)",
                                 name="Avg ROI"))
        fig.update_layout(title="📈 Average ROI Trend by Year", **CHART_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with rc2:
        fig2 = px.box(df.dropna(subset=["ROI_Percentage","Sector"]),
                      x="Sector", y="ROI_Percentage",
                      color="Sector", color_discrete_sequence=GREEN_PALETTE,
                      title="📦 ROI Distribution by Sector (Box Plot)")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── ROI histogram + ROI × ESG ───────────
    st.markdown('<div class="section-title">🔍 ROI Deep Dive</div>', unsafe_allow_html=True)
    rd1, rd2 = st.columns(2)

    with rd1:
        fig3 = px.histogram(df.dropna(subset=["ROI_Percentage"]), x="ROI_Percentage",
                            color="Sector", nbins=50, barmode="overlay",
                            color_discrete_sequence=GREEN_PALETTE,
                            title="📊 ROI Distribution Histogram")
        apply_template(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    with rd2:
        roi_risk = df.groupby("Risk_Category")["ROI_Percentage"].mean().reset_index()
        fig4 = px.bar(roi_risk, x="Risk_Category", y="ROI_Percentage",
                      color="Risk_Category",
                      color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                      text_auto=".2f",
                      title="⚠️ Avg ROI by ESG Risk Category")
        apply_template(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Investment vs ROI scatter ────────────
    st.markdown('<div class="section-title">💹 Investment Size vs ROI</div>', unsafe_allow_html=True)
    scatter_df = df.dropna(subset=["Investment_Amount_USD","ROI_Percentage","ESG_Score"])
    fig5 = px.scatter(scatter_df.sample(min(5000,len(scatter_df))),
                      x="Investment_Amount_USD", y="ROI_Percentage",
                      color="Sector", size="ESG_Score", opacity=0.65,
                      hover_data=["Company_Name","State","Year"],
                      color_discrete_sequence=GREEN_PALETTE,
                      size_max=20,
                      title="💹 Investment Amount vs ROI (Size = ESG Score)")
    fig5.update_xaxes(type="log", title="Investment (USD, log scale)")
    apply_template(fig5)
    st.plotly_chart(fig5, use_container_width=True)

    # ── ROI by Region ────────────────────────
    st.markdown('<div class="section-title">📍 ROI by Region & Quarter</div>', unsafe_allow_html=True)
    rrc1, rrc2 = st.columns(2)

    with rrc1:
        roi_reg = df.groupby("Region")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage",ascending=False)
        fig6 = px.bar(roi_reg, x="Region", y="ROI_Percentage",
                      color="ROI_Percentage", color_continuous_scale="Teal",
                      text_auto=".1f", title="📍 Avg ROI by Region")
        apply_template(fig6)
        st.plotly_chart(fig6, use_container_width=True)

    with rrc2:
        qtr_order = {"Q1":0,"Q2":1,"Q3":2,"Q4":3}
        roi_q = df.groupby("Quarter")["ROI_Percentage"].mean().reset_index()
        roi_q["ord"] = roi_q["Quarter"].map(qtr_order)
        roi_q = roi_q.sort_values("ord")
        fig7 = px.line(roi_q, x="Quarter", y="ROI_Percentage",
                       markers=True, line_shape="spline",
                       color_discrete_sequence=["#FFD700"],
                       title="📅 Avg ROI by Quarter")
        apply_template(fig7)
        st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════════
#  PAGE 6 — SECTOR DEEP DIVE
# ══════════════════════════════════════════════
elif st.session_state.page == "sector":
    st.markdown("""
    <div class="page-header">
        <h1>🔍 Sector Deep Dive</h1>
        <p>Granular sector analysis — investment, performance, carbon & ESG metrics</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sector selector ──────────────────────
    available_sectors = sorted(df["Sector"].dropna().unique().tolist())
    chosen_sector = st.selectbox("🏭 Select Sector for Deep Dive", available_sectors)
    sec_df = df[df["Sector"] == chosen_sector]

    s_inv  = sec_df["Investment_Amount_USD"].sum() / 1e9
    s_co2  = sec_df["CO2_Reduction_Tons"].sum() / 1e6
    s_roi  = sec_df["ROI_Percentage"].mean()
    s_esg  = sec_df["ESG_Score"].mean()
    s_proj = sec_df["Project_ID"].nunique()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, val, lbl in [
        (c1, f"${s_inv:.2f}B",  f"{chosen_sector} Investment"),
        (c2, f"{s_co2:.2f}M T", "CO₂ Reduced"),
        (c3, f"{s_roi:.2f}%",   "Avg ROI"),
        (c4, f"{s_esg:.1f}",    "Avg ESG Score"),
        (c5, f"{s_proj:,}",     "Projects"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sector description ───────────────────
    sec_desc = sector_df[sector_df["Sector"] == chosen_sector]["Description"].values
    if len(sec_desc):
        st.info(f"📋 **{chosen_sector}**: {sec_desc[0]}")

    # ── Trend charts ─────────────────────────
    st.markdown('<div class="section-title">📈 Investment & Carbon Trends</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)

    with sc1:
        yr_data = sec_df.groupby("Year").agg(
            Investment=("Investment_Amount_USD","sum"),
            CO2=("CO2_Reduction_Tons","sum"),
            ROI=("ROI_Percentage","mean")
        ).reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=yr_data["Year"], y=yr_data["Investment"],
                             name="Investment (USD)", marker_color="#00C896"), secondary_y=False)
        fig.add_trace(go.Scatter(x=yr_data["Year"], y=yr_data["ROI"],
                                 mode="lines+markers", name="ROI %",
                                 line=dict(color="#FFD700",width=3),
                                 marker=dict(size=7)), secondary_y=True)
        fig.update_layout(title=f"📈 {chosen_sector}: Investment & ROI by Year", **CHART_TEMPLATE["layout"])
        fig.update_yaxes(title_text="Investment (USD)", secondary_y=False)
        fig.update_yaxes(title_text="ROI %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with sc2:
        co2_yr = sec_df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        fig2 = px.area(co2_yr, x="Year", y="CO2_Reduction_Tons",
                       color_discrete_sequence=["#00C896"],
                       title=f"🌍 {chosen_sector}: CO₂ Reduction Trend")
        fig2.update_traces(fill="tozeroy", fillcolor="rgba(0,200,150,0.15)")
        apply_template(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # ── State + Risk breakdown ───────────────
    st.markdown('<div class="section-title">🗺️ Geographic & Risk Breakdown</div>', unsafe_allow_html=True)
    scc1, scc2 = st.columns(2)

    with scc1:
        st_data = sec_df.groupby("State")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(12)
        fig3 = px.bar(st_data, x="State", y="Investment_Amount_USD",
                      color="Investment_Amount_USD", color_continuous_scale="Greens",
                      text_auto=".2s", title=f"🗺️ {chosen_sector}: Top States")
        fig3.update_xaxes(tickangle=35)
        apply_template(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    with scc2:
        risk_data = sec_df["Risk_Category"].value_counts().reset_index()
        risk_data.columns = ["Risk","Count"]
        fig4 = px.pie(risk_data, values="Count", names="Risk", hole=0.55,
                      color="Risk",
                      color_discrete_map={"Low":"#00C896","Medium":"#FFD700","High":"#FF6B6B"},
                      title=f"⚠️ {chosen_sector}: ESG Risk Split")
        apply_template(fig4)
        st.plotly_chart(fig4, use_container_width=True)

    # ── All sectors comparison radar ─────────
    st.markdown('<div class="section-title">🕸️ All Sectors Comparison Radar</div>', unsafe_allow_html=True)
    radar_df = df.groupby("Sector").agg(
        ROI=("ROI_Percentage","mean"),
        ESG=("ESG_Score","mean"),
        CO2=("CO2_Reduction_Tons","mean"),
        Inv=("Investment_Amount_USD","mean"),
    ).reset_index()

    # Normalize 0-100
    for col in ["ROI","ESG","CO2","Inv"]:
        mn, mx = radar_df[col].min(), radar_df[col].max()
        radar_df[col+"_n"] = ((radar_df[col]-mn)/(mx-mn+1e-9))*100

    fig5 = go.Figure()
    for i, row in radar_df.iterrows():
        fig5.add_trace(go.Scatterpolar(
            r=[row["ROI_n"], row["ESG_n"], row["CO2_n"], row["Inv_n"], row["ROI_n"]],
            theta=["ROI","ESG Score","CO₂ Reduction","Investment","ROI"],
            name=row["Sector"],
            mode="lines+markers",
            line=dict(color=GREEN_PALETTE[i % len(GREEN_PALETTE)], width=2),
        ))
    fig5.update_layout(
        polar=dict(bgcolor="#111827",
                   radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.1)",color="#90A4AE"),
                   angularaxis=dict(gridcolor="rgba(255,255,255,0.1)",color="#90A4AE")),
        title="🕸️ Sector Comparison Radar (Normalized)",
        **CHART_TEMPLATE["layout"]
    )
    st.plotly_chart(fig5, use_container_width=True)

    # ── Waterfall: Investment progression ────
    st.markdown('<div class="section-title">🌊 Investment Waterfall by Year</div>', unsafe_allow_html=True)
    wf_data = sec_df.groupby("Year")["Investment_Amount_USD"].sum().reset_index().sort_values("Year")
    wf_data["delta"] = wf_data["Investment_Amount_USD"].diff().fillna(wf_data["Investment_Amount_USD"])

    fig6 = go.Figure(go.Waterfall(
        x=wf_data["Year"].astype(str).tolist(),
        y=wf_data["delta"].tolist(),
        measure=["absolute"] + ["relative"]*(len(wf_data)-1),
        connector=dict(line=dict(color="#90A4AE")),
        increasing=dict(marker_color="#00C896"),
        decreasing=dict(marker_color="#FF6B6B"),
        totals=dict(marker_color="#FFD700"),
    ))
    fig6.update_layout(title=f"🌊 {chosen_sector}: Investment Waterfall (Year-over-Year)",
                       **CHART_TEMPLATE["layout"])
    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:24px 0 8px; color:#37474F; font-size:0.78rem;">
    🌿 HDFC Bank Green Finance & ESG Investment Tracker &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; Data refreshes on filter change
</div>
""", unsafe_allow_html=True)