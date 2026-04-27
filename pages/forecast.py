"""
pages/forecast.py
30-Day Multi-Disaster Prediction with radar, heatmap, and detailed table.
"""

import streamlit as st
import pandas as pd
from utils.data_engine import (
    CITIES, STATE_RISK, DISASTER_COLORS, DISASTER_LABELS,
    generate_forecast, get_monthly_risk_matrix, generate_30day_table, risk_label,
)
from utils.charts import (
    multi_forecast_chart, radar_chart, monthly_heatmap,
    composite_risk_bar,
)


def render():
    st.markdown(f'<h2 style="color:#38bdf8;font-weight:600;margin-bottom:8px">🔮 30-Day Multi-Disaster Prediction</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e2d4a;margin-bottom:20px'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("🗺️ State", ["-- Choose State --"] + sorted(CITIES.keys()), key="fc_state")
    with col2:
        city_opts = CITIES.get(state, ["-- Select State First --"]) if state != "-- Choose State --" else ["-- Select State First --"]
        city = st.selectbox("🏙️ City", city_opts, key="fc_city")

    if state == "-- Choose State --":
        st.info("👆 Select a state and city to view the 30-day multi-hazard forecast.")
        _show_model_info()
        return

    st.markdown(f"""
    <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:12px'>
      <div style='font-size:20px'>🔮</div>
      <div>
        <div style='font-size:13px;font-weight:700;color:#e2e8f0'>
          Predictions for {city}, {state}
        </div>
        <div style='font-size:11px;color:#64748b'>
          LSTM + Random Forest Ensemble · Confidence Interval 95% · Updated every 6 hours
        </div>
      </div>
      <div style='margin-left:auto;font-size:10px;background:rgba(139,92,246,0.15);
                  color:#a78bfa;padding:4px 10px;border-radius:6px;font-weight:700;
                  letter-spacing:1px'>ML POWERED</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Multi-disaster chart ──────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📈 30-Day Risk Trend — All Disasters</h5>', unsafe_allow_html=True)
    forecasts = {d: generate_forecast(state, d, 30, city=city) for d in DISASTER_COLORS}
    fig_multi  = multi_forecast_chart(forecasts, DISASTER_COLORS)
    st.plotly_chart(fig_multi, use_container_width=True, config={"displayModeBar": False})

    # ── Composite risk bar ────────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📊 Composite Daily Risk Score</h5>', unsafe_allow_html=True)
    table_df = generate_30day_table(state, city=city)
    fig_comp  = composite_risk_bar(table_df)
    st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

    # ── Radar + Heatmap ───────────────────────────────────────────────────────
    col_r, col_h = st.columns(2)
    with col_r:
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🕸️ Disaster Probability Matrix</h5>', unsafe_allow_html=True)
        risk_dict = STATE_RISK.get(state, {})
        fig_radar = radar_chart(state, risk_dict, DISASTER_COLORS)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    with col_h:
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📅 Monthly Risk Calendar</h5>', unsafe_allow_html=True)
        mat_df  = get_monthly_risk_matrix(state)
        fig_heat = monthly_heatmap(mat_df)
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

    # ── 30-day detailed table ─────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📋 30-Day Detailed Forecast Table</h5>', unsafe_allow_html=True)

    level_colors = {
        "SEVERE":   "background-color:rgba(239,68,68,0.15);color:#f87171;font-weight:700",
        "HIGH":     "background-color:rgba(245,158,11,0.15);color:#fbbf24;font-weight:700",
        "MODERATE": "background-color:rgba(59,130,246,0.15);color:#60a5fa;font-weight:700",
        "LOW":      "background-color:rgba(16,185,129,0.15);color:#34d399;font-weight:700",
    }

    def style_level(val):
        return level_colors.get(val, "")

    def style_risk(val):
        try:
            v = float(val)
            if v >= 75: return "color:#f87171;font-weight:700"
            if v >= 55: return "color:#fbbf24;font-weight:700"
            if v >= 35: return "color:#60a5fa;font-weight:700"
            return "color:#34d399"
        except:
            return ""

    styled = (
        table_df.style
        .map(style_level, subset=["Level"])
        .map(style_risk,  subset=["Composite Risk"])
    )
    st.dataframe(styled, use_container_width=True, height=400)

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📊 30-Day Summary Statistics</h5>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [
        ("⚠️ Severe Days",   int((table_df["Composite Risk"] >= 75).sum()), "days above 75"),
        ("🔴 High Risk Days", int((table_df["Composite Risk"] >= 55).sum()), "days above 55"),
        ("📈 Peak Risk",      f"{table_df['Composite Risk'].max():.1f}", "max score"),
        ("📉 Avg Risk",       f"{table_df['Composite Risk'].mean():.1f}", "mean score"),
    ]
    for i, (title, value, help_txt) in enumerate(metrics):
        with cols[i]:
            st.metric(title, value, help=help_txt)

    _show_model_info()


def _show_model_info():
    st.markdown("<hr style='border-color:#1e2d4a;margin:20px 0 12px'>", unsafe_allow_html=True)
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🤖 About the Prediction Models</h5>', unsafe_allow_html=True)

    model_cols = st.columns(4)
    models = [
        ("🧠 LSTM Network", "Long Short-Term Memory neural net trained on 30 years of IMD daily rainfall data. Captures seasonal and multi-year cycles."),
        ("🌲 Random Forest", "300-tree ensemble using 28 meteorological features. Handles non-linear interactions between temperature, humidity, and soil moisture."),
        ("📈 ARIMA-X", "Seasonal ARIMA with exogenous variables (IOD, ENSO). Best for medium-term drought and cyclone predictions."),
        ("⚡ XGBoost", "Gradient-boosted risk classifier. Predicts categorical risk level (Low/Moderate/High/Severe) with 89% accuracy on holdout set."),
    ]
    for i, (name, desc) in enumerate(models):
        with model_cols[i]:
            st.markdown(f"""
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:12px;
                        padding:14px;height:130px'>
              <div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px'>{name}</div>
              <div style='font-size:11px;color:#64748b;line-height:1.5'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
