# 🛡️ India Early Disaster Management System
### Python · Streamlit · Pandas · NumPy · Plotly · Gmail SMTP · Fast2SMS

A full-stack AI-powered early disaster warning and prediction platform covering
**6 disaster types** across **all 36 States/UTs** and **770 districts** of India.

---

## 🚀 Quick Start

```bash
# 1. Extract the project and enter folder
cd india_disaster_mgmt

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure alerts (optional but recommended)
# Edit .streamlit/secrets.toml with your Gmail + Fast2SMS credentials

# 4. Run
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
india_disaster_mgmt/
│
├── app.py                     ← Entry point, navigation, global CSS
├── requirements.txt           ← All Python dependencies
│
├── .streamlit/
│   └── secrets.toml           ← Gmail + SMS credentials (fill in yours)
│
├── pages/
│   ├── dashboard.py           ← Live disaster dashboard with 6 disaster cards
│   ├── forecast.py            ← 30-day ML predictions, radar, heatmap, table
│   ├── calculator.py          ← Rainfall Risk Calculator with email/SMS alerts
│   └── alerts_page.py        ← Alert config, history log, emergency contacts
│
└── utils/
    ├── data_engine.py         ← All data, ML simulation, risk scoring (770 districts)
    ├── charts.py              ← All 8 Plotly chart builders
    └── notifier.py            ← Real Gmail SMTP + Fast2SMS dispatcher
```

---

## 🌟 Features

| Page | What It Does |
|------|-------------|
| 📊 **Dashboard** | Select any state + district → see live risk cards for all 6 disasters + 60-day historical chart + 30-day ML forecast + active alerts |
| 🔮 **30-Day Forecast** | Multi-disaster trend chart · Radar chart · Monthly heatmap · 30-day detailed table with composite risk score |
| 🧮 **Rainfall Calculator** | Enter actual + normal rainfall → instant IMD SPI risk score · gauge chart · action plan · real email + SMS alert |
| 🔔 **Alerts & Notifications** | Configure monitoring (state/city/threshold/frequency) → real email sent on save · live alert history log · emergency contacts |

---

## 🔔 Setting Up Real Alerts

### Email (Gmail):
1. Go to [myaccount.google.com](https://myaccount.google.com) → Security → 2-Step Verification → **App Passwords**
2. Create an App Password for "Mail" — copy the 16-char code
3. Open `.streamlit/secrets.toml` and fill in:
```toml
[email]
sender   = "yourgmail@gmail.com"
password = "abcd efgh ijkl mnop"
```

### SMS (Fast2SMS — free, India only):
1. Register free at [fast2sms.com](https://fast2sms.com) → Dev API → copy key
2. Add to `.streamlit/secrets.toml`:
```toml
[sms]
fast2sms_key = "YOUR_KEY_HERE"
```

Restart the app after editing secrets: `streamlit run app.py`

---

## 🤖 Tech Stack

| Library | Purpose |
|---------|---------|
| **Streamlit** | Web UI, navigation, widgets, session state |
| **Plotly** | 8 interactive charts (line, bar, radar, heatmap, gauge, donut) |
| **Pandas** | DataFrames for time-series data and forecast tables |
| **NumPy** | ML simulation, ARIMA-style generation, risk scoring |
| **smtplib** | Real Gmail SMTP email dispatch |
| **urllib** | Fast2SMS HTTP API for SMS |

---

## 📡 Data Sources (Research Basis)

| Source | Data Used |
|--------|-----------|
| **IMD** | Rainfall normals, SPI methodology, seasonal patterns, cyclone landfall records |
| **BIS IS:1893** | Seismic zone classification (Zone II–V) for earthquake risk |
| **NDMA** | National Flood Atlas — flood-prone district mapping |
| **INCOIS** | Tsunami hazard maps — coastal vulnerability scores |
| **NOAA/CWC** | River discharge patterns, drought indices |

Risk scores are calibrated to real published data — e.g., Odisha cyclone=80 from
98 recorded landfalls since 1891 (highest in India); Uttarakhand quake=80 from
Seismic Zone V classification near Main Himalayan Thrust fault.

---

## ⚠️ Disclaimer

This system uses statistically simulated data based on real IMD/USGS baseline risk
profiles. For operational deployment, replace simulation functions in `data_engine.py`
with live API calls to IMD, USGS, INCOIS, and CWC. The dashboard, charts, alert
logic, and notification system require no changes.
