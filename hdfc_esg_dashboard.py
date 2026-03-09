"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  HDFC Bank: Green Finance & ESG Investment Tracker  v4.0                     ║
║  RUN:  pip install streamlit plotly pandas numpy requests                     ║
║        streamlit run hdfc_esg_dashboard.py                                    ║
║  CSV files must be in the SAME folder as this script                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import datetime, warnings, requests
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
warnings.filterwarnings("ignore")
# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HDFC Bank · Green Finance & ESG",
    page_icon="🌿", layout="wide",
    initial_sidebar_state="expanded",
)
# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
:root{
  --bg:#040914;--surf:rgba(14, 24, 41, 0.65);--surf2:rgba(19, 32, 53, 0.65);
  --bord:rgba(32,196,138,0.25);--green:#20C48A;--green2:#00FFB3;
  --gold:#FFC107;--blue:#42A5F5;--red:#FF5252;
  --muted:#8096b8;--text:#F1F5F9;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:var(--bg) !important;
  background-image: radial-gradient(circle at 15% 15%, rgba(32, 196, 138, 0.04) 0%, transparent 40%), radial-gradient(circle at 85% 85%, rgba(66, 165, 245, 0.04) 0%, transparent 40%) !important;
  font-family:'Plus Jakarta Sans',sans-serif!important;color:var(--text)!important;
}
[data-testid="block-container"]{padding:1.5rem 2rem 2.5rem!important; max-width: 1400px;}
[data-testid="stSidebar"]{
  background:rgba(5, 16, 31, 0.85)!important;
  backdrop-filter: blur(12px);
  border-right:1px solid rgba(255,255,255,0.08)!important;
}
[data-testid="stSidebar"] *{color:var(--text)!important;}
[data-testid="stSidebar"] label{color:var(--muted)!important;font-size:.73rem!important;
  text-transform:uppercase;letter-spacing:1px;font-weight:600;}
/* sidebar select/multiselect boxes */
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input{
  background:rgba(14,24,41,0.5)!important;border-color:rgba(255,255,255,0.1)!important;
  color:var(--text)!important;}
[data-testid="stSidebar"] [data-baseweb="select"] div:focus-within{
  border-color:var(--green)!important;box-shadow: 0 0 0 1px var(--green)!important;}
/* logo */
.logo-wrap{background:linear-gradient(135deg,rgba(183,28,28,0.8),rgba(123,0,0,0.8));
  border-radius:12px;padding:18px 20px 14px;margin-bottom:24px;
  border:1px solid rgba(255,255,255,.1); box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
.logo-title{font-family:'Inter',sans-serif;font-size:1.1rem;font-weight:700;color:#fff;margin:0;letter-spacing:0.5px;}
.logo-sub{font-size:.7rem;color:rgba(255,255,255,.6);margin:4px 0 0;font-weight:500;}
/* nav buttons */
div[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;border:1px solid transparent!important;
  color:var(--muted)!important;border-radius:8px!important;width:100%!important;
  text-align:left!important;padding:10px 14px!important;font-size:.85rem!important;
  font-family:'Inter',sans-serif!important;font-weight:500!important;margin-bottom:4px!important;
  transition:all .2s cubic-bezier(0.4, 0, 0.2, 1)!important;}
div[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(255,255,255,0.05)!important;
  color:var(--text)!important;transform:translateX(4px)!important;}
div[data-testid="stSidebar"] .stButton>button:active, div[data-testid="stSidebar"] .stButton>button:focus{
  background:rgba(32,196,138,.15)!important;border-color:rgba(32,196,138,.3)!important;
  color:var(--green)!important;}
/* KPI cards */
.kpi-card{background:var(--surf); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border:1px solid rgba(255,255,255,0.06);border-radius:14px;
  padding:20px;position:relative;overflow:hidden;
  transition:transform .25s ease,box-shadow .25s ease;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--green),var(--blue));opacity:0;transition:opacity .25s ease;}
.kpi-card:hover{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,0.25);border-color:rgba(255,255,255,0.12);}
.kpi-card:hover::before{opacity:1;}
.kpi-icon{font-size:1.4rem;margin-bottom:10px;display:inline-block;padding:8px;background:rgba(255,255,255,0.05);border-radius:10px;}
.kpi-val{font-family:'Inter',sans-serif;font-size:1.8rem;font-weight:700;
  color:var(--text);line-height:1.1;margin:0 0 6px;letter-spacing:-0.5px;}
.kpi-label{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px;font-weight:600;}
.kpi-delta{font-size:.75rem;color:var(--green);font-weight:600;margin-top:6px;display:flex;align-items:center;gap:4px;}
/* page header */
.pg-header{background:linear-gradient(135deg,rgba(12,30,56,0.8),rgba(6,24,18,0.8));
  backdrop-filter: blur(10px); border:1px solid rgba(255,255,255,0.08);border-radius:16px;
  padding:24px 32px;margin-bottom:28px;display:flex;align-items:center;gap:18px;box-shadow:0 4px 20px rgba(0,0,0,0.15);}
.pg-icon{font-size:2.2rem;background:rgba(255,255,255,0.05);padding:12px;border-radius:14px;}
.pg-title{font-family:'Inter',sans-serif;font-size:1.6rem;font-weight:700;
  color:#fff;margin:0 0 4px;letter-spacing:-0.5px;}
.pg-sub{font-size:.85rem;color:var(--muted);margin:0;font-weight:500;}
/* section titles */
.sec-title{font-family:'Inter',sans-serif;font-size:1.05rem;font-weight:600;
  color:var(--text);display:flex;align-items:center;gap:10px;
  border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;margin:32px 0 16px;}
.sec-title::before{content:'';width:4px;height:16px;background:var(--green);border-radius:2px;}
/* ribbon */
.ribbon{background:var(--surf2);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.06);border-radius:12px;
  padding:14px 16px;display:flex;gap:0;margin-bottom:24px;box-shadow:0 4px 15px rgba(0,0,0,0.1);}
.rib-item{flex:1;text-align:center;border-right:1px solid rgba(255,255,255,0.06);padding:0 12px;}
.rib-item:last-child{border-right:none;}
.rib-val{font-family:'Inter',sans-serif;font-weight:700;color:var(--text);font-size:1.1rem;}
.rib-lbl{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600;}
/* insight */
.insight{background:rgba(32,196,138,0.04);
  backdrop-filter: blur(5px); border:1px solid rgba(32,196,138,0.15);border-left:4px solid var(--green);
  border-radius:10px;padding:16px 20px;font-size:.88rem;color:var(--text);
  margin-top:16px;line-height:1.7;}
.insight b{color:var(--green2);font-weight:600;}
/* filter section header in sidebar */
.flt-head{font-size:.7rem;color:var(--muted);text-transform:uppercase;font-weight:600;
  letter-spacing:1px;margin-bottom:6px;margin-top:16px;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
/* Plotly tooltip aesthetics */
.hovertext {font-family: 'Inter', sans-serif !important;}
</style>
""", unsafe_allow_html=True)
# ── COLOUR / TEMPLATE CONSTANTS ───────────────────────────────────────────────
D_BG  = "rgba(0,0,0,0)" # Transparent for glassmorphism
D_BG2 = "#040914" 
GRN   = "#20C48A"; GRN2 = "#00FFB3"
GOLD  = "#F59E0B"; BLUE = "#3B82F6"
MUT   = "#94A3B8"; TXT  = "#F8FAFC"
GRID  = "rgba(255,255,255,0.03)"; LINE = "rgba(255,255,255,0.05)"
# Tailored distinct colors for sectors
PAL   = ["#34D399","#60A5FA","#FBBF24","#F87171","#A78BFA",
         "#2DD4BF","#FB923C","#38BDF8","#4ADE80","#F472B6"]
RISK_C = {"Low":"#10B981","Medium":"#F59E0B","High":"#EF4444"}
# Base layout dict (plain dict — safe to ** unpack)
BL = dict(
    paper_bgcolor=D_BG, plot_bgcolor=D_BG,
    font=dict(family="Inter,sans-serif", color=MUT, size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TXT, size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(gridcolor=GRID, linecolor=LINE, zeroline=False,
               tickfont=dict(color=MUT, size=11), title_font=dict(color=MUT)),
    yaxis=dict(gridcolor=GRID, linecolor="rgba(0,0,0,0)", zeroline=False,
               tickfont=dict(color=MUT, size=11), title_font=dict(color=MUT)),
    margin=dict(l=10,r=10,t=50,b=20),
    coloraxis_colorbar=dict(tickfont=dict(color=MUT), title_font=dict(color=MUT)),
    hoverlabel=dict(bgcolor="rgba(14,24,41,0.9)", font_size=12, font_family="Inter,sans-serif", bordercolor="rgba(255,255,255,0.1)"),
    hovermode="x unified"
)
def T(fig, title="", h=None):
    kw = dict(**BL)
    kw["title"] = dict(text=title,
                       font=dict(family="Inter,sans-serif", color=TXT, size=14, weight=600),
                       x=0.01, xanchor="left", y=0.96)
    if h: kw["height"] = h
    fig.update_layout(**kw)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, griddash="dash")
    return fig
def combo_lay(fig, title, h=350):
    """Layout for make_subplots dual-axis."""
    fig.update_layout(
        paper_bgcolor=D_BG, plot_bgcolor=D_BG, hovermode="x unified",
        font=dict(family="Inter,sans-serif", color=MUT, size=11),
        title=dict(text=title,
                   font=dict(family="Inter,sans-serif", color=TXT, size=14, weight=600),
                   x=0.01, y=0.96),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TXT, size=11), orientation="h", y=1.05, x=1, xanchor="right"),
        xaxis=dict(gridcolor=GRID, linecolor=LINE, zeroline=False, tickfont=dict(color=MUT), showgrid=False),
        yaxis=dict(gridcolor=GRID, linecolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(color=MUT), griddash="dash"),
        margin=dict(l=10,r=10,t=50,b=20), height=h,
        hoverlabel=dict(bgcolor="rgba(14,24,41,0.9)", bordercolor="rgba(255,255,255,0.1)"),
    )
def hmap_lay(fig, title, h=350):
    """Layout for go.Heatmap figures."""
    fig.update_layout(
        paper_bgcolor=D_BG, plot_bgcolor=D_BG,
        font=dict(family="Inter,sans-serif", color=MUT, size=11),
        title=dict(text=title,
                   font=dict(family="Inter,sans-serif", color=TXT, size=14, weight=600),
                   x=0.01, y=0.96),
        xaxis=dict(tickfont=dict(color=TXT), showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(color=TXT), showgrid=False, zeroline=False),
        margin=dict(l=10,r=10,t=50,b=20), height=h,
        hoverlabel=dict(bgcolor="rgba(14,24,41,0.9)", bordercolor="rgba(255,255,255,0.1)"),
    )
# ── INDIA STATE LAT/LON ───────────────────────────────────────────────────────
STATE_LL = {
    "Bihar":(25.10,85.31),"Chhattisgarh":(21.28,81.87),"Delhi":(28.70,77.10),
    "Gujarat":(22.26,71.19),"Haryana":(29.06,76.09),"Karnataka":(15.32,75.71),
    "Madhya Pradesh":(22.97,78.66),"Maharashtra":(19.75,75.71),"Odisha":(20.95,85.10),
    "Punjab":(31.15,75.34),"Rajasthan":(27.02,74.22),"Tamil Nadu":(11.13,78.66),
    "Telangana":(18.11,79.02),"Uttar Pradesh":(26.85,80.95),"West Bengal":(22.99,87.86),
}
# State name mapping: our CSV names → GeoJSON ST_NM names
STATE_NAME_MAP = {
    "Delhi": "NCT of Delhi",
    "Uttarakhand": "Uttarakhand",
    "Jammu and Kashmir": "Jammu & Kashmir",
}
# ── INDIA GeoJSON (cached) ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_india_geojson():
    """Fetch India states GeoJSON. Returns dict or None on failure."""
    url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112"
           "/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None
# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="🌿 Loading ESG data…")
def load_data():
    geo  = pd.read_csv("green_investments_geographic.csv",
                       parse_dates=["Project_Start_Date"])
    cr   = pd.read_csv("carbon_reduction.csv")
    esg  = pd.read_csv("esg_scores_companies.csv")
    roi  = pd.read_csv("roi_returns.csv")
    sec  = pd.read_csv("sector_info.csv", header=None,
                       names=["Sector","Description"])
    m = geo.merge(cr,  on="Project_ID", how="left", suffixes=("","_cr"))
    m = m.merge(roi, on="Project_ID", how="left")
    m = m.merge(esg, on="Company_Name", how="left")
    if "Year_cr" in m.columns:
        m["Year"] = m["Year"].fillna(m["Year_cr"])
        m.drop(columns=["Year_cr"], inplace=True)
    m["Year"] = m["Year"].astype(int)
    m["Investment_M"] = m["Investment_Amount_USD"] / 1e6
    m["lat"] = m["State"].map(lambda s: STATE_LL.get(s,(None,None))[0])
    m["lon"] = m["State"].map(lambda s: STATE_LL.get(s,(None,None))[1])
    # GeoJSON state name column
    m["State_geo"] = m["State"].map(lambda s: STATE_NAME_MAP.get(s, s))
    return m, sec
try:
    master, sector_df = load_data()
    DATA_OK  = True
    MIN_DATE = datetime.date(int(master["Year"].min()), 1, 1)
    MAX_DATE = datetime.date(int(master["Year"].max()), 12, 31)
    ALL_SECTORS = ["All Sectors"] + sorted(master["Sector"].dropna().unique().tolist())
    ALL_STATES  = ["All States"]  + sorted(master["State"].dropna().unique().tolist())
except FileNotFoundError as e:
    DATA_OK = False; ERR_MSG = str(e)
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-wrap">
      <div class="logo-title">🏦 HDFC Bank</div>
      <div class="logo-sub">Green Finance &amp; ESG Investment Tracker</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("##### 📌 Navigation")
    PAGES = {
        "🏠 Executive Overview":       "overview",
        "🌿 ESG Analysis":             "esg",
        "🗺️  Geographic Intelligence":  "geo",
        "🌍 Carbon Reduction":         "carbon",
        "💰 ROI & Returns":            "roi",
        "🔍 Sector Deep Dive":         "sector",
    }
    if "page" not in st.session_state:
        st.session_state.page = "overview"
    for lbl, key in PAGES.items():
        if st.button(lbl, key=f"nav_{key}"):
            st.session_state.page = key
    if DATA_OK:
        st.markdown("---")
        st.markdown("##### 🎛️ Global Filters")
        # ── Date Range ──
        st.markdown('<div class="flt-head">📅 Date Range</div>', unsafe_allow_html=True)
        date_range = st.date_input(
            "", value=(MIN_DATE, MAX_DATE),
            min_value=MIN_DATE, max_value=MAX_DATE,
            label_visibility="collapsed",
        )
        # ── Year Slider ──
        years = sorted(master["Year"].unique().tolist())
        yr_range = st.select_slider("🗓️ Year Slider", options=years,
                                    value=(min(years), max(years)))
        # ── Sector Dropdown ──
        st.markdown('<div class="flt-head">🏭 Sector</div>', unsafe_allow_html=True)
        sel_sector = st.selectbox("", ALL_SECTORS,
                                  label_visibility="collapsed",
                                  key="sb_sector")
        # ── State Dropdown ──
        st.markdown('<div class="flt-head">📍 State</div>', unsafe_allow_html=True)
        sel_state = st.selectbox("", ALL_STATES,
                                 label_visibility="collapsed",
                                 key="sb_state")
        # ── Region ──
        st.markdown('<div class="flt-head">🗺️ Region</div>', unsafe_allow_html=True)
        regions = ["All Regions"] + sorted(master["Region"].dropna().unique().tolist())
        sel_region = st.selectbox("", regions,
                                  label_visibility="collapsed",
                                  key="sb_region")
        # ── ESG Risk ──
        st.markdown('<div class="flt-head">⚠️ ESG Risk</div>', unsafe_allow_html=True)
        sel_risk = st.selectbox("", ["All Risk Tiers","Low","Medium","High"],
                                label_visibility="collapsed",
                                key="sb_risk")
        st.markdown("---")
        st.caption(f"📊 v4.0  ·  {len(master):,} records")
# ── GUARD ─────────────────────────────────────────────────────────────────────
if not DATA_OK:
    st.error(f"❌ CSV not found: {ERR_MSG}")
    st.stop()
# ── FILTER LOGIC ──────────────────────────────────────────────────────────────
def filt(df):
    d = df.copy()
    if len(date_range) == 2:
        d = d[(d["Year"] >= date_range[0].year) & (d["Year"] <= date_range[1].year)]
    d = d[(d["Year"] >= yr_range[0]) & (d["Year"] <= yr_range[1])]
    if sel_sector != "All Sectors":
        d = d[d["Sector"] == sel_sector]
    if sel_state != "All States":
        d = d[d["State"] == sel_state]
    if sel_region != "All Regions":
        d = d[d["Region"] == sel_region]
    if sel_risk not in ("All Risk Tiers",""):
        d = d[d["Risk_Category"] == sel_risk]
    return d
df = filt(master)
# ── KPI CARD HTML ─────────────────────────────────────────────────────────────
def kpi(icon, val, label, delta=""):
    dl = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    return (f"<div class='kpi-card'><div class='kpi-icon'>{icon}</div>"
            f"<div class='kpi-val'>{val}</div>"
            f"<div class='kpi-label'>{label}</div>{dl}</div>")
# ── ACTIVE FILTER BADGE ───────────────────────────────────────────────────────
def filter_badge():
    parts = []
    if sel_sector != "All Sectors": parts.append(f"Sector: {sel_sector}")
    if sel_state  != "All States":  parts.append(f"State: {sel_state}")
    if sel_region != "All Regions": parts.append(f"Region: {sel_region}")
    if sel_risk not in ("All Risk Tiers",""):  parts.append(f"Risk: {sel_risk}")
    parts.append(f"Years: {yr_range[0]}–{yr_range[1]}")
    if parts:
        tags = "".join(
            f"<span style='background:rgba(32,196,138,.12);border:1px solid rgba(32,196,138,.3);"
            f"border-radius:6px;padding:2px 10px;font-size:.72rem;color:#20C48A;margin-right:6px;'>"
            f"{p}</span>" for p in parts
        )
        st.markdown(f"<div style='margin-bottom:14px;'>{tags}</div>",
                    unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P1 — EXECUTIVE OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "overview":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🏠</div><div>
    <div class="pg-title">Executive Overview</div>
    <div class="pg-sub">HDFC Bank Green Finance &amp; ESG — Consolidated Performance Dashboard</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()
    inv  = df["Investment_Amount_USD"].sum() / 1e9
    co2  = df["CO2_Reduction_Tons"].sum() / 1e6
    roi_ = df["ROI_Percentage"].mean()
    esg_ = df["ESG_Score"].mean()
    npr  = df["Project_ID"].nunique()
    nst  = df["State"].nunique()
    cols = st.columns(6)
    for col,(ic,vl,lb,dl) in zip(cols,[
        ("💵",f"${inv:.2f}B","Total Investment","↑ Green Portfolio"),
        ("🌍",f"{co2:.2f}M T","CO₂ Avoided",f"≈{co2/4.6:.1f}M cars off road"),
        ("📈",f"{roi_:.1f}%","Avg Portfolio ROI","Risk-Adjusted"),
        ("🌿",f"{esg_:.1f}","Avg ESG Score","Portfolio Health"),
        ("🏗️",f"{npr:,}","Active Projects","All sectors"),
        ("📍",f"{nst}","States Covered","Pan-India Reach"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb,dl), unsafe_allow_html=True)
    bsec = df.groupby("Sector")["Investment_Amount_USD"].sum().idxmax() if len(df)>0 else "—"
    breg = df.groupby("Region")["Investment_Amount_USD"].sum().idxmax() if len(df)>0 else "—"
    brs  = df.groupby("Sector")["ROI_Percentage"].mean().idxmax() if len(df)>0 else "—"
    lrp  = round(len(df[df["Risk_Category"]=="Low"])/max(len(df),1)*100,1)
    st.markdown(f"""<div class="ribbon" style="margin-top:14px;">
    <div class="rib-item"><div class="rib-val">{df['Sector'].nunique()}</div><div class="rib-lbl">Sectors</div></div>
    <div class="rib-item"><div class="rib-val">{bsec}</div><div class="rib-lbl">Top Invested</div></div>
    <div class="rib-item"><div class="rib-val">{breg}</div><div class="rib-lbl">Leading Region</div></div>
    <div class="rib-item"><div class="rib-val">{brs}</div><div class="rib-lbl">Best ROI Sector</div></div>
    <div class="rib-item"><div class="rib-val">{lrp}%</div><div class="rib-lbl">Low-Risk Share</div></div>
    <div class="rib-item"><div class="rib-val">{yr_range[0]}–{yr_range[1]}</div><div class="rib-lbl">Period</div></div>
    </div>""", unsafe_allow_html=True)
    # Stacked area + donut
    st.markdown('<div class="sec-title">📈 Investment Trajectory &amp; Allocations</div>', unsafe_allow_html=True)
    a1,a2 = st.columns([7,3])
    with a1:
        tr = df.groupby(["Year","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f = px.area(tr, x="Year", y="Investment_Amount_USD", color="Sector",
                    color_discrete_sequence=PAL, line_shape="spline")
        f.update_traces(line=dict(width=2.5), mode="lines")
        T(f,"📈 Annual Green Investment Trajectory by Sector",340)
        st.plotly_chart(f, use_container_width=True)
    with a2:
        pd_ = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
        f2 = px.pie(pd_, values="Investment_Amount_USD", names="Sector",
                    color_discrete_sequence=PAL, hole=0.65)
        f2.update_traces(textinfo="label+percent", textfont_size=11,
                         marker=dict(line=dict(color=D_BG,width=3)), pull=[0.02]*len(pd_))
        T(f2,"🥧 Portfolio Sector Allocation",340)
        st.plotly_chart(f2, use_container_width=True)
    # NEW SUPER CHART: Executive Investment & Impact Combo
    st.markdown('<div class="sec-title">🏛️ Executive Investment &amp; Impact Analysis</div>', unsafe_allow_html=True)
    
    # We need a summarized view of Year: Inv (Sum), ESG (Mean), ROI (Mean)
    # The dataset relies on df which has already been joined with ROI and ESG scores
    agg_df = df.dropna(subset=["ESG_Score", "ROI_Percentage"]).groupby("Year").agg({
        "Investment_Amount_USD":"sum",
        "ESG_Score":"mean",
        "ROI_Percentage":"mean"
    }).reset_index()
    
    f_combo = make_subplots(specs=[[{"secondary_y":True}]])
    # Bar for Investment
    f_combo.add_trace(go.Bar(x=agg_df["Year"], y=agg_df["Investment_Amount_USD"],
                             name="Total Investment", marker_color=GRN, opacity=0.85,
                             hovertemplate="%{x}<br>Inv: $%{y:,.2s}<extra></extra>"),
                      secondary_y=False)
    # Line for ROI
    f_combo.add_trace(go.Scatter(x=agg_df["Year"], y=agg_df["ROI_Percentage"],
                                 name="Avg ROI %", mode="lines+markers",
                                 line=dict(color=GOLD, width=3.5, dash="dash"),
                                 marker=dict(size=8, color=GOLD, line=dict(color=D_BG,width=2)),
                                 hovertemplate="%{x}<br>ROI: %{y:.1f}%<extra></extra>"),
                      secondary_y=True)
    # Line for ESG
    f_combo.add_trace(go.Scatter(x=agg_df["Year"], y=agg_df["ESG_Score"],
                                 name="Avg ESG Score", mode="lines+markers",
                                 line=dict(color="#00E5FF", width=3.5),
                                 marker=dict(size=10, symbol="diamond", color="#00E5FF", line=dict(color=D_BG,width=2)),
                                 hovertemplate="%{x}<br>ESG: %{y:.1f}<extra></extra>"),
                      secondary_y=True)
                      
    combo_lay(f_combo, "📊 Investment Volume vs. Avg ROI and Avg ESG Matrix", 420)
    f_combo.update_yaxes(title_text="Investment (USD)", showgrid=False, secondary_y=False)
    f_combo.update_yaxes(title_text="Score / Percentage", showgrid=False, secondary_y=True)
    st.plotly_chart(f_combo, use_container_width=True)
    # 3-col snapshot -> Upgraded to include Waterfall
    st.markdown('<div class="sec-title">🌿 Advanced Risk &amp; Momentum Snapshot</div>', unsafe_allow_html=True)
    b1,b2,b3 = st.columns([3,3,4])
    with b1:
        er = df.groupby("Risk_Category")["Investment_Amount_USD"].sum().reset_index()
        er["ord"]=er["Risk_Category"].map({"Low":0,"Medium":1,"High":2})
        er = er.sort_values("ord")
        f3 = px.bar(er, x="Risk_Category", y="Investment_Amount_USD",
                    color="Risk_Category", text_auto=".2s", color_discrete_map=RISK_C)
        f3.update_traces(textposition="outside",textfont_color=TXT, cliponaxis=False)
        T(f3,"⚠️ Investment by Risk Tier",360)
        st.plotly_chart(f3, use_container_width=True)
    with b2:
        rs = df.groupby("Sector")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage")
        f5 = px.bar(rs, x="ROI_Percentage", y="Sector", orientation="h",
                    color="ROI_Percentage", color_continuous_scale="Teal", text_auto=".1f")
        f5.update_traces(textposition="outside",textfont_color=TXT, cliponaxis=False)
        f5.update_layout(coloraxis_showscale=False)
        T(f5,"💰 Avg ROI by Sector (%)",360)
        st.plotly_chart(f5, use_container_width=True)
    # YoY + Quarter
    st.markdown('<div class="sec-title">📆 Seasonality &amp; YoY Growth</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([2,3])
    with g1:
        qd = df.groupby("Quarter")["Investment_Amount_USD"].sum().reset_index()
        qd["ord"]=qd["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
        qd = qd.sort_values("ord")
        f6 = px.pie(qd, values="Investment_Amount_USD", names="Quarter",
                    color_discrete_sequence=[GRN,GRN2,GOLD,BLUE], hole=0.6)
        f6.update_traces(textinfo="label+percent", marker=dict(line=dict(color=D_BG,width=3)), pull=[0.02]*len(qd))
        T(f6,"📅 Investment by Quarter",340)
        st.plotly_chart(f6, use_container_width=True)
    with g2:
        # Waterfall momentum replacement
        max_year = df["Year"].max() if len(df)>0 else 2024
        fwf = df[df["Year"]==max_year].groupby("Quarter")["Investment_Amount_USD"].sum().reset_index()
        if not fwf.empty:
            fwf["ord"]=fwf["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
            fwf = fwf.sort_values("ord")
            
            diffs = [fwf["Investment_Amount_USD"].iloc[0]]
            for i in range(1, len(fwf)):
                diffs.append(fwf["Investment_Amount_USD"].iloc[i] - fwf["Investment_Amount_USD"].iloc[i-1])
                
            f_wf = go.Figure(go.Waterfall(
                name="20", orientation="v",
                measure=["relative"] * len(fwf),
                x=fwf["Quarter"],
                textposition="outside",
                text=[f"${d/1e6:.0f}M" for d in diffs],
                y=diffs,
                connector={"line":{"color":MUT}},
                decreasing={"marker":{"color":"#FF5252"}},
                increasing={"marker":{"color":GRN}},
                totals={"marker":{"color":GOLD}}
            ))
            T(f_wf, f"🌊 QoQ Investment Momentum ({max_year})", 340)
            st.plotly_chart(f_wf, use_container_width=True)
        else:
            st.info("No timeline data currently available.")
    c_m = agg_df["ROI_Percentage"].corr(agg_df["Investment_Amount_USD"]) if len(agg_df)>1 else 0
    st.markdown(f"""<div class="insight" style="margin-top:10px;">
        🤖 <b>AI Executive Core Summary:</b> The overall portfolio stands at <b>${inv:.2f}B</b> distributed across <b>{df['Sector'].nunique()}</b> key green sectors. 
        Steady YoY growth signals an accelerating commitment to transition financing. 
        Crucially, analytical modeling reveals that ROI metrics <b>{"align securely" if c_m > 0 else "show complex variations"}</b> 
        with scaled capital deployment, verifying our advanced ESG investment thesis across the {yr_range[0]}–{yr_range[1]} target epoch.
    </div>""", unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P2 — ESG ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "esg":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🌿</div><div>
    <div class="pg-title">ESG Analysis</div>
    <div class="pg-sub">Environmental · Social · Governance deep-dive across companies and risk tiers</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()
    ae  = df["ESG_Score"].mean()
    lp  = round(len(df[df["Risk_Category"]=="Low"])/max(len(df),1)*100,1)
    hp  = round(len(df[df["Risk_Category"]=="High"])/max(len(df),1)*100,1)
    tco = (df.dropna(subset=["ESG_Score"]).groupby("Company_Name")["ESG_Score"]
             .mean().idxmax() if len(df)>0 else "N/A")
    c1,c2,c3,c4 = st.columns(4)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4],[
        ("🌿",f"{ae:.1f}","Avg ESG Score"),("✅",f"{lp}%","Low-Risk Projects"),
        ("⚠️",f"{hp}%","High-Risk Projects"),
        ("🏅",(tco[:16]+"…") if len(tco)>16 else tco,"Top ESG Company"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 ESG Score Distribution &amp; Advanced Risk Profile</div>', unsafe_allow_html=True)
    h1,h2 = st.columns([3,2])
    with h1:
        f = px.histogram(df.dropna(subset=["ESG_Score"]), x="ESG_Score",
                         color="Risk_Category", nbins=45, barmode="overlay",
                         color_discrete_map=RISK_C, opacity=0.8)
        f.update_layout(bargap=0.06, showlegend=False)
        T(f,"📊 ESG Score Distribution",340)
        st.plotly_chart(f, use_container_width=True)
    with h2:
        # SUPER CHART: Interactive Sunburst for Risk Profile -> Sector
        st.markdown('<div style="margin-bottom:-10px;"></div>', unsafe_allow_html=True)
        sb_df = df.groupby(["Risk_Category", "Sector"])["Investment_Amount_USD"].sum().reset_index()
        f9 = px.sunburst(sb_df, path=["Risk_Category", "Sector"], values="Investment_Amount_USD",
                         color="Risk_Category", color_discrete_map=RISK_C)
        f9.update_traces(textinfo="label+percent entry", marker=dict(line=dict(color=D_BG,width=2)))
        T(f9,"🎯 Risk Profile by Sector Allocation",340)
        st.plotly_chart(f9, use_container_width=True)
    # 4D Bubble scatter
    st.markdown('<div class="sec-title">🔬 ESG Risk vs. Reward Spectrum (4D Matrix)</div>', unsafe_allow_html=True)
    bub = (df.dropna(subset=["ESG_Score","ROI_Percentage"])
           .groupby("Company_Name")
           .agg(ESG=("ESG_Score","first"), ROI=("ROI_Percentage","mean"),
                Inv=("Investment_Amount_USD","sum"), CO2=("CO2_Reduction_Tons","sum"),
                Risk=("Risk_Category","first"), Sector=("Sector","first"))
           .reset_index())
    
    # X=ESG, Y=ROI, Size=CO2_Reduction, Color=Risk Tier
    f3 = px.scatter(bub, x="ESG", y="ROI", size="CO2", color="Risk",
                    hover_name="Company_Name",
                    hover_data={"Sector":True,"Inv":":.2s","CO2":":.2s"},
                    color_discrete_map=RISK_C, size_max=45, opacity=0.85)
                    
    f3.update_traces(marker=dict(line=dict(width=1.5, color=D_BG)))
    f3.add_vline(x=bub["ESG"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ESG: {bub['ESG'].mean():.1f}",
                 annotation_font_color=MUT)
    f3.add_hline(y=bub["ROI"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ROI: {bub['ROI'].mean():.1f}%",
                 annotation_position="top right", annotation_font_color=MUT)
    f3.update_layout(xaxis=dict(title="ESG Score Rating"), yaxis=dict(title="Average ROI (%)"))
    T(f3,"📈 4D Matrix: ESG Rating vs. Yield vs. Lifecycle CO₂ Reduction", 420)
    st.plotly_chart(f3, use_container_width=True)
    # Sector Breakdown Maps Below
    # Violin + avg bar
    st.markdown('<div class="sec-title">🎻 ESG Score per Sector</div>', unsafe_allow_html=True)
    v1,v2 = st.columns(2)
    with v1:
        f4 = px.violin(df.dropna(subset=["ESG_Score","Sector"]),
                       x="Sector", y="ESG_Score", box=True,
                       color="Sector", color_discrete_sequence=PAL, points=False)
        T(f4,"🎻 ESG Violin — per Sector",340)
        st.plotly_chart(f4, use_container_width=True)
    with v2:
        es = df.groupby("Sector")["ESG_Score"].mean().reset_index().sort_values("ESG_Score",ascending=False)
        f5 = px.bar(es, y="Sector", x="ESG_Score", orientation="h",
                    color="ESG_Score", color_continuous_scale="Greens", text_auto=".1f")
        f5.update_traces(textposition="outside",textfont_color=TXT)
        T(f5,"📊 Avg ESG Score by Sector",340)
        st.plotly_chart(f5, use_container_width=True)
    # ── FIXED Decomposition Treemap ─────────────────────────────────────────
    st.markdown('<div class="sec-title">🌳 Decomposition Tree — Investment: Risk → Sector → Region → State</div>', unsafe_allow_html=True)
    tree = df.groupby(["Risk_Category","Sector","Region","State"])["Investment_Amount_USD"].sum().reset_index()
    f6 = px.treemap(
        tree,
        path=[px.Constant("🌏 ALL INDIA"), "Risk_Category","Sector","Region","State"],
        values="Investment_Amount_USD",
        color="Investment_Amount_USD",
        color_continuous_scale=[[0,"#051020"],[0.25,"#003D2A"],[0.6,GRN],[1.0,GRN2]],
    )
    # ✅ FIXED: NO custom_data, NO hovertemplate in update_traces (caused TypeError)
    f6.update_traces(
        textinfo="label+percent root",
        textfont=dict(family="Inter,sans-serif", size=12, color="#FFFFFF", weight=500),
        marker=dict(line=dict(color=D_BG, width=2)),
    )
    f6.update_layout(
        paper_bgcolor=D_BG,
        margin=dict(l=6,r=6,t=8,b=8), height=520,
        font=dict(color=TXT, family="Inter,sans-serif"),
        coloraxis_colorbar=dict(
            tickfont=dict(color=MUT),
            title=dict(text="Investment USD", font=dict(color=MUT)),
        ),
    )
    st.plotly_chart(f6, use_container_width=True)
    # Top 15 ESG companies
    st.markdown('<div class="sec-title">🏆 Top 15 Companies by ESG Score</div>', unsafe_allow_html=True)
    top = (df.dropna(subset=["ESG_Score"])
           .groupby("Company_Name")
           .agg(ESG=("ESG_Score","first"), Risk=("Risk_Category","first"))
           .sort_values("ESG",ascending=False).head(15).reset_index())
    f7 = px.bar(top, x="Company_Name", y="ESG", color="Risk",
                text="ESG", color_discrete_map=RISK_C)
    f7.update_traces(textposition="outside", textfont_color=TXT,
                     texttemplate="%{text:.1f}", cliponaxis=False)
    T(f7,"🏆 Top 15 Companies by ESG Score",380)
    st.plotly_chart(f7, use_container_width=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P3 — GEOGRAPHIC INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "geo":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🗺️</div><div>
    <div class="pg-title">Geographic Intelligence</div>
    <div class="pg-sub">India investment maps · Regional patterns · State-level spatial analysis</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()
    # ── State-level aggregate ────────────────────────────────────────────────
    st_agg = (df.dropna(subset=["State"])
              .groupby(["State","State_geo"])
              .agg(Investment=("Investment_Amount_USD","sum"),
                   Projects=("Project_ID","nunique"),
                   Avg_ROI=("ROI_Percentage","mean"),
                   CO2=("CO2_Reduction_Tons","sum"),
                   Avg_ESG=("ESG_Score","mean"))
              .reset_index())
    # ── TAB: Filled Map | Bubble Map ────────────────────────────────────────
    map_tab1, map_tab2 = st.tabs(["🗺️ Filled Choropleth Map", "🔵 Bubble Map"])
    with map_tab1:
        india_geo = get_india_geojson()
        if india_geo is not None:
            st.markdown('<div class="sec-title">🗺️ India — Filled State Choropleth (Investment USD)</div>',
                        unsafe_allow_html=True)
            fc = px.choropleth(
                st_agg,
                geojson=india_geo,
                locations="State_geo",
                featureidkey="properties.ST_NM",
                color="Investment",
                color_continuous_scale=[[0,"#0A1628"],[0.2,"#00563F"],
                                        [0.55,GRN],[0.8,GRN2],[1.0,"#FFFFFF"]],
                hover_name="State",
                hover_data={"Investment":":.2s","Projects":True,
                            "Avg_ROI":":.1f","CO2":":.0f",
                            "State_geo":False},
                scope="asia",
            )
            fc.update_geos(
                fitbounds="locations",
                visible=False,
                bgcolor=D_BG2,
                showcoastlines=True,  coastlinecolor="rgba(130,180,255,0.2)",
                showocean=True,       oceancolor="#060F1A",
                showland=True,        landcolor="#0D1E30",
                showframe=False,
            )
            fc.update_layout(
                paper_bgcolor=D_BG,
                geo_bgcolor=D_BG,
                font=dict(family="Inter,sans-serif", color=TXT, size=11),
                title=dict(
                    text="🗺️ Green Investment Filled Map — India States",
                    font=dict(family="Inter,sans-serif",color=TXT,size=14,weight=600),
                    x=0.01, y=0.96),
                coloraxis_colorbar=dict(
                    title="Investment (USD)",
                    tickfont=dict(color=MUT),
                    title_font=dict(color=MUT),
                    bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)",
                ),
                margin=dict(l=0,r=0,t=50,b=0), height=540,
            )
            fc.update_traces(marker_line_color="rgba(255,255,255,0.2)",
                             marker_line_width=1)
            st.plotly_chart(fc, use_container_width=True)
        else:
            st.warning("⚠️ Could not load India GeoJSON (check internet). Showing bubble map instead.")
    with map_tab2:
        st.markdown('<div class="sec-title">🔵 India Green Investment — Bubble Map</div>',
                    unsafe_allow_html=True)
        mp = (df.dropna(subset=["lat","lon"])
              .groupby(["State","lat","lon","Region"])
              .agg(Investment=("Investment_Amount_USD","sum"),
                   Projects=("Project_ID","nunique"),
                   Avg_ROI=("ROI_Percentage","mean"),
                   CO2=("CO2_Reduction_Tons","sum"))
              .reset_index())
        fm = px.scatter_geo(mp, lat="lat", lon="lon", size="Investment",
                            color="Region", hover_name="State",
                            hover_data={"Investment":":.2s","Projects":True,
                                        "Avg_ROI":":.1f","CO2":":.0f",
                                        "lat":False,"lon":False},
                            color_discrete_sequence=[GRN,GRN2,GOLD,BLUE,"#CE93D8"],
                            size_max=50, scope="asia",
                            projection="natural earth")
        fm.update_geos(
            visible=True, resolution=50,
            showcountries=True,  countrycolor="rgba(255,255,255,0.1)",
            showcoastlines=True, coastlinecolor="rgba(255,255,255,0.1)",
            showland=True,       landcolor=D_BG2,
            showocean=True,      oceancolor=D_BG,
            showsubunits=True,   subunitcolor="rgba(255,255,255,0.05)",
            showframe=False,     bgcolor=D_BG,
            center=dict(lat=22,lon=80),
            lataxis_range=[6,38], lonaxis_range=[65,100],
        )
        fm.update_layout(
            paper_bgcolor=D_BG, geo_bgcolor=D_BG,
            font=dict(family="Inter,sans-serif",color=TXT,size=11),
            title=dict(
                text="🔵 Green Investment Bubble Map",
                font=dict(family="Inter,sans-serif",color=TXT,size=14,weight=600),x=0.01,y=0.96),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=TXT,size=11),orientation="h",y=1.05),
            margin=dict(l=8,r=8,t=48,b=8), height=520,
        )
        st.plotly_chart(fm, use_container_width=True)
    # ── State detail card ────────────────────────────────────────────────────
    if sel_state != "All States":
        sd_ = df[df["State"]==sel_state]
        st.markdown(f'<div class="sec-title">📍 {sel_state} — State Detail</div>',
                    unsafe_allow_html=True)
        cc1,cc2,cc3,cc4 = st.columns(4)
        for col,(ic,vl,lb) in zip([cc1,cc2,cc3,cc4],[
            ("💵",f"${sd_['Investment_Amount_USD'].sum()/1e6:.1f}M","Investment"),
            ("🌍",f"{sd_['CO2_Reduction_Tons'].sum()/1e3:.1f}K T","CO₂ Avoided"),
            ("📈",f"{sd_['ROI_Percentage'].mean():.1f}%","Avg ROI"),
            ("🏗️",f"{sd_['Project_ID'].nunique():,}","Projects"),
        ]):
            with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🎯 Regional Efficiency Index</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([1,1])
    with g1:
        # SUPER CHART: Efficiency Scatter (Investment vs CO2 by Region)
        ri = df.groupby("Region").agg({
            "Investment_Amount_USD":"sum",
            "CO2_Reduction_Tons":"sum",
            "State":"nunique",
            "Project_ID":"nunique"
        }).reset_index()
        
        f = px.scatter(ri, x="Investment_Amount_USD", y="CO2_Reduction_Tons", color="Region",
                       size="Project_ID", hover_name="Region",
                       hover_data={"State":True, "Investment_Amount_USD":":.2s", "CO2_Reduction_Tons":":.2s", "Project_ID":False},
                       color_discrete_sequence=PAL, size_max=40, opacity=0.9)
        f.update_traces(marker=dict(line=dict(width=2, color=D_BG)))
        
        # Add diagonal reference line (Average Efficiency)
        avg_eff = ri["CO2_Reduction_Tons"].sum() / ri["Investment_Amount_USD"].sum()
        x_max = ri["Investment_Amount_USD"].max()
        f.add_shape(type="line", x0=0, y0=0, x1=x_max, y1=x_max * avg_eff,
                    line=dict(color=MUT, width=1, dash="dot"))
        
        # Annotate
        f.add_annotation(x=x_max*0.8, y=x_max*avg_eff*0.8, text="Avg Efficiency", showarrow=False, yshift=15, font=dict(color=MUT))
        T(f,"🎯 Efficiency: CO₂ Reduction vs. Capital Deployed",380)
        f.update_layout(xaxis=dict(title="Total Investment (USD)"), yaxis=dict(title="Total CO₂ Reduction (Tons)"))
        st.plotly_chart(f, use_container_width=True)
        
    with g2:
        # Calculate specific efficiency metric (CO2 per $1M)
        si = df.groupby("State").agg({
            "Investment_Amount_USD":"sum", 
            "CO2_Reduction_Tons":"sum"
        }).reset_index()
        si["Efficiency"] = si["CO2_Reduction_Tons"] / (si["Investment_Amount_USD"] / 1e6)
        si = si.sort_values("Efficiency", ascending=False).head(15)
        
        f3 = px.bar(si, y="State", x="Efficiency", orientation="h",
                    color="Efficiency", color_continuous_scale="Teal", text_auto=".1f")
        f3.update_traces(textposition="outside",textfont_color=TXT, cliponaxis=False)
        T(f3,"🏆 Top 15 States by Efficiency (CO₂ Tons per $1M Inv)",380)
        st.plotly_chart(f3, use_container_width=True)
    # Heatmaps
    st.markdown('<div class="sec-title">🔥 Investment Heatmaps</div>', unsafe_allow_html=True)
    hm1,hm2 = st.columns(2)
    with hm1:
        hp_df = df.groupby(["Sector","Region"])["Investment_Amount_USD"].sum().reset_index()
        pv = hp_df.pivot(index="Sector",columns="Region",values="Investment_Amount_USD").fillna(0)
        fh1 = go.Figure(go.Heatmap(
            z=pv.values, x=pv.columns.tolist(), y=pv.index.tolist(),
            colorscale=[[0,D_BG2],[0.4,"#0F766E"],[1.0,GRN2]],
            text=pv.values, texttemplate="%{text:.2s}", hoverongaps=False,
            colorbar=dict(tickfont=dict(color=MUT)),
        ))
        hmap_lay(fh1,"🔥 Sector × Region Heatmap",340)
        st.plotly_chart(fh1, use_container_width=True)
    with hm2:
        mo=["January","February","March","April","May","June",
            "July","August","September","October","November","December"]
        mp2 = df.groupby(["Year","Month_Name"])["Investment_Amount_USD"].sum().reset_index()
        mp2["Month_Name"] = pd.Categorical(mp2["Month_Name"],categories=mo,ordered=True)
        mp2 = mp2.sort_values("Month_Name")
        pv2 = mp2.pivot(index="Year",columns="Month_Name",values="Investment_Amount_USD").fillna(0)
        fh2 = go.Figure(go.Heatmap(
            z=pv2.values, x=pv2.columns.tolist(),
            y=pv2.index.astype(str).tolist(),
            colorscale=[[0,D_BG2],[0.4,"#0F766E"],[1.0,GRN2]],
            texttemplate="%{z:.2s}", hoverongaps=False,
            colorbar=dict(tickfont=dict(color=MUT)),
        ))
        hmap_lay(fh2,"📆 Monthly Heatmap (Year × Month)",340)
        fh2.update_xaxes(tickangle=38, tickfont=dict(color=MUT,size=10))
        st.plotly_chart(fh2, use_container_width=True)
    # City + Sunburst
    st.markdown('<div class="sec-title">🏙️ City Analysis &amp; Sunburst</div>', unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        ci = df.groupby("City")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(15)
        f5 = px.bar(ci, y="City", x="Investment_Amount_USD", orientation="h",
                    color="Investment_Amount_USD", color_continuous_scale="Teal",
                    text_auto=".2s")
        f5.update_traces(textposition="outside",textfont_color=TXT, cliponaxis=False)
        T(f5,"🏙️ Top 15 Cities by Investment",400)
        st.plotly_chart(f5, use_container_width=True)
    with cb:
        sn = df.groupby(["Region","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f6 = px.sunburst(sn, path=["Region","Sector"], values="Investment_Amount_USD",
                         color="Investment_Amount_USD",
                         color_continuous_scale=[[0,D_BG2],[0.3,"#0F766E"],[1.0,GRN2]])
        f6.update_traces(textfont=dict(family="Inter,sans-serif",size=11,color="#FFF",weight=500),
                         insidetextorientation="radial", marker=dict(line=dict(color=D_BG,width=2)))
        f6.update_layout(paper_bgcolor=D_BG,
                         font=dict(color=TXT,family="Inter,sans-serif"),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                         title=dict(text="☀️ Investment Sunburst: Region → Sector",
                                    font=dict(family="Inter,sans-serif",
                                              color=TXT,size=14,weight=600),x=0.01,y=0.96),
                         margin=dict(l=8,r=8,t=48,b=8), height=400)
        st.plotly_chart(f6, use_container_width=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P4 — CARBON REDUCTION
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "carbon":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🌍</div><div>
    <div class="pg-title">Carbon Reduction Analysis</div>
    <div class="pg-sub">CO₂ impact tracking · Sector-level emission abatement · Efficiency metrics</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()
    tc = df["CO2_Reduction_Tons"].sum()
    ac = df["CO2_Reduction_Tons"].mean()
    ef = df["Investment_Amount_USD"].sum() / max(tc,1)
    py = df.groupby("Year")["CO2_Reduction_Tons"].sum().idxmax() if len(df)>0 else "N/A"
    bs = df.groupby("Sector")["CO2_Reduction_Tons"].sum().idxmax() if len(df)>0 else "N/A"
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4,c5],[
        ("🌍",f"{tc/1e6:.2f}M T","Total CO₂ Reduced"),
        ("📊",f"{ac:,.0f} T","Avg CO₂ / Project"),
        ("📅",str(py),"Peak Year"),
        ("💵",f"${ef:.0f}","USD / Tonne CO₂"),
        ("🌱",bs,"Top CO₂ Sector"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
    # Trend + sector bar
    st.markdown('<div class="sec-title">📈 Carbon Trajectory &amp; Sectoral Contribution</div>', unsafe_allow_html=True)
    t1,t2 = st.columns([6,4])
    with t1:
        # SUPER CHART: Stacked Area Carbon Trajectory
        cy = df.groupby(["Year", "Sector"])["CO2_Reduction_Tons"].sum().reset_index()
        f = px.area(cy, x="Year", y="CO2_Reduction_Tons", color="Sector",
                    color_discrete_sequence=PAL, line_shape="spline")
        f.update_traces(line=dict(width=2.5), mode="lines")
        T(f,"📈 Sectoral Contribution to Annual CO₂ Abatement",340)
        f.update_layout(yaxis=dict(title="Tons of CO₂ Avoided"))
        st.plotly_chart(f, use_container_width=True)
    with t2:
        # SUPER CHART: Top 10 Carbon Savers (Company Level)
        cs = df.groupby("Company_Name")["CO2_Reduction_Tons"].sum().reset_index().sort_values("CO2_Reduction_Tons", ascending=False).head(10)
        cs = cs.sort_values("CO2_Reduction_Tons", ascending=True) # Sort ascending for Plotly h-bar
        f2 = px.bar(cs, x="CO2_Reduction_Tons", y="Company_Name", orientation="h",
                    color="CO2_Reduction_Tons", color_continuous_scale="Teal", text_auto=".2s")
        f2.update_traces(textposition="outside",textfont_color=TXT, cliponaxis=False)
        f2.update_layout(coloraxis_showscale=False)
        T(f2,"🏆 Top 10 Corporate Carbon Savers",340)
        st.plotly_chart(f2, use_container_width=True)
    # Heatmap
    st.markdown('<div class="sec-title">🔥 Carbon Heatmap — Sector × Year</div>', unsafe_allow_html=True)
    cp = df.groupby(["Year","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    pv = cp.pivot(index="Sector",columns="Year",values="CO2_Reduction_Tons").fillna(0)
    f3 = go.Figure(go.Heatmap(
        z=pv.values, x=pv.columns.astype(str).tolist(), y=pv.index.tolist(),
        colorscale=[[0,D_BG2],[0.3,"#0F766E"],[0.7,GRN],[1.0,GRN2]],
        text=pv.values, texttemplate="%{text:.2s}", hoverongaps=False,
        colorbar=dict(tickfont=dict(color=MUT)),
    ))
    hmap_lay(f3,"🔥 CO₂ Reduction Heatmap — Sector × Year",350)
    st.plotly_chart(f3, use_container_width=True)
    # Efficiency + sunburst
    st.markdown('<div class="sec-title">⚡ Efficiency &amp; Sunburst</div>', unsafe_allow_html=True)
    e1,e2 = st.columns(2)
    with e1:
        ed = df.groupby("Sector").agg(CO2=("CO2_Reduction_Tons","sum"),
                                       Inv=("Investment_Amount_USD","sum")).reset_index()
        ed["CO2_per_M"] = ed["CO2"]/(ed["Inv"]/1e6)
        f4 = px.bar(ed.sort_values("CO2_per_M",ascending=False),
                    x="Sector",y="CO2_per_M",
                    color="CO2_per_M",color_continuous_scale="Greens",text_auto=".1f")
        f4.update_traces(textposition="outside",textfont_color=TXT)
        T(f4,"⚡ CO₂ per $1M Invested — Sector Efficiency",340)
        st.plotly_chart(f4, use_container_width=True)
    with e2:
        sn = df.groupby(["Region","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
        f5 = px.sunburst(sn,path=["Region","Sector"],values="CO2_Reduction_Tons",
                         color="CO2_Reduction_Tons",
                         color_continuous_scale=[[0,D_BG2],[0.4,"#0F766E"],[1.0,GRN2]])
        f5.update_traces(textfont=dict(family="Inter,sans-serif",size=11,color="#FFF",weight=500),
                         insidetextorientation="radial", marker=dict(line=dict(color=D_BG,width=2)))
        f5.update_layout(paper_bgcolor=D_BG, font=dict(color=TXT),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                         title=dict(text="☀️ CO₂ Sunburst — Region → Sector",
                                    font=dict(family="Inter,sans-serif",color=TXT,size=14,weight=600),x=0.01,y=0.96),
                         margin=dict(l=8,r=8,t=48,b=8), height=350)
        st.plotly_chart(f5, use_container_width=True)
    # Region CO2 line
    st.markdown('<div class="sec-title">📍 Region CO₂ Trend by Year</div>', unsafe_allow_html=True)
    rc = df.groupby(["Year","Region"])["CO2_Reduction_Tons"].sum().reset_index()
    f6 = px.line(rc,x="Year",y="CO2_Reduction_Tons",color="Region",
                 markers=True,line_shape="spline",color_discrete_sequence=PAL)
    f6.update_traces(line=dict(width=2.5),marker=dict(size=7))
    T(f6,"📍 CO₂ Reduction Trend by Region",320)
    st.plotly_chart(f6, use_container_width=True)
    st.markdown(f"""<div class="insight">
    💡 <b>Carbon Insight:</b> Total CO₂ avoided = <b>{tc/1e6:.2f}M Tonnes</b>.
    At global carbon price ~$65/tonne → carbon credit value ≈ <b>${tc*65/1e9:.2f}B</b>.
    Efficiency: <b>${ef:.0f} USD per tonne CO₂</b>.
    <b>{bs}</b> leads in absolute carbon abatement.
    </div>""", unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P5 — ROI & RETURNS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "roi":
    st.markdown("""<div class="pg-header"><div class="pg-icon">💰</div><div>
    <div class="pg-title">ROI &amp; Returns Analysis</div>
    <div class="pg-sub">Return on investment · Risk-adjusted performance · Portfolio optimization signals</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()
    avg_r=df["ROI_Percentage"].mean()
    med_r=df["ROI_Percentage"].median()
    max_r=df["ROI_Percentage"].max()
    std_r=df["ROI_Percentage"].std()
    shrp=avg_r/max(std_r,0.001)
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4,c5],[
        ("📈",f"{avg_r:.2f}%","Avg ROI"),("📊",f"{med_r:.2f}%","Median ROI"),
        ("🚀",f"{max_r:.2f}%","Peak ROI"),("📉",f"{std_r:.2f}%","Volatility σ"),
        ("⚖️",f"{shrp:.2f}","Sharpe Ratio"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
    # Trend + box
    st.markdown('<div class="sec-title">📈 Yield Curve &amp; Investment Tier Analysis</div>', unsafe_allow_html=True)
    r1,r2 = st.columns([6,4])
    with r1:
        # SUPER CHART: Yield Curve Grid (Faceted Lines by Sector)
        ry = df.groupby(["Year", "Sector"])["ROI_Percentage"].mean().reset_index()
        f = px.line(ry, x="Year", y="ROI_Percentage", color="Sector", facet_col="Sector",
                    facet_col_wrap=3, line_shape="spline", color_discrete_sequence=PAL,
                    markers=True)
        f.update_traces(line=dict(width=3), marker=dict(size=6, line=dict(color=D_BG,width=1)))
        f.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font=dict(color=MUT)))
        f.update_xaxes(showgrid=False, title="")
        f.update_yaxes(showgrid=False, title="")
        T(f,"📈 Sectoral Yield Curves over Time (%)", 400)
        st.plotly_chart(f, use_container_width=True)
    with r2:
        # SUPER CHART: Investment Tier Analysis
        # Bin investments into Small, Medium, Large based on quantiles
        q33 = df['Investment_Amount_USD'].quantile(0.33)
        q66 = df['Investment_Amount_USD'].quantile(0.66)
        
        def tier(x):
            if x <= q33: return "Small"
            elif x <= q66: return "Medium"
            else: return "Large"
            
        df_tier = df.dropna(subset=["ROI_Percentage", "Investment_Amount_USD"]).copy()
        df_tier["Inv_Tier"] = df_tier["Investment_Amount_USD"].apply(tier)
        # Ensure ordering
        df_tier["Inv_Tier"] = pd.Categorical(df_tier["Inv_Tier"], categories=["Small", "Medium", "Large"], ordered=True)
        
        f2 = px.violin(df_tier, x="Inv_Tier", y="ROI_Percentage", color="Inv_Tier",
                       box=True, points="all", color_discrete_sequence=[BLUE, GOLD, GRN],
                       hover_data=["Company_Name", "Sector"])
        f2.update_traces(marker=dict(size=4, opacity=0.5, line=dict(width=0)))
        T(f2,"🎻 Yield Distribution by Project Scale", 400)
        st.plotly_chart(f2, use_container_width=True)
    # Histogram + error bar
    st.markdown('<div class="sec-title">🔍 ROI Deep Dive</div>', unsafe_allow_html=True)
    d1,d2 = st.columns(2)
    with d1:
        f3=px.histogram(df.dropna(subset=["ROI_Percentage"]),x="ROI_Percentage",
                        color="Sector",nbins=50,barmode="overlay",
                        color_discrete_sequence=PAL,opacity=0.75)
        f3.update_layout(bargap=0.04)
        T(f3,"📊 ROI Distribution Histogram — by Sector",340)
        st.plotly_chart(f3, use_container_width=True)
    with d2:
        rr=df.groupby("Risk_Category")["ROI_Percentage"].agg(["mean","std"]).reset_index()
        rr.columns=["Risk","Mean","Std"]
        f4=go.Figure(go.Bar(x=rr["Risk"],y=rr["Mean"],
                            error_y=dict(type="data",array=rr["Std"],visible=True,color=MUT),
                            marker_color=[RISK_C.get(r,"#aaa") for r in rr["Risk"]],
                            text=rr["Mean"].round(2),textposition="outside",
                            textfont=dict(color=TXT)))
        T(f4,"⚠️ Avg ROI ± σ Error Bars — by ESG Risk",340)
        st.plotly_chart(f4, use_container_width=True)
    # Scatter
    st.markdown('<div class="sec-title">💹 Investment vs ROI Portfolio Scatter</div>', unsafe_allow_html=True)
    sc=df.dropna(subset=["Investment_Amount_USD","ROI_Percentage","ESG_Score"])
    sc_s=sc.sample(min(5000,len(sc)))
    f5=px.scatter(sc_s,x="Investment_Amount_USD",y="ROI_Percentage",
                  color="Sector",size="ESG_Score",opacity=0.75,
                  hover_data=["Company_Name","State","Year"],
                  color_discrete_sequence=PAL,size_max=22)
    f5.update_xaxes(type="log",title_text="Investment (USD — log scale)")
    f5.update_traces(marker=dict(line=dict(color=D_BG,width=1)))
    T(f5,"💹 Investment Amount vs ROI  (Bubble = ESG Score  |  Colour = Sector)",450)
    st.plotly_chart(f5, use_container_width=True)
    # Region + Quarter
    st.markdown('<div class="sec-title">📍 ROI by Region &amp; Quarter</div>', unsafe_allow_html=True)
    rr1,rr2 = st.columns(2)
    with rr1:
        reg=df.groupby("Region")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage",ascending=False)
        f6=px.bar(reg,x="Region",y="ROI_Percentage",
                  color="ROI_Percentage",color_continuous_scale="Teal",text_auto=".1f")
        f6.update_traces(textposition="outside",textfont_color=TXT)
        T(f6,"📍 Avg ROI by Region",300)
        st.plotly_chart(f6, use_container_width=True)
    with rr2:
        rq=df.groupby(["Quarter","Sector"])["ROI_Percentage"].mean().reset_index()
        rq["ord"]=rq["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
        rq=rq.sort_values("ord")
        f7=px.line(rq,x="Quarter",y="ROI_Percentage",color="Sector",
                   markers=True,line_shape="spline",color_discrete_sequence=PAL)
        f7.update_traces(line=dict(width=2.2),marker=dict(size=7))
        T(f7,"📅 Avg ROI by Quarter — per Sector",300)
        st.plotly_chart(f7, use_container_width=True)
    # Parallel coords
    st.markdown('<div class="sec-title">🔗 Parallel Coordinates</div>', unsafe_allow_html=True)
    pc=df.dropna(subset=["ESG_Score","ROI_Percentage","CO2_Reduction_Tons","Investment_Amount_USD"])
    pc_s=pc.sample(min(3000,len(pc))).copy()
    pc_s["Risk_n"]=pc_s["Risk_Category"].map({"Low":0,"Medium":1,"High":2})
    f8=px.parallel_coordinates(pc_s,
        dimensions=["ESG_Score","ROI_Percentage","CO2_Reduction_Tons","Investment_M"],
        color="Risk_n",
        color_continuous_scale=[[0,GRN],[0.5,GOLD],[1.0,"#FF5252"]],
        labels={"ESG_Score":"ESG Score","ROI_Percentage":"ROI %",
                "CO2_Reduction_Tons":"CO₂ (T)","Investment_M":"Inv ($M)",
                "Risk_n":"Risk (0=Low)"})
    f8.update_layout(paper_bgcolor=D_BG,plot_bgcolor=D_BG,
                     font=dict(family="Inter,sans-serif",color=TXT,size=11),
                     coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                     title=dict(text="🔗 Parallel Coordinates: ESG · ROI · CO₂ · Investment",
                                font=dict(family="Inter,sans-serif",color=TXT,size=14,weight=600),x=0.01,y=0.96),
                     margin=dict(l=20,r=20,t=60,b=20),height=400)
    st.plotly_chart(f8, use_container_width=True)
# ════════════════════════════════════════════════════════════════════════════════
#  P6 — SECTOR DEEP DIVE
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "sector":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🔍</div><div>
    <div class="pg-title">Sector Deep Dive</div>
    <div class="pg-sub">Granular per-sector analysis — investment, ESG, carbon &amp; returns</div>
    </div></div>""", unsafe_allow_html=True)
    # Sector + State inline pickers
    dp1,dp2 = st.columns(2)
    with dp1:
        avail_sec = sorted(df["Sector"].dropna().unique().tolist())
        chosen = st.selectbox("🏭 Select Sector", avail_sec, key="sd_sector")
    with dp2:
        avail_st = ["All States"] + sorted(df["State"].dropna().unique().tolist())
        chosen_state = st.selectbox("📍 Filter by State", avail_st, key="sd_state")
    sd = df[df["Sector"]==chosen]
    if chosen_state != "All States":
        sd = sd[sd["State"]==chosen_state]
    si2=sd["Investment_Amount_USD"].sum()/1e9
    sc2=sd["CO2_Reduction_Tons"].sum()/1e6
    sr2=sd["ROI_Percentage"].mean()
    se2=sd["ESG_Score"].mean()
    sp2=sd["Project_ID"].nunique()
    dr=sector_df[sector_df["Sector"]==chosen]["Description"].values
    if len(dr): st.info(f"📋 **{chosen}**: {dr[0]}")
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4,c5],[
        ("💵",f"${si2:.2f}B","Investment"),
        ("🌍",f"{sc2:.2f}M T","CO₂ Reduced"),
        ("📈",f"{sr2:.2f}%","Avg ROI"),
        ("🌿",f"{se2:.1f}","Avg ESG Score"),
        ("🏗️",f"{sp2:,}","Projects"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
    # Combo + CO2 area
    st.markdown('<div class="sec-title">📈 Investment, ROI &amp; Carbon Trends</div>', unsafe_allow_html=True)
    s1,s2 = st.columns(2)
    with s1:
        yd=sd.groupby("Year").agg(Investment=("Investment_Amount_USD","sum"),
                                    ROI=("ROI_Percentage","mean")).reset_index()
        fc=make_subplots(specs=[[{"secondary_y":True}]])
        fc.add_trace(go.Bar(x=yd["Year"],y=yd["Investment"],name="Investment",
                            marker_color=GRN,opacity=0.8),secondary_y=False)
        fc.add_trace(go.Scatter(x=yd["Year"],y=yd["ROI"],name="ROI %",
                               mode="lines+markers",line=dict(color=GOLD,width=2.8),
                               marker=dict(size=8,color=GOLD,line=dict(color=D_BG,width=2))),
                     secondary_y=True)
        combo_lay(fc,f"📈 {chosen}: Investment &amp; ROI — Dual Axis",340)
        fc.update_yaxes(gridcolor="rgba(0,0,0,0)",tickfont=dict(color=GOLD),secondary_y=True)
        st.plotly_chart(fc, use_container_width=True)
    with s2:
        cy2=sd.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f2=go.Figure(go.Scatter(x=cy2["Year"],y=cy2["CO2_Reduction_Tons"],
                                mode="lines+markers",
                                line=dict(color=GRN2,width=3),
                                marker=dict(size=8,color=GRN,line=dict(color=D_BG,width=2)),
                                fill="tozeroy",fillcolor="rgba(0,255,179,0.08)"))
        T(f2,f"🌍 {chosen}: CO₂ Reduction Trend (Tonnes)",340)
        st.plotly_chart(f2, use_container_width=True)
    # State + Risk
    st.markdown('<div class="sec-title">🗺️ Geographic &amp; Risk Breakdown</div>', unsafe_allow_html=True)
    g1,g2 = st.columns(2)
    with g1:
        std_=sd.groupby("State")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(12)
        f3=px.bar(std_,y="State",x="Investment_Amount_USD",orientation="h",
                  color="Investment_Amount_USD",color_continuous_scale="Greens",text_auto=".2s")
        f3.update_traces(textposition="outside",textfont_color=TXT)
        T(f3,f"🗺️ {chosen}: Top States by Investment",380)
        st.plotly_chart(f3, use_container_width=True)
    with g2:
        rk=sd["Risk_Category"].value_counts().reset_index()
        rk.columns=["Risk","Count"]
        f4=px.pie(rk,values="Count",names="Risk",hole=0.58,
                  color="Risk",color_discrete_map=RISK_C)
        f4.update_traces(textinfo="label+percent",marker=dict(line=dict(color=D_BG,width=2)))
        T(f4,f"⚠️ {chosen}: ESG Risk Distribution",380)
        st.plotly_chart(f4, use_container_width=True)
    # Parallel + Data Table
    st.markdown('<div class="sec-title">🔗 Sector Performance Benchmarking</div>', unsafe_allow_html=True)
    
    tab_para, tab_data = st.tabs(["🔗 Aggressive Parallel Coordinates", "🧮 Multi-Metric Data Table"])
    
    with tab_para:
        st.markdown(f"<p style='color:{MUT}; font-size:0.9rem; margin-top:-10px; margin-bottom:10px;'>Comparing <b>{chosen}</b> against top and bottom portfolio quartiles to isolate outperformance.</p>", unsafe_allow_html=True)
        # Filter noise: Keep only the chosen sector OR top/bottom 25% of ROI to highlight extremes
        q25 = df["ROI_Percentage"].quantile(0.25)
        q75 = df["ROI_Percentage"].quantile(0.75)
        pc_df = df[(df["Sector"] == chosen) | (df["ROI_Percentage"] >= q75) | (df["ROI_Percentage"] <= q25)].copy()
        
        # We need a numeric color column. Let's color by whether it's the chosen sector or not.
        pc_df["Is_Chosen"] = (pc_df["Sector"] == chosen).astype(int)
        
        f8 = px.parallel_coordinates(
            pc_df,
            dimensions=["ESG_Score","ROI_Percentage","CO2_Reduction_Tons","Investment_Amount_USD"],
            color="Is_Chosen",
            color_continuous_scale=[[0, MUT], [1.0, GRN]], # Muted for others, Green for chosen
            labels={"ESG_Score":"ESG Score","ROI_Percentage":"ROI %",
                    "CO2_Reduction_Tons":"CO₂ (T)","Investment_Amount_USD":"Inv ($)"}
        )
        f8.update_layout(paper_bgcolor=D_BG, plot_bgcolor=D_BG,
                         font=dict(family="Inter,sans-serif",color=TXT,size=11),
                         coloraxis_showscale=False, # Hide the boolean scale
                         title=dict(text=f"🔗 {chosen} vs. Portfolio Extremes",
                                    font=dict(family="Inter,sans-serif",color=TXT,size=14,weight=600),x=0.01,y=0.96),
                         margin=dict(l=40,r=40,t=60,b=20),height=400)
        st.plotly_chart(f8, use_container_width=True)
        
    with tab_data:
        st.markdown(f"<p style='color:{MUT}; font-size:0.9rem; margin-top:-10px; margin-bottom:10px;'>Comprehensive sector-level aggregation for tabular analysis.</p>", unsafe_allow_html=True)
        
        # Multi-metric table
        agg_table = df.groupby("Sector").agg(
            Total_Investment_USD=("Investment_Amount_USD", "sum"),
            Avg_ROI_Pct=("ROI_Percentage", "mean"),
            Avg_ESG_Score=("ESG_Score", "mean"),
            Total_CO2_Tons=("CO2_Reduction_Tons", "sum"),
            Projects=("Project_ID", "nunique")
        ).reset_index()
        
        # Format for display
        display_df = agg_table.copy()
        display_df["Total_Investment_USD"] = display_df["Total_Investment_USD"].apply(lambda x: f"${x/1e9:.2f}B")
        display_df["Avg_ROI_Pct"] = display_df["Avg_ROI_Pct"].apply(lambda x: f"{x:.1f}%")
        display_df["Avg_ESG_Score"] = display_df["Avg_ESG_Score"].apply(lambda x: f"{x:.1f}")
        display_df["Total_CO2_Tons"] = display_df["Total_CO2_Tons"].apply(lambda x: f"{x/1e6:.2f}M")
        
        # Style the dataframe
        st.dataframe(
            display_df.style.highlight_max(subset=["Avg_ROI_Pct", "Avg_ESG_Score"], color="rgba(32, 196, 138, 0.2)"),
            use_container_width=True,
            hide_index=True,
            height=300
        )
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 4px;color:#1E3050;font-size:.73rem;
            border-top:1px solid rgba(32,196,138,.06);margin-top:24px;">
  🌿 HDFC Bank Green Finance &amp; ESG Investment Tracker &nbsp;·&nbsp;
  Streamlit + Plotly &nbsp;·&nbsp; v4.0
</div>""", unsafe_allow_html=True)
