"""
HDFC Bank: Green Finance & ESG Investment Tracker v5.1
CSV files required in the same folder:
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

st.set_page_config(
    page_title="HDFC Bank - Green Finance & ESG",
    page_icon="HDFC",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root{
  --bg:#050914;--panel:#101827;--panel2:#132033;--line:rgba(255,255,255,.09);
  --text:#F8FAFC;--muted:#94A3B8;--green:#20C48A;--blue:#3B82F6;
  --gold:#F59E0B;--red:#EF4444;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--text);}
[data-testid="block-container"]{padding:1.3rem 2rem 2rem;max-width:1450px;}
[data-testid="stSidebar"]{background:#07111f;border-right:1px solid var(--line);}
h1,h2,h3,p,span,label{font-family:Inter,Arial,sans-serif;}
.page-head{background:linear-gradient(135deg,#12213a,#08271d);border:1px solid var(--line);
  border-radius:14px;padding:20px 24px;margin-bottom:18px;}
.page-head h1{font-size:1.55rem;margin:0;color:#fff;}
.page-head p{font-size:.86rem;color:var(--muted);margin:.25rem 0 0;}
.card{background:rgba(16,24,39,.86);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;margin-bottom:12px;}
.kpi{background:rgba(16,24,39,.86);border:1px solid var(--line);border-radius:12px;
  padding:16px;min-height:118px;}
.kpi .v{font-size:1.65rem;font-weight:800;color:#fff;line-height:1.1;}
.kpi .l{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:6px;}
.kpi .d{font-size:.76rem;color:var(--green);margin-top:8px;font-weight:700;}
.sec{font-size:1.02rem;font-weight:800;color:#fff;border-bottom:1px solid var(--line);
  padding-bottom:8px;margin:24px 0 14px;}
.insight{background:rgba(32,196,138,.07);border:1px solid rgba(32,196,138,.24);
  border-left:4px solid var(--green);border-radius:10px;padding:14px 16px;color:#DFFCF1;
  line-height:1.55;font-size:.9rem;margin:12px 0;}
.small{color:var(--muted);font-size:.82rem;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).resolve().parent
PAL = ["#20C48A", "#3B82F6", "#F59E0B", "#EF4444", "#A78BFA", "#14B8A6"]
RISK_C = {"Low": "#10B981", "Medium": "#F59E0B", "High": "#EF4444"}

STATE_LL = {
    "Bihar": (25.10, 85.31), "Chhattisgarh": (21.28, 81.87), "Delhi": (28.70, 77.10),
    "Gujarat": (22.26, 71.19), "Haryana": (29.06, 76.09), "Karnataka": (15.32, 75.71),
    "Madhya Pradesh": (22.97, 78.66), "Maharashtra": (19.75, 75.71), "Odisha": (20.95, 85.10),
    "Punjab": (31.15, 75.34), "Rajasthan": (27.02, 74.22), "Tamil Nadu": (11.13, 78.66),
    "Telangana": (18.11, 79.02), "Uttar Pradesh": (26.85, 80.95), "West Bengal": (22.99, 87.86),
}

def money(x):
    if pd.isna(x): return "-"
    if abs(x) >= 1e9: return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6: return f"${x/1e6:.1f}M"
    return f"${x:,.0f}"

def pct(x):
    return "-" if pd.isna(x) else f"{x:.1f}%"

def safe_div(a, b, default=np.nan):
    return default if b in (0, None) or pd.isna(b) else a / b

def weighted_avg(df, value, weight):
    x = df[[value, weight]].dropna()
    if x.empty or x[weight].sum() == 0: return np.nan
    return np.average(x[value], weights=x[weight])

def layout(fig, title, h=360):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#F8FAFC", size=15), x=.01),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter,Arial", size=11),
        height=h, margin=dict(l=10, r=10, t=52, b=25),
        legend=dict(orientation="h", y=1.04, x=1, xanchor="right"),
        hoverlabel=dict(bgcolor="#111827", font_color="#fff"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False)
    return fig

def kpi(value, label, delta=""):
    return f"<div class='kpi'><div class='v'>{value}</div><div class='l'>{label}</div><div class='d'>{delta}</div></div>"

def head(title, sub):
    st.markdown(f"<div class='page-head'><h1>{title}</h1><p>{sub}</p></div>", unsafe_allow_html=True)

def section(title):
    st.markdown(f"<div class='sec'>{title}</div>", unsafe_allow_html=True)

def cardinality(left, right, key):
    lu = left[key].nunique() == len(left)
    ru = right[key].nunique() == len(right)
    if lu and ru: return "1:1"
    if lu and not ru: return "1:M"
    if not lu and ru: return "M:1"
    return "M:M"

def rel_row(raw, left, right, key, expected, meaning):
    l, r = raw[left], raw[right]
    detected = cardinality(l, r, key)
    lc = l[key].isin(r[key]).mean() * 100
    rc = r[key].isin(l[key]).mean() * 100
    return {
        "Left Table": left, "Right Table": right, "Key": key,
        "Expected": expected, "Detected": detected,
        "Left Rows": len(l), "Right Rows": len(r),
        "Left Key Duplicates": int(l[key].duplicated().sum()),
        "Right Key Duplicates": int(r[key].duplicated().sum()),
        "Left Coverage %": lc, "Right Coverage %": rc,
        "Status": "Pass" if detected == expected and lc == 100 and rc == 100 else "Review",
        "Business Meaning": meaning,
    }

@st.cache_data(show_spinner="Loading ESG datasets...")
def load_data():
    geo = pd.read_csv(BASE / "green_investments_geographic.csv", parse_dates=["Project_Start_Date"])
    carbon = pd.read_csv(BASE / "carbon_reduction.csv")
    esg = pd.read_csv(BASE / "esg_scores_companies.csv")
    roi = pd.read_csv(BASE / "roi_returns.csv")
    sector = pd.read_csv(BASE / "sector_info.csv", header=None, names=["Sector", "Description"])

    raw = {
        "green_investments_geographic": geo,
        "carbon_reduction": carbon,
        "roi_returns": roi,
        "esg_scores_companies": esg,
        "sector_info": sector,
    }

    rel = pd.DataFrame([
        rel_row(raw, "green_investments_geographic", "carbon_reduction", "Project_ID", "1:1",
                "Every financed project has one carbon impact record."),
        rel_row(raw, "green_investments_geographic", "roi_returns", "Project_ID", "1:1",
                "Every financed project has one ROI record."),
        rel_row(raw, "esg_scores_companies", "green_investments_geographic", "Company_Name", "1:M",
                "One company ESG profile supports many project rows."),
        rel_row(raw, "sector_info", "green_investments_geographic", "Sector", "1:M",
                "One sector definition supports many project rows."),
    ])

    m = geo.merge(carbon, on="Project_ID", how="left", suffixes=("", "_Carbon"), validate="one_to_one")
    m["Project_Year"] = pd.to_numeric(m["Year"], errors="coerce").astype("Int64")
    m["CO2_Report_Year"] = pd.to_numeric(m.get("Year_Carbon", m["Year"]), errors="coerce").astype("Int64")
    if "Year_Carbon" in m.columns: m.drop(columns=["Year_Carbon"], inplace=True)

    m = m.merge(roi, on="Project_ID", how="left", validate="one_to_one")
    m = m.merge(esg, on="Company_Name", how="left", validate="many_to_one")
    m = m.merge(sector, on="Sector", how="left", validate="many_to_one")

    m["Year"] = m["Project_Year"].astype(int)
    m["Investment_M"] = m["Investment_Amount_USD"] / 1e6
    m["Estimated_Return_USD"] = m["Investment_Amount_USD"] * m["ROI_Percentage"] / 100
    m["CO2_per_Million_USD"] = m["CO2_Reduction_Tons"] / (m["Investment_Amount_USD"] / 1e6)
    m["USD_per_Ton_CO2"] = m["Investment_Amount_USD"] / m["CO2_Reduction_Tons"].replace(0, np.nan)
    m["Risk_Score"] = m["Risk_Category"].map({"Low": 1, "Medium": 2, "High": 3})
    m["lat"] = m["State"].map(lambda s: STATE_LL.get(s, (None, None))[0])
    m["lon"] = m["State"].map(lambda s: STATE_LL.get(s, (None, None))[1])

    roi_med, esg_med = m["ROI_Percentage"].median(), m["ESG_Score"].median()
    m["Strategic_Quadrant"] = np.select(
        [
            (m["ROI_Percentage"] >= roi_med) & (m["ESG_Score"] >= esg_med),
            (m["ROI_Percentage"] >= roi_med) & (m["ESG_Score"] < esg_med),
            (m["ROI_Percentage"] < roi_med) & (m["ESG_Score"] >= esg_med),
        ],
        ["Scale", "Yield-led", "ESG-led"],
        default="Watchlist",
    )

    profile = pd.DataFrame([
        {"Table": k, "Rows": len(v), "Columns": len(v.columns),
         "Key": {"green_investments_geographic":"Project_ID","carbon_reduction":"Project_ID",
                 "roi_returns":"Project_ID","esg_scores_companies":"Company_Name","sector_info":"Sector"}[k]}
        for k, v in raw.items()
    ])

    qa = pd.DataFrame([
        {"Check": "Master grain", "Status": "Pass" if m["Project_ID"].nunique() == len(m) else "Review",
         "Detail": "Analytical table is one row per project."},
        {"Check": "Relationship integrity", "Status": "Pass" if rel["Status"].eq("Pass").all() else "Review",
         "Detail": "All declared relationships reconcile to source keys."},
        {"Check": "Completeness", "Status": "Pass" if m.isna().sum().sum() == 0 else "Review",
         "Detail": f"{int(m.isna().sum().sum()):,} missing cells after joins."},
        {"Check": "Carbon year audit", "Status": "Info",
         "Detail": f"{m['Project_Year'].eq(m['CO2_Report_Year']).mean()*100:.1f}% same project year and carbon reporting year."},
    ])
    return m, sector, rel, profile, qa

def sector_score(df):
    rows = []
    total = df["Investment_Amount_USD"].sum()
    for sec, g in df.groupby("Sector"):
        inv = g["Investment_Amount_USD"].sum()
        rows.append({
            "Sector": sec, "Investment": inv, "Capital Share %": safe_div(inv, total, 0) * 100,
            "Weighted ROI %": weighted_avg(g, "ROI_Percentage", "Investment_Amount_USD"),
            "Avg ESG": g["ESG_Score"].mean(),
            "CO2 / $1M": safe_div(g["CO2_Reduction_Tons"].sum(), inv / 1e6),
            "Low Risk %": g["Risk_Category"].eq("Low").mean() * 100,
            "Projects": g["Project_ID"].nunique(),
        })
    s = pd.DataFrame(rows)
    if s.empty: return s
    s["Analyst Score"] = (
        s["Weighted ROI %"].rank(pct=True) * 35 +
        s["Avg ESG"].rank(pct=True) * 25 +
        s["CO2 / $1M"].rank(pct=True) * 25 +
        s["Low Risk %"].rank(pct=True) * 15
    )
    return s.sort_values("Analyst Score", ascending=False)

try:
    master, sector_info, rel_df, profile_df, qa_df = load_data()
except Exception as e:
    st.error(f"Data load failed: {e}")
    st.stop()

st.sidebar.title("HDFC Bank")
st.sidebar.caption("Green Finance & ESG Investment Tracker")

pages = [
    "Executive Overview", "ESG Analysis", "Geographic Intelligence",
    "Carbon Reduction", "ROI & Returns", "Sector Deep Dive", "Data Model & QA"
]
page = st.sidebar.radio("Navigation", pages)

years = sorted(master["Year"].dropna().unique())
st.sidebar.markdown("---")
yr_range = st.sidebar.select_slider("Project year", options=years, value=(min(years), max(years)))
sector_filter = st.sidebar.selectbox("Sector", ["All"] + sorted(master["Sector"].unique()))
state_filter = st.sidebar.selectbox("State", ["All"] + sorted(master["State"].unique()))
region_filter = st.sidebar.selectbox("Region", ["All"] + sorted(master["Region"].unique()))
risk_filter = st.sidebar.selectbox("Risk", ["All", "Low", "Medium", "High"])

df = master[(master["Year"] >= yr_range[0]) & (master["Year"] <= yr_range[1])].copy()
if sector_filter != "All": df = df[df["Sector"] == sector_filter]
if state_filter != "All": df = df[df["State"] == state_filter]
if region_filter != "All": df = df[df["Region"] == region_filter]
if risk_filter != "All": df = df[df["Risk_Category"] == risk_filter]

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

inv = df["Investment_Amount_USD"].sum()
co2 = df["CO2_Reduction_Tons"].sum()
wroi = weighted_avg(df, "ROI_Percentage", "Investment_Amount_USD")
avg_esg = df["ESG_Score"].mean()

if page == "Executive Overview":
    head("Executive Overview", "Board-level view of green finance deployment, ESG quality, carbon impact, and returns.")
    cols = st.columns(6)
    vals = [
        (money(inv), "Total investment", "Filtered portfolio"),
        (f"{co2/1e6:.2f}M", "CO2 reduced tons", "Impact scale"),
        (pct(wroi), "Weighted ROI", "Capital weighted"),
        (f"{avg_esg:.1f}", "Avg ESG score", "Company quality"),
        (f"{df['Project_ID'].nunique():,}", "Projects", "Project grain"),
        (f"{df['State'].nunique()}", "States", "Coverage"),
    ]
    for c, v in zip(cols, vals): c.markdown(kpi(*v), unsafe_allow_html=True)

    section("Business Analyst Diagnostics")
    score = sector_score(df)
    c1, c2 = st.columns([4, 6])
    high_risk_share = safe_div(df.loc[df["Risk_Category"].eq("High"), "Investment_Amount_USD"].sum(), inv, 0) * 100
    top_conc = safe_div(df.groupby("Sector")["Investment_Amount_USD"].sum().max(), inv, 0) * 100
    diag = pd.DataFrame({
        "Metric": ["Return proxy", "CO2 efficiency", "Top sector concentration", "High-risk capital share"],
        "Value": [money(df["Estimated_Return_USD"].sum()),
                  f"{safe_div(co2, inv/1e6):,.1f} tons / $1M", pct(top_conc), pct(high_risk_share)]
    })
    c1.dataframe(diag, hide_index=True, use_container_width=True)
    c2.dataframe(score.head(6), hide_index=True, use_container_width=True)
    st.markdown(f"<div class='insight'><b>Analyst insight:</b> {score.iloc[0]['Sector']} ranks highest on blended ROI, ESG, carbon efficiency and low-risk share. High-risk capital is {high_risk_share:.1f}% of the selected portfolio.</div>", unsafe_allow_html=True)

    section("Investment Trajectory and Allocation")
    a, b = st.columns([7, 3])
    yearly = df.groupby(["Year", "Sector"])["Investment_Amount_USD"].sum().reset_index()
    a.plotly_chart(layout(px.area(yearly, x="Year", y="Investment_Amount_USD", color="Sector", color_discrete_sequence=PAL), "Annual investment by sector"), use_container_width=True)
    pie = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
    b.plotly_chart(layout(px.pie(pie, values="Investment_Amount_USD", names="Sector", hole=.55, color_discrete_sequence=PAL), "Sector allocation"), use_container_width=True)

    section("Strategic Quadrants")
    q = df.groupby("Strategic_Quadrant").agg(Investment=("Investment_Amount_USD","sum"), ROI=("ROI_Percentage","mean"), ESG=("ESG_Score","mean"), Projects=("Project_ID","nunique")).reset_index()
    fig = px.scatter(q, x="ESG", y="ROI", size="Investment", color="Strategic_Quadrant", hover_data=["Projects"], size_max=60)
    st.plotly_chart(layout(fig, "ROI vs ESG quadrants weighted by capital", 390), use_container_width=True)

elif page == "ESG Analysis":
    head("ESG Analysis", "Company ESG quality, risk tiers, and capital exposure.")
    cols = st.columns(4)
    top_company = df.groupby("Company_Name")["ESG_Score"].mean().idxmax()
    for c, v in zip(cols, [(f"{avg_esg:.1f}", "Avg ESG", ""), (pct(df["Risk_Category"].eq("Low").mean()*100), "Low-risk projects", ""),
                           (pct(df["Risk_Category"].eq("High").mean()*100), "High-risk projects", ""), (top_company[:24], "Top ESG company", "")]):
        c.markdown(kpi(*v), unsafe_allow_html=True)

    section("ESG Distribution and Risk Allocation")
    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(layout(px.histogram(df, x="ESG_Score", color="Risk_Category", nbins=40, color_discrete_map=RISK_C), "ESG score distribution"), use_container_width=True)
    risk_sec = df.groupby(["Risk_Category", "Sector"])["Investment_Amount_USD"].sum().reset_index()
    c2.plotly_chart(layout(px.sunburst(risk_sec, path=["Risk_Category","Sector"], values="Investment_Amount_USD", color="Risk_Category", color_discrete_map=RISK_C), "Risk -> sector capital"), use_container_width=True)

    section("ESG vs Returns Matrix")
    bub = df.groupby("Company_Name").agg(ESG=("ESG_Score","mean"), ROI=("ROI_Percentage","mean"), CO2=("CO2_Reduction_Tons","sum"), Investment=("Investment_Amount_USD","sum"), Risk=("Risk_Category","first"), Sector=("Sector","first")).reset_index()
    fig = px.scatter(bub, x="ESG", y="ROI", size="Investment", color="Risk", hover_name="Company_Name", hover_data=["Sector","CO2"], color_discrete_map=RISK_C, size_max=45)
    fig.add_vline(x=bub["ESG"].mean(), line_dash="dash")
    fig.add_hline(y=bub["ROI"].mean(), line_dash="dash")
    st.plotly_chart(layout(fig, "Company ESG vs ROI, bubble sized by capital", 440), use_container_width=True)

elif page == "Geographic Intelligence":
    head("Geographic Intelligence", "State, city, and regional deployment quality.")
    state = df.groupby(["State","Region","lat","lon"]).agg(Investment=("Investment_Amount_USD","sum"), CO2=("CO2_Reduction_Tons","sum"), ROI=("ROI_Percentage","mean"), Projects=("Project_ID","nunique")).reset_index()
    section("India Bubble Map")
    fig = px.scatter_geo(state.dropna(), lat="lat", lon="lon", size="Investment", color="Region", hover_name="State", hover_data=["Projects","ROI","CO2"], scope="asia", size_max=45)
    fig.update_geos(center=dict(lat=22, lon=80), lataxis_range=[6,38], lonaxis_range=[65,100], showland=True, landcolor="#07111f", bgcolor="#050914")
    st.plotly_chart(layout(fig, "State investment map", 500), use_container_width=True)

    section("Regional Efficiency")
    c1, c2 = st.columns(2)
    reg = df.groupby("Region").agg(Investment=("Investment_Amount_USD","sum"), CO2=("CO2_Reduction_Tons","sum"), Projects=("Project_ID","nunique")).reset_index()
    c1.plotly_chart(layout(px.scatter(reg, x="Investment", y="CO2", size="Projects", color="Region", size_max=55), "CO2 impact vs capital by region"), use_container_width=True)
    state["CO2 / $1M"] = state["CO2"] / (state["Investment"] / 1e6)
    c2.plotly_chart(layout(px.bar(state.sort_values("CO2 / $1M", ascending=False).head(15), y="State", x="CO2 / $1M", orientation="h", color="CO2 / $1M"), "Top states by CO2 efficiency"), use_container_width=True)

elif page == "Carbon Reduction":
    head("Carbon Reduction", "Impact tracking using CO2 reporting year.")
    cdf = df.dropna(subset=["CO2_Report_Year"]).copy()
    cdf["CO2_Report_Year"] = cdf["CO2_Report_Year"].astype(int)
    usd_per_ton = safe_div(inv, co2)
    cols = st.columns(5)
    vals = [(f"{co2/1e6:.2f}M", "Total CO2 tons", ""), (f"{df['CO2_Reduction_Tons'].mean():,.0f}", "Avg CO2/project", ""),
            (money(usd_per_ton), "USD per ton CO2", ""), (money(co2*65), "Carbon value at $65/t", ""), (cdf.groupby("CO2_Report_Year")["CO2_Reduction_Tons"].sum().idxmax(), "Peak impact year", "")]
    for c, v in zip(cols, vals): c.markdown(kpi(*v), unsafe_allow_html=True)

    section("Carbon Trajectory")
    carbon_y = cdf.groupby(["CO2_Report_Year","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    st.plotly_chart(layout(px.area(carbon_y, x="CO2_Report_Year", y="CO2_Reduction_Tons", color="Sector", color_discrete_sequence=PAL), "Annual CO2 reduction by sector"), use_container_width=True)

    section("Efficiency and Leaders")
    c1, c2 = st.columns(2)
    eff = df.groupby("Sector").agg(CO2=("CO2_Reduction_Tons","sum"), Investment=("Investment_Amount_USD","sum")).reset_index()
    eff["CO2 / $1M"] = eff["CO2"] / (eff["Investment"] / 1e6)
    c1.plotly_chart(layout(px.bar(eff.sort_values("CO2 / $1M", ascending=False), x="Sector", y="CO2 / $1M", color="CO2 / $1M"), "Sector CO2 efficiency"), use_container_width=True)
    comp = df.groupby("Company_Name")["CO2_Reduction_Tons"].sum().sort_values(ascending=False).head(12).reset_index()
    c2.plotly_chart(layout(px.bar(comp, y="Company_Name", x="CO2_Reduction_Tons", orientation="h", color="CO2_Reduction_Tons"), "Top corporate carbon reducers"), use_container_width=True)

elif page == "ROI & Returns":
    head("ROI & Returns", "Capital weighted yield, volatility, and risk-adjusted return quality.")
    avg, med, mx, sd = df["ROI_Percentage"].mean(), df["ROI_Percentage"].median(), df["ROI_Percentage"].max(), df["ROI_Percentage"].std()
    cols = st.columns(5)
    vals = [(pct(wroi), "Weighted ROI", ""), (pct(avg), "Avg ROI", ""), (pct(med), "Median ROI", ""), (pct(mx), "Peak ROI", ""), (f"{safe_div(avg, sd, 0):.2f}", "Return / volatility", "")]
    for c, v in zip(cols, vals): c.markdown(kpi(*v), unsafe_allow_html=True)

    section("ROI Distribution")
    c1, c2 = st.columns(2)
    c1.plotly_chart(layout(px.histogram(df, x="ROI_Percentage", color="Sector", nbins=45, color_discrete_sequence=PAL), "ROI distribution by sector"), use_container_width=True)
    risk = df.groupby("Risk_Category")["ROI_Percentage"].agg(["mean","std"]).reset_index()
    fig = go.Figure(go.Bar(x=risk["Risk_Category"], y=risk["mean"], error_y=dict(type="data", array=risk["std"]), marker_color=[RISK_C.get(x) for x in risk["Risk_Category"]]))
    c2.plotly_chart(layout(fig, "Avg ROI with volatility by risk tier"), use_container_width=True)

    section("Investment vs ROI")
    sample = df.sample(min(len(df), 6000), random_state=7)
    fig = px.scatter(sample, x="Investment_Amount_USD", y="ROI_Percentage", color="Sector", size="ESG_Score", hover_data=["Company_Name","State","Year"], color_discrete_sequence=PAL)
    fig.update_xaxes(type="log")
    st.plotly_chart(layout(fig, "Project investment vs ROI, bubble sized by ESG", 440), use_container_width=True)

elif page == "Sector Deep Dive":
    head("Sector Deep Dive", "Sector-level investment, ROI, ESG, carbon, and geography.")
    chosen = st.selectbox("Select sector for deep dive", sorted(df["Sector"].unique()))
    sd = df[df["Sector"] == chosen]
    desc = sector_info.loc[sector_info["Sector"].eq(chosen), "Description"]
    if not desc.empty: st.info(desc.iloc[0])

    cols = st.columns(5)
    vals = [(money(sd["Investment_Amount_USD"].sum()), "Investment", ""), (f"{sd['CO2_Reduction_Tons'].sum()/1e6:.2f}M", "CO2 tons", ""),
            (pct(weighted_avg(sd, "ROI_Percentage", "Investment_Amount_USD")), "Weighted ROI", ""), (f"{sd['ESG_Score'].mean():.1f}", "Avg ESG", ""), (f"{sd['Project_ID'].nunique():,}", "Projects", "")]
    for c, v in zip(cols, vals): c.markdown(kpi(*v), unsafe_allow_html=True)

    section("Sector Trends")
    c1, c2 = st.columns(2)
    trend = sd.groupby("Year").agg(Investment=("Investment_Amount_USD","sum"), ROI=("ROI_Percentage","mean"), CO2=("CO2_Reduction_Tons","sum")).reset_index()
    c1.plotly_chart(layout(px.bar(trend, x="Year", y="Investment"), f"{chosen}: investment trend"), use_container_width=True)
    c2.plotly_chart(layout(px.line(trend, x="Year", y="ROI", markers=True), f"{chosen}: ROI trend"), use_container_width=True)

    section("State and Risk Mix")
    c1, c2 = st.columns(2)
    st_inv = sd.groupby("State")["Investment_Amount_USD"].sum().sort_values(ascending=False).head(12).reset_index()
    c1.plotly_chart(layout(px.bar(st_inv, y="State", x="Investment_Amount_USD", orientation="h"), "Top states"), use_container_width=True)
    rk = sd["Risk_Category"].value_counts().reset_index()
    rk.columns = ["Risk", "Projects"]
    c2.plotly_chart(layout(px.pie(rk, values="Projects", names="Risk", hole=.55, color="Risk", color_discrete_map=RISK_C), "Risk distribution"), use_container_width=True)

elif page == "Data Model & QA":
    head("Data Model & QA", "Professional relationship audit: 1:1, 1:M, table grain, and quality checks.")
    cols = st.columns(5)
    vals = [(f"{master['Project_ID'].nunique():,}", "Project primary key", ""), ("2", "1:1 fact joins", "Carbon + ROI"),
            ("2", "1:M dimensions", "Company + sector"), (f"{rel_df['Status'].eq('Pass').sum()}/{len(rel_df)}", "Relationships pass", ""),
            (f"{qa_df['Status'].eq('Pass').sum()}/{len(qa_df)}", "QA pass", "")]
    for c, v in zip(cols, vals): c.markdown(kpi(*v), unsafe_allow_html=True)

    st.markdown("<div class='insight'><b>Model logic:</b> the master table is one row per Project_ID. Carbon and ROI join 1:1 by Project_ID. ESG joins 1:M from Company_Name to projects. Sector info joins 1:M from Sector to projects.</div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Relationships", "QA Checks", "Table Dictionary"])
    with t1:
        st.dataframe(rel_df, hide_index=True, use_container_width=True)
    with t2:
        st.dataframe(qa_df, hide_index=True, use_container_width=True)
    with t3:
        st.dataframe(profile_df, hide_index=True, use_container_width=True)

st.markdown("<p class='small'>HDFC Bank Green Finance & ESG Investment Tracker v5.1 - Streamlit + Plotly</p>", unsafe_allow_html=True)
