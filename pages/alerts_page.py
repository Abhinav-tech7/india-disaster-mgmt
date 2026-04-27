"""
pages/alerts_page.py — Dynamic alerts with real email notification on Save.
"""

import streamlit as st
import random
from datetime import datetime, timedelta
from utils.data_engine import CITIES, STATE_RISK, get_active_alerts
from utils.charts import alert_donut

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False


# ── Helpers ────────────────────────────────────────────────────────────────────
def _time_ago(dt: datetime) -> str:
    secs = int((datetime.now() - dt).total_seconds())
    if secs < 60:    return f"{secs} sec{'s' if secs!=1 else ''} ago"
    elif secs < 3600: return f"{secs//60} min{'s' if secs//60!=1 else ''} ago"
    elif secs < 86400:return f"{secs//3600} hr{'s' if secs//3600!=1 else ''} ago"
    elif secs < 172800: return "1 day ago"
    else:            return f"{secs//86400} days ago"


def _abs_time(dt: datetime) -> str:
    return dt.strftime("%d %b %Y, %H:%M IST")


# ── Dynamic alert generator ────────────────────────────────────────────────────
def _generate_live_alerts() -> list:
    now      = datetime.now()
    day_seed = int(now.strftime("%Y%m%d"))
    rng      = random.Random(day_seed)

    all_templates = [
        {"type":"CRITICAL","icon":"🌀","disaster":"cyclone","state":"Odisha",
         "title":"Cyclone Alert — Bay of Bengal",
         "desc":(f"Category {rng.randint(2,4)} cyclone intensifying. "
                 f"Landfall on Odisha coast expected in {rng.randint(36,72)} hours. "
                 f"Wind speed {rng.randint(110,160)} km/h. "
                 f"Evacuation of {rng.randint(3,8)} coastal districts ordered."),
         "hours_ago":rng.uniform(0.3,2.5)},
        {"type":"CRITICAL","icon":"💧","disaster":"flood","state":"Assam",
         "title":"Severe Flood Warning — Assam",
         "desc":(f"Brahmaputra river at {rng.randint(91,99)}% of danger level. "
                 f"{rng.randint(5,14)} districts on Red Alert. "
                 f"{rng.randint(2,6)} NDRF teams deployed."),
         "hours_ago":rng.uniform(0.5,3)},
        {"type":"CRITICAL","icon":"🌧️","disaster":"rain","state":"Kerala",
         "title":"Extreme Rainfall Red Alert — Kerala",
         "desc":(f"IMD Red Alert for {rng.randint(6,11)} districts. "
                 f"Rainfall {rng.randint(190,280)}% of normal. "
                 f"Landslides reported in Idukki and Wayanad."),
         "hours_ago":rng.uniform(0.2,1.8)},
        {"type":"CRITICAL","icon":"💧","disaster":"flood","state":"Bihar",
         "title":"Flood Emergency — Bihar",
         "desc":(f"Kosi river breached embankment near Supaul. "
                 f"{rng.randint(4,9)} districts submerged. "
                 f"Army and NDRF teams conducting rescue operations."),
         "hours_ago":rng.uniform(1,4)},
        {"type":"CRITICAL","icon":"🌍","disaster":"quake","state":"Uttarakhand",
         "title":"Major Earthquake — Uttarakhand",
         "desc":(f"Magnitude {rng.uniform(5.5,6.4):.1f} earthquake near Chamoli. "
                 f"Depth {rng.randint(8,20)} km. "
                 f"Tremors felt in Dehradun, Haridwar, Rishikesh."),
         "hours_ago":rng.uniform(2,6)},
        {"type":"HIGH","icon":"🌧️","disaster":"rain","state":"Maharashtra",
         "title":"Excess Rainfall — Maharashtra",
         "desc":(f"Mumbai and Pune recording {rng.randint(155,210)}% of normal rainfall. "
                 f"Flash flood risk in low-lying areas. IMD Orange alert."),
         "hours_ago":rng.uniform(2,8)},
        {"type":"HIGH","icon":"💧","disaster":"flood","state":"West Bengal",
         "title":"Flood Watch — West Bengal",
         "desc":(f"Damodar river at {rng.randint(87,96)}% of danger mark. "
                 f"{rng.randint(2,6)} districts on alert. "
                 f"DVC releases {rng.randint(80,150)*1000:,} cusecs from Panchet dam."),
         "hours_ago":rng.uniform(4,12)},
        {"type":"HIGH","icon":"🌀","disaster":"cyclone","state":"Andhra Pradesh",
         "title":"Cyclone Watch — Andhra Coast",
         "desc":(f"Low pressure system intensifying. Wind speed {rng.randint(65,110)} km/h. "
                 f"Yellow alert for {rng.randint(3,7)} coastal districts."),
         "hours_ago":rng.uniform(5,14)},
        {"type":"HIGH","icon":"🌍","disaster":"quake","state":"Gujarat",
         "title":"Seismic Activity — Gujarat",
         "desc":(f"Magnitude {rng.uniform(3.8,5.1):.1f} earthquake near Bhuj. "
                 f"Depth {rng.randint(10,28)} km. No tsunami risk."),
         "hours_ago":rng.uniform(3,10)},
        {"type":"HIGH","icon":"🌧️","disaster":"rain","state":"Himachal Pradesh",
         "title":"Heavy Rain & Landslide — Himachal Pradesh",
         "desc":(f"Cloudbursts in Kullu, Mandi, Shimla. "
                 f"{rng.randint(2,8)} roads blocked due to landslides."),
         "hours_ago":rng.uniform(6,16)},
        {"type":"HIGH","icon":"💧","disaster":"flood","state":"Uttar Pradesh",
         "title":"Flood Alert — Uttar Pradesh",
         "desc":(f"Yamuna river rising near Prayagraj. "
                 f"Ganga at {rng.randint(85,94)}% of danger mark near Varanasi."),
         "hours_ago":rng.uniform(8,18)},
        {"type":"MODERATE","icon":"🌀","disaster":"cyclone","state":"Tamil Nadu",
         "title":"Low-Pressure System — Bay of Bengal",
         "desc":(f"Depression deepening. May intensify in {rng.randint(36,60)} hours. "
                 f"IMD monitoring. Fishermen alert issued."),
         "hours_ago":rng.uniform(10,22)},
        {"type":"MODERATE","icon":"☀️","disaster":"drought","state":"Rajasthan",
         "title":"Drought Watch — Rajasthan",
         "desc":(f"{rng.randint(8,15)} districts at {rng.randint(38,58)}% below normal rainfall. "
                 f"NDMA monitoring. Kharif crop stress developing."),
         "hours_ago":rng.uniform(18,32)},
        {"type":"MODERATE","icon":"💧","disaster":"flood","state":"Odisha",
         "title":"Flood Watch — Odisha Rivers",
         "desc":(f"Mahanadi river rising. Hirakud dam spillway gates opened. "
                 f"{rng.randint(2,5)} districts on Yellow alert."),
         "hours_ago":rng.uniform(16,30)},
        {"type":"LOW","icon":"🌊","disaster":"tsunami","state":"Andaman & Nicobar Islands",
         "title":"Tsunami Advisory — Andaman Sea",
         "desc":(f"Magnitude {rng.uniform(5.8,6.4):.1f} earthquake in Andaman Sea. "
                 f"INCOIS monitoring sea level gauges. No coastal threat."),
         "hours_ago":rng.uniform(28,48)},
        {"type":"LOW","icon":"🌍","disaster":"quake","state":"Assam",
         "title":"Minor Tremors — Assam",
         "desc":(f"Series of minor tremors M{rng.uniform(2.5,3.4):.1f} near Tezpur. "
                 f"No damage or injuries reported."),
         "hours_ago":rng.uniform(36,56)},
        {"type":"LOW","icon":"☀️","disaster":"drought","state":"Karnataka",
         "title":"Dry Spell Watch — North Karnataka",
         "desc":(f"Bidar and Kalaburagi showing {rng.randint(18,30)}% below normal rainfall. "
                 f"Karnataka SDMA issued precautionary advisory."),
         "hours_ago":rng.uniform(40,60)},
    ]

    count = min(12, len(all_templates))
    indices = list(range(len(all_templates)))
    rng.shuffle(indices)
    picked = [all_templates[i] for i in indices[:count]]
    picked.sort(key=lambda x: x["hours_ago"])

    alerts = []
    for t in picked:
        alert_dt = now - timedelta(hours=t["hours_ago"])
        alerts.append({
            "type":     t["type"],
            "icon":     t["icon"],
            "disaster": t["disaster"],
            "state":    t["state"],
            "title":    t["title"],
            "desc":     t["desc"],
            "datetime": alert_dt,
        })
    return alerts


# ── Send alert email for saved configuration ───────────────────────────────────
def _send_config_alert(email: str, phone: str, state: str, city: str,
                       threshold: str, freq: str, selected_disasters: list):
    """
    Called when user clicks Save Configuration.
    Sends a confirmation email immediately and sends current active alerts
    based on the configured state/city and threshold.
    """
    from utils.notifier import send_email_alert, send_sms_alert

    now    = datetime.now()
    alerts = get_active_alerts(state if state != "All States" else "Kerala",
                               city  if city  != "All Cities"  else "Kochi")

    # Filter by threshold
    thresh_map = {
        "All Alerts":            ["CRITICAL","HIGH","MODERATE","LOW"],
        "Moderate & Above":      ["CRITICAL","HIGH","MODERATE"],
        "High & Critical Only":  ["CRITICAL","HIGH"],
        "Critical Only":         ["CRITICAL"],
    }
    allowed = thresh_map.get(threshold, ["CRITICAL","HIGH"])
    alerts  = [a for a in alerts if a["type"] in allowed]

    results = []

    if email:
        # Build a custom result dict that matches notifier's return format
        # We send a "monitoring active" confirmation email
        mock_result = {
            "risk_level":        "HIGH" if alerts else "LOW",
            "risk_score":        75.0   if alerts else 25.0,
            "dev_pct":           0.0,
            "imd_category":      "Monitoring Active",
            "flood_threshold":   0,
            "drought_threshold": 0,
            "recommendations":   [
                f"🔔 Alert monitoring is now ACTIVE for {state}, {city}",
                f"📋 Threshold: {threshold}",
                f"🔄 Frequency: {freq}",
                f"⚠️ Disasters monitored: {', '.join(selected_disasters)}",
                f"📅 Configured at: {now.strftime('%d %b %Y, %H:%M IST')}",
            ] + [f"{a['icon']} {a['title']}: {a['desc']}" for a in alerts[:3]],
        }
        outcome = send_email_alert(email, mock_result,
                                   f"{city}, {state}" if city != "All Cities" else state,
                                   0, 0)
        results.append({"channel": "Email", **outcome})

    if phone:
        import re
        cleaned = re.sub(r"[\s\-\(\)\+]","", phone)
        if cleaned.startswith("91"): cleaned = cleaned[2:]
        if re.fullmatch(r"[6-9]\d{9}", cleaned):
            mock_result = {
                "risk_level": "HIGH" if alerts else "LOW",
                "risk_score": 75.0   if alerts else 25.0,
                "dev_pct":    0.0,
            }
            outcome = send_sms_alert(phone, mock_result,
                                     f"{city}, {state}" if city != "All Cities" else state)
            results.append({"channel": "SMS", **outcome})

    return results, alerts


# ── Main render ────────────────────────────────────────────────────────────────
def render():
    if _HAS_AUTOREFRESH:
        st.markdown("""<style>
        div[data-testid="stCustomComponentV1"],
        iframe[title="streamlit_autorefresh"] { display:none!important; height:0!important; }
        </style>""", unsafe_allow_html=True)
        st_autorefresh(interval=60_000, key="alerts_refresh", debounce=False)

    st.markdown('<h2 style="color:#f59e0b;font-weight:700;margin-bottom:0">🔔 Alerts & Notifications</h2>',
                unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e2d4a;margin-bottom:20px'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1])
    with left_col:
        _notification_config()
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        _alert_history()
    with right_col:
        _alert_stats()
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        _emergency_contacts()


# ── Notification Configuration ────────────────────────────────────────────────
def _notification_config():
    st.markdown('<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">⚙️ Notification Configuration</h5>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        state     = st.selectbox("🗺️ Monitor State",
                                 ["All States"] + sorted(CITIES.keys()), key="al_state")
        email     = st.text_input("📧 Alert Email", placeholder="your@email.com", key="al_email")
        threshold = st.selectbox("⚠️ Alert Threshold",
            ["All Alerts","Moderate & Above","High & Critical Only","Critical Only"],
            index=2, key="al_thresh")
    with c2:
        city_opts = (["All Cities"] +
                     (CITIES.get(state, []) if state != "All States" else []))
        city  = st.selectbox("🏙️ Monitor City", city_opts, key="al_city")
        phone = st.text_input("📱 Mobile (SMS)", placeholder="+91 98765 43210", key="al_phone")
        freq  = st.selectbox("🔄 Frequency",
            ["Real-time (Instant)","Every Hour","Every 6 Hours","Daily Digest"],
            index=2, key="al_freq")

    st.markdown("**📋 Disaster Types to Monitor**")
    options = [("🌧️ Rain","al_rain"),("🌍 Quake","al_quake"),
               ("☀️ Drought","al_drought"),("🌊 Tsunami","al_tsunami"),
               ("🌀 Cyclone","al_cyclone"),("💧 Flood","al_flood")]
    d_cols = st.columns(len(options))
    for i, (lbl, key) in enumerate(options):
        with d_cols[i]:
            st.checkbox(lbl, value=True, key=key)
    selected = [lbl for lbl, key in options if st.session_state.get(key, True)]

    # ── Setup instructions ──────────────────────────────────────────────────
    with st.expander("⚙️ How to set up Email & SMS — click to expand", expanded=False):
        st.markdown("""
**Email (Gmail):**
1. Go to [myaccount.google.com](https://myaccount.google.com) → **Security** → **2-Step Verification** → **App Passwords**
2. Create App Password → copy the 16-character code
3. Open **`.streamlit/secrets.toml`** in the project folder:
```toml
[email]
sender   = "yourgmail@gmail.com"
password = "xxxx xxxx xxxx xxxx"
```

**SMS (Fast2SMS — free, India only):**
1. Register at [fast2sms.com](https://fast2sms.com) → Dev API → copy key
2. Add to **`.streamlit/secrets.toml`**:
```toml
[sms]
fast2sms_key = "YOUR_API_KEY"
```
Then restart: `streamlit run app.py`
        """)

    save = st.button("💾 Save & Send Alert", key="al_save")
    if save:
        if not email and not phone:
            st.error("❌ Enter at least one contact — email address or mobile number.")
            return

        if email and "@" not in email:
            st.error("❌ Invalid email address.")
            return

        # Persist config in session_state so other parts can read it
        st.session_state["alert_config"] = {
            "email":     email,
            "phone":     phone,
            "state":     state,
            "city":      city,
            "threshold": threshold,
            "freq":      freq,
            "disasters": selected,
            "saved_at":  datetime.now(),
        }

        with st.spinner("Saving configuration and sending alert..."):
            outcomes, triggered_alerts = _send_config_alert(
                email, phone, state, city, threshold, freq, selected
            )

        # Show per-channel results
        all_ok = True
        for outcome in outcomes:
            ch = outcome["channel"]
            if outcome["ok"]:
                st.success(f"✅ **{ch} alert sent** to `{email if ch=='Email' else phone}`")
            else:
                all_ok = False
                st.warning(f"**{ch}:** {outcome['message']}")

        if not outcomes:
            st.info("ℹ️ Configuration saved. Add credentials in `.streamlit/secrets.toml` to enable real alerts.")
        elif all_ok:
            st.success(
                f"✅ **Configuration saved & alerts activated!**\n\n"
                f"Monitoring **{state}** · **{threshold}** alerts · Every **{freq}**\n\n"
                f"Active alerts found: **{len(triggered_alerts)}**"
            )

        # Log this as a sent alert in session history
        if "sent_alerts" not in st.session_state:
            st.session_state["sent_alerts"] = []
        st.session_state["sent_alerts"].insert(0, {
            "type":     "LOW",
            "icon":     "⚙️",
            "disaster": "none",
            "state":    state,
            "title":    f"Alert Configuration Saved — {state}",
            "desc":     (f"Monitoring activated for {', '.join(selected)}. "
                         f"Threshold: {threshold}. Frequency: {freq}. "
                         f"Contact: {email or ''} {phone or ''}"),
            "datetime": datetime.now(),
        })


# ── Alert History Log ─────────────────────────────────────────────────────────
def _alert_history():
    st.markdown('<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📨 Alert History Log</h5>',
                unsafe_allow_html=True)

    history = _generate_live_alerts()

    if "sent_alerts" in st.session_state and st.session_state["sent_alerts"]:
        history = st.session_state["sent_alerts"] + history

    type_cfg = {
        "CRITICAL": ("#f87171", "rgba(239,68,68,0.10)",  "rgba(239,68,68,0.25)"),
        "HIGH":     ("#fbbf24", "rgba(245,158,11,0.10)", "rgba(245,158,11,0.25)"),
        "MODERATE": ("#60a5fa", "rgba(59,130,246,0.10)", "rgba(59,130,246,0.25)"),
        "LOW":      ("#34d399", "rgba(16,185,129,0.10)", "rgba(16,185,129,0.25)"),
    }

    f1, f2, f3 = st.columns(3)
    with f1:
        sev_filter = st.selectbox("Filter by Severity",
                                  ["All","CRITICAL","HIGH","MODERATE","LOW"], key="hist_sev")
    with f2:
        search = st.text_input("Search", placeholder="State or title...", key="hist_search")
    with f3:
        dis_filter = st.selectbox("Filter by Disaster",
                                  ["All","rain","flood","cyclone","quake","drought","tsunami"],
                                  key="hist_disaster")

    filtered = [
        a for a in history
        if (sev_filter == "All"  or a["type"] == sev_filter)
        and (dis_filter == "All" or a.get("disaster","") == dis_filter)
        and (not search or search.lower() in a["title"].lower()
             or search.lower() in a.get("state","").lower())
    ]

    now_str = datetime.now().strftime("%d %b %Y, %H:%M:%S IST")
    hdr1, hdr2 = st.columns([3, 1])
    with hdr1:
        st.markdown(f"""<div style='font-size:11px;color:#475569;margin-bottom:8px;
                    font-family:monospace'>🕐 {now_str} · {len(filtered)} of {len(history)} alerts</div>""",
                    unsafe_allow_html=True)
    with hdr2:
        if st.button("🔄 Refresh", key="al_refresh", use_container_width=True):
            st.rerun()

    for a in filtered:
        col_text, bg, border = type_cfg.get(a["type"], type_cfg["LOW"])
        time_display = _time_ago(a["datetime"]) if "datetime" in a else "–"
        abs_display  = _abs_time(a["datetime"]) if "datetime" in a else ""

        st.markdown(f"""
        <div style='background:{bg};border:1px solid {border};
                    border-radius:10px;padding:12px 16px;margin-bottom:10px'>
          <div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:4px'>
            {a["icon"]} {a["title"]}
            <span style='font-size:10px;color:#64748b;font-weight:400;margin-left:8px'>
              📍 {a.get("state","")}
            </span>
          </div>
          <div style='font-size:11px;color:#94a3b8;line-height:1.6;margin-bottom:8px'>{a["desc"]}</div>
          <div style='display:flex;justify-content:space-between;align-items:center'>
            <div>
              <span style='font-size:11px;color:#60a5fa;font-family:monospace;
                           font-weight:600'>{time_display}</span>
              <span style='font-size:10px;color:#374151;font-family:monospace;
                           margin-left:10px'>{abs_display}</span>
            </div>
            <span style='font-size:9px;font-weight:700;background:{border};
                         color:{col_text};padding:3px 10px;border-radius:20px;
                         text-transform:uppercase;letter-spacing:0.5px'>{a["type"]}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    if not filtered:
        st.info("No alerts match the current filter.")


# ── Alert Statistics ──────────────────────────────────────────────────────────
def _alert_stats():
    st.markdown('<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">📊 Alert Statistics (Last 30 Days)</h5>',
                unsafe_allow_html=True)

    all_alerts = _generate_live_alerts()
    label_map  = {"rain":"Rainfall","flood":"Flood","cyclone":"Cyclone",
                  "quake":"Earthquake","drought":"Drought","tsunami":"Tsunami"}
    weight     = {"CRITICAL":5,"HIGH":3,"MODERATE":2,"LOW":1}
    counts     = {v:0 for v in label_map.values()}
    for a in all_alerts:
        k = label_map.get(a.get("disaster",""))
        if k: counts[k] += weight.get(a["type"],1)

    scale  = max(1, 30 / max(1, datetime.now().day))
    counts = {k: max(1, int(v * scale)) for k,v in counts.items()}

    st.plotly_chart(alert_donut(counts), use_container_width=True,
                    config={"displayModeBar": False})

    total    = sum(counts.values())
    critical = sum(1 for a in all_alerts if a["type"] == "CRITICAL")
    high     = sum(1 for a in all_alerts if a["type"] == "HIGH")
    today_s  = datetime.now().strftime("%d %b %Y")

    st.markdown(f"""
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px'>
      <div style='background:#111827;border:1px solid #1e2d4a;border-radius:8px;padding:10px;text-align:center'>
        <div style='font-size:20px;font-weight:700;color:#e2e8f0;font-family:monospace'>{total}</div>
        <div style='font-size:10px;color:#64748b'>Total (30 Days)</div>
      </div>
      <div style='background:#111827;border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:10px;text-align:center'>
        <div style='font-size:20px;font-weight:700;color:#f87171;font-family:monospace'>{critical}</div>
        <div style='font-size:10px;color:#64748b'>Critical Today</div>
      </div>
      <div style='background:#111827;border:1px solid rgba(245,158,11,0.3);border-radius:8px;padding:10px;text-align:center'>
        <div style='font-size:20px;font-weight:700;color:#fbbf24;font-family:monospace'>{high}</div>
        <div style='font-size:10px;color:#64748b'>High Today</div>
      </div>
      <div style='background:#111827;border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:10px;text-align:center'>
        <div style='font-size:13px;font-weight:700;color:#34d399;font-family:monospace'>{today_s}</div>
        <div style='font-size:10px;color:#64748b'>Last Updated</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ── Emergency Contacts ────────────────────────────────────────────────────────
def _emergency_contacts():
    st.markdown('<h5 style="color:#cbd5e1;font-weight:600;margin-bottom:8px">🏛️ Emergency Contacts</h5>',
                unsafe_allow_html=True)
    for icon, name, number, color in [
        ("🆘","NDRF Helpline",               "011-24363260",    "#f87171"),
        ("🌧️","IMD — Meteorological Dept",   "+91-11-24631913", "#fbbf24"),
        ("🌊","INCOIS Tsunami Warning",       "040-23895000",    "#22d3ee"),
        ("🌍","National Seismological Centre","011-24611680",    "#60a5fa"),
        ("💧","CWC Flood Forecasting Cell",   "011-26179285",    "#34d399"),
        ("📱","National Emergency Number",     "112",             "#34d399"),
    ]:
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #1e2d4a;border-radius:8px;
                    padding:10px 12px;margin-bottom:6px;display:flex;align-items:center;gap:10px'>
          <div style='font-size:18px'>{icon}</div>
          <div style='flex:1'>
            <div style='font-size:12px;font-weight:600;color:{color}'>{name}</div>
            <div style='font-size:12px;color:#64748b;font-family:monospace'>{number}</div>
          </div>
        </div>""", unsafe_allow_html=True)
