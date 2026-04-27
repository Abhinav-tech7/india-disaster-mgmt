"""
pages/calculator.py
Rainfall Risk Calculator — real email (Gmail SMTP) + SMS (Fast2SMS) alerts.
"""

import streamlit as st
from utils.data_engine import calculate_rainfall_risk, risk_color
from utils.charts import rainfall_comparison_chart, risk_gauge
from utils.notifier import dispatch_alert


def render():
    st.markdown(f'<h2 style="color:#38bdf8;font-weight:600;margin-bottom:8px">🧮 Rainfall Risk Calculator</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e2d4a;margin-bottom:20px'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:13px;color:#64748b;margin-bottom:20px;line-height:1.6'>
      Enter actual and normal rainfall values to compute disaster risk using
      <b style='color:#94a3b8'>IMD deviation methodology</b> combined with a
      <b style='color:#94a3b8'>multi-factor ML risk score</b>.
      Real email and SMS alerts are dispatched when you click Send.
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ────────────────────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📥 Input Parameters</h5>', unsafe_allow_html=True)
    row1 = st.columns(3)
    with row1[0]:
        actual = st.number_input("🌧️ Actual Rainfall (mm)", min_value=0.0, value=0.0,
                                 step=1.0, format="%.1f", key="calc_actual")
    with row1[1]:
        normal = st.number_input("📊 Normal Rainfall (mm)", min_value=0.1, value=100.0,
                                 step=1.0, format="%.1f", key="calc_normal")
    with row1[2]:
        region = st.text_input("📍 Region / City", value="", placeholder="e.g. Mumbai",
                               key="calc_region")

    row2 = st.columns(3)
    with row2[0]:
        season = st.selectbox("🌾 Season", ["kharif","rabi","summer","annual"],
                              format_func=lambda x: {
                                  "kharif":"Kharif (Jun–Sep)", "rabi":"Rabi (Oct–Mar)",
                                  "summer":"Summer (Apr–May)", "annual":"Annual",
                              }[x], key="calc_season")
    with row2[1]:
        dry_days = st.number_input("☀️ Consecutive Dry Days", min_value=0, value=0,
                                   step=1, key="calc_dry")
    with row2[2]:
        soil_moisture = st.slider("🌱 Soil Moisture Index (%)", 0, 100, 50, key="calc_soil")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    calc_btn = st.button("⚡ Calculate Risk", use_container_width=False)

    if not (calc_btn or (actual > 0)):
        _show_imd_methodology()
        return

    # ── Calculate ─────────────────────────────────────────────────────────────
    result = calculate_rainfall_risk(actual, normal, dry_days, soil_moisture, season)
    lbl    = result["risk_level"]
    score  = result["risk_score"]
    dev    = result["dev_pct"]

    lbl_colors = {"SEVERE":"#f87171","HIGH":"#fbbf24","MODERATE":"#60a5fa","LOW":"#34d399"}
    lbl_bgs    = {"SEVERE":"rgba(239,68,68,0.15)","HIGH":"rgba(245,158,11,0.15)",
                  "MODERATE":"rgba(59,130,246,0.15)","LOW":"rgba(16,185,129,0.15)"}
    dev_color  = "#f87171" if dev > 20 else "#fbbf24" if dev < -20 else "#34d399"
    score_color= risk_color(score)

    st.markdown("<hr style='border-color:#1e2d4a;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📊 Risk Analysis Results</h5>', unsafe_allow_html=True)

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    for col, heading, value, vc in [
        (c1, "Departure from Normal",
         f"{'+'if dev>=0 else ''}{dev:.1f}%", dev_color),
        (c2, "Risk Score",
         f"{score:.0f}/100", score_color),
        (c3, "IMD Category",
         result["imd_category"], "#e2e8f0"),
        (c4, "Risk Level",
         f"<span style='background:{lbl_bgs.get(lbl)};padding:4px 12px;border-radius:8px'>{lbl}</span>",
         lbl_colors.get(lbl,"#64748b")),
    ]:
        with col:
            st.markdown(f"""
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:12px;
                        padding:16px;text-align:center;min-height:80px'>
              <div style='font-size:11px;color:#64748b;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:6px'>{heading}</div>
              <div style='font-size:22px;font-weight:700;color:{vc};
                          font-family:JetBrains Mono,monospace'>{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Charts
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📈 Rainfall Comparison</h5>', unsafe_allow_html=True)
        st.plotly_chart(
            rainfall_comparison_chart(actual, normal,
                                      result["flood_threshold"],
                                      result["drought_threshold"]),
            use_container_width=True, config={"displayModeBar": False})
    with c_right:
        st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🎯 Risk Gauge</h5>', unsafe_allow_html=True)
        st.plotly_chart(
            risk_gauge(score, f"Risk Score — {region or 'Location'}"),
            use_container_width=True, config={"displayModeBar": False})

    # Recommendations
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🚨 Recommendations & Actions</h5>', unsafe_allow_html=True)
    rec_color = lbl_colors.get(lbl, "#64748b")
    rec_bg    = lbl_bgs.get(lbl, "rgba(59,130,246,0.15)")
    recs_html = "".join(
        f"<div style='padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05)'>{r}</div>"
        for r in result["recommendations"]
    )
    st.markdown(f"""
    <div style='background:{rec_bg};border:1px solid {rec_color}40;
                border-radius:12px;padding:16px 20px;margin-bottom:16px'>
      <div style='font-size:13px;font-weight:700;color:{rec_color};margin-bottom:10px'>
        {lbl} Risk — Action Plan
      </div>
      <div style='font-size:12px;color:#94a3b8;line-height:1.8'>{recs_html}</div>
    </div>""", unsafe_allow_html=True)

    # ── Alert Section ─────────────────────────────────────────────────────────
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📤 Send Alert</h5>', unsafe_allow_html=True)

    # Setup instructions expander
    with st.expander("⚙️ How to configure Email & SMS — click to expand", expanded=False):
        st.markdown("""
**Email (Gmail):**
1. Go to [myaccount.google.com](https://myaccount.google.com) → **Security** → **2-Step Verification** → **App Passwords**
2. Create an App Password for "Mail"
3. Open the file **`.streamlit/secrets.toml`** inside the project folder and fill in:
```toml
[email]
sender   = "yourgmail@gmail.com"
password = "xxxx xxxx xxxx xxxx"
```

**SMS (Fast2SMS — free, India only):**
1. Register free at [fast2sms.com](https://fast2sms.com)
2. Go to **Dev API** and copy your API key
3. Add to **`.streamlit/secrets.toml`**:
```toml
[sms]
fast2sms_key = "YOUR_API_KEY"
```
4. Restart the app: `streamlit run app.py`
        """)

    e_col1, e_col2, e_col3 = st.columns([2, 2, 1])
    with e_col1:
        email = st.text_input("📧 Email Address",
                              placeholder="admin@ndma.gov.in", key="calc_email")
    with e_col2:
        phone = st.text_input("📱 Mobile Number (India)",
                              placeholder="+91 98765 43210", key="calc_phone")
    with e_col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        btn_label = "🚨 Send Emergency Alert" if score >= 55 else "📧 Send Alert"
        send = st.button(btn_label, use_container_width=True, key="calc_send")

    if send:
        # Validation
        if not email and not phone:
            st.error("❌ Please enter at least one contact — email address or mobile number.")
            return
        if email and "@" not in email:
            st.error("❌ Invalid email address format.")
            return
        if phone:
            import re
            cleaned = re.sub(r"[\s\-\(\)\+]","", phone)
            if cleaned.startswith("91"): cleaned = cleaned[2:]
            if not re.fullmatch(r"[6-9]\d{9}", cleaned):
                st.error("❌ Invalid Indian mobile number. Enter a 10-digit number starting with 6, 7, 8, or 9.")
                return

        # Dispatch
        with st.spinner("Sending alert..."):
            outcomes = dispatch_alert(
                email=email.strip() if email else "",
                phone=phone.strip() if phone else "",
                result=result,
                region=region or "India",
                actual=actual,
                normal=normal,
            )

        # Push to session_state so it appears in Alert History Log
        if "sent_alerts" not in st.session_state:
            st.session_state["sent_alerts"] = []
        from datetime import datetime
        lbl_icon = {"SEVERE":"🚨","HIGH":"⚠️","MODERATE":"🔶","LOW":"✅"}.get(result["risk_level"],"📧")
        st.session_state["sent_alerts"].insert(0, {
            "type":     result["risk_level"] if result["risk_level"] in ["CRITICAL","HIGH","MODERATE","LOW"] else "MODERATE",
            "icon":     lbl_icon,
            "disaster": "rain",
            "state":    region or "India",
            "title":    f"Rainfall Risk Alert — {region or 'India'}",
            "desc":     (f"Actual: {actual:.1f}mm | Normal: {normal:.1f}mm | "
                         f"Deviation: {'+' if result['dev_pct']>=0 else ''}{result['dev_pct']:.1f}% | "
                         f"Risk Score: {result['risk_score']:.0f}/100 | IMD: {result['imd_category']}"),
            "datetime": datetime.now(),
        })

        # Show results for each channel
        for outcome in outcomes:
            ch = outcome["channel"]
            if outcome["ok"]:
                st.success(f"**{ch}:** {outcome['message']}")
            else:
                # Show as warning (not error) so config instructions are readable
                st.warning(f"**{ch}:** {outcome['message']}")

    _show_imd_methodology()


def _show_imd_methodology():
    st.markdown("<hr style='border-color:#1e2d4a;margin:20px 0 12px'>", unsafe_allow_html=True)
    st.markdown(f'<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📐 IMD Risk Classification Methodology</h5>', unsafe_allow_html=True)
    cats = [
        ("✅","Normal",       "±19% of normal", "#34d399","rgba(16,185,129,0.1)","rgba(16,185,129,0.2)"),
        ("🟢","Above Normal", "+20% to +59%",   "#34d399","rgba(16,185,129,0.08)","rgba(16,185,129,0.15)"),
        ("⚡","Excess",       "> +60% above",   "#fbbf24","rgba(245,158,11,0.08)","rgba(245,158,11,0.15)"),
        ("🌵","Deficient",    "−20% to −59%",   "#f87171","rgba(239,68,68,0.08)","rgba(239,68,68,0.15)"),
        ("🆘","Large Deficit","> −60% below",   "#f87171","rgba(239,68,68,0.15)","rgba(239,68,68,0.3)"),
    ]
    cols = st.columns(5)
    for i,(icon,name,rng,col,bg,border) in enumerate(cats):
        with cols[i]:
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {border};border-radius:10px;
                        padding:14px;text-align:center'>
              <div style='font-size:20px;margin-bottom:6px'>{icon}</div>
              <div style='font-size:12px;font-weight:700;color:{col}'>{name}</div>
              <div style='font-size:11px;color:#64748b;margin-top:4px'>{rng}</div>
            </div>""", unsafe_allow_html=True)
