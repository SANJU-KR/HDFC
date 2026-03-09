"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  HDFC Bank: Green Finance & ESG Investment Tracker  v5.0                     ║
║  RUN:  pip install streamlit plotly pandas numpy requests                     ║
║        streamlit run hdfc_esg_dashboard.py                                    ║
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
    page_title="HDFC Bank · Green Finance & ESG Tracker",
    page_icon="🏦", layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  HDFC BRAND COLOUR SYSTEM
#  Primary   : HDFC Red       #D32F2F / #B71C1C
#  Background: Navy-Black     #06090F / #0A0F1E
#  Surface   : Dark Navy      #0D1526 / #111D35
#  Accent    : Warm Gold      #C8953A / #E6AB50
#  Text      : Soft White     #EDF2FA / #B8C7E0
# ══════════════════════════════════════════════════════════════════════════════
HDFC_RED   = "#D32F2F"
HDFC_RED2  = "#B71C1C"
HDFC_RED_L = "#EF5350"          # lighter red for hover
GOLD       = "#C8953A"
GOLD2      = "#E6AB50"
GOLD_L     = "#FFD180"
NAVY       = "#06090F"
NAVY2      = "#0A0F1E"
SURF       = "#0D1526"
SURF2      = "#111D35"
SURF3      = "#162040"
BLUE_A     = "#1565C0"
BLUE_L     = "#42A5F5"
TEAL       = "#00796B"
TEAL_L     = "#26A69A"
TXT        = "#EDF2FA"
TXT2       = "#B8C7E0"
MUT        = "#5A7194"
GRID       = "rgba(255,255,255,0.04)"
LINE_C     = "rgba(255,255,255,0.07)"
BORD       = "rgba(210,47,47,0.18)"  # red-tinted borders
BORD_G     = "rgba(200,149,58,0.18)" # gold-tinted borders

# Chart palette — HDFC brand-aligned
PAL = [HDFC_RED, GOLD, BLUE_L, TEAL_L, "#7E57C2",
       "#EF6C00", "#00ACC1", "#8BC34A", "#EC407A", "#78909C"]

RISK_C = {"Low": "#2E7D32", "Medium": GOLD, "High": HDFC_RED}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Open+Sans:wght@300;400;500;600&display=swap');

/* ── Root tokens ── */
:root{{
  --red:{HDFC_RED};--red2:{HDFC_RED2};--redl:{HDFC_RED_L};
  --gold:{GOLD};--gold2:{GOLD2};
  --navy:{NAVY};--navy2:{NAVY2};
  --surf:{SURF};--surf2:{SURF2};--surf3:{SURF3};
  --bord:{BORD};--bord-g:{BORD_G};
  --txt:{TXT};--txt2:{TXT2};--muted:{MUT};
}}

/* ── Base ── */
html,body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]{{
  background:var(--navy)!important;
  font-family:'Open Sans',sans-serif!important;
  color:var(--txt)!important;
}}
[data-testid="block-container"]{{padding:0.8rem 1.6rem 2rem!important;}}

/* ── Sidebar ── */
[data-testid="stSidebar"]{{
  background:linear-gradient(180deg, #08060E 0%, {NAVY2} 40%, #0B1020 100%)!important;
  border-right:1px solid rgba(210,47,47,0.25)!important;
}}
[data-testid="stSidebar"] *{{color:var(--txt)!important;}}
[data-testid="stSidebar"] label{{
  color:var(--muted)!important;font-size:.69rem!important;
  text-transform:uppercase;letter-spacing:1px;font-family:'Montserrat',sans-serif!important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] div{{
  background:{SURF}!important;border-color:rgba(210,47,47,.2)!important;color:var(--txt)!important;
}}

/* ── HDFC Logo block ── */
.hdfc-logo{{
  background:linear-gradient(135deg,{HDFC_RED2} 0%,{HDFC_RED} 55%,#8B0000 100%);
  border-radius:12px;padding:16px 18px 14px;margin-bottom:20px;
  border:1px solid rgba(255,255,255,.08);position:relative;overflow:hidden;
}}
.hdfc-logo::after{{
  content:'';position:absolute;right:-20px;top:-20px;
  width:80px;height:80px;border-radius:50%;
  background:rgba(255,255,255,.04);
}}
.hdfc-logo-title{{
  font-family:'Montserrat',sans-serif;font-size:1.1rem;
  font-weight:800;color:#fff;margin:0;letter-spacing:.5px;
}}
.hdfc-logo-badge{{
  display:inline-block;background:rgba(255,255,255,.15);
  border-radius:4px;padding:2px 8px;font-size:.62rem;
  color:rgba(255,255,255,.9);letter-spacing:1px;margin-top:6px;
  font-family:'Montserrat',sans-serif;font-weight:600;text-transform:uppercase;
}}
.hdfc-logo-sub{{font-size:.7rem;color:rgba(255,255,255,.55);margin:8px 0 0;font-style:italic;}}

/* ── Nav buttons ── */
div[data-testid="stSidebar"] .stButton>button{{
  background:transparent!important;
  border:1px solid rgba(210,47,47,.2)!important;
  color:var(--txt2)!important;border-radius:8px!important;
  width:100%!important;text-align:left!important;
  padding:9px 13px!important;font-size:.8rem!important;
  font-family:'Open Sans',sans-serif!important;
  margin-bottom:3px!important;transition:all .15s ease!important;
  letter-spacing:.2px;
}}
div[data-testid="stSidebar"] .stButton>button:hover{{
  background:rgba(210,47,47,.12)!important;
  border-color:var(--red)!important;
  color:#fff!important;
  transform:translateX(4px)!important;
}}

/* ── Filter section heads ── */
.flt-head{{
  font-size:.67rem;color:var(--muted);text-transform:uppercase;
  letter-spacing:1px;margin-bottom:4px;margin-top:12px;
  font-family:'Montserrat',sans-serif;font-weight:600;
}}

/* ── Page header ── */
.pg-header{{
  background:linear-gradient(135deg, #0D1828 0%, #101520 50%, #0D0810 100%);
  border:1px solid rgba(210,47,47,.22);
  border-left:4px solid var(--red);
  border-radius:0 12px 12px 0;
  padding:20px 28px 16px;margin-bottom:20px;
  display:flex;align-items:center;gap:14px;
  position:relative;overflow:hidden;
}}
.pg-header::before{{
  content:'';position:absolute;right:0;top:0;bottom:0;width:200px;
  background:linear-gradient(90deg,transparent,rgba(210,47,47,.04));
}}
.pg-icon{{font-size:1.8rem;}}
.pg-title{{
  font-family:'Montserrat',sans-serif;font-size:1.4rem;
  font-weight:800;color:#fff;margin:0 0 2px;letter-spacing:.3px;
}}
.pg-sub{{font-size:.78rem;color:var(--muted);margin:0;}}

/* ── KPI Cards ── */
.kpi-card{{
  background:linear-gradient(145deg,{SURF} 0%,{SURF2} 100%);
  border:1px solid rgba(210,47,47,.16);
  border-radius:10px;padding:16px 18px 13px;
  position:relative;overflow:hidden;
  transition:transform .18s,box-shadow .18s;
}}
.kpi-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2.5px;
  background:linear-gradient(90deg,var(--red),var(--gold),transparent);
}}
.kpi-card::after{{
  content:'';position:absolute;bottom:0;right:0;
  width:60px;height:60px;border-radius:50%;
  background:rgba(210,47,47,.04);transform:translate(20px,20px);
}}
.kpi-card:hover{{
  transform:translateY(-3px);
  box-shadow:0 8px 30px rgba(210,47,47,.15);
  border-color:rgba(210,47,47,.35);
}}
.kpi-icon{{font-size:1.2rem;margin-bottom:8px;}}
.kpi-val{{
  font-family:'Montserrat',sans-serif;font-size:1.6rem;
  font-weight:800;color:{GOLD2};line-height:1;margin:0 0 5px;
}}
.kpi-label{{
  font-size:.67rem;color:var(--muted);text-transform:uppercase;
  letter-spacing:1.1px;font-family:'Montserrat',sans-serif;font-weight:600;
}}
.kpi-delta{{font-size:.71rem;color:#81C784;margin-top:4px;}}

/* ── Section titles ── */
.sec-title{{
  font-family:'Montserrat',sans-serif;font-size:.88rem;
  font-weight:700;color:{GOLD2};
  display:flex;align-items:center;gap:8px;
  border-bottom:1px solid rgba(200,149,58,.2);
  padding-bottom:8px;margin:22px 0 12px;
  text-transform:uppercase;letter-spacing:.8px;
}}

/* ── Ribbon ── */
.ribbon{{
  background:linear-gradient(135deg,{SURF} 0%,{SURF2} 100%);
  border:1px solid var(--bord);border-radius:10px;
  padding:12px 16px;display:flex;gap:0;margin-bottom:18px;
}}
.rib-item{{
  flex:1;text-align:center;
  border-right:1px solid rgba(210,47,47,.12);padding:0 10px;
}}
.rib-item:last-child{{border-right:none;}}
.rib-val{{
  font-family:'Montserrat',sans-serif;font-weight:700;
  color:{GOLD2};font-size:.95rem;
}}
.rib-lbl{{
  font-size:.63rem;color:var(--muted);text-transform:uppercase;
  letter-spacing:.9px;margin-top:3px;font-family:'Montserrat',sans-serif;
}}

/* ── Insight box ── */
.insight{{
  background:linear-gradient(135deg,rgba(210,47,47,.06),rgba(200,149,58,.04));
  border:1px solid rgba(210,47,47,.2);
  border-left:3px solid var(--red);
  border-radius:8px;padding:14px 18px;
  font-size:.82rem;color:var(--txt2);
  margin-top:14px;line-height:1.7;
}}
.insight b{{color:{GOLD2};}}
.insight .tag{{
  display:inline-block;background:rgba(210,47,47,.12);
  border:1px solid rgba(210,47,47,.25);border-radius:4px;
  padding:1px 8px;font-size:.68rem;color:{HDFC_RED_L};
  margin-right:5px;font-family:'Montserrat',sans-serif;font-weight:600;
}}

/* ── Filter badges ── */
.fbadge{{
  display:inline-flex;align-items:center;gap:5px;
  background:rgba(210,47,47,.1);
  border:1px solid rgba(210,47,47,.28);border-radius:5px;
  padding:3px 10px;font-size:.7rem;color:{HDFC_RED_L};
  margin-right:6px;margin-bottom:10px;font-family:'Montserrat',sans-serif;font-weight:600;
}}

/* ── Tabs styling ── */
[data-testid="stTabs"] [data-baseweb="tab"]{{
  background:transparent!important;color:var(--muted)!important;
  border:none!important;font-family:'Montserrat',sans-serif!important;
  font-size:.78rem!important;font-weight:600!important;letter-spacing:.5px;
}}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]{{
  color:{GOLD2}!important;border-bottom:2px solid {GOLD2}!important;
}}
[data-testid="stTabs"] [data-baseweb="tab-list"]{{
  background:{SURF}!important;border-radius:8px!important;
  border:1px solid var(--bord)!important;padding:4px!important;
}}

/* ── Divider ── */
hr{{border-color:rgba(210,47,47,.15)!important;}}

/* ── Info boxes ── */
[data-testid="stInfo"]{{
  background:rgba(21,101,192,.1)!important;
  border-left:3px solid {BLUE_L}!important;border-radius:6px!important;
  color:var(--txt2)!important;font-size:.82rem!important;
}}

/* ── Selectbox / slider ── */
[data-testid="stSelectbox"]>div,
[data-testid="stDateInput"]>div{{border-radius:7px!important;}}

/* ── Hide clutter ── */
#MainMenu,footer,header{{visibility:hidden;}}
[data-testid="stDecoration"]{{display:none;}}
</style>
""", unsafe_allow_html=True)

# ── CHART LAYOUT BASE ─────────────────────────────────────────────────────────
BL = dict(
    paper_bgcolor = SURF,
    plot_bgcolor  = SURF,
    font          = dict(family="Open Sans,sans-serif", color=TXT2, size=11),
    legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUT, size=10),
                         bordercolor="rgba(0,0,0,0)"),
    xaxis         = dict(gridcolor=GRID, linecolor=LINE_C,
                         tickfont=dict(color=MUT, size=10), title_font=dict(color=MUT)),
    yaxis         = dict(gridcolor=GRID, linecolor=LINE_C,
                         tickfont=dict(color=MUT, size=10), title_font=dict(color=MUT)),
    margin        = dict(l=12, r=12, t=46, b=12),
    coloraxis_colorbar = dict(tickfont=dict(color=MUT, size=9),
                               title_font=dict(color=MUT, size=9),
                               bgcolor=SURF2, bordercolor="rgba(0,0,0,0)",
                               thickness=12),
)

def T(fig, title="", h=None):
    kw = dict(**BL)
    kw["title"] = dict(
        text=title,
        font=dict(family="Montserrat,sans-serif", color=TXT, size=12, weight="bold"),
        x=0.02, xanchor="left")
    if h: kw["height"] = h
    fig.update_layout(**kw)
    return fig

def combo_lay(fig, title, h=340):
    fig.update_layout(
        paper_bgcolor=SURF, plot_bgcolor=SURF,
        font=dict(family="Open Sans,sans-serif", color=TXT2, size=11),
        title=dict(text=title,
                   font=dict(family="Montserrat,sans-serif", color=TXT, size=12),
                   x=0.02),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUT, size=10)),
        xaxis=dict(gridcolor=GRID, linecolor=LINE_C, tickfont=dict(color=MUT, size=10)),
        yaxis=dict(gridcolor=GRID, linecolor=LINE_C, tickfont=dict(color=MUT, size=10)),
        margin=dict(l=12, r=12, t=46, b=12), height=h,
    )

def hmap_lay(fig, title, h=340):
    fig.update_layout(
        paper_bgcolor=SURF, plot_bgcolor=SURF,
        font=dict(family="Open Sans,sans-serif", color=TXT2, size=10),
        title=dict(text=title,
                   font=dict(family="Montserrat,sans-serif", color=TXT, size=12),
                   x=0.02),
        xaxis=dict(tickfont=dict(color=MUT, size=9)),
        yaxis=dict(tickfont=dict(color=MUT, size=9)),
        margin=dict(l=12, r=12, t=46, b=12), height=h,
    )

# ── INDIA STATE COORDS ────────────────────────────────────────────────────────
STATE_LL = {
    "Bihar":(25.10,85.31),"Chhattisgarh":(21.28,81.87),"Delhi":(28.70,77.10),
    "Gujarat":(22.26,71.19),"Haryana":(29.06,76.09),"Karnataka":(15.32,75.71),
    "Madhya Pradesh":(22.97,78.66),"Maharashtra":(19.75,75.71),"Odisha":(20.95,85.10),
    "Punjab":(31.15,75.34),"Rajasthan":(27.02,74.22),"Tamil Nadu":(11.13,78.66),
    "Telangana":(18.11,79.02),"Uttar Pradesh":(26.85,80.95),"West Bengal":(22.99,87.86),
}
STATE_NAME_MAP = {"Delhi":"NCT of Delhi"}

@st.cache_data(show_spinner=False)
def get_india_geojson():
    url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112"
           "/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200: return r.json()
    except: pass
    return None

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading ESG data…")
def load_data():
    geo  = pd.read_csv("green_investments_geographic.csv", parse_dates=["Project_Start_Date"])
    cr   = pd.read_csv("carbon_reduction.csv")
    esg  = pd.read_csv("esg_scores_companies.csv")
    roi  = pd.read_csv("roi_returns.csv")
    sec  = pd.read_csv("sector_info.csv", header=None, names=["Sector","Description"])
    m = geo.merge(cr,  on="Project_ID", how="left", suffixes=("","_cr"))
    m = m.merge(roi, on="Project_ID", how="left")
    m = m.merge(esg, on="Company_Name", how="left")
    if "Year_cr" in m.columns:
        m["Year"] = m["Year"].fillna(m["Year_cr"]); m.drop(columns=["Year_cr"], inplace=True)
    m["Year"] = m["Year"].astype(int)
    m["Investment_M"] = m["Investment_Amount_USD"] / 1e6
    m["lat"] = m["State"].map(lambda s: STATE_LL.get(s,(None,None))[0])
    m["lon"] = m["State"].map(lambda s: STATE_LL.get(s,(None,None))[1])
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

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="hdfc-logo">
      <div class="hdfc-logo-title">🏦 HDFC Bank</div>
      <div><span class="hdfc-logo-badge">Green Finance Division</span></div>
      <div class="hdfc-logo-sub">ESG Investment Tracker v5.0</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("##### 📌 Navigation")
    PAGES = {
        "🏠  Executive Overview":       "overview",
        "🌿  ESG Analysis":             "esg",
        "🗺️   Geographic Intelligence":  "geo",
        "🌍  Carbon Reduction":         "carbon",
        "💰  ROI & Returns":            "roi",
        "🔍  Sector Deep Dive":         "sector",
    }
    if "page" not in st.session_state:
        st.session_state.page = "overview"
    for lbl, key in PAGES.items():
        if st.button(lbl, key=f"nav_{key}"):
            st.session_state.page = key

    if DATA_OK:
        st.markdown("---")
        st.markdown("##### 🎛️ Filters")

        st.markdown('<div class="flt-head">📅 Date Range</div>', unsafe_allow_html=True)
        date_range = st.date_input("", value=(MIN_DATE, MAX_DATE),
                                   min_value=MIN_DATE, max_value=MAX_DATE,
                                   label_visibility="collapsed")
        years = sorted(master["Year"].unique().tolist())
        yr_range = st.select_slider("🗓️ Year", options=years,
                                    value=(min(years), max(years)))

        st.markdown('<div class="flt-head">🏭 Sector</div>', unsafe_allow_html=True)
        sel_sector = st.selectbox("", ALL_SECTORS, label_visibility="collapsed", key="sb_sector")

        st.markdown('<div class="flt-head">📍 State</div>', unsafe_allow_html=True)
        sel_state = st.selectbox("", ALL_STATES, label_visibility="collapsed", key="sb_state")

        st.markdown('<div class="flt-head">🗺️ Region</div>', unsafe_allow_html=True)
        regions = ["All Regions"] + sorted(master["Region"].dropna().unique().tolist())
        sel_region = st.selectbox("", regions, label_visibility="collapsed", key="sb_region")

        st.markdown('<div class="flt-head">⚠️ ESG Risk</div>', unsafe_allow_html=True)
        sel_risk = st.selectbox("", ["All Risk Tiers","Low","Medium","High"],
                                label_visibility="collapsed", key="sb_risk")

        st.markdown("---")
        st.markdown(f"""
        <div style='font-size:.67rem;color:{MUT};font-family:Montserrat,sans-serif;'>
        📊 v5.0 &nbsp;·&nbsp; {len(master):,} records<br>
        <span style='color:rgba(210,47,47,.5);'>HDFC Bank — Green Finance Division</span>
        </div>""", unsafe_allow_html=True)

# ── GUARD ─────────────────────────────────────────────────────────────────────
if not DATA_OK:
    st.error(f"❌ CSV not found: {ERR_MSG}")
    st.stop()

# ── FILTER ────────────────────────────────────────────────────────────────────
def filt(df):
    d = df.copy()
    if len(date_range) == 2:
        d = d[(d["Year"] >= date_range[0].year) & (d["Year"] <= date_range[1].year)]
    d = d[(d["Year"] >= yr_range[0]) & (d["Year"] <= yr_range[1])]
    if sel_sector != "All Sectors":  d = d[d["Sector"] == sel_sector]
    if sel_state  != "All States":   d = d[d["State"]  == sel_state]
    if sel_region != "All Regions":  d = d[d["Region"] == sel_region]
    if sel_risk not in ("All Risk Tiers",""):
        d = d[d["Risk_Category"] == sel_risk]
    return d

df = filt(master)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def kpi(icon, val, label, delta=""):
    dl = f"<div class='kpi-delta'>▲ {delta}</div>" if delta else ""
    return (f"<div class='kpi-card'><div class='kpi-icon'>{icon}</div>"
            f"<div class='kpi-val'>{val}</div>"
            f"<div class='kpi-label'>{label}</div>{dl}</div>")

def filter_badge():
    parts = []
    if sel_sector != "All Sectors":           parts.append(("🏭", sel_sector))
    if sel_state  != "All States":            parts.append(("📍", sel_state))
    if sel_region != "All Regions":           parts.append(("🗺️", sel_region))
    if sel_risk not in ("All Risk Tiers",""):  parts.append(("⚠️", sel_risk))
    parts.append(("🗓️", f"{yr_range[0]}–{yr_range[1]}"))
    badges = "".join(f"<span class='fbadge'>{ic} {lb}</span>" for ic,lb in parts)
    st.markdown(f"<div style='margin-bottom:12px;'>{badges}</div>", unsafe_allow_html=True)

# Colour scales — HDFC branded
RED_SCALE  = [[0,"#0D0810"],[0.25,"#4A0A0A"],[0.6,HDFC_RED],[0.85,HDFC_RED_L],[1.0,"#FFCDD2"]]
GOLD_SCALE = [[0,"#0D0C08"],[0.3,"#3E2800"],[0.65,GOLD],[1.0,GOLD_L]]
MIXED_SCALE= [[0,"#0A0D18"],[0.3,"#1A3A6A"],[0.65,HDFC_RED],[1.0,GOLD2]]

# ══════════════════════════════════════════════════════════════════════════════
#  TOP BANNER — shown on every page
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style='background:linear-gradient(135deg,{HDFC_RED2} 0%,#8B0000 40%,#3E0000 100%);
            border-radius:10px;padding:10px 24px;margin-bottom:16px;
            display:flex;align-items:center;justify-content:space-between;
            border:1px solid rgba(255,255,255,.08);'>
  <div>
    <span style='font-family:Montserrat,sans-serif;font-size:.78rem;font-weight:700;
                 color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:2px;'>
      HDFC Bank Ltd
    </span><br>
    <span style='font-family:Montserrat,sans-serif;font-size:1.05rem;font-weight:800;
                 color:#fff;letter-spacing:.3px;'>
      Green Finance &amp; ESG Investment Tracker
    </span>
  </div>
  <div style='text-align:right;'>
    <span style='font-size:.68rem;color:rgba(255,255,255,.5);font-family:Montserrat,sans-serif;'>
      FY {yr_range[0]}–{yr_range[1]} &nbsp;|&nbsp; {df["Project_ID"].nunique():,} Projects &nbsp;|&nbsp;
      ${df["Investment_Amount_USD"].sum()/1e9:.2f}B Deployed
    </span><br>
    <span style='font-size:.65rem;color:{GOLD_L};font-family:Montserrat,sans-serif;font-weight:600;'>
      ● LIVE DASHBOARD
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  P1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "overview":
    st.markdown(f"""<div class="pg-header"><div class="pg-icon">🏠</div><div>
    <div class="pg-title">Executive Overview</div>
    <div class="pg-sub">Consolidated Green Finance Performance · HDFC Bank Portfolio Intelligence</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()

    inv  = df["Investment_Amount_USD"].sum() / 1e9
    co2  = df["CO2_Reduction_Tons"].sum() / 1e6
    roi_ = df["ROI_Percentage"].mean()
    esg_ = df["ESG_Score"].mean()
    npr  = df["Project_ID"].nunique()
    nst  = df["State"].nunique()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,(ic,vl,lb,dl) in zip([c1,c2,c3,c4,c5,c6],[
        ("💵", f"${inv:.2f}B",  "Total Green Investment", "Portfolio AUM"),
        ("🌍", f"{co2:.2f}M T", "CO₂ Tonnes Avoided",    f"{co2/4.6:.1f}M Cars Off Road"),
        ("📈", f"{roi_:.1f}%",  "Avg Portfolio ROI",      "Risk-Adjusted Returns"),
        ("🌿", f"{esg_:.1f}",   "Avg ESG Score",          "ESG Health Index"),
        ("🏗️", f"{npr:,}",      "Active Projects",        "Across All Sectors"),
        ("📍", f"{nst}",        "States Covered",         "Pan-India Reach"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb,dl), unsafe_allow_html=True)

    # Ribbon
    bsec = df.groupby("Sector")["Investment_Amount_USD"].sum().idxmax() if len(df)>0 else "—"
    breg = df.groupby("Region")["Investment_Amount_USD"].sum().idxmax() if len(df)>0 else "—"
    brs  = df.groupby("Sector")["ROI_Percentage"].mean().idxmax()       if len(df)>0 else "—"
    lrp  = round(len(df[df["Risk_Category"]=="Low"])/max(len(df),1)*100,1)
    st.markdown(f"""<div class="ribbon" style="margin-top:14px;">
    <div class="rib-item"><div class="rib-val">{df['Sector'].nunique()}</div><div class="rib-lbl">Sectors</div></div>
    <div class="rib-item"><div class="rib-val">{bsec}</div><div class="rib-lbl">Top Invested Sector</div></div>
    <div class="rib-item"><div class="rib-val">{breg}</div><div class="rib-lbl">Leading Region</div></div>
    <div class="rib-item"><div class="rib-val">{brs}</div><div class="rib-lbl">Best ROI Sector</div></div>
    <div class="rib-item"><div class="rib-val">{lrp}%</div><div class="rib-lbl">Low-Risk Share</div></div>
    <div class="rib-item"><div class="rib-val">{yr_range[0]}–{yr_range[1]}</div><div class="rib-lbl">Analysis Period</div></div>
    </div>""", unsafe_allow_html=True)

    # Row 1: Stacked area + donut
    st.markdown('<div class="sec-title">📊 Investment Trends &amp; Sector Allocation</div>', unsafe_allow_html=True)
    a1,a2 = st.columns([3,2])
    with a1:
        tr = df.groupby(["Year","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f = px.area(tr, x="Year", y="Investment_Amount_USD", color="Sector",
                    color_discrete_sequence=PAL, line_shape="spline")
        f.update_traces(line=dict(width=1.8), opacity=0.88)
        T(f, "Annual Green Investment by Sector — Stacked Area", 340)
        st.plotly_chart(f, use_container_width=True)
    with a2:
        pd_ = df.groupby("Sector")["Investment_Amount_USD"].sum().reset_index()
        f2 = px.pie(pd_, values="Investment_Amount_USD", names="Sector",
                    color_discrete_sequence=PAL, hole=0.60)
        f2.update_traces(textinfo="label+percent", textfont_size=10,
                         marker=dict(line=dict(color=SURF, width=2)))
        T(f2, "Portfolio Sector Allocation", 340)
        st.plotly_chart(f2, use_container_width=True)

    # Row 2: 3-col snapshot
    st.markdown('<div class="sec-title">⚡ Risk · Carbon · Returns — At a Glance</div>', unsafe_allow_html=True)
    b1,b2,b3 = st.columns(3)
    with b1:
        er = df.groupby("Risk_Category")["Investment_Amount_USD"].sum().reset_index()
        er["ord"] = er["Risk_Category"].map({"Low":0,"Medium":1,"High":2})
        er = er.sort_values("ord")
        f3 = px.bar(er, x="Risk_Category", y="Investment_Amount_USD",
                    color="Risk_Category", text_auto=".2s", color_discrete_map=RISK_C)
        f3.update_traces(textposition="outside", textfont_color=TXT2)
        T(f3, "Investment by ESG Risk Tier", 300)
        st.plotly_chart(f3, use_container_width=True)
    with b2:
        cy = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f4 = px.bar(cy, x="Year", y="CO2_Reduction_Tons",
                    color="CO2_Reduction_Tons", color_continuous_scale=GOLD_SCALE,
                    text_auto=".2s")
        f4.update_traces(textposition="outside", textfont_color=TXT2)
        T(f4, "CO₂ Reduced Per Year (Tonnes)", 300)
        st.plotly_chart(f4, use_container_width=True)
    with b3:
        rs = df.groupby("Sector")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage")
        f5 = px.bar(rs, x="ROI_Percentage", y="Sector", orientation="h",
                    color="ROI_Percentage", color_continuous_scale=RED_SCALE,
                    text_auto=".1f")
        f5.update_traces(textposition="outside", textfont_color=TXT2)
        T(f5, "Avg ROI by Sector (%)", 300)
        st.plotly_chart(f5, use_container_width=True)

    # Row 3: YoY dual-axis + quarterly
    st.markdown('<div class="sec-title">📆 Year-over-Year Growth &amp; Seasonality</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([3,2])
    with g1:
        yy = df.groupby("Year")["Investment_Amount_USD"].sum().reset_index()
        yy["YoY"] = yy["Investment_Amount_USD"].pct_change() * 100
        f6 = make_subplots(specs=[[{"secondary_y":True}]])
        f6.add_trace(go.Bar(x=yy["Year"], y=yy["Investment_Amount_USD"],
                            name="Investment (USD)", marker_color=HDFC_RED,
                            marker_line_color=HDFC_RED_L, marker_line_width=0.5,
                            opacity=0.85), secondary_y=False)
        f6.add_trace(go.Scatter(x=yy["Year"], y=yy["YoY"], name="YoY Growth %",
                                mode="lines+markers",
                                line=dict(color=GOLD2, width=2.8),
                                marker=dict(size=8, color=GOLD2,
                                            line=dict(color=SURF, width=2))),
                     secondary_y=True)
        combo_lay(f6, "Investment Volume &amp; YoY Growth (%)", 310)
        f6.update_yaxes(gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=GOLD2), secondary_y=True)
        st.plotly_chart(f6, use_container_width=True)
    with g2:
        qd = df.groupby("Quarter")["Investment_Amount_USD"].sum().reset_index()
        qd["ord"] = qd["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
        qd = qd.sort_values("ord")
        f7 = px.pie(qd, values="Investment_Amount_USD", names="Quarter",
                    color_discrete_sequence=[HDFC_RED, GOLD, BLUE_L, TEAL_L], hole=0.55)
        f7.update_traces(textinfo="label+percent")
        T(f7, "Investment Distribution by Quarter", 310)
        st.plotly_chart(f7, use_container_width=True)

    # Insight
    st.markdown(f"""<div class="insight">
    <span class="tag">PORTFOLIO SUMMARY</span>
    HDFC's green portfolio spans <b>{df['Sector'].nunique()} sectors</b> across <b>{nst} states</b>,
    deploying <b>${inv:.2f}B</b> in sustainable capital.
    Total CO₂ avoided: <b>{co2:.2f}M tonnes</b>
    (equivalent to removing <b>~{co2/4.6:.1f}M cars</b> from roads for a year).
    <b>{bsec}</b> leads investment volume; <b>{brs}</b> delivers the highest avg ROI.
    <b>{lrp}%</b> of projects fall within the Low ESG Risk tier.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  P2 — ESG ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "esg":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🌿</div><div>
    <div class="pg-title">ESG Analysis</div>
    <div class="pg-sub">Environmental · Social · Governance Deep-Dive</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()

    ae  = df["ESG_Score"].mean()
    lp  = round(len(df[df["Risk_Category"]=="Low"]) /max(len(df),1)*100,1)
    hp  = round(len(df[df["Risk_Category"]=="High"])/max(len(df),1)*100,1)
    tco = (df.dropna(subset=["ESG_Score"])
           .groupby("Company_Name")["ESG_Score"].mean().idxmax() if len(df)>0 else "N/A")

    c1,c2,c3,c4 = st.columns(4)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4],[
        ("🌿",f"{ae:.1f}","Avg ESG Score"),
        ("✅",f"{lp}%","Low-Risk Projects"),
        ("⚠️",f"{hp}%","High-Risk Projects"),
        ("🏅",(tco[:16]+"…") if len(tco)>16 else tco,"Top ESG Company"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)

    # Histogram + donut
    st.markdown('<div class="sec-title">📊 Score Distribution &amp; Risk Profile</div>', unsafe_allow_html=True)
    h1,h2 = st.columns([3,2])
    with h1:
        f = px.histogram(df.dropna(subset=["ESG_Score"]), x="ESG_Score",
                         color="Risk_Category", nbins=45, barmode="overlay",
                         color_discrete_map=RISK_C, opacity=0.82)
        f.update_layout(bargap=0.04)
        T(f, "ESG Score Distribution — Coloured by Risk Category", 320)
        st.plotly_chart(f, use_container_width=True)
    with h2:
        rc = df["Risk_Category"].value_counts().reset_index()
        rc.columns = ["Risk","Count"]
        f2 = px.pie(rc, values="Count", names="Risk", hole=0.62,
                    color="Risk", color_discrete_map=RISK_C)
        f2.update_traces(textinfo="label+percent",
                         marker=dict(line=dict(color=SURF, width=2)))
        T(f2, "Risk Category Distribution", 320)
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
                    color_discrete_map=RISK_C, size_max=28, opacity=0.75)
    f3.add_vline(x=bub["ESG"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ESG {bub['ESG'].mean():.1f}",
                 annotation_font_color=MUT, annotation_font_size=10)
    f3.add_hline(y=bub["ROI"].mean(), line_dash="dash", line_color=MUT,
                 annotation_text=f"Avg ROI {bub['ROI'].mean():.1f}%",
                 annotation_position="top right",
                 annotation_font_color=MUT, annotation_font_size=10)
    T(f3, "ESG Score vs Avg ROI  (Bubble = Investment Size  |  Colour = Risk Category)", 400)
    st.plotly_chart(f3, use_container_width=True)

    # Violin + bar
    st.markdown('<div class="sec-title">🎻 ESG Score Distribution per Sector</div>', unsafe_allow_html=True)
    v1,v2 = st.columns(2)
    with v1:
        f4 = px.violin(df.dropna(subset=["ESG_Score","Sector"]),
                       x="Sector", y="ESG_Score", box=True,
                       color="Sector", color_discrete_sequence=PAL, points=False)
        T(f4, "ESG Violin Plot — per Sector", 340)
        st.plotly_chart(f4, use_container_width=True)
    with v2:
        es = df.groupby("Sector")["ESG_Score"].mean().reset_index().sort_values("ESG_Score",ascending=False)
        f5 = px.bar(es, y="Sector", x="ESG_Score", orientation="h",
                    color="ESG_Score", color_continuous_scale=RED_SCALE, text_auto=".1f")
        f5.update_traces(textposition="outside", textfont_color=TXT2)
        T(f5, "Average ESG Score by Sector", 340)
        st.plotly_chart(f5, use_container_width=True)

    # Decomposition Treemap — FIXED: no cornerradius, no insidetextanchor
    st.markdown('<div class="sec-title">🌳 Decomposition Tree — Risk → Sector → Region → State</div>', unsafe_allow_html=True)
    tree = df.groupby(["Risk_Category","Sector","Region","State"])["Investment_Amount_USD"].sum().reset_index()
    f6 = px.treemap(
        tree,
        path=[px.Constant("🏦 HDFC PORTFOLIO"), "Risk_Category","Sector","Region","State"],
        values="Investment_Amount_USD",
        color="Investment_Amount_USD",
        color_continuous_scale=MIXED_SCALE,
    )
    f6.update_traces(
        textinfo="label+percent root",
        textfont=dict(family="Montserrat,sans-serif", size=11, color="#FFFFFF"),
        marker=dict(line=dict(color=NAVY, width=1.2)),
    )
    f6.update_layout(
        paper_bgcolor=SURF2,
        margin=dict(l=4,r=4,t=6,b=4), height=520,
        font=dict(color=TXT, family="Open Sans,sans-serif"),
        coloraxis_colorbar=dict(
            tickfont=dict(color=MUT, size=9),
            title=dict(text="Investment", font=dict(color=MUT, size=9)),
            bgcolor=SURF, bordercolor="rgba(0,0,0,0)", thickness=10,
        ),
    )
    st.plotly_chart(f6, use_container_width=True)

    # Top 15 companies
    st.markdown('<div class="sec-title">🏆 Top 15 Companies by ESG Score</div>', unsafe_allow_html=True)
    top = (df.dropna(subset=["ESG_Score"])
           .groupby("Company_Name")
           .agg(ESG=("ESG_Score","first"), Risk=("Risk_Category","first"))
           .sort_values("ESG",ascending=False).head(15).reset_index())
    f7 = px.bar(top, x="Company_Name", y="ESG", color="Risk",
                text="ESG", color_discrete_map=RISK_C)
    f7.update_traces(textposition="outside", textfont_color=TXT2, texttemplate="%{text:.1f}")
    T(f7, "Top 15 Companies — ESG Score Ranking", 360)
    st.plotly_chart(f7, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  P3 — GEOGRAPHIC INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "geo":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🗺️</div><div>
    <div class="pg-title">Geographic Intelligence</div>
    <div class="pg-sub">India Investment Maps · Regional Patterns · State-Level Spatial Analysis</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()

    st_agg = (df.dropna(subset=["State"])
              .groupby(["State","State_geo"])
              .agg(Investment=("Investment_Amount_USD","sum"),
                   Projects=("Project_ID","nunique"),
                   Avg_ROI=("ROI_Percentage","mean"),
                   CO2=("CO2_Reduction_Tons","sum"),
                   Avg_ESG=("ESG_Score","mean"))
              .reset_index())

    # State detail if filtered
    if sel_state != "All States":
        sd_ = df[df["State"]==sel_state]
        st.markdown(f'<div class="sec-title">📍 {sel_state} — State Snapshot</div>', unsafe_allow_html=True)
        cc1,cc2,cc3,cc4 = st.columns(4)
        for col,(ic,vl,lb) in zip([cc1,cc2,cc3,cc4],[
            ("💵",f"${sd_['Investment_Amount_USD'].sum()/1e6:.1f}M","Investment"),
            ("🌍",f"{sd_['CO2_Reduction_Tons'].sum()/1e3:.1f}K T","CO₂ Avoided"),
            ("📈",f"{sd_['ROI_Percentage'].mean():.1f}%","Avg ROI"),
            ("🏗️",f"{sd_['Project_ID'].nunique():,}","Projects"),
        ]):
            with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for maps
    map_tab1, map_tab2 = st.tabs(["🗺️  Filled Choropleth Map", "🔵  Bubble Map"])

    with map_tab1:
        india_geo = get_india_geojson()
        if india_geo:
            st.markdown('<div class="sec-title">🗺️ India — State Investment Filled Map</div>', unsafe_allow_html=True)
            fc = px.choropleth(
                st_agg, geojson=india_geo, locations="State_geo",
                featureidkey="properties.ST_NM", color="Investment",
                color_continuous_scale=RED_SCALE,
                hover_name="State",
                hover_data={"Investment":":.2s","Projects":True,
                            "Avg_ROI":":.1f","CO2":":.0f","State_geo":False},
                scope="asia",
            )
            fc.update_geos(fitbounds="locations", visible=False, bgcolor=NAVY,
                           showcoastlines=True,  coastlinecolor="rgba(200,149,58,.2)",
                           showocean=True,       oceancolor="#040608",
                           showland=True,        landcolor="#101828",
                           showframe=False)
            fc.update_traces(marker_line_color="rgba(200,149,58,.3)", marker_line_width=1)
            fc.update_layout(
                paper_bgcolor=NAVY, geo_bgcolor=NAVY,
                font=dict(family="Open Sans,sans-serif", color=TXT2, size=11),
                title=dict(text="Green Investment Filled Map — India States",
                           font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
                coloraxis_colorbar=dict(title="Investment (USD)", thickness=12,
                                        tickfont=dict(color=MUT,size=9),
                                        title_font=dict(color=MUT,size=9),
                                        bgcolor=SURF, bordercolor="rgba(0,0,0,0)"),
                margin=dict(l=0,r=0,t=48,b=0), height=540,
            )
            st.plotly_chart(fc, use_container_width=True)
        else:
            st.warning("⚠️ Could not load India GeoJSON — check internet. Using bubble map below.")

    with map_tab2:
        st.markdown('<div class="sec-title">🔵 India — Green Investment Bubble Map</div>', unsafe_allow_html=True)
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
                            color_discrete_sequence=[HDFC_RED,GOLD,BLUE_L,TEAL_L,"#9C27B0"],
                            size_max=52, scope="asia", projection="natural earth")
        fm.update_geos(visible=True, resolution=50,
                       showcountries=True,  countrycolor="rgba(200,149,58,.2)",
                       showcoastlines=True, coastlinecolor="rgba(200,149,58,.2)",
                       showland=True,       landcolor="#0D1828",
                       showocean=True,      oceancolor="#040810",
                       showframe=False,     bgcolor=NAVY,
                       center=dict(lat=22,lon=80),
                       lataxis_range=[6,38], lonaxis_range=[65,100])
        fm.update_layout(paper_bgcolor=NAVY, geo_bgcolor=NAVY,
                         font=dict(family="Open Sans,sans-serif",color=TXT2,size=11),
                         title=dict(text="Green Investment Bubble Map — India",
                                    font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
                         legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=MUT,size=10)),
                         margin=dict(l=8,r=8,t=48,b=8), height=520)
        st.plotly_chart(fm, use_container_width=True)

    # Region breakdown
    st.markdown('<div class="sec-title">📍 Regional Investment Breakdown</div>', unsafe_allow_html=True)
    g1,g2 = st.columns([3,2])
    with g1:
        ri = df.groupby(["Region","Year"])["Investment_Amount_USD"].sum().reset_index()
        f = px.bar(ri, x="Year", y="Investment_Amount_USD", color="Region",
                   barmode="group", color_discrete_sequence=PAL, text_auto=".2s")
        f.update_traces(textposition="outside", textfont_color=TXT2)
        T(f, "Regional Investment by Year", 330)
        st.plotly_chart(f, use_container_width=True)
    with g2:
        rt = df.groupby("Region")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False)
        f2 = px.funnel(rt, x="Investment_Amount_USD", y="Region",
                       color_discrete_sequence=PAL)
        T(f2, "Region Investment Funnel", 330)
        st.plotly_chart(f2, use_container_width=True)

    # Top states bar
    st.markdown('<div class="sec-title">🗺️ Top 15 States by Green Investment</div>', unsafe_allow_html=True)
    si = (df.groupby("State")["Investment_Amount_USD"].sum().reset_index()
          .sort_values("Investment_Amount_USD",ascending=False).head(15))
    f3 = px.bar(si, y="State", x="Investment_Amount_USD", orientation="h",
                color="Investment_Amount_USD", color_continuous_scale=RED_SCALE,
                text_auto=".2s")
    f3.update_traces(textposition="outside", textfont_color=TXT2)
    T(f3, "Top 15 States — Total Green Investment (USD)", 380)
    st.plotly_chart(f3, use_container_width=True)

    # Heatmaps
    st.markdown('<div class="sec-title">🔥 Investment Heatmaps</div>', unsafe_allow_html=True)
    hm1,hm2 = st.columns(2)
    with hm1:
        hp_df = df.groupby(["Sector","Region"])["Investment_Amount_USD"].sum().reset_index()
        pv = hp_df.pivot(index="Sector",columns="Region",values="Investment_Amount_USD").fillna(0)
        fh1 = go.Figure(go.Heatmap(
            z=pv.values, x=pv.columns.tolist(), y=pv.index.tolist(),
            colorscale=RED_SCALE, text=pv.values, texttemplate="%{text:.2s}",
            hoverongaps=False, colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
        ))
        hmap_lay(fh1, "Sector × Region Investment Heatmap", 340)
        st.plotly_chart(fh1, use_container_width=True)
    with hm2:
        mo = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
        mp2 = df.groupby(["Year","Month_Name"])["Investment_Amount_USD"].sum().reset_index()
        mp2["Month_Name"] = pd.Categorical(mp2["Month_Name"],categories=mo,ordered=True)
        pv2 = mp2.sort_values("Month_Name").pivot(
            index="Year",columns="Month_Name",values="Investment_Amount_USD").fillna(0)
        fh2 = go.Figure(go.Heatmap(
            z=pv2.values, x=pv2.columns.tolist(),
            y=pv2.index.astype(str).tolist(),
            colorscale=GOLD_SCALE, texttemplate="%{z:.2s}",
            hoverongaps=False, colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
        ))
        hmap_lay(fh2, "Monthly Investment Heatmap (Year × Month)", 340)
        fh2.update_xaxes(tickangle=38, tickfont=dict(color=MUT,size=8))
        st.plotly_chart(fh2, use_container_width=True)

    # City + Sunburst
    st.markdown('<div class="sec-title">🏙️ City Analysis &amp; Regional Sunburst</div>', unsafe_allow_html=True)
    ca,cb = st.columns(2)
    with ca:
        ci = (df.groupby("City")["Investment_Amount_USD"].sum().reset_index()
              .sort_values("Investment_Amount_USD",ascending=False).head(15))
        f5 = px.bar(ci, y="City", x="Investment_Amount_USD", orientation="h",
                    color="Investment_Amount_USD", color_continuous_scale=RED_SCALE,
                    text_auto=".2s")
        f5.update_traces(textposition="outside", textfont_color=TXT2)
        T(f5, "Top 15 Cities by Investment", 400)
        st.plotly_chart(f5, use_container_width=True)
    with cb:
        sn = df.groupby(["Region","Sector"])["Investment_Amount_USD"].sum().reset_index()
        f6 = px.sunburst(sn, path=["Region","Sector"], values="Investment_Amount_USD",
                         color="Investment_Amount_USD", color_continuous_scale=MIXED_SCALE)
        f6.update_traces(textfont=dict(family="Montserrat,sans-serif",size=11,color="#FFF"),
                         insidetextorientation="radial")
        f6.update_layout(paper_bgcolor=SURF, font=dict(color=TXT),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
                         title=dict(text="Investment Sunburst: Region → Sector",
                                    font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
                         margin=dict(l=8,r=8,t=48,b=8), height=400)
        st.plotly_chart(f6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  P4 — CARBON REDUCTION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "carbon":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🌍</div><div>
    <div class="pg-title">Carbon Reduction Analysis</div>
    <div class="pg-sub">CO₂ Impact Tracking · Sector Emission Abatement · Efficiency Metrics</div>
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

    st.markdown('<div class="sec-title">📈 Carbon Reduction Trends</div>', unsafe_allow_html=True)
    t1,t2 = st.columns(2)
    with t1:
        cy = df.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f = go.Figure(go.Scatter(
            x=cy["Year"],y=cy["CO2_Reduction_Tons"],mode="lines+markers",
            line=dict(color=HDFC_RED,width=3),
            marker=dict(size=9,color=GOLD2,line=dict(color=SURF,width=2)),
            fill="tozeroy",fillcolor="rgba(211,47,47,0.10)"))
        T(f,"Annual CO₂ Reduction Trend",320)
        st.plotly_chart(f, use_container_width=True)
    with t2:
        cs = df.groupby("Sector")["CO2_Reduction_Tons"].sum().reset_index().sort_values("CO2_Reduction_Tons")
        f2 = px.bar(cs, x="CO2_Reduction_Tons", y="Sector", orientation="h",
                    color="CO2_Reduction_Tons", color_continuous_scale=GOLD_SCALE,
                    text_auto=".2s")
        f2.update_traces(textposition="outside", textfont_color=TXT2)
        T(f2,"CO₂ Reduced by Sector (Total Tonnes)",320)
        st.plotly_chart(f2, use_container_width=True)

    st.markdown('<div class="sec-title">🔥 Carbon Heatmap — Sector × Year</div>', unsafe_allow_html=True)
    cp = df.groupby(["Year","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
    pv = cp.pivot(index="Sector",columns="Year",values="CO2_Reduction_Tons").fillna(0)
    f3 = go.Figure(go.Heatmap(
        z=pv.values, x=pv.columns.astype(str).tolist(), y=pv.index.tolist(),
        colorscale=RED_SCALE, text=pv.values, texttemplate="%{text:.2s}",
        hoverongaps=False, colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
    ))
    hmap_lay(f3,"CO₂ Reduction Heatmap — Sector × Year",340)
    st.plotly_chart(f3, use_container_width=True)

    st.markdown('<div class="sec-title">⚡ Efficiency &amp; Sunburst</div>', unsafe_allow_html=True)
    e1,e2 = st.columns(2)
    with e1:
        ed = df.groupby("Sector").agg(CO2=("CO2_Reduction_Tons","sum"),
                                       Inv=("Investment_Amount_USD","sum")).reset_index()
        ed["CO2_per_M"] = ed["CO2"]/(ed["Inv"]/1e6)
        f4 = px.bar(ed.sort_values("CO2_per_M",ascending=False),
                    x="Sector",y="CO2_per_M",
                    color="CO2_per_M", color_continuous_scale=GOLD_SCALE,
                    text_auto=".1f")
        f4.update_traces(textposition="outside", textfont_color=TXT2)
        T(f4,"CO₂ per $1M Invested — Sector Efficiency",340)
        st.plotly_chart(f4, use_container_width=True)
    with e2:
        sn = df.groupby(["Region","Sector"])["CO2_Reduction_Tons"].sum().reset_index()
        f5 = px.sunburst(sn,path=["Region","Sector"],values="CO2_Reduction_Tons",
                         color="CO2_Reduction_Tons", color_continuous_scale=MIXED_SCALE)
        f5.update_traces(textfont=dict(family="Montserrat,sans-serif",size=11,color="#FFF"),
                         insidetextorientation="radial")
        f5.update_layout(paper_bgcolor=SURF,font=dict(color=TXT),
                         coloraxis_colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
                         title=dict(text="CO₂ Sunburst — Region → Sector",
                                    font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
                         margin=dict(l=8,r=8,t=48,b=8),height=340)
        st.plotly_chart(f5, use_container_width=True)

    st.markdown('<div class="sec-title">📍 Region CO₂ Trend by Year</div>', unsafe_allow_html=True)
    rc = df.groupby(["Year","Region"])["CO2_Reduction_Tons"].sum().reset_index()
    f6 = px.line(rc,x="Year",y="CO2_Reduction_Tons",color="Region",
                 markers=True,line_shape="spline",
                 color_discrete_sequence=[HDFC_RED,GOLD,BLUE_L,TEAL_L,"#9C27B0"])
    f6.update_traces(line=dict(width=2.5),marker=dict(size=7))
    T(f6,"CO₂ Reduction Trend by Region — Year-on-Year",320)
    st.plotly_chart(f6, use_container_width=True)

    st.markdown(f"""<div class="insight">
    <span class="tag">CARBON IMPACT</span>
    Total CO₂ avoided = <b>{tc/1e6:.2f}M Tonnes</b>.
    At global carbon price ~$65/tonne → carbon credit value ≈ <b>${tc*65/1e9:.2f}B</b>.
    Investment efficiency: <b>${ef:.0f} USD per tonne CO₂</b>.
    <b>{bs}</b> leads absolute carbon abatement across all sectors.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  P5 — ROI & RETURNS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "roi":
    st.markdown("""<div class="pg-header"><div class="pg-icon">💰</div><div>
    <div class="pg-title">ROI &amp; Returns Analysis</div>
    <div class="pg-sub">Return on Investment · Risk-Adjusted Performance · Portfolio Optimization</div>
    </div></div>""", unsafe_allow_html=True)
    filter_badge()

    avg_r=df["ROI_Percentage"].mean()
    med_r=df["ROI_Percentage"].median()
    max_r=df["ROI_Percentage"].max()
    std_r=df["ROI_Percentage"].std()
    shrp =avg_r/max(std_r,0.001)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(ic,vl,lb) in zip([c1,c2,c3,c4,c5],[
        ("📈",f"{avg_r:.2f}%","Avg ROI"),
        ("📊",f"{med_r:.2f}%","Median ROI"),
        ("🚀",f"{max_r:.2f}%","Peak ROI"),
        ("📉",f"{std_r:.2f}%","Volatility σ"),
        ("⚖️",f"{shrp:.2f}","Sharpe Ratio"),
    ]):
        with col: st.markdown(kpi(ic,vl,lb), unsafe_allow_html=True)

    st.markdown('<div class="sec-title">📈 ROI Trends &amp; Sector Distribution</div>', unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        ry=df.groupby("Year")["ROI_Percentage"].mean().reset_index()
        f=go.Figure(go.Scatter(x=ry["Year"],y=ry["ROI_Percentage"],
                               mode="lines+markers",
                               line=dict(color=GOLD2,width=3),
                               marker=dict(size=9,color=GOLD_L,line=dict(color=SURF,width=2)),
                               fill="tozeroy",fillcolor="rgba(200,149,58,0.08)"))
        T(f,"Average ROI Trend by Year",320)
        st.plotly_chart(f, use_container_width=True)
    with r2:
        f2=px.box(df.dropna(subset=["ROI_Percentage","Sector"]),
                  x="Sector",y="ROI_Percentage",
                  color="Sector",color_discrete_sequence=PAL,points=False)
        T(f2,"ROI Distribution per Sector — Box Plot",320)
        st.plotly_chart(f2, use_container_width=True)

    st.markdown('<div class="sec-title">🔍 ROI Deep Dive</div>', unsafe_allow_html=True)
    d1,d2 = st.columns(2)
    with d1:
        f3=px.histogram(df.dropna(subset=["ROI_Percentage"]),x="ROI_Percentage",
                        color="Sector",nbins=50,barmode="overlay",
                        color_discrete_sequence=PAL,opacity=0.78)
        f3.update_layout(bargap=0.04)
        T(f3,"ROI Distribution Histogram — by Sector",340)
        st.plotly_chart(f3, use_container_width=True)
    with d2:
        rr=df.groupby("Risk_Category")["ROI_Percentage"].agg(["mean","std"]).reset_index()
        rr.columns=["Risk","Mean","Std"]
        f4=go.Figure(go.Bar(x=rr["Risk"],y=rr["Mean"],
                            error_y=dict(type="data",array=rr["Std"],
                                         visible=True,color=MUT),
                            marker_color=[RISK_C.get(r,"#aaa") for r in rr["Risk"]],
                            text=rr["Mean"].round(2),textposition="outside",
                            textfont=dict(color=TXT2)))
        T(f4,"Avg ROI ± σ — by ESG Risk Category",340)
        st.plotly_chart(f4, use_container_width=True)

    st.markdown('<div class="sec-title">💹 Investment vs ROI — Portfolio Scatter</div>', unsafe_allow_html=True)
    sc=df.dropna(subset=["Investment_Amount_USD","ROI_Percentage","ESG_Score"])
    sc_s=sc.sample(min(5000,len(sc)))
    f5=px.scatter(sc_s,x="Investment_Amount_USD",y="ROI_Percentage",
                  color="Sector",size="ESG_Score",opacity=0.65,
                  hover_data=["Company_Name","State","Year"],
                  color_discrete_sequence=PAL,size_max=18)
    f5.update_xaxes(type="log",title_text="Investment (USD — log scale)")
    T(f5,"Investment Amount vs ROI  (Bubble = ESG Score  |  Colour = Sector)",420)
    st.plotly_chart(f5, use_container_width=True)

    st.markdown('<div class="sec-title">📍 ROI by Region &amp; Quarter</div>', unsafe_allow_html=True)
    rr1,rr2 = st.columns(2)
    with rr1:
        reg=df.groupby("Region")["ROI_Percentage"].mean().reset_index().sort_values("ROI_Percentage",ascending=False)
        f6=px.bar(reg,x="Region",y="ROI_Percentage",
                  color="ROI_Percentage",color_continuous_scale=RED_SCALE,text_auto=".1f")
        f6.update_traces(textposition="outside",textfont_color=TXT2)
        T(f6,"Avg ROI by Region",300)
        st.plotly_chart(f6, use_container_width=True)
    with rr2:
        rq=df.groupby(["Quarter","Sector"])["ROI_Percentage"].mean().reset_index()
        rq["ord"]=rq["Quarter"].map({"Q1":0,"Q2":1,"Q3":2,"Q4":3})
        rq=rq.sort_values("ord")
        f7=px.line(rq,x="Quarter",y="ROI_Percentage",color="Sector",
                   markers=True,line_shape="spline",color_discrete_sequence=PAL)
        f7.update_traces(line=dict(width=2.2),marker=dict(size=7))
        T(f7,"Avg ROI by Quarter — per Sector",300)
        st.plotly_chart(f7, use_container_width=True)

    st.markdown('<div class="sec-title">🔗 Parallel Coordinates — Multi-Metric View</div>', unsafe_allow_html=True)
    pc=df.dropna(subset=["ESG_Score","ROI_Percentage","CO2_Reduction_Tons","Investment_Amount_USD"])
    pc_s=pc.sample(min(3000,len(pc))).copy()
    pc_s["Risk_n"]=pc_s["Risk_Category"].map({"Low":0,"Medium":1,"High":2})
    f8=px.parallel_coordinates(pc_s,
        dimensions=["ESG_Score","ROI_Percentage","CO2_Reduction_Tons","Investment_M"],
        color="Risk_n",
        color_continuous_scale=[[0,"#2E7D32"],[0.5,GOLD],[1.0,HDFC_RED]],
        labels={"ESG_Score":"ESG Score","ROI_Percentage":"ROI %",
                "CO2_Reduction_Tons":"CO₂ (T)","Investment_M":"Inv ($M)",
                "Risk_n":"Risk (0=Low)"})
    f8.update_layout(paper_bgcolor=SURF,plot_bgcolor=SURF,
                     font=dict(family="Open Sans,sans-serif",color=TXT2,size=11),
                     coloraxis_colorbar=dict(tickfont=dict(color=MUT,size=9),thickness=10),
                     title=dict(text="Parallel Coordinates: ESG · ROI · CO₂ · Investment",
                                font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
                     margin=dict(l=12,r=12,t=48,b=12),height=380)
    st.plotly_chart(f8, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  P6 — SECTOR DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "sector":
    st.markdown("""<div class="pg-header"><div class="pg-icon">🔍</div><div>
    <div class="pg-title">Sector Deep Dive</div>
    <div class="pg-sub">Granular Per-Sector Analysis — Investment · ESG · Carbon · Returns</div>
    </div></div>""", unsafe_allow_html=True)

    dp1,dp2 = st.columns(2)
    with dp1:
        chosen = st.selectbox("🏭 Select Sector",
                              sorted(df["Sector"].dropna().unique().tolist()),
                              key="sd_sector")
    with dp2:
        chosen_state = st.selectbox("📍 Filter by State",
                                    ["All States"]+sorted(df["State"].dropna().unique().tolist()),
                                    key="sd_state")

    sd = df[df["Sector"]==chosen]
    if chosen_state != "All States": sd = sd[sd["State"]==chosen_state]

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

    st.markdown('<div class="sec-title">📈 Investment, ROI &amp; Carbon Trends</div>', unsafe_allow_html=True)
    s1,s2 = st.columns(2)
    with s1:
        yd=sd.groupby("Year").agg(Investment=("Investment_Amount_USD","sum"),
                                    ROI=("ROI_Percentage","mean")).reset_index()
        fc=make_subplots(specs=[[{"secondary_y":True}]])
        fc.add_trace(go.Bar(x=yd["Year"],y=yd["Investment"],name="Investment",
                            marker_color=HDFC_RED, marker_line_color=HDFC_RED_L,
                            marker_line_width=0.5, opacity=0.85),secondary_y=False)
        fc.add_trace(go.Scatter(x=yd["Year"],y=yd["ROI"],name="ROI %",
                                mode="lines+markers",line=dict(color=GOLD2,width=2.8),
                                marker=dict(size=8,color=GOLD_L,line=dict(color=SURF,width=2))),
                     secondary_y=True)
        combo_lay(fc,f"{chosen}: Investment &amp; ROI — Dual Axis",340)
        fc.update_yaxes(gridcolor="rgba(0,0,0,0)",tickfont=dict(color=GOLD2),secondary_y=True)
        st.plotly_chart(fc, use_container_width=True)
    with s2:
        cy2=sd.groupby("Year")["CO2_Reduction_Tons"].sum().reset_index()
        f2=go.Figure(go.Scatter(x=cy2["Year"],y=cy2["CO2_Reduction_Tons"],
                                mode="lines+markers",
                                line=dict(color=GOLD2,width=3),
                                marker=dict(size=9,color=GOLD_L,line=dict(color=SURF,width=2)),
                                fill="tozeroy",fillcolor="rgba(200,149,58,0.08)"))
        T(f2,f"{chosen}: CO₂ Reduction Trend (Tonnes)",340)
        st.plotly_chart(f2, use_container_width=True)

    st.markdown('<div class="sec-title">🗺️ Geographic &amp; Risk Breakdown</div>', unsafe_allow_html=True)
    g1,g2 = st.columns(2)
    with g1:
        std_=sd.groupby("State")["Investment_Amount_USD"].sum().reset_index().sort_values("Investment_Amount_USD",ascending=False).head(12)
        f3=px.bar(std_,y="State",x="Investment_Amount_USD",orientation="h",
                  color="Investment_Amount_USD",color_continuous_scale=RED_SCALE,
                  text_auto=".2s")
        f3.update_traces(textposition="outside",textfont_color=TXT2)
        T(f3,f"{chosen}: Top States by Investment",380)
        st.plotly_chart(f3, use_container_width=True)
    with g2:
        rk=sd["Risk_Category"].value_counts().reset_index()
        rk.columns=["Risk","Count"]
        f4=px.pie(rk,values="Count",names="Risk",hole=0.58,
                  color="Risk",color_discrete_map=RISK_C)
        f4.update_traces(textinfo="label+percent",
                         marker=dict(line=dict(color=SURF,width=2)))
        T(f4,f"{chosen}: ESG Risk Distribution",380)
        st.plotly_chart(f4, use_container_width=True)

    # Radar
    st.markdown('<div class="sec-title">🕸️ All-Sector Comparison Radar</div>', unsafe_allow_html=True)
    rad=df.groupby("Sector").agg(ROI=("ROI_Percentage","mean"),ESG=("ESG_Score","mean"),
                                  CO2=("CO2_Reduction_Tons","mean"),
                                  Inv=("Investment_Amount_USD","mean")).reset_index()
    for c_ in ["ROI","ESG","CO2","Inv"]:
        mn,mx=rad[c_].min(),rad[c_].max()
        rad[c_+"_n"]=((rad[c_]-mn)/(mx-mn+1e-9))*100
    f5=go.Figure()
    cats=["ROI","ESG Score","CO₂ Impact","Investment","ROI"]
    for i,row in rad.iterrows():
        is_sel=row["Sector"]==chosen
        c_r=HDFC_RED if is_sel else PAL[i%len(PAL)]
        f5.add_trace(go.Scatterpolar(
            r=[row["ROI_n"],row["ESG_n"],row["CO2_n"],row["Inv_n"],row["ROI_n"]],
            theta=cats,name=row["Sector"],mode="lines+markers",
            line=dict(color=c_r,width=3 if is_sel else 1.5),
            marker=dict(size=7 if is_sel else 4,color=c_r),
            opacity=1.0 if is_sel else 0.45,
        ))
    f5.update_layout(
        polar=dict(bgcolor=SURF2,
                   radialaxis=dict(visible=True,gridcolor=GRID,
                                   tickfont=dict(color=MUT,size=9),
                                   color=MUT,range=[0,110]),
                   angularaxis=dict(gridcolor=GRID,
                                    tickfont=dict(color=TXT2,size=11),color=MUT)),
        paper_bgcolor=SURF,font=dict(color=TXT,family="Open Sans,sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=MUT,size=10)),
        title=dict(text=f"Sector Radar — Highlighted: {chosen}",
                   font=dict(family="Montserrat,sans-serif",color=TXT,size=12),x=0.02),
        margin=dict(l=30,r=30,t=50,b=30),height=460,
    )
    st.plotly_chart(f5, use_container_width=True)

    # Waterfall
    st.markdown('<div class="sec-title">🌊 Investment Waterfall — Year-over-Year Change</div>', unsafe_allow_html=True)
    wf=sd.groupby("Year")["Investment_Amount_USD"].sum().reset_index().sort_values("Year")
    wf["delta"]=wf["Investment_Amount_USD"].diff().fillna(wf["Investment_Amount_USD"])
    f6=go.Figure(go.Waterfall(
        x=wf["Year"].astype(str).tolist(),y=wf["delta"].tolist(),
        measure=["absolute"]+["relative"]*(len(wf)-1),
        connector=dict(line=dict(color=MUT,width=1.5)),
        increasing=dict(marker=dict(color=HDFC_RED, line=dict(color=HDFC_RED_L,width=1))),
        decreasing=dict(marker=dict(color=GOLD,     line=dict(color=GOLD2,width=1))),
        totals=dict(marker=dict(color=BLUE_L,       line=dict(color=BLUE_L,width=1))),
        textposition="outside",textfont=dict(color=TXT2,size=11),
        text=[f"${v/1e6:.1f}M" for v in wf["delta"]],
    ))
    T(f6,f"{chosen}: Investment Waterfall — YoY Change",360)
    st.plotly_chart(f6, use_container_width=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-top:30px;padding:16px 24px;
            background:linear-gradient(135deg,{SURF} 0%,{SURF2} 100%);
            border:1px solid rgba(210,47,47,.15);border-radius:8px;
            display:flex;justify-content:space-between;align-items:center;'>
  <div>
    <span style='font-family:Montserrat,sans-serif;font-weight:700;
                 font-size:.8rem;color:{HDFC_RED_L};'>HDFC Bank Ltd</span>
    <span style='color:{MUT};font-size:.75rem;'> &nbsp;·&nbsp; Green Finance Division
     &nbsp;·&nbsp; ESG Investment Tracker v5.0</span>
  </div>
  <div>
    <span style='font-size:.72rem;color:{MUT};font-family:Montserrat,sans-serif;'>
      Built with Streamlit &amp; Plotly &nbsp;·&nbsp;
      <span style='color:{GOLD};'>Confidential — Internal Use Only</span>
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
