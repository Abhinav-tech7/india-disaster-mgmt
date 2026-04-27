"""
pages/dashboard.py
Main dashboard: state/city selector, 6 disaster overview cards, charts, alerts.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False
from utils.data_engine import (
    CITIES, STATE_RISK, DISASTER_COLORS, DISASTER_LABELS,
    generate_historical, generate_forecast,
    get_risk_score, risk_label, risk_color, get_display_value, get_active_alerts,
)
from utils.charts import historical_forecast_chart


def render():
    # Hide the autorefresh widget — it renders a visible box otherwise
    st.markdown("""<style>
    div[data-testid="stCustomComponentV1"],
    iframe[title="streamlit_autorefresh"] { display:none!important; height:0!important; }
    </style>""", unsafe_allow_html=True)
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=300_000, key="dashboard_refresh", debounce=False)

    st.markdown(f'<h2 style="color:#38bdf8;font-weight:600;margin-bottom:8px">📊 Disaster Dashboard</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e2d4a;margin-bottom:20px'>", unsafe_allow_html=True)

    # ── Location selectors ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([1.4, 1.4, 0.7, 0.4])
    with col1:
        state = st.selectbox("🗺️ Select State", ["-- Choose State --"] + sorted(CITIES.keys()), key="db_state")
    with col2:
        city_options = ["-- Select State First --"]
        if state != "-- Choose State --":
            city_options = CITIES[state]
        city = st.selectbox("🏙️ Select City / District", city_options, key="db_city")
    with col3:
        # Spacer to align button with dropdowns
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        analyze = st.button("🔍 Analyze Region", use_container_width=True)
    with col4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        # Styled dark refresh button — override white default with inline CSS wrapper
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-child(4) .stButton > button {
            background: #1c2539 !important;
            border: 1px solid #2a3a5c !important;
            color: #94a3b8 !important;
            font-size: 18px !important;
            padding: 6px 8px !important;
            border-radius: 8px !important;
            font-weight: 400 !important;
            box-shadow: none !important;
        }
        div[data-testid="column"]:nth-child(4) .stButton > button:hover {
            background: #2a3a5c !important;
            border-color: #3b82f6 !important;
            color: #e2e8f0 !important;
            transform: none !important;
            box-shadow: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🔄", use_container_width=True, key="db_refresh", help="Refresh data"):
            st.rerun()

    # Live timestamp shown below selectors
    now_str = datetime.now().strftime("%d %b %Y  %H:%M IST")
    st.markdown(f"<div style='font-size:11px;color:#475569;font-family:monospace;margin:-8px 0 4px'>🕐 Last updated: {now_str}</div>", unsafe_allow_html=True)

    # ── Overview cards ────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    valid = state != "-- Choose State --" and city not in ("-- Select State First --", "-- Choose State --")

    risk_data = STATE_RISK.get(state, {}) if valid else {}

    disasters   = ["rain", "quake", "drought", "tsunami", "cyclone", "flood"]
    icons       = {"rain":"🌧️","quake":"🌍","drought":"☀️","tsunami":"🌊","cyclone":"🌀","flood":"💧"}
    short_names = {"rain":"Rainfall","quake":"Earthquake","drought":"Drought",
                   "tsunami":"Tsunami","cyclone":"Cyclone","flood":"Flood"}

    cols = st.columns(6)
    for i, d in enumerate(disasters):
        score = risk_data.get(d, 0) if valid else 0
        lbl   = risk_label(score) if valid else "–"
        val   = get_display_value(state, d, city=city) if valid else "–"
        col_hex = DISASTER_COLORS[d]
        lbl_colors = {"SEVERE":"#f87171","HIGH":"#fbbf24","MODERATE":"#60a5fa","LOW":"#34d399"}
        lc = lbl_colors.get(lbl, "#64748b")

        with cols[i]:
            st.markdown(f"""
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:12px;
                        padding:14px 12px;border-top:3px solid {col_hex};text-align:center;
                        min-height:110px'>
              <div style='font-size:20px'>{icons[d]}</div>
              <div style='font-size:10px;color:#64748b;text-transform:uppercase;
                          letter-spacing:1px;font-weight:600;margin:4px 0 2px'>{short_names[d]}</div>
              <div style='font-size:17px;font-weight:700;color:#e2e8f0;margin:2px 0'>{val}</div>
              <div style='font-size:10px;font-weight:700;color:{lc};
                          background:{"rgba(239,68,68,0.15)" if lbl=="SEVERE" else
                                       "rgba(245,158,11,0.15)" if lbl=="HIGH" else
                                       "rgba(59,130,246,0.15)" if lbl=="MODERATE" else
                                       "rgba(16,185,129,0.15)"};
                          padding:2px 8px;border-radius:20px;display:inline-block;margin-top:4px'>
                {lbl}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Main content: chart + right panel ─────────────────────────────────────
    if not valid:
        st.info("👆 Select a State and City above, then click **Analyze Region** to load disaster data.")
        return

    # ── Disaster selector tabs ────────────────────────────────────────────────
    tab_labels = [f"{icons[d]} {short_names[d]}" for d in disasters]
    tabs = st.tabs(tab_labels)

    for i, d in enumerate(disasters):
        with tabs[i]:
            _render_disaster_tab(state, city, d, DISASTER_COLORS[d])


def _render_disaster_tab(state, city, disaster, color):
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Main historical + forecast chart
        hist = generate_historical(state, disaster, days=60, city=city)
        pred = generate_forecast(state, disaster, days=30, city=city)
        icons = {"rain":"🌧️","quake":"🌍","drought":"☀️","tsunami":"🌊","cyclone":"🌀","flood":"💧"}
        short = {"rain":"Rainfall","quake":"Earthquake","drought":"Drought",
                 "tsunami":"Tsunami","cyclone":"Cyclone","flood":"Flood"}

        fig = historical_forecast_chart(
            hist, pred, disaster, color,
            title=f"{icons[disaster]} {short[disaster]} — {city}, {state}"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # 30-day forecast strip as a small table
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🗓️ 30-Day Forecast Strip</h5>', unsafe_allow_html=True)
        strip_df = pred[["date", "value", "ci_lower", "ci_upper"]].copy()
        strip_df["date"]  = strip_df["date"].dt.strftime("%d %b")
        strip_df.columns  = ["Date", "Predicted", "CI Lower", "CI Upper"]
        strip_df = strip_df.set_index("Date")

        # colour the risk level column
        score_col = []
        for v in strip_df["Predicted"]:
            max_v = max(strip_df["Predicted"])
            pct   = (v / max_v * 100) if max_v > 0 else 0
            score_col.append(risk_label(pct))
        strip_df["Risk"] = score_col

        st.dataframe(
            strip_df.style.map(
                lambda v: (
                    "color:#f87171;font-weight:600" if v == "SEVERE" else
                    "color:#fbbf24;font-weight:600" if v == "HIGH"   else
                    "color:#60a5fa;font-weight:600" if v == "MODERATE" else
                    "color:#34d399;font-weight:600"
                ),
                subset=["Risk"],
            ),
            height=220,
            use_container_width=True,
        )

    with col_right:
        # Risk score card
        score = get_risk_score(state, disaster)
        lbl   = risk_label(score)
        col_hex = color
        lbl_colors = {"SEVERE":"#f87171","HIGH":"#fbbf24","MODERATE":"#60a5fa","LOW":"#34d399"}

        st.markdown(f"""
        <div style='background:#111827;border:1px solid #1e2d4a;border-radius:14px;
                    padding:20px;margin-bottom:12px;text-align:center'>
          <div style='font-size:11px;color:#64748b;text-transform:uppercase;
                      letter-spacing:1.5px;font-weight:600;margin-bottom:8px'>Current Risk Score</div>
          <div style='font-size:52px;font-weight:800;color:{col_hex};
                      font-family:JetBrains Mono,monospace'>{score:.0f}</div>
          <div style='font-size:11px;color:#475569;margin-bottom:10px'>out of 100</div>
          <div style='font-size:13px;font-weight:700;color:{lbl_colors.get(lbl,"#64748b")};
                      background:{"rgba(239,68,68,0.15)" if lbl=="SEVERE" else
                                   "rgba(245,158,11,0.15)" if lbl=="HIGH" else
                                   "rgba(59,130,246,0.15)" if lbl=="MODERATE" else
                                   "rgba(16,185,129,0.15)"};
                      padding:5px 16px;border-radius:20px;display:inline-block'>{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

        # Active alerts
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🔔 Active Alerts</h5>', unsafe_allow_html=True)
        alerts = get_active_alerts(state, city)
        relevant = [a for a in alerts if a["disaster"] == disaster or a["disaster"] == "none"]
        if not relevant:
            relevant = alerts[:2]

        type_styles = {
            "CRITICAL": ("#ef4444", "rgba(239,68,68,0.08)", "rgba(239,68,68,0.2)"),
            "HIGH":     ("#f59e0b", "rgba(245,158,11,0.08)", "rgba(245,158,11,0.2)"),
            "MODERATE": ("#3b82f6", "rgba(59,130,246,0.08)",  "rgba(59,130,246,0.2)"),
            "LOW":      ("#10b981", "rgba(16,185,129,0.08)",  "rgba(16,185,129,0.2)"),
        }
        sev_colors = {"CRITICAL":"#f87171","HIGH":"#fbbf24","MODERATE":"#60a5fa","LOW":"#34d399"}
        sev_bgs    = {"CRITICAL":"rgba(239,68,68,0.2)","HIGH":"rgba(245,158,11,0.2)",
                      "MODERATE":"rgba(59,130,246,0.2)","LOW":"rgba(16,185,129,0.2)"}

        for a in relevant[:4]:
            dot_c, bg_c, border_c = type_styles.get(a["type"], type_styles["LOW"])
            st.markdown(f"""
            <div style='background:{bg_c};border:1px solid {border_c};border-radius:10px;
                        padding:10px 12px;margin-bottom:8px'>
              <div style='font-size:12px;font-weight:700;color:#e2e8f0;margin-bottom:3px'>
                {a["icon"]} {a["title"]}
              </div>
              <div style='font-size:11px;color:#94a3b8;margin-bottom:6px'>{a["desc"]}</div>
              <div style='display:flex;justify-content:space-between;align-items:center'>
                <span style='font-size:10px;color:#64748b;font-family:monospace'>{a["time"]}</span>
                <span style='font-size:9px;font-weight:700;
                             background:{sev_bgs.get(a["type"],"rgba(59,130,246,0.2)")};
                             color:{sev_colors.get(a["type"],"#60a5fa")};
                             padding:2px 7px;border-radius:20px;text-transform:uppercase'>
                  {a["type"]}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)
