"""
utils/notifier.py
Real email (Gmail SMTP) + SMS (Fast2SMS) alert dispatcher.

HOW IT WORKS FOR DEPLOYED APPS:
─────────────────────────────────────────────────────────────────────────────
YOU (the developer/deployer) set up ONE sender Gmail account once.
USERS just type their own email address in the input box to RECEIVE alerts.
Users never see or touch any credentials — exactly like any real website.

SETUP (one time, done by you before deploying):
─────────────────────────────────────────────────────────────────────────────
Option A — Local / Hackathon demo:
  Edit .streamlit/secrets.toml:
    [email]
    sender   = "yourgmail@gmail.com"
    password = "abcd efgh ijkl mnop"   ← 16-char App Password from Google

Option B — Streamlit Cloud (free hosting at share.streamlit.io):
  Go to your app → Settings → Secrets → paste:
    [email]
    sender   = "yourgmail@gmail.com"
    password = "abcd efgh ijkl mnop"
  No secrets.toml file needed — Streamlit Cloud stores it securely.

Option C — Render / Railway / Heroku:
  Set environment variables:
    EMAIL_SENDER   = yourgmail@gmail.com
    EMAIL_PASSWORD = abcd efgh ijkl mnop
    FAST2SMS_KEY   = your_key

HOW TO GET A GMAIL APP PASSWORD:
  1. myaccount.google.com → Security → 2-Step Verification → App Passwords
  2. Select "Mail" → Generate → copy the 16-character code
  3. This is NOT your Gmail password — it's a special code just for this app
─────────────────────────────────────────────────────────────────────────────
"""

import smtplib
import ssl
import urllib.request
import urllib.parse
import json
import re
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import streamlit as st


# ── credential reader — checks secrets.toml, then environment variables ────────
def _get_credential(section: str, key: str) -> str | None:
    """
    Read credentials in priority order:
    1. st.secrets (secrets.toml for local, Streamlit Cloud secrets panel)
    2. Environment variables (Render, Railway, Heroku, Docker)
    3. Return None if not configured anywhere
    """
    # Try st.secrets first (local secrets.toml or Streamlit Cloud secrets panel)
    try:
        val = st.secrets[section][key]
        if val and val not in ("yourgmail@gmail.com", "xxxx xxxx xxxx xxxx",
                               "YOUR_FAST2SMS_API_KEY_HERE", "abcd efgh ijkl mnop"):
            return val
    except Exception:
        pass

    # Try environment variables as fallback (for Render/Railway/Heroku/Docker)
    env_map = {
        ("email",  "sender"):       "EMAIL_SENDER",
        ("email",  "password"):     "EMAIL_PASSWORD",
        ("sms",    "fast2sms_key"): "FAST2SMS_KEY",
    }
    env_key = env_map.get((section, key))
    if env_key:
        val = os.environ.get(env_key)
        if val:
            return val

    return None


def _risk_emoji(level: str) -> str:
    return {"SEVERE": "🚨", "HIGH": "⚠️", "MODERATE": "🔶", "LOW": "✅"}.get(level, "ℹ️")


def _risk_color_hex(level: str) -> str:
    return {"SEVERE": "#ef4444", "HIGH": "#f59e0b",
            "MODERATE": "#3b82f6", "LOW": "#10b981"}.get(level, "#3b82f6")


# ── HTML email template ────────────────────────────────────────────────────────
def _build_html_email(result: dict, region: str, actual: float, normal: float) -> str:
    lbl   = result["risk_level"]
    score = result["risk_score"]
    dev   = result["dev_pct"]
    recs  = result["recommendations"]
    color = _risk_color_hex(lbl)
    emoji = _risk_emoji(lbl)
    dev_str  = f"{'+'if dev>=0 else ''}{dev:.1f}%"
    now_str  = datetime.now().strftime("%d %b %Y, %H:%M IST")
    rec_rows = "".join(
        f"<tr><td style='padding:6px 0;border-bottom:1px solid #1e2d4a;"
        f"color:#94a3b8;font-size:13px'>{r}</td></tr>"
        for r in recs
    )
    return f"""
<!DOCTYPE html><html>
<body style='margin:0;padding:0;background:#0a0e1a;font-family:Arial,sans-serif'>
<div style='max-width:600px;margin:0 auto;background:#111827;border-radius:12px;overflow:hidden'>
  <div style='background:linear-gradient(135deg,#1d4ed8,#0891b2);padding:28px 32px'>
    <div style='font-size:28px;margin-bottom:6px'>{emoji}</div>
    <div style='font-size:20px;font-weight:700;color:#fff'>{lbl} Rainfall Risk Alert</div>
    <div style='font-size:13px;color:#bfdbfe;margin-top:4px'>{region} · {now_str}</div>
  </div>
  <div style='background:{color};padding:16px 32px;display:flex;align-items:center;gap:16px'>
    <div style='font-size:42px;font-weight:800;color:#fff'>{score:.0f}</div>
    <div>
      <div style='font-size:11px;color:rgba(255,255,255,0.75);text-transform:uppercase'>Risk Score / 100</div>
      <div style='font-size:18px;font-weight:700;color:#fff'>{lbl}</div>
    </div>
  </div>
  <div style='padding:24px 32px'>
    <table style='width:100%;border-collapse:collapse'>
      <tr>
        <td style='padding:10px 0;border-bottom:1px solid #1e2d4a'>
          <div style='font-size:11px;color:#64748b;text-transform:uppercase'>Actual Rainfall</div>
          <div style='font-size:18px;font-weight:700;color:#e2e8f0'>{actual:.1f} mm</div>
        </td>
        <td style='padding:10px 0;border-bottom:1px solid #1e2d4a'>
          <div style='font-size:11px;color:#64748b;text-transform:uppercase'>Normal Rainfall</div>
          <div style='font-size:18px;font-weight:700;color:#e2e8f0'>{normal:.1f} mm</div>
        </td>
        <td style='padding:10px 0;border-bottom:1px solid #1e2d4a'>
          <div style='font-size:11px;color:#64748b;text-transform:uppercase'>Departure</div>
          <div style='font-size:18px;font-weight:700;color:{color}'>{dev_str}</div>
        </td>
        <td style='padding:10px 0;border-bottom:1px solid #1e2d4a'>
          <div style='font-size:11px;color:#64748b;text-transform:uppercase'>IMD Category</div>
          <div style='font-size:16px;font-weight:700;color:#e2e8f0'>{result["imd_category"]}</div>
        </td>
      </tr>
    </table>
    <div style='margin:16px 0;padding:12px 16px;background:#0f1424;border-radius:8px;
                border-left:3px solid {color}'>
      <div style='font-size:12px;color:#64748b'>
        Flood threshold: <b style='color:#f59e0b'>{result["flood_threshold"]:.1f} mm</b> &nbsp;|&nbsp;
        Drought threshold: <b style='color:#f97316'>{result["drought_threshold"]:.1f} mm</b>
      </div>
    </div>
    <div style='font-size:13px;font-weight:700;color:#e2e8f0;margin:20px 0 8px'>📋 Recommended Actions</div>
    <table style='width:100%;border-collapse:collapse'>{rec_rows}</table>
  </div>
  <div style='background:#0f1424;padding:16px 32px;font-size:11px;color:#475569;line-height:1.6'>
    🛡️ India Early Disaster Management System &nbsp;|&nbsp; Data: IMD · NDMA · INCOIS<br>
    This is an automated alert sent to you because you subscribed to disaster alerts.
  </div>
</div>
</body></html>"""


def _build_plain_text(result: dict, region: str, actual: float, normal: float) -> str:
    lbl = result["risk_level"]
    lines = [
        f"INDIA DISASTER ALERT — {_risk_emoji(lbl)} {lbl} RISK",
        f"Region : {region}",
        f"Time   : {datetime.now().strftime('%d %b %Y %H:%M IST')}",
        "",
        f"Risk Score      : {result['risk_score']:.0f}/100",
        f"Actual Rainfall : {actual:.1f} mm",
        f"Normal Rainfall : {normal:.1f} mm",
        f"Departure       : {'+' if result['dev_pct']>=0 else ''}{result['dev_pct']:.1f}%",
        f"IMD Category    : {result['imd_category']}",
        "",
        "RECOMMENDED ACTIONS:",
    ] + [f"  • {r}" for r in result["recommendations"]] + [
        "",
        "— India Early Disaster Management System",
        "  Unsubscribe by removing your email from the Alerts page.",
    ]
    return "\n".join(lines)


# ── not-configured message (shown to user in the UI) ─────────────────────────
_SETUP_GUIDE = """⚙️ **Email not configured by the app owner.**

**If you are the developer / deployer:**

**Option 1 — Local run:** Edit `.streamlit/secrets.toml`:
```toml
[email]
sender   = "yourgmail@gmail.com"
password = "abcd efgh ijkl mnop"
```
Get your App Password: [myaccount.google.com](https://myaccount.google.com) → Security → 2-Step Verification → App Passwords

**Option 2 — Streamlit Cloud:** Go to your app → ⚙️ Settings → **Secrets** → paste the same block above. No file needed.

**Option 3 — Render/Railway/Heroku:** Set environment variables:
- `EMAIL_SENDER` = yourgmail@gmail.com
- `EMAIL_PASSWORD` = abcd efgh ijkl mnop
"""


# ── Email sender ───────────────────────────────────────────────────────────────
def send_email_alert(to_email: str, result: dict, region: str,
                     actual: float, normal: float) -> dict:
    """
    Send alert email FROM the configured sender TO the user's email address.
    The user only provides their recipient email — no credentials needed from them.
    """
    sender   = _get_credential("email", "sender")
    password = _get_credential("email", "password")

    if not sender or not password:
        return {"ok": False, "message": _SETUP_GUIDE}

    lbl     = result["risk_level"]
    subject = f"{_risk_emoji(lbl)} {lbl} Rainfall Risk Alert — {region}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"India Disaster Alert System <{sender}>"
    msg["To"]      = to_email
    msg["Reply-To"]= sender

    msg.attach(MIMEText(_build_plain_text(result, region, actual, normal), "plain"))
    msg.attach(MIMEText(_build_html_email(result, region, actual, normal), "html"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return {"ok": True, "message": f"✅ Alert email sent to **{to_email}**"}
    except smtplib.SMTPAuthenticationError:
        return {"ok": False, "message": (
            "❌ **Gmail authentication failed.**\n\n"
            "Make sure you used an **App Password** (not your normal Gmail password).\n"
            "Get one at: myaccount.google.com → Security → App Passwords"
        )}
    except smtplib.SMTPRecipientsRefused:
        return {"ok": False, "message": f"❌ Invalid recipient email address: `{to_email}`"}
    except Exception as e:
        return {"ok": False, "message": f"❌ Email error: `{str(e)}`"}


# ── SMS sender (Fast2SMS — India) ─────────────────────────────────────────────
def send_sms_alert(phone: str, result: dict, region: str) -> dict:
    """
    Send SMS alert to the user's phone number.
    The user provides their phone — API key is configured by the developer.
    """
    api_key = _get_credential("sms", "fast2sms_key")

    if not api_key:
        return {"ok": False, "message": (
            "⚙️ **SMS not configured.** Add `fast2sms_key` to your secrets "
            "(see EMAIL setup guide above for where to add it)."
        )}

    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not re.fullmatch(r"[6-9]\d{9}", cleaned):
        return {"ok": False, "message": "❌ Invalid Indian mobile number (must be 10 digits, start with 6–9)."}

    lbl   = result["risk_level"]
    score = result["risk_score"]
    dev   = result["dev_pct"]
    msg   = (
        f"{_risk_emoji(lbl)} DISASTER ALERT | {lbl} RISK | "
        f"{region} | Score:{score:.0f}/100 | "
        f"Rainfall: {'+' if dev>=0 else ''}{dev:.1f}% from normal | "
        f"India Disaster Mgmt System"
    )[:160]

    payload = urllib.parse.urlencode({
        "authorization": api_key,
        "message":       msg,
        "language":      "english",
        "route":         "q",
        "numbers":       cleaned,
    }).encode()

    req = urllib.request.Request(
        "https://www.fast2sms.com/dev/bulkV2",
        data=payload, method="POST",
        headers={"cache-control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data.get("return"):
            return {"ok": True,  "message": f"✅ SMS sent to **{phone}**"}
        else:
            return {"ok": False, "message": f"❌ SMS failed: {data.get('message','Unknown error')}"}
    except Exception as e:
        return {"ok": False, "message": f"❌ SMS error: `{str(e)}`"}


# ── Combined dispatcher ────────────────────────────────────────────────────────
def dispatch_alert(email: str, phone: str, result: dict,
                   region: str, actual: float, normal: float) -> list:
    """
    Send to email and/or phone. Returns list of result dicts.
    Called from calculator.py and alerts_page.py.
    """
    results = []
    if email:
        results.append({"channel": "Email",
                        **send_email_alert(email, result, region, actual, normal)})
    if phone:
        results.append({"channel": "SMS",
                        **send_sms_alert(phone, result, region)})
    return results
