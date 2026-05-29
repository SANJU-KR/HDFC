"""
HDFC Bank Green Finance & ESG Investment Tracker
Paste this file as: hdfc_esg_dashboard.py

Required CSV files in the same GitHub repo folder:
- green_investments_geographic.csv
- carbon_reduction.csv
- esg_scores_companies.csv
- roi_returns.csv
- sector_info.csv
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="HDFC Bank Green Finance & ESG",
    page_icon="HDFC",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = (
    "<style>\n"
    ":root{--bg:#050914;--panel:#101827;--panel2:#132033;--line:rgba(255,255,255,.09);"
    "--text:#F8FAFC;--muted:#94A3B8;--green:#20C48A;--blue:#3B82F6;--gold:#F59E0B;--red:#EF4444;}\n"
    "html,body,[data-testid='stAppViewContainer']{background:var(--bg);color:var(--text);}\n"
    "[data-testid='block-container']{padding:1.3rem 2rem 2rem;max-width:1450px;}\n"
    "[data-testid='stSidebar']{background:#07111f;border-right:1px solid var(--line);}\n"
    "h1,h2,h3,p,span,label{font-family:Inter,Arial,sans-serif;}\n"
    ".page-head{background:linear-gradient(135deg,#12213a,#08271d);border:1px solid var(--line);"
    "border-radius:14px;padding:20px 24px;margin-bottom:18px;}\n"
    ".page-head h1{font-size:1.55rem;margin:0;color:#fff;}\n"
    ".page-head p{font-size:.86rem;color:var(--muted);margin:.25rem 0 0;}\n"
    ".kpi{background:rgba(16,24,39,.88);border:1px solid var(--line);border-radius:12px;"
    "padding:16px;min-height:112px;}\n"
    ".kpi .v{font-size:1.58rem;font-weight:800;color:#fff;line-height:1.1;}\n"
    ".kpi .l{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:7px;}\n"
    ".kpi .d{font-size:.76rem;color:var(--green);margin-top:8px;font-weight:700;}\n"
    ".sec{font-size:1.02rem;font-weight:800;color:#fff;border-bottom:1px solid var(--line);"
    "padding-bottom:8px;margin:24px 0 14px;}\n"
    ".insight{background:rgba(32,196,138,.07);border:1px solid rgba(32,196,138,.24);"
    "border-left:4px solid var(--green);border-radius:10px;padding:14px 16px;color:#DFFCF1;"
    "line-height:1.55;font-size:.9rem;margin:12px 0;}\n"
    ".small{color:var(--muted);font-size:.82rem;}\n"
    "#MainMenu,footer,header{visibility:hidden;}\n"
    "</style>"
)
st.markdown(CSS, unsafe_allow_html=True)

PAL = ["#20C48A", "#3B82F6", "#F59E0B", "#EF4444", "#A78BFA", "#14B8A6"]
RISK_C = {"Low": "#10B981", "Medium": "#F59E0B", "High": "#EF4444"}

STATE_LL = {
    "Bihar": (25.10, 85.31),
    "Chhattisgarh": (21.28, 81.87),
    "Delhi": (28.70, 77.10),
    "Gujarat": (22.26, 71.19),
    "Haryana": (29.06, 76.09),
    "Karnataka": (15.32, 75.71),
    "Madhya Pradesh": (22.97, 78.66),
    "Maharashtra": (19.75, 75.71),
    "Odisha": (20.95, 85.10),
    "Punjab": (31.15, 75.34),
    "Rajasthan": (27.02, 74.22),
    "Tamil Nadu": (11.13, 78.66),
    "Telangana": (18.11, 79.02),
    "Uttar Pradesh": (26.85, 80.95),
    "West Bengal": (22.99, 87.86),
}


def money(x):
    if pd.isna(x):
        return "-"
    x = float(x)
    if abs(x) >= 1e9:
        return f"${x / 1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"${x / 1e6:.1f}M"
    return f"${x:,.0f}"


def pct(x):
    return "-" if pd.isna(x) else f"{x:.1f}%"


def safe_div(a, b, default=np.nan):
    if b is None or pd.isna(b) or b == 0:
        return default
    return a / b


def weighted_avg(df, value_col, weight_col):
    x = df[[value_col, weight_col]].dropna()
    if x.empty or x[weight_col].sum() == 0:
        return np.nan
    return np.average(x[value_col], weights=x[weight_col])


def page_head(title, subtitle):
    st.markdown(
        f"<div class='page-head'><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f"<div class='sec'>{title}</div>", unsafe_allow_html=True)


def kpi_card(value, label, delta=""):
    return (
        f"<div class='kpi'><div class='v'>{value}</div>"
        f"<div class='l'>{label}</div><div class='d'>{delta}</div></div>"
    )


def plot(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def table(df, **kwargs):
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)


def apply_layout(fig, title, height=360):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#F8FAFC", size=15), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter,Arial", size=11),
        height=height,
        margin=dict(l=10, r=10, t=52, b=25),
        legend=dict(orientation="h", y=1.04, x=1, xanchor="right"),
        hoverlabel=dict(bgcolor="#111827", font_color="#fff"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False)
    return fig


def require_columns(df, table_name, columns):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{table_name} is missing columns: {', '.join(missing)}")


def cardinality(left, right, key):
    left_unique = left[key].nunique(dropna=True) == len(left)
    right_unique = right[key].nunique(dropna=True) == len(right)
    if left_unique and right_unique:
        return "1:1"
    if left_unique and not right_unique:
        return "1:M"
    if not left_unique and right_unique:
        return "M:1"
    return "M:M"


def relationship_row(raw, left_name, right_name, key, expected, meaning):
    left = raw[left_name]
    right = raw[right_name]
    detected = cardinality(left, right, key)
    left_coverage = left[key].isin(right[key]).mean() * 100
    right_coverage = right[key].isin(left[key]).mean() * 100
    return {
        "Left Table": left_name,
        "Right Table": right_name,
        "Key": key,
        "Expected": expected,
        "Detected": detected,
        "Left Rows": len(left),
        "Right Rows": len(right),
        "Left Key Duplicates": int(left[key].duplicated().sum()),
        "Right Key Duplicates": int(right[key].duplicated().sum()),
        "Left Coverage %": left_coverage,
        "Right Coverage %": right_coverage,
        "Status": "Pass"
        if detected == expected and left_coverage == 100 and right_coverage == 100
        else "Review",
        "Business Meaning": meaning,
    }


@st.cache_data(show_spinner="Loading ESG datasets...")
def load_data():
    geo = pd.read_csv(BASE_DIR / "green_investments_geographic.csv")
    carbon = pd.read_csv(BASE_DIR / "carbon_reduction.csv")
    esg = pd.read_csv(BASE_DIR / "esg_scores_companies.csv")
    roi = pd.read_csv(BASE_DIR / "roi_returns.csv")
    sector = pd.read_csv(BASE_DIR / "sector_info.csv", header=None, names=["Sector", "Description"])

    require_columns(
        geo,
        "green_investments_geographic.csv",
        [
            "Project_ID",
            "Company_Name",
            "Sector",
            "Investment_Amount_USD",
            "Project_Start_Date",
            "Region",
            "State",
            "City",
            "Year",
            "Month",
            "Month_Name",
            "Quarter",
        ],
    )
    require_columns(carbon, "carbon_reduction.csv", ["Project_ID", "Year", "CO2_Reduction_Tons"])
    require_columns(roi, "roi_returns.csv", ["Project_ID", "ROI_Percentage"])
    require_columns(esg, "esg_scores_companies.csv", ["Company_Name", "ESG_Score", "Risk_Category"])
    require_columns(sector, "sector_info.csv", ["Sector", "Description"])

    geo["Project_Start_Date"] = pd.to_datetime(geo["Project_Start_Date"], errors="coerce")

    raw = {
        "green_investments_geographic": geo,
        "carbon_reduction": carbon,
        "roi_returns": roi,
        "esg_scores_companies": esg,
        "sector_info": sector,
    }

    relationships = pd.DataFrame(
        [
            relationship_row(
                raw,
                "green_investments_geographic",
                "carbon_reduction",
                "Project_ID",
                "1:1",
                "Each financed project has one carbon impact record.",
            ),
            relationship_row(
                raw,
                "green_investments_geographic",
                "roi_returns",
                "Project_ID",
                "1:1",
                "Each financed project has one ROI record.",
            ),
            relationship_row(
                raw,
                "esg_scores_companies",
                "green_investments_geographic",
                "Company_Name",
                "1:M",
                "One company ESG profile supports many project rows.",
            ),
            relationship_row(
                raw,
                "sector_info",
                "green_investments_geographic",
                "Sector",
                "1:M",
                "One sector definition supports many project rows.",
            ),
        ]
    )

    master = geo.rename(columns={"Year": "Project_Year"}).merge(
        carbon.rename(columns={"Year": "CO2_Report_Year"}),
        on="Project_ID",
        how="left",
        validate="one_to_one",
    )
    master = master.merge(roi, on="Project_ID", how="left", validate="one_to_one")
    master = master.merge(esg, on="Company_Name", how="left", validate="many_to_one")
    master = master.merge(sector, on="Sector", how="left", validate="many_to_one")

    master["Project_Year"] = pd.to_numeric(master["Project_Year"], errors="coerce").astype("Int64")
    master["CO2_Report_Year"] = pd.to_numeric(master["CO2_Report_Year"], errors="coerce").astype("Int64")
    master["Year"] = master["Project_Year"].astype(int)
    master["Investment_M"] = master["Investment_Amount_USD"] / 1e6
    master["Estimated_Return_USD"] = master["Investment_Amount_USD"] * master["ROI_Percentage"] / 100
    master["CO2_per_Million_USD"] = master["CO2_Reduction_Tons"] / (
        master["Investment_Amount_USD"] / 1e6
    )
    master["USD_per_Ton_CO2"] = master["Investment_Amount_USD"] / master[
        "CO2_Reduction_Tons"
    ].replace(0, np.nan)
    master["Risk_Score"] = master["Risk_Category"].map({"Low": 1, "Medium": 2, "High": 3})
    master["lat"] = master["State"].map(lambda s: STATE_LL.get(s, (None, None))[0])
    master["lon"] = master["State"].map(lambda s: STATE_LL.get(s, (None, None))[1])

    roi_median = master["ROI_Percentage"].median()
    esg_median = master["ESG_Score"].median()
    master["Strategic_Quadrant"] = np.select(
        [
            (master["ROI_Percentage"] >= roi_median) & (master["ESG_Score"] >= esg_median),
            (master["ROI_Percentage"] >= roi_median) & (master["ESG_Score"] < esg_median),
            (master["ROI_Percentage"] < roi_median) & (master["ESG_Score"] >= esg_median),
        ],
        ["Scale", "Yield-led", "ESG-led"],
        default="Watchlist",
    )

    key_map = {
        "green_investments_geographic": "Project_ID",
        "carbon_reduction": "Project_ID",
        "roi_returns": "Project_ID",
        "esg_scores_companies": "Company_Name",
        "sector_info": "Sector",
    }
    table_profile = pd.DataFrame(
        [
            {
                "Table": name,
                "Rows": len(frame),
                "Columns": len(frame.columns),
                "Primary Key": key_map[name],
                "Unique Key Values": frame[key_map[name]].nunique(dropna=True),
                "Duplicate Key Rows": int(frame[key_map[name]].duplicated().sum()),
                "Missing Cells": int(frame.isna().sum().sum()),
            }
            for name, frame in raw.items()
        ]
    )

    qa = pd.DataFrame(
        [
            {
                "Check": "Master grain",
                "Status": "Pass" if master["Project_ID"].nunique() == len(master) else "Review",
                "Detail": "Analytical master is one row per Project_ID.",
            },
            {
                "Check": "Relationship integrity",
                "Status": "Pass" if relationships["Status"].eq("Pass").all() else "Review",
                "Detail": "Declared 1:1 and 1:M relationships reconcile to source keys.",
            },
            {
                "Check": "Join completeness",
                "Status": "Pass" if master.isna().sum().sum() == 0 else "Review",
                "Detail": f"{int(master.isna().sum().sum()):,} missing cells after joining all datasets.",
            },
            {
                "Check": "Carbon reporting year audit",
                "Status": "Info",
                "Detail": f"{master['Project_Year'].eq(master['CO2_Report_Year']).mean() * 100:.1f}% of rows have same project year and carbon reporting year.",
            },
        ]
    )

    return master, sector, relationships, table_profile, qa


def sector_scorecard(source):
    rows = []
    total_investment = source["Investment_Amount_USD"].sum()

    for sector_name, group in source.groupby("Sector"):
        investment = group["Investment_Amount_USD"].sum()
        rows.append(
            {
                "Sector": sector_name,
                "Investment": investment,
                "Capital Share %": safe_div(investment, total_investment, 0) * 100,
                "Weighted ROI %": weighted_avg(group, "ROI_Percentage", "Investment_Amount_USD"),
                "Avg ESG": group["ESG_Score"].mean(),
                "CO2 / $1M": safe_div(group["CO2_Reduction_Tons"].sum(), investment / 1e6),
                "Low Risk %": group["Risk_Category"].eq("Low").mean() * 100,
                "Projects": group["Project_ID"].nunique(),
            }
        )

    score = pd.DataFrame(rows)
    if score.empty:
        return score

    score["Analyst Score"] = (
        score["Weighted ROI %"].rank(pct=True) * 35
        + score["Avg ESG"].rank(pct=True) * 25
        + score["CO2 / $1M"].rank(pct=True) * 25
        + score["Low Risk %"].rank(pct=True) * 15
    )
    return score.sort_values("Analyst Score", ascending=False)


try:
    master, sector_info, relationship_df, table_profile_df, qa_df = load_data()
except Exception as exc:
    st.error(f"Data load failed: {exc}")
    st.stop()

st.sidebar.title("HDFC Bank")
st.sidebar.caption("Green Finance & ESG Investment Tracker")

PAGES = [
    "Executive Overview",
    "ESG Analysis",
    "Geographic Intelligence",
    "Carbon Reduction",
    "ROI & Returns",
    "Sector Deep Dive",
    "Data Model & QA",
]
page = st.sidebar.radio("Navigation", PAGES)

st.sidebar.markdown("---")
years = sorted(master["Year"].dropna().astype(int).unique().tolist())
year_range = st.sidebar.slider(
    "Project start year",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years)),
)
sector_filter = st.sidebar.selectbox("Sector", ["All"] + sorted(master["Sector"].dropna().unique()))
state_filter = st.sidebar.selectbox("State", ["All"] + sorted(master["State"].dropna().unique()))
region_filter = st.sidebar.selectbox("Region", ["All"] + sorted(master["Region"].dropna().unique()))
risk_filter = st.sidebar.selectbox("Risk category", ["All", "Low", "Medium", "High"])

df = master[(master["Year"] >= year_range[0]) & (master["Year"] <= year_range[1])].copy()
if sector_filter != "All":
    df = df[df["Sector"] == sector_filter]
if state_filter != "All":
    df = df[df["State"] == state_filter]
if region_filter != "All":
    df = df[df["Region"] == region_filter]
if risk_filter != "All":
    df = df[df["Risk_Category"] == risk_filter]

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

total_investment = df["Investment_Amount_USD"].sum()
total_co2 = df["CO2_Reduction_Tons"].sum()
weighted_roi = weighted_avg(df, "ROI_Percentage", "Investment_Amount_USD")
avg_esg = df["ESG_Score"].mean()

if page == "Executive Overview":
    page_head(
        "Executive Overview",
        "Board-level view of green capital deployment, ESG quality, carbon impact, and return performance.",
    )

    cols = st.columns(6)
    kpis = [
        (money(total_investment), "Total investment", "Filtered portfolio"),
        (f"{total_co2 / 1e6:.2f}M", "CO2 reduced tons", "Impact scale"),
        (pct(weighted_roi), "Weighted ROI", "Capital weighted"),
        (f"{avg_esg:.1f}", "Avg ESG score", "Company quality"),
        (f"{df['Project_ID'].nunique():,}", "Projects", "Project grain"),
        (f"{df['State'].nunique()}", "States", "Coverage"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    section("Business Analyst Diagnostics")
    score = sector_scorecard(df)
    c1, c2 = st.columns([4, 6])

    high_risk_share = (
        safe_div(
            df.loc[df["Risk_Category"].eq("High"), "Investment_Amount_USD"].sum(),
            total_investment,
            0,
        )
        * 100
    )
    top_sector_concentration = (
        safe_div(df.groupby("Sector")["Investment_Amount_USD"].sum().max(), total_investment, 0)
        * 100
    )

    diagnostics = pd.DataFrame(
        {
            "Metric": [
                "Return proxy",
                "CO2 efficiency",
                "Top sector concentration",
                "High-risk capital share",
            ],
            "Value": [
                money(df["Estimated_Return_USD"].sum()),
                f"{safe_div(total_co2, total_investment / 1e6):,.1f} tons / $1M",
                pct(top_sector_concentration),
                pct(high_risk_share),
            ],
        }
    )

    with c1:
        table(diagnostics, hide_index=True)
    with c2:
        table(score.head(6), hide_index=True)

    if not score.empty:
        leader = score.iloc[0]
        st.markdown(
            f"<div class='insight'><b>Analyst insight:</b> "
            f"<b>{leader['Sector']}</b> ranks highest on blended weighted ROI, ESG quality, "
            f"carbon efficiency, and low-risk share. High-risk capital is "
            f"<b>{high_risk_share:.1f}%</b> of the selected portfolio.</div>",
            unsafe_allow_html=True,
        )

    section("Investment Trajectory and Allocation")
    c1, c2 = st.columns([7, 3])

    annual = (
        df.groupby(["Project_Year", "Sector"])["Investment_Amount_USD"].sum().reset_index()
    )
    fig = px.area(
        annual,
        x="Project_Year",
        y="Investment_Amount_USD",
        color="Sector",
        color_discrete_sequence=PAL,
    )
    with c1:
        plot(apply_layout(fig, "Annual green investment by sector", 380))

    allocation = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
    fig = px.pie(
        allocation,
        values="Investment_Amount_USD",
        names="Sector",
        hole=0.55,
        color_discrete_sequence=PAL,
    )
    with c2:
        plot(apply_layout(fig, "Sector allocation", 380))

    section("Strategic Portfolio Quadrants")
    quadrant = (
        df.groupby("Strategic_Quadrant")
        .agg(
            Investment=("Investment_Amount_USD", "sum"),
            ROI=("ROI_Percentage", "mean"),
            ESG=("ESG_Score", "mean"),
            Projects=("Project_ID", "nunique"),
            CO2=("CO2_Reduction_Tons", "sum"),
        )
        .reset_index()
    )
    fig = px.scatter(
        quadrant,
        x="ESG",
        y="ROI",
        size="Investment",
        color="Strategic_Quadrant",
        hover_data=["Projects", "CO2"],
        size_max=60,
    )
    plot(apply_layout(fig, "ROI vs ESG quadrants weighted by deployed capital", 430))

elif page == "ESG Analysis":
    page_head(
        "ESG Analysis",
        "Company ESG quality, risk-tier exposure, and ESG-return alignment.",
    )

    top_company = df.groupby("Company_Name")["ESG_Score"].mean().idxmax()
    cols = st.columns(4)
    kpis = [
        (f"{avg_esg:.1f}", "Avg ESG score", "Portfolio quality"),
        (pct(df["Risk_Category"].eq("Low").mean() * 100), "Low-risk projects", "Risk quality"),
        (pct(df["Risk_Category"].eq("High").mean() * 100), "High-risk projects", "Watchlist"),
        (top_company[:24], "Top ESG company", "Highest score"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    section("ESG Distribution and Risk Allocation")
    c1, c2 = st.columns([3, 2])

    fig = px.histogram(
        df,
        x="ESG_Score",
        color="Risk_Category",
        nbins=40,
        color_discrete_map=RISK_C,
    )
    with c1:
        plot(apply_layout(fig, "ESG score distribution by risk category"))

    risk_sector = (
        df.groupby(["Risk_Category", "Sector"])["Investment_Amount_USD"].sum().reset_index()
    )
    fig = px.sunburst(
        risk_sector,
        path=["Risk_Category", "Sector"],
        values="Investment_Amount_USD",
        color="Risk_Category",
        color_discrete_map=RISK_C,
    )
    with c2:
        plot(apply_layout(fig, "Risk category to sector capital"))

    section("ESG vs Return Matrix")
    company_matrix = (
        df.groupby("Company_Name")
        .agg(
            ESG=("ESG_Score", "mean"),
            ROI=("ROI_Percentage", "mean"),
            Investment=("Investment_Amount_USD", "sum"),
            CO2=("CO2_Reduction_Tons", "sum"),
            Risk=("Risk_Category", "first"),
            Sector=("Sector", "first"),
        )
        .reset_index()
    )
    fig = px.scatter(
        company_matrix,
        x="ESG",
        y="ROI",
        size="Investment",
        color="Risk",
        hover_name="Company_Name",
        hover_data=["Sector", "CO2"],
        color_discrete_map=RISK_C,
        size_max=45,
    )
    fig.add_vline(x=company_matrix["ESG"].mean(), line_dash="dash", line_color="#94A3B8")
    fig.add_hline(y=company_matrix["ROI"].mean(), line_dash="dash", line_color="#94A3B8")
    plot(apply_layout(fig, "Company ESG vs ROI, bubble sized by investment", 450))

elif page == "Geographic Intelligence":
    page_head(
        "Geographic Intelligence",
        "State, region, and city-level investment quality and impact efficiency.",
    )

    state_summary = (
        df.groupby(["State", "Region", "lat", "lon"])
        .agg(
            Investment=("Investment_Amount_USD", "sum"),
            CO2=("CO2_Reduction_Tons", "sum"),
            ROI=("ROI_Percentage", "mean"),
            ESG=("ESG_Score", "mean"),
            Projects=("Project_ID", "nunique"),
        )
        .reset_index()
    )

    section("India Investment Bubble Map")
    fig = px.scatter_geo(
        state_summary.dropna(subset=["lat", "lon"]),
        lat="lat",
        lon="lon",
        size="Investment",
        color="Region",
        hover_name="State",
        hover_data=["Projects", "ROI", "ESG", "CO2"],
        scope="asia",
        size_max=45,
        color_discrete_sequence=PAL,
    )
    fig.update_geos(
        center=dict(lat=22, lon=80),
        lataxis_range=[6, 38],
        lonaxis_range=[65, 100],
        showland=True,
        landcolor="#07111f",
        bgcolor="#050914",
        showcountries=True,
    )
    plot(apply_layout(fig, "State investment map", 520))

    section("Regional Efficiency")
    c1, c2 = st.columns(2)

    region_summary = (
        df.groupby("Region")
        .agg(
            Investment=("Investment_Amount_USD", "sum"),
            CO2=("CO2_Reduction_Tons", "sum"),
            Projects=("Project_ID", "nunique"),
            ROI=("ROI_Percentage", "mean"),
        )
        .reset_index()
    )
    fig = px.scatter(
        region_summary,
        x="Investment",
        y="CO2",
        size="Projects",
        color="Region",
        hover_data=["ROI"],
        size_max=55,
        color_discrete_sequence=PAL,
    )
    with c1:
        plot(apply_layout(fig, "CO2 impact vs capital by region"))

    state_summary["CO2 / $1M"] = state_summary["CO2"] / (state_summary["Investment"] / 1e6)
    fig = px.bar(
        state_summary.sort_values("CO2 / $1M", ascending=False).head(15),
        y="State",
        x="CO2 / $1M",
        orientation="h",
        color="CO2 / $1M",
        color_continuous_scale="Teal",
    )
    with c2:
        plot(apply_layout(fig, "Top states by CO2 efficiency"))

    section("City Leaders")
    city_summary = (
        df.groupby("City")
        .agg(
            Investment=("Investment_Amount_USD", "sum"),
            Projects=("Project_ID", "nunique"),
            CO2=("CO2_Reduction_Tons", "sum"),
        )
        .sort_values("Investment", ascending=False)
        .head(15)
        .reset_index()
    )
    fig = px.bar(
        city_summary,
        y="City",
        x="Investment",
        orientation="h",
        color="Investment",
        color_continuous_scale="Teal",
        hover_data=["Projects", "CO2"],
    )
    plot(apply_layout(fig, "Top cities by green investment", 420))

elif page == "Carbon Reduction":
    page_head(
        "Carbon Reduction",
        "Carbon impact tracking using carbon reporting year and efficiency metrics.",
    )

    cdf = df.dropna(subset=["CO2_Report_Year"]).copy()
    cdf["CO2_Report_Year"] = cdf["CO2_Report_Year"].astype(int)
    usd_per_ton = safe_div(total_investment, total_co2)
    peak_year = cdf.groupby("CO2_Report_Year")["CO2_Reduction_Tons"].sum().idxmax()

    cols = st.columns(5)
    kpis = [
        (f"{total_co2 / 1e6:.2f}M", "Total CO2 tons", "Avoided/reduced"),
        (f"{df['CO2_Reduction_Tons'].mean():,.0f}", "Avg CO2/project", "Project impact"),
        (money(usd_per_ton), "USD per ton CO2", "Capital efficiency"),
        (money(total_co2 * 65), "Carbon value at $65/t", "Impact proxy"),
        (str(peak_year), "Peak impact year", "Reporting year"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    section("Carbon Trajectory by Sector")
    carbon_trend = (
        cdf.groupby(["CO2_Report_Year", "Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    )
    fig = px.area(
        carbon_trend,
        x="CO2_Report_Year",
        y="CO2_Reduction_Tons",
        color="Sector",
        color_discrete_sequence=PAL,
    )
    plot(apply_layout(fig, "Annual CO2 reduction by sector", 410))

    section("Efficiency and Carbon Leaders")
    c1, c2 = st.columns(2)

    sector_eff = (
        df.groupby("Sector")
        .agg(CO2=("CO2_Reduction_Tons", "sum"), Investment=("Investment_Amount_USD", "sum"))
        .reset_index()
    )
    sector_eff["CO2 / $1M"] = sector_eff["CO2"] / (sector_eff["Investment"] / 1e6)
    fig = px.bar(
        sector_eff.sort_values("CO2 / $1M", ascending=False),
        x="Sector",
        y="CO2 / $1M",
        color="CO2 / $1M",
        color_continuous_scale="Greens",
    )
    with c1:
        plot(apply_layout(fig, "Sector CO2 efficiency"))

    company_carbon = (
        df.groupby("Company_Name")["CO2_Reduction_Tons"]
        .sum()
        .sort_values(ascending=False)
        .head(12)
        .reset_index()
    )
    fig = px.bar(
        company_carbon,
        y="Company_Name",
        x="CO2_Reduction_Tons",
        orientation="h",
        color="CO2_Reduction_Tons",
        color_continuous_scale="Teal",
    )
    with c2:
        plot(apply_layout(fig, "Top corporate carbon reducers"))

elif page == "ROI & Returns":
    page_head(
        "ROI & Returns",
        "Capital-weighted yield, volatility, risk-adjusted returns, and sector return signals.",
    )

    avg_roi = df["ROI_Percentage"].mean()
    median_roi = df["ROI_Percentage"].median()
    max_roi = df["ROI_Percentage"].max()
    roi_std = df["ROI_Percentage"].std()
    return_volatility = safe_div(avg_roi, roi_std, 0)

    cols = st.columns(5)
    kpis = [
        (pct(weighted_roi), "Weighted ROI", "Capital weighted"),
        (pct(avg_roi), "Avg ROI", "Simple average"),
        (pct(median_roi), "Median ROI", "Middle project"),
        (pct(max_roi), "Peak ROI", "Best project"),
        (f"{return_volatility:.2f}", "Return / volatility", "Risk-adjusted proxy"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    section("ROI Distribution and Risk Tier Performance")
    c1, c2 = st.columns(2)

    fig = px.histogram(
        df,
        x="ROI_Percentage",
        color="Sector",
        nbins=45,
        color_discrete_sequence=PAL,
    )
    with c1:
        plot(apply_layout(fig, "ROI distribution by sector"))

    risk_return = df.groupby("Risk_Category")["ROI_Percentage"].agg(["mean", "std"]).reset_index()
    fig = go.Figure(
        go.Bar(
            x=risk_return["Risk_Category"],
            y=risk_return["mean"],
            error_y=dict(type="data", array=risk_return["std"]),
            marker_color=[RISK_C.get(x, "#94A3B8") for x in risk_return["Risk_Category"]],
        )
    )
    with c2:
        plot(apply_layout(fig, "Average ROI with volatility by risk category"))

    section("Investment vs ROI")
    sample = df.sample(min(len(df), 6000), random_state=7)
    fig = px.scatter(
        sample,
        x="Investment_Amount_USD",
        y="ROI_Percentage",
        color="Sector",
        size="ESG_Score",
        hover_data=["Company_Name", "State", "Year"],
        color_discrete_sequence=PAL,
    )
    fig.update_xaxes(type="log")
    plot(apply_layout(fig, "Project investment vs ROI, bubble sized by ESG score", 450))

    section("Sector Return Ranking")
    roi_sector = (
        df.groupby("Sector")
        .agg(
            Weighted_ROI=("ROI_Percentage", "mean"),
            Investment=("Investment_Amount_USD", "sum"),
            Projects=("Project_ID", "nunique"),
        )
        .sort_values("Weighted_ROI", ascending=False)
        .reset_index()
    )
    fig = px.bar(
        roi_sector,
        x="Sector",
        y="Weighted_ROI",
        color="Weighted_ROI",
        color_continuous_scale="Teal",
        hover_data=["Investment", "Projects"],
    )
    plot(apply_layout(fig, "Average ROI by sector", 390))

elif page == "Sector Deep Dive":
    page_head(
        "Sector Deep Dive",
        "Sector-level investment, ESG, carbon, return, geography, and risk diagnostics.",
    )

    chosen_sector = st.selectbox("Select sector for deep dive", sorted(df["Sector"].unique()))
    sector_df = df[df["Sector"] == chosen_sector].copy()

    description = sector_info.loc[sector_info["Sector"].eq(chosen_sector), "Description"]
    if not description.empty:
        st.info(description.iloc[0])

    cols = st.columns(5)
    kpis = [
        (money(sector_df["Investment_Amount_USD"].sum()), "Investment", "Sector capital"),
        (f"{sector_df['CO2_Reduction_Tons'].sum() / 1e6:.2f}M", "CO2 tons", "Impact"),
        (
            pct(weighted_avg(sector_df, "ROI_Percentage", "Investment_Amount_USD")),
            "Weighted ROI",
            "Capital weighted",
        ),
        (f"{sector_df['ESG_Score'].mean():.1f}", "Avg ESG", "Company quality"),
        (f"{sector_df['Project_ID'].nunique():,}", "Projects", "Project count"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    section("Sector Trends")
    c1, c2 = st.columns(2)

    trend = (
        sector_df.groupby("Year")
        .agg(
            Investment=("Investment_Amount_USD", "sum"),
            ROI=("ROI_Percentage", "mean"),
            CO2=("CO2_Reduction_Tons", "sum"),
        )
        .reset_index()
    )
    fig = px.bar(trend, x="Year", y="Investment", color_discrete_sequence=[PAL[0]])
    with c1:
        plot(apply_layout(fig, f"{chosen_sector}: investment trend"))

    fig = px.line(trend, x="Year", y="ROI", markers=True, color_discrete_sequence=[PAL[2]])
    with c2:
        plot(apply_layout(fig, f"{chosen_sector}: ROI trend"))

    section("Geography and Risk Mix")
    c1, c2 = st.columns(2)

    state_investment = (
        sector_df.groupby("State")["Investment_Amount_USD"]
        .sum()
        .sort_values(ascending=False)
        .head(12)
        .reset_index()
    )
    fig = px.bar(
        state_investment,
        y="State",
        x="Investment_Amount_USD",
        orientation="h",
        color="Investment_Amount_USD",
        color_continuous_scale="Teal",
    )
    with c1:
        plot(apply_layout(fig, "Top states by sector investment"))

    risk_mix = sector_df["Risk_Category"].value_counts().reset_index()
    risk_mix.columns = ["Risk", "Projects"]
    fig = px.pie(
        risk_mix,
        values="Projects",
        names="Risk",
        hole=0.55,
        color="Risk",
        color_discrete_map=RISK_C,
    )
    with c2:
        plot(apply_layout(fig, "Sector risk distribution"))

    section("Sector Benchmark Scorecard")
    table(sector_scorecard(df), hide_index=True)

elif page == "Data Model & QA":
    page_head(
        "Data Model & QA",
        "Relationship audit for 1:1 and 1:M joins, table grain, data quality, and business definitions.",
    )

    cols = st.columns(5)
    kpis = [
        (f"{master['Project_ID'].nunique():,}", "Project primary key", "Master grain"),
        ("2", "1:1 fact joins", "Carbon + ROI"),
        ("2", "1:M dimensions", "Company + sector"),
        (
            f"{relationship_df['Status'].eq('Pass').sum()}/{len(relationship_df)}",
            "Relationships pass",
            "Key integrity",
        ),
        (f"{qa_df['Status'].eq('Pass').sum()}/{len(qa_df)}", "QA pass", "Automated checks"),
    ]
    for col, item in zip(cols, kpis):
        col.markdown(kpi_card(*item), unsafe_allow_html=True)

    st.markdown(
        "<div class='insight'><b>Model logic:</b> the analytical master is one row per "
        "<b>Project_ID</b>. Carbon and ROI join <b>1:1</b> by Project_ID. ESG joins "
        "<b>1:M</b> from Company_Name to project records. Sector info joins <b>1:M</b> "
        "from Sector to project records. Project year and carbon reporting year are kept "
        "separate for audit-quality analysis.</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Relationships", "QA Checks", "Table Dictionary", "Field Definitions"]
    )

    with tab1:
        table(relationship_df, hide_index=True)

    with tab2:
        table(qa_df, hide_index=True)

    with tab3:
        table(table_profile_df, hide_index=True)

    with tab4:
        dictionary = pd.DataFrame(
            [
                {
                    "Field": "Project_ID",
                    "Role": "Primary key",
                    "Business Definition": "Unique financed green project.",
                },
                {
                    "Field": "Company_Name",
                    "Role": "Foreign key to ESG table",
                    "Business Definition": "Company-level ESG and risk profile.",
                },
                {
                    "Field": "Sector",
                    "Role": "Foreign key to sector table",
                    "Business Definition": "Green finance sector classification.",
                },
                {
                    "Field": "Project_Year",
                    "Role": "Investment time dimension",
                    "Business Definition": "Year of project start or capital deployment.",
                },
                {
                    "Field": "CO2_Report_Year",
                    "Role": "Impact time dimension",
                    "Business Definition": "Year associated with carbon impact reporting.",
                },
                {
                    "Field": "Investment_Amount_USD",
                    "Role": "Capital measure",
                    "Business Definition": "Capital deployed to the project in USD.",
                },
                {
                    "Field": "ROI_Percentage",
                    "Role": "Return measure",
                    "Business Definition": "Project-level return on investment percentage.",
                },
                {
                    "Field": "ESG_Score",
                    "Role": "Quality measure",
                    "Business Definition": "Company ESG score joined to project rows.",
                },
                {
                    "Field": "Risk_Category",
                    "Role": "Risk dimension",
                    "Business Definition": "Low, Medium, or High ESG risk tier.",
                },
                {
                    "Field": "CO2_Reduction_Tons",
                    "Role": "Impact measure",
                    "Business Definition": "Estimated tons of CO2 reduced or avoided.",
                },
            ]
        )
        table(dictionary, hide_index=True)

st.markdown(
    "<p class='small'>HDFC Bank Green Finance & ESG Investment Tracker v5.1 - Streamlit + Plotly</p>",
    unsafe_allow_html=True,
)
