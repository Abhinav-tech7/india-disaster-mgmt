"""
India Early Disaster Management System
Run: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="India Disaster Alert System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0e1a; }
[data-testid="stSidebar"]          { background: #0f1424; border-right: 1px solid #1e2d4a; }
.main .block-container             { padding-top: 1rem; max-width: 1400px; }

/* Hide deploy button and footer only — DO NOT touch header at all */

/* Hide Streamlit's auto-generated multi-page nav (the file picker in image 1) */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] > div > div > div > ul,
section[data-testid="stSidebar"] nav {
    display: none !important;
}

[data-testid="stDeployButton"]     { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
#MainMenu                          { display: none !important; }
footer                             { display: none !important; }

/* Make header transparent so it doesn't show as a bar */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0) !important;
    border-bottom: none !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #111827; border: 1px solid #1e2d4a;
    border-radius: 12px; padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 20px !important; }

/* Selects */
[data-testid="stSelectbox"] > div > div {
    background: #111827; border: 1px solid #2a3a5c;
    border-radius: 10px; color: #e2e8f0;
}
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"]   input {
    background: #111827 !important; border: 1px solid #2a3a5c !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}

/* Buttons — all primary buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    color: white !important; border: none; border-radius: 10px;
    font-weight: 600; padding: 10px 24px; width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    box-shadow: 0 4px 15px rgba(59,130,246,0.4);
    transform: translateY(-1px);
}
/* Refresh icon button — smaller, dark background, no gradient */
[data-testid="stButton"] button[kind="secondary"],
div[data-testid="column"]:last-child .stButton > button {
    background: #1c2539 !important;
    border: 1px solid #2a3a5c !important;
    color: #94a3b8 !important;
    font-size: 16px !important;
    padding: 8px !important;
    border-radius: 8px !important;
}
div[data-testid="column"]:last-child .stButton > button:hover {
    background: #2a3a5c !important;
    color: #e2e8f0 !important;
    border-color: #3b82f6 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Typography — bright colors matching the dark navy theme */
h1 { color: #60a5fa !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2 { color: #38bdf8 !important; font-weight: 700 !important; }
h3 { color: #7dd3fc !important; font-weight: 600 !important; }
h4 { color: #93c5fd !important; font-weight: 600 !important; }
h5 { color: #cbd5e1 !important; font-weight: 600 !important; }
h6 { color: #94a3b8 !important; font-weight: 600 !important; }
p, li  { color: #94a3b8; }
hr     { border-color: #1e2d4a; }

/* Streamlit specific heading elements */
[data-testid="stMarkdown"] h1 { color: #60a5fa !important; }
[data-testid="stMarkdown"] h2 { color: #38bdf8 !important; }
[data-testid="stMarkdown"] h3 { color: #7dd3fc !important; }
[data-testid="stMarkdown"] h4 { color: #93c5fd !important; }
[data-testid="stMarkdown"] h5 { color: #cbd5e1 !important; font-size: 15px !important; }
[data-testid="stMarkdown"] strong { color: #e2e8f0 !important; }

/* Alerts */
[data-testid="stInfo"]    { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.25); }
[data-testid="stWarning"] { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25); }
[data-testid="stError"]   { background:rgba(239,68,68,0.08);  border:1px solid rgba(239,68,68,0.25); }
[data-testid="stSuccess"] { background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    background: #0f1424; border-radius: 10px; padding: 4px; gap: 2px;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent; color: #64748b; border-radius: 8px; font-weight: 500;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #1c2539; color: #e2e8f0;
}
[data-testid="stRadio"] label       { color: #94a3b8 !important; }
[data-testid="stRadio"] label:hover { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

from pages import dashboard, forecast, calculator, alerts_page

with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;padding:8px 0 20px'>
      <div style='width:40px;height:40px;background:linear-gradient(135deg,#ef4444,#f59e0b);
                  border-radius:10px;display:flex;align-items:center;justify-content:center;
                  font-size:20px;flex-shrink:0'>🛡️</div>
      <div>
        <div style='font-size:13px;font-weight:700;color:#60a5fa;line-height:1.2'>INDIA DISASTER</div>
        <div style='font-size:13px;font-weight:700;color:#60a5fa;line-height:1.2'>ALERT SYSTEM</div>
        <div style='font-size:9px;color:#475569;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px'>Early Warning Platform</div>
      </div>
    </div>
    <hr style='border-color:#1e2d4a;margin-bottom:16px'>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "📊  Dashboard",
        "🔮  30-Day Forecast",
        "🧮  Rainfall Calculator",
        "🔔  Alerts & Notifications",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1e2d4a;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#475569;line-height:1.9'>
      <div style='color:#64748b;font-weight:600;margin-bottom:6px;font-size:10px;
                  text-transform:uppercase;letter-spacing:1px'>Data Sources</div>
      🌧️ IMD — Meteorological Dept<br>🌍 USGS — Seismic Data<br>
      🌊 INCOIS — Ocean / Tsunami<br>☀️ NOAA — Climate Indices<br>💧 CWC — Flood Forecasting
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2d4a;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#475569;line-height:1.9'>
      <div style='color:#64748b;font-weight:600;margin-bottom:6px;font-size:10px;
                  text-transform:uppercase;letter-spacing:1px'>ML Stack</div>
      🤖 LSTM Neural Network<br>🌲 Random Forest Ensemble<br>
      📈 ARIMA Seasonal Model<br>🔬 XGBoost Risk Classifier
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2d4a;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#475569'>
      <span style='color:#10b981;font-weight:700'>● SYSTEM ONLINE</span><br>v2.3 · Python + Streamlit
    </div>""", unsafe_allow_html=True)

if "Dashboard" in page:
    dashboard.render()
elif "Forecast" in page:
    forecast.render()
elif "Calculator" in page:
    calculator.render()
elif "Alerts" in page:
    alerts_page.render()

