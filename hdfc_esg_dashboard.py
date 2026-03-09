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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{
  --bg:#080E1C;--surf:#0E1829;--surf2:#132035;
  --bord:rgba(32,196,138,0.14);--green:#20C48A;--green2:#00FFB3;
  --gold:#FFC107;--blue:#42A5F5;--red:#FF5252;
  --muted:#6B7FA3;--text:#DDE6F0;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:var(--bg)!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;color:var(--text)!important;
}
[data-testid="block-container"]{padding:1.1rem 1.8rem 2rem!important;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#05101F 0%,#09182E 100%)!important;
  border-right:1px solid var(--bord)!important;
}
[data-testid="stSidebar"] *{color:var(--text)!important;}
[data-testid="stSidebar"] label{color:var(--muted)!important;font-size:.71rem!important;
  text-transform:uppercase;letter-spacing:.9px;}
/* sidebar select/multiselect boxes */
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input{
  background:#0E1829!important;border-color:rgba(32,196,138,.2)!important;
  color:var(--text)!important;}
/* logo */
.logo-wrap{background:linear-gradient(135deg,#B71C1C,#C62828 55%,#7B0000);
  border-radius:14px;padding:16px 18px 12px;margin-bottom:18px;
  border:1px solid rgba(255,255,255,.06);}
.logo-title{font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#fff;margin:0;}
.logo-sub{font-size:.68rem;color:rgba(255,255,255,.48);margin:3px 0 0;}
/* nav buttons */
div[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;border:1px solid rgba(32,196,138,.16)!important;
  color:var(--text)!important;border-radius:9px!important;width:100%!important;
  text-align:left!important;padding:8px 13px!important;font-size:.81rem!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;margin-bottom:3px!important;
  transition:all .16s ease!important;}
div[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(32,196,138,.11)!important;border-color:var(--green)!important;
  color:var(--green)!important;transform:translateX(3px)!important;}
/* KPI cards */
.kpi-card{background:var(--surf);border:1px solid var(--bord);border-radius:13px;
  padding:16px 18px 12px;position:relative;overflow:hidden;
  transition:transform .18s,box-shadow .18s;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--green),transparent);}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 28px rgba(32,196,138,.1);}
.kpi-icon{font-size:1.2rem;margin-bottom:7px;}
.kpi-val{font-family:'Space Grotesk',sans-serif;font-size:1.6rem;font-weight:700;
  color:var(--green);line-height:1;margin:0 0 4px;}
.kpi-label{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;}
.kpi-delta{font-size:.72rem;color:#69F0AE;margin-top:4px;}
/* page header */
.pg-header{background:linear-gradient(135deg,#0C1E38,#091425 60%,#061812);
  border:1px solid var(--bord);border-radius:16px;
  padding:22px 28px 16px;margin-bottom:22px;display:flex;align-items:center;gap:14px;}
.pg-icon{font-size:1.9rem;}
.pg-title{font-family:'Space Grotesk',sans-serif;font-size:1.45rem;font-weight:700;
  color:#fff;margin:0 0 2px;}
.pg-sub{font-size:.79rem;color:var(--muted);margin:0;}
/* section titles */
.sec-title{font-family:'Space Grotesk',sans-serif;font-size:.93rem;font-weight:600;
  color:var(--green);display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--bord);padding-bottom:7px;margin:22px 0 11px;}
/* ribbon */
.ribbon{background:var(--surf2);border:1px solid var(--bord);border-radius:11px;
  padding:11px 16px;display:flex;gap:0;margin-bottom:18px;}
.rib-item{flex:1;text-align:center;border-right:1px solid var(--bord);padding:0 8px;}
.rib-item:last-child{border-right:none;}
.rib-val{font-family:'Space Grotesk',sans-serif;font-weight:700;color:var(--green);font-size:.98rem;}
.rib-lbl{font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-top:2px;}
/* insight */
.insight{background:linear-gradient(135deg,rgba(32,196,138,.06),rgba(32,196,138,.01));
  border:1px solid rgba(32,196,138,.18);border-left:3px solid var(--green);
  border-radius:9px;padding:13px 16px;font-size:.82rem;color:var(--muted);
  margin-top:12px;line-height:1.65;}
.insight b{color:var(--green);}
/* filter section header in sidebar */
.flt-head{font-size:.68rem;color:var(--muted);text-transform:uppercase;
  letter-spacing:.9px;margin-bottom:4px;margin-top:10px;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
</style>
""", unsafe_allow_html=True)

# ── COLOUR / TEMPLATE CONSTANTS ───────────────────────────────────────────────
D_BG  = "#0E1829"
D_BG2 = "#080E1C"
GRN   = "#20C48A"; GRN2 = "#00FFB3"
GOLD  = "#FFC107"; BLUE = "#42A5F5"
MUT   = "#6B7FA3"; TXT  = "#DDE6F0"
GRID  = "rgba(255,255,255,0.05)"; LINE = "rgba(255,255,255,0.07)"
PAL   = [GRN,"#00FFB3","#26D07C","#69F0AE","#00897B",
         "#1DE9B6",GOLD,"#FF7043",BLUE,"#CE93D8"]
RISK_C = {"Low":GRN,"Medium":GOLD,"High":"#FF5252"}

# Base layout dict (plain dict — safe to ** unpack)
BL = dict(
    paper_bgcolor=D_BG, plot_bgcolor=D_BG,
    font=dict(family="Plus Jakarta Sans,sans-serif", color=TXT, size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUT, size=11)),
    xaxis=dict(gridcolor=GRID, linecolor=LINE,
               tickfont=dict(color=MUT, size=11), title_font=dict(color=MUT)),
    yaxis=dict(gridcolor=GRID, linecolor=LINE,
               tickfont=dict(color=MUT, size=11), title_font=dict(color=MUT)),
    margin=dict(l=12,r=12,t=48,b=12),
    coloraxis_colorbar=dict(tickfont=dict(color=MUT), title_font=dict(color=MUT)),
)

def T(fig, title="", h=None):
    kw = dict(**BL)
    kw["title"] = dict(text=title,
                       font=dict(family="Space Grotesk,sans-serif", color=TXT, size=13),
                       x=0.02, xanchor="left")
    if h: kw["height"] = h
    fig.update_layout(**kw)
    return fig

def combo_lay(fig, title, h=340):
    """Layout for make_subplots dual-axis (avoids xaxis/yaxis key conflicts)."""
    fig.update_layout(
        paper_bgcolor=D_BG, plot_bgcolor=D_BG,
        font=dict(family="Plus Jakarta Sans,sans-serif", color=TXT, size=11),
        title=dict(text=title,
                   font=dict(family="Space Grotesk,sans-serif", color=TXT, size=13),
                   x=0.02),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUT, size=11)),
        xaxis=dict(gridcolor=GRID, linecolor=LINE, tickfont=dict(color=MUT)),
        yaxis=dict(gridcolor=GRID, linecolor=LINE, tickfont=dict(color=MUT)),
        margin=dict(l=12,r=12,t=48,b=12), height=h,
    )

def hmap_lay(fig, title, h=340):
    """Layout for go.Heatmap figures."""
    fig.update_layout(
        paper_bgcolor=D_BG, plot_bgcolor=D_BG,
        font=dict(family="Plus Jakarta Sans,sans-serif", color=TXT, size=11),
        title=dict(text=title,
                   font=dict(family="Space Grotesk,sans-serif", color=TXT, size=13),
                   x=0.02),
        xaxis=dict(tickfont=dict(color=MUT)),
        yaxis=dict(tickfont=dict(color=MUT)),
        margin=dict(l=12,r=12,t=48,b=12), height=h,
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
    st.markdown('<div class="sec-title">📊 Investment Trends &amp; Sector Mix</div>', unsafe_allow_html=True)
    a1,a2 = st.columns([3,2])
    with a1:
        tr = df.groupby(["Year","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f = px.area(tr, x="Year", y="Investment_Amount_USD", color="Sector",
                    color_discrete_sequence=PAL, line_shape="spline")
        f.update_traces(line=dict(width=1.8))
        T(f,"📈 Annual Green Investment by Sector — Stacked Area",340)
        st.plotly_chart(f, use_container_width=True)
    with a2:
        pd_ = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
        f2 = px.pie(pd_, values="Investment_Amount_USD", names="Sector",
                    color_discrete_sequence=PAL, hole=0.58)
        f2.update_traces(textinfo="label+percent", textfont_size=10,
                         marker=dict(line=dict(color=D_BG,width=2)))
        T(f2,"🥧 Portfolio Sector Allocation",340)
        st.plotly_chart(f2, use_container_width=True)

    # 3-col snapshot
    st.markdown('<div class="sec-title">🌿 Risk · Carbon · ROI Snapshot</div>', unsafe_allow_html=True)
    b1,b2,b3 = st.columns(3)
    with b1:
        er = df.groupby("Risk_Category")["Investment_Amount_USD"].sum().reset_index()
        er["ord"]=er["Risk_Category"].map({"Low":0,"Medium":1,"High":2})
        er = er.sort_values("ord")
        f3 = px.bar(er, x="Risk_Category", y="Investment_Amount_USD",
                    color="Risk_Category", text_auto=".2s", color_discrete_map=RISK_C)
        f3.update_traces(textposition="outside",textfont_color=TXT)
        T(f3,"⚠️ Investment by ESG Risk Tier",300)
        st.plotly_chart(f3, use_container_width=True)
    with b2:
        cy = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f4 = px.bar(cy, x="Year", y="CO2_Reduction_Tons",
                    color="CO2_Reduction_Tons", color_continuous_scale="Greens",
                    text_auto=".2s")
        f4.update_traces(textposition="outside",textfont_color=TXT)
        T(f4,"🌍 CO₂ Reduced Per Year (Tonnes)",300)
        st.plotly_chart(f4, use_container_width=True)
    with b3:
        rs = df.groupby("Sector")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage")
        f5 = px.bar(rs, x="ROI_Percentage", y="Sector", orientation="h",
                    color="ROI_Percentage", color_continuous_scale="Teal", text_auto=".1f")
        f5.update_traces(textposition="outside",textfont_color=TXT)
        T(f5,"💰 Avg ROI by Sector (%)",300)
        st.plotly_chart(f5, use_container_width=True)

    # YoY + Quarter
    st.markdown('<div class="sec-title">📆 Seasonality &amp; YoY Growth</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([2,3])
    with g1:
        qd = df.groupby("Quarter")["Investment_Amount_USD"].sum().reset_index()
        qd["ord"]=qd["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
        qd = qd.sort_values("ord")
        f6 = px.pie(qd, values="Investment_Amount_USD", names="Quarter",
                    color_discrete_sequence=[GRN,GRN2,GOLD,BLUE], hole=0.52)
        f6.update_traces(textinfo="label+percent")
        T(f6,"📅 Investment by Quarter",300)
        st.plotly_chart(f6, use_container_width=True)
    with g2:
        yy = df.groupby("Year")["Investment_Amount_USD"].sum().reset_index()
        yy["YoY"] = yy["Investment_Amount_USD"].pct_change()*100
        f7 = make_subplots(specs=[[{"secondary_y":True}]])
        f7.add_trace(go.Bar(x=yy["Year"],y=yy["Investment_Amount_USD"],
                            name="Investment",marker_color=GRN,opacity=0.78),
                     secondary_y=False)
        f7.add_trace(go.Scatter(x=yy["Year"],y=yy["YoY"],name="YoY Growth %",
                                mode="lines+markers",line=dict(color=GOLD,width=2.5),
                                marker=dict(size=7,color=GOLD,line=dict(color=D_BG,width=2))),
                     secondary_y=True)
        combo_lay(f7,"📊 Investment Volume &amp; YoY Growth (%)",300)
        f7.update_yaxes(gridcolor="rgba(0,0,0,0)",tickfont=dict(color=GOLD),secondary_y=True)
        st.plotly_chart(f7, use_container_width=True)

    st.markdown(f"""<div class="insight">
    💡 <b>Executive Summary:</b> HDFC's green portfolio spans <b>{df['Sector'].nunique()} sectors</b>
    across <b>{nst} states</b>, deploying <b>${inv:.2f}B</b>.  Total CO₂ avoided:
    <b>{co2:.2f}M tonnes</b> (≈ <b>{co2/4.6:.1f}M cars</b> off road).
    <b>{bsec}</b> leads investment; <b>{brs}</b> delivers the highest ROI.
    <b>{lrp}%</b> of projects are in the Low ESG Risk tier.
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

    st.markdown('<div class="sec-title">📊 ESG Score Distribution &amp; Risk Profile</div>', unsafe_allow_html=True)
    h1,h2 = st.columns([3,2])
    with h1:
        f = px.histogram(df.dropna(subset=["ESG_Score"]), x="ESG_Score",
                         color="Risk_Category", nbins=45, barmode="overlay",
                         color_discrete_map=RISK_C, opacity=0.8)
        f.update_layout(bargap=0.04)
        T(f,"📊 ESG Score Distribution — coloured by Risk Category",320)
        st.plotly_chart(f, use_container_width=True)
    with h2:
        rc = df["Risk_Category"].value_counts().reset_index()
        rc.columns = ["Risk","Count"]
        f2 = px.pie(rc, values="Count", names="Risk", hole=0.62,
                    color="Risk", color_discrete_map=RISK_C)
        f2.update_traces(textinfo="label+percent",
                         marker=dict(line=dict(color=D_BG,width=2)))
        T(f2,"🥧 Risk Category Distribution",320)
        st.plotly_chart(f2, use_container_width=True)

    # Bubble scatter
    st.markdown('<div class="sec-title">🔬 ESG Score vs ROI — Bubble Analysis</div>', unsafe_allow_html=True)
    bub = (df.dropna(subset=["ESG_Score","ROI_Percentage"])
           .groupby("Company_Name")
           .agg(ESG=("ESG_Score","first"), ROI=("ROI_Percentage","mean"),
                Inv=("Investment_Amount_USD","sum"),
                Risk=("Risk_Category","first"), Sector=("Sector","first"))
           .reset_index())
    f3 = px.scatter(bub, x="ESG", y="ROI", size="Inv", color="Risk",
                    hover_name="Company_Name",
                    hover_data={"Sector":True,"Inv":":.2s"},
                    color_discrete_map=RISK_C, size_max=26, opacity=0.72)
    f3.add_vline(x=bub["ESG"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ESG {bub['ESG'].mean():.1f}",
                 annotation_font_color=MUT)
    f3.add_hline(y=bub["ROI"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ROI {bub['ROI'].mean():.1f}%",
                 annotation_position="top right", annotation_font_color=MUT)
    T(f3,"🔬 ESG Score vs Avg ROI  (Bubble = Investment  |  Colour = Risk)",400)
    st.plotly_chart(f3, use_container_width=True)

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
        color_continuous_scale=[[0,"#0A1623"],[0.25,"#003D2A"],[0.6,GRN],[1.0,GRN2]],
    )
    # ✅ FIXED: NO custom_data, NO hovertemplate in update_traces (caused TypeError)
    f6.update_traces(
        textinfo="label+percent root",
        textfont=dict(family="Space Grotesk,sans-serif", size=11, color="#FFFFFF"),
        marker=dict(line=dict(color=D_BG2, width=1.5)),
    )
    f6.update_layout(
        paper_bgcolor=D_BG2,
        margin=dict(l=6,r=6,t=8,b=8), height=520,
        font=dict(color=TXT, family="Plus Jakarta Sans,sans-serif"),
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
                     texttemplate="%{text:.1f}")
    T(f7,"🏆 Top 15 Companies by ESG Score",360)
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
                color_continuous_scale=[[0,"#07111F"],[0.2,"#003D2A"],
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
                paper_bgcolor=D_BG2,
                geo_bgcolor=D_BG2,
                font=dict(family="Plus Jakarta Sans,sans-serif", color=TXT, size=11),
                title=dict(
                    text="🗺️ Green Investment Filled Map — India States",
                    font=dict(family="Space Grotesk,sans-serif",color=TXT,size=13),
                    x=0.02),
                coloraxis_colorbar=dict(
                    title="Investment (USD)",
                    tickfont=dict(color=MUT),
                    title_font=dict(color=MUT),
                    bgcolor=D_BG,
                    bordercolor="rgba(0,0,0,0)",
                ),
                margin=dict(l=0,r=0,t=50,b=0), height=540,
            )
            fc.update_traces(marker_line_color="rgba(0,255,180,0.25)",
                             marker_line_width=1.2)
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
            showcountries=True,  countrycolor="rgba(130,180,255,0.2)",
            showcoastlines=True, coastlinecolor="rgba(130,180,255,0.2)",
            showland=True,       landcolor="#0D2137",
            showocean=True,      oceancolor="#071525",
            showsubunits=True,   subunitcolor="rgba(100,160,255,0.12)",
            showframe=False,     bgcolor=D_BG2,
            center=dict(lat=22,lon=80),
            lataxis_range=[6,38], lonaxis_range=[65,100],
        )
        fm.update_layout(
            paper_bgcolor=D_BG2, geo_bgcolor=D_BG2,
            font=dict(family="Plus Jakarta Sans,sans-serif",color=TXT,size=11),
            title=dict(
                text="🔵 Green Investment Bubble Map (Bubble = Investment  |  Colour = Region)",
                font=dict(family="Space Grotesk,sans-serif",color=TXT,size=13),x=0.02),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=MUT,size=11)),
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

    # Region grouped + Funnel
    st.markdown('<div class="sec-title">📍 Regional Investment Breakdown</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([3,2])
    with g1:
        ri = df.groupby(["Region","Year"])["Investment_Amount_USD"].sum().reset_index()
        f = px.bar(ri, x="Year", y="Investment_Amount_USD", color="Region",
                   barmode="group", color_discrete_sequence=PAL, text_auto=".2s")
        f.update_traces(textposition="outside",textfont_color=TXT)
        T(f,"📍 Regional Investment by Year",330)
        st.plotly_chart(f, use_container_width=True)
    with g2:
        rt = df.groupby("Region")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False)
        f2 = px.funnel(rt, x="Investment_Amount_USD", y="Region",
                       color_discrete_sequence=PAL)
        T(f2,"🏆 Region Investment Funnel",330)
        st.plotly_chart(f2, use_container_width=True)

    # Top 20 states bar
    st.markdown('<div class="sec-title">🗺️ Top 15 States by Green Investment</div>', unsafe_allow_html=True)
    si = df.groupby("State")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(15)
    f3 = px.bar(si, y="State", x="Investment_Amount_USD", orientation="h",
                color="Investment_Amount_USD", color_continuous_scale="Greens", text_auto=".2s")
    f3.update_traces(textposition="outside",textfont_color=TXT)
    T(f3,"🗺️ Top 15 States — Total Green Investment (USD)",380)
    st.plotly_chart(f3, use_container_width=True)

    # Heatmaps
    st.markdown('<div class="sec-title">🔥 Investment Heatmaps</div>', unsafe_allow_html=True)
    hm1,hm2 = st.columns(2)
    with hm1:
        hp_df = df.groupby(["Sector","Region"])["Investment_Amount_USD"].sum().reset_index()
        pv = hp_df.pivot(index="Sector",columns="Region",values="Investment_Amount_USD").fillna(0)
        fh1 = go.Figure(go.Heatmap(
            z=pv.values, x=pv.columns.tolist(), y=pv.index.tolist(),
            colorscale=[[0,D_BG],[0.4,"#00563F"],[1.0,GRN2]],
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
            colorscale=[[0,D_BG],[0.4,"#00563F"],[1.0,GRN2]],
            texttemplate="%{z:.2s}", hoverongaps=False,
            colorbar=dict(tickfont=dict(color=MUT)),
        ))
        hmap_lay(fh2,"📆 Monthly Heatmap (Year × Month)",340)
        fh2.update_xaxes(tickangle=38, tickfont=dict(color=MUT,size=9))
        st.plotly_chart(fh2, use_container_width=True)

    # City + Sunburst
    st.markdown('<div class="sec-title">🏙️ City Analysis &amp; Sunburst</div>', unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        ci = df.groupby("City")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(15)
        f5 = px.bar(ci, y="City", x="Investment_Amount_USD", orientation="h",
                    color="Investment_Amount_USD", color_continuous_scale="Greens",
                    text_auto=".2s")
        f5.update_traces(textposition="outside",textfont_color=TXT)
        T(f5,"🏙️ Top 15 Cities by Investment",400)
        st.plotly_chart(f5, use_container_width=True)
    with cb:
        sn = df.groupby(["Region","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f6 = px.sunburst(sn, path=["Region","Sector"], values="Investment_Amount_USD",
                         color="Investment_Amount_USD",
                         color_continuous_scale=[[0,D_BG],[0.3,"#00563F"],[1.0,GRN2]])
        f6.update_traces(textfont=dict(family="Space Grotesk,sans-serif",size=11,color="#FFF"),
                         insidetextorientation="radial")
        f6.update_layout(paper_bgcolor=D_BG,
                         font=dict(color=TXT,family="Plus Jakarta Sans,sans-serif"),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                         title=dict(text="☀️ Investment Sunburst: Region → Sector",
                                    font=dict(family="Space Grotesk,sans-serif",
                                              color=TXT,size=13),x=0.02),
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
    st.markdown('<div class="sec-title">📈 Carbon Reduction Trends</div>', unsafe_allow_html=True)
    t1,t2 = st.columns(2)
    with t1:
        cy = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f = go.Figure(go.Scatter(x=cy["Year"],y=cy["CO2_Reduction_Tons"],
                                 mode="lines+markers",
                                 line=dict(color=GRN,width=3),
                                 marker=dict(size=8,color=GRN2,line=dict(color=D_BG,width=2)),
                                 fill="tozeroy",fillcolor="rgba(32,196,138,0.10)"))
        T(f,"📈 Annual CO₂ Reduction Trend",320)
        st.plotly_chart(f, use_container_width=True)
    with t2:
        cs = df.groupby("Sector")["CO2_Reduction_Tons"].sum().reset_index().sort_values("CO2_Reduction_Tons")
        f2 = px.bar(cs, x="CO2_Reduction_Tons", y="Sector", orientation="h",
                    color="CO2_Reduction_Tons", color_continuous_scale="Greens", text_auto=".2s")
        f2.update_traces(textposition="outside",textfont_color=TXT)
        T(f2,"🌱 CO₂ Reduced by Sector (Total)",320)
        st.plotly_chart(f2, use_container_width=True)

    # Heatmap
    st.markdown('<div class="sec-title">🔥 Carbon Heatmap — Sector × Year</div>', unsafe_allow_html=True)
    cp = df.groupby(["Year","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    pv = cp.pivot(index="Sector",columns="Year",values="CO2_Reduction_Tons").fillna(0)
    f3 = go.Figure(go.Heatmap(
        z=pv.values, x=pv.columns.astype(str).tolist(), y=pv.index.tolist(),
        colorscale=[[0,D_BG],[0.3,"#004D40"],[0.7,GRN],[1.0,GRN2]],
        text=pv.values, texttemplate="%{text:.2s}", hoverongaps=False,
        colorbar=dict(tickfont=dict(color=MUT)),
    ))
    hmap_lay(f3,"🔥 CO₂ Reduction Heatmap — Sector × Year",340)
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
                         color_continuous_scale=[[0,D_BG],[0.4,"#004D40"],[1.0,GRN2]])
        f5.update_traces(textfont=dict(family="Space Grotesk,sans-serif",size=11,color="#FFF"),
                         insidetextorientation="radial")
        f5.update_layout(paper_bgcolor=D_BG, font=dict(color=TXT),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                         title=dict(text="☀️ CO₂ Sunburst — Region → Sector",
                                    font=dict(family="Space Grotesk,sans-serif",color=TXT,size=13),x=0.02),
                         margin=dict(l=8,r=8,t=48,b=8), height=340)
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
    st.markdown('<div class="sec-title">📈 ROI Trends &amp; Distribution</div>', unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        ry=df.groupby("Year")["ROI_Percentage"].mean().reset_index()
        f=go.Figure(go.Scatter(x=ry["Year"],y=ry["ROI_Percentage"],
                               mode="lines+markers",
                               line=dict(color=GOLD,width=3),
                               marker=dict(size=8,color=GOLD,line=dict(color=D_BG,width=2)),
                               fill="tozeroy",fillcolor="rgba(255,193,7,0.08)"))
        T(f,"📈 Average ROI Trend by Year",320)
        st.plotly_chart(f, use_container_width=True)
    with r2:
        f2=px.box(df.dropna(subset=["ROI_Percentage","Sector"]),
                  x="Sector",y="ROI_Percentage",
                  color="Sector",color_discrete_sequence=PAL,points=False)
        T(f2,"📦 ROI Distribution per Sector — Box Plot",320)
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
                  color="Sector",size="ESG_Score",opacity=0.6,
                  hover_data=["Company_Name","State","Year"],
                  color_discrete_sequence=PAL,size_max=18)
    f5.update_xaxes(type="log",title_text="Investment (USD — log scale)")
    T(f5,"💹 Investment Amount vs ROI  (Bubble = ESG Score  |  Colour = Sector)",420)
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
                     font=dict(family="Plus Jakarta Sans,sans-serif",color=TXT,size=11),
                     coloraxis_colorbar=dict(tickfont=dict(color=MUT)),
                     title=dict(text="🔗 Parallel Coordinates: ESG · ROI · CO₂ · Investment",
                                font=dict(family="Space Grotesk,sans-serif",color=TXT,size=13),x=0.02),
                     margin=dict(l=12,r=12,t=48,b=12),height=380)
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

    # Radar
    st.markdown('<div class="sec-title">🕸️ All-Sector Comparison Radar</div>', unsafe_allow_html=True)
    rad=df.groupby("Sector").agg(ROI=("ROI_Percentage","mean"),ESG=("ESG_Score","mean"),
                                  CO2=("CO2_Reduction_Tons","mean"),Inv=("Investment_Amount_USD","mean")).reset_index()
    for c_ in ["ROI","ESG","CO2","Inv"]:
        mn,mx=rad[c_].min(),rad[c_].max()
        rad[c_+"_n"]=((rad[c_]-mn)/(mx-mn+1e-9))*100
    f5=go.Figure()
    cats=["ROI","ESG Score","CO₂ Impact","Investment","ROI"]
    for i,row in rad.iterrows():
        is_sel=row["Sector"]==chosen
        c_r=GRN if is_sel else PAL[i%len(PAL)]
        f5.add_trace(go.Scatterpolar(
            r=[row["ROI_n"],row["ESG_n"],row["CO2_n"],row["Inv_n"],row["ROI_n"]],
            theta=cats,name=row["Sector"],mode="lines+markers",
            line=dict(color=c_r,width=3 if is_sel else 1.5),
            marker=dict(size=7 if is_sel else 4,color=c_r),
            opacity=1.0 if is_sel else 0.50,
        ))
    f5.update_layout(
        polar=dict(bgcolor=D_BG2,
                   radialaxis=dict(visible=True,gridcolor=GRID,
                                   tickfont=dict(color=MUT,size=9),color=MUT,range=[0,110]),
                   angularaxis=dict(gridcolor=GRID,tickfont=dict(color=TXT,size=11),color=MUT)),
        paper_bgcolor=D_BG,font=dict(color=TXT,family="Plus Jakarta Sans,sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=MUT,size=11)),
        title=dict(text=f"🕸️ Sector Radar — highlighted: {chosen}",
                   font=dict(family="Space Grotesk,sans-serif",color=TXT,size=13),x=0.02),
        margin=dict(l=30,r=30,t=50,b=30),height=460,
    )
    st.plotly_chart(f5, use_container_width=True)

    # Waterfall
    st.markdown('<div class="sec-title">🌊 Investment Waterfall — Year-over-Year</div>', unsafe_allow_html=True)
    wf=sd.groupby("Year")["Investment_Amount_USD"].sum().reset_index().sort_values("Year")
    wf["delta"]=wf["Investment_Amount_USD"].diff().fillna(wf["Investment_Amount_USD"])
    f6=go.Figure(go.Waterfall(
        x=wf["Year"].astype(str).tolist(),y=wf["delta"].tolist(),
        measure=["absolute"]+["relative"]*(len(wf)-1),
        connector=dict(line=dict(color=MUT,width=1.5)),
        increasing=dict(marker=dict(color=GRN,line=dict(color=GRN2,width=1))),
        decreasing=dict(marker=dict(color="#FF5252",line=dict(color="#FF8A80",width=1))),
        totals=dict(marker=dict(color=GOLD,line=dict(color="#FFE082",width=1))),
        textposition="outside",textfont=dict(color=TXT,size=11),
        text=[f"${v/1e6:.1f}M" for v in wf["delta"]],
    ))
    T(f6,f"🌊 {chosen}: Investment Waterfall — YoY Change",360)
    st.plotly_chart(f6, use_container_width=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 4px;color:#1E3050;font-size:.73rem;
            border-top:1px solid rgba(32,196,138,.06);margin-top:24px;">
  🌿 HDFC Bank Green Finance &amp; ESG Investment Tracker &nbsp;·&nbsp;
  Streamlit + Plotly &nbsp;·&nbsp; v4.0
</div>""", unsafe_allow_html=True)
