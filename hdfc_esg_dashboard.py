"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  HDFC Bank: Green Finance & ESG Investment Tracker  v5.0                     ║
║  RUN:  pip install streamlit plotly pandas numpy requests                     ║
║        streamlit run hdfc_esg_dashboard.py                                    ║
║  CSV files must be in the SAME folder as this script                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import datetime, warnings, requests
from pathlib import Path
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
