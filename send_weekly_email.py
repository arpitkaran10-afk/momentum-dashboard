"""
send_weekly_email.py — Weekly MomentumIQ digest emailer
Reads data.json, builds an HTML email with top picks + dashboard link,
sends to every address listed in clients.txt via Gmail SMTP.

Required env vars (or set them directly below):
  GMAIL_USER      — your Gmail address
  GMAIL_APP_PASS  — 16-char Gmail App Password (not your login password)
                    Generate at: https://myaccount.google.com/apppasswords

Usage:
  python send_weekly_email.py
  python send_weekly_email.py --dry-run   # print email without sending
"""

import json, os, smtplib, argparse, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
GMAIL_USER     = os.getenv("GMAIL_USER", "")          # your Gmail address
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS", "")      # App Password

DASHBOARD_URL  = "https://arpitkaran10-afk.github.io/momentum-dashboard"
DATA_JSON      = Path(__file__).parent / "data.json"
CLIENTS_FILE   = Path(__file__).parent / "clients.txt"
TOP_N          = 5   # how many stocks/ETFs to feature in the email
# ─────────────────────────────────────────────────────────────────────────────


def load_data():
    with open(DATA_JSON) as f:
        return json.load(f)


def load_clients():
    clients = []
    for line in CLIENTS_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            clients.append(line)
    return clients


def pct(val):
    if val is None:
        return "—"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def grade_color(grade):
    return {"A": "#16a34a", "B": "#2563eb", "C": "#d97706", "D": "#dc2626"}.get(grade, "#6b7280")


def arrow(val):
    if val is None:
        return ""
    return "▲" if val >= 0 else "▼"


def build_rows(items, top_n):
    rows = ""
    for s in items[:top_n]:
        grade = s.get("grade", "—")
        color = grade_color(grade)
        ret1m = s.get("ret_1m")
        ret3m = s.get("ret_3m")
        score = s.get("score", s.get("momentum_score", "—"))
        score_str = f"{score:.1f}" if isinstance(score, (int, float)) else str(score)
        rows += f"""
        <tr>
          <td style="padding:10px 14px;font-weight:700;font-size:15px;">{s.get('rank','')}</td>
          <td style="padding:10px 14px;font-weight:700;font-size:15px;">{s.get('ticker','')}</td>
          <td style="padding:10px 14px;color:#374151;">{s.get('sector', s.get('category',''))}</td>
          <td style="padding:10px 14px;font-weight:600;">${s.get('price', 0):.2f}</td>
          <td style="padding:10px 14px;color:{'#16a34a' if ret1m and ret1m>=0 else '#dc2626'};">
            {arrow(ret1m)} {pct(ret1m)}
          </td>
          <td style="padding:10px 14px;color:{'#16a34a' if ret3m and ret3m>=0 else '#dc2626'};">
            {arrow(ret3m)} {pct(ret3m)}
          </td>
          <td style="padding:10px 14px;">
            <span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-weight:700;font-size:13px;">{grade}</span>
          </td>
          <td style="padding:10px 14px;font-weight:600;">{score_str}</td>
        </tr>"""
    return rows


def build_html(data):
    week       = data.get("week", "—")
    year       = data.get("year", "—")
    generated  = data.get("generated_at", "")[:10]
    avg_score  = data.get("avg_score", 0)
    pct_ma200  = data.get("pct_above_ma200", 0)
    total      = data.get("total_universe", 0)

    stocks = data.get("stocks", [])
    etfs   = data.get("etfs", [])

    stock_rows = build_rows(stocks, TOP_N)
    etf_rows   = build_rows(etfs, TOP_N)

    table_header = """
      <tr style="background:#1e293b;color:#fff;">
        <th style="padding:10px 14px;text-align:left;">#</th>
        <th style="padding:10px 14px;text-align:left;">Ticker</th>
        <th style="padding:10px 14px;text-align:left;">Sector</th>
        <th style="padding:10px 14px;text-align:left;">Price</th>
        <th style="padding:10px 14px;text-align:left;">1M Return</th>
        <th style="padding:10px 14px;text-align:left;">3M Return</th>
        <th style="padding:10px 14px;text-align:left;">Grade</th>
        <th style="padding:10px 14px;text-align:left;">Score</th>
      </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
  <tr><td align="center">
    <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08);">

      <!-- HEADER -->
      <tr>
        <td style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);padding:36px 40px;text-align:center;">
          <p style="margin:0 0 6px;color:#94a3b8;font-size:13px;letter-spacing:2px;text-transform:uppercase;">Weekly Digest</p>
          <h1 style="margin:0;color:#fff;font-size:28px;font-weight:800;">MomentumIQ</h1>
          <p style="margin:8px 0 0;color:#64748b;font-size:14px;">Week {week}, {year} &nbsp;·&nbsp; {generated}</p>
        </td>
      </tr>

      <!-- MARKET PULSE -->
      <tr>
        <td style="padding:28px 40px 0;">
          <h2 style="margin:0 0 16px;font-size:16px;color:#0f172a;text-transform:uppercase;letter-spacing:1px;">Market Pulse</h2>
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td width="33%" style="text-align:center;padding:16px;background:#f8fafc;border-radius:8px;">
                <p style="margin:0 0 4px;font-size:24px;font-weight:800;color:#1e293b;">{avg_score:.1f}</p>
                <p style="margin:0;font-size:12px;color:#64748b;text-transform:uppercase;">Avg Score</p>
              </td>
              <td width="4%"></td>
              <td width="33%" style="text-align:center;padding:16px;background:#f8fafc;border-radius:8px;">
                <p style="margin:0 0 4px;font-size:24px;font-weight:800;color:#1e293b;">{pct_ma200:.0f}%</p>
                <p style="margin:0;font-size:12px;color:#64748b;text-transform:uppercase;">Above MA200</p>
              </td>
              <td width="4%"></td>
              <td width="26%" style="text-align:center;padding:16px;background:#f8fafc;border-radius:8px;">
                <p style="margin:0 0 4px;font-size:24px;font-weight:800;color:#1e293b;">{total}</p>
                <p style="margin:0;font-size:12px;color:#64748b;text-transform:uppercase;">Tickers Scanned</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- TOP STOCKS -->
      <tr>
        <td style="padding:28px 40px 0;">
          <h2 style="margin:0 0 12px;font-size:16px;color:#0f172a;text-transform:uppercase;letter-spacing:1px;">Top {TOP_N} Momentum Stocks</h2>
          <div style="overflow-x:auto;">
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:13px;">
              {table_header}
              {stock_rows}
            </table>
          </div>
        </td>
      </tr>

      <!-- TOP ETFs -->
      <tr>
        <td style="padding:28px 40px 0;">
          <h2 style="margin:0 0 12px;font-size:16px;color:#0f172a;text-transform:uppercase;letter-spacing:1px;">Top {TOP_N} Momentum ETFs</h2>
          <div style="overflow-x:auto;">
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:13px;">
              {table_header}
              {etf_rows}
            </table>
          </div>
        </td>
      </tr>

      <!-- CTA -->
      <tr>
        <td style="padding:32px 40px;text-align:center;">
          <a href="{DASHBOARD_URL}" style="display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:14px 36px;border-radius:8px;font-weight:700;font-size:15px;letter-spacing:.3px;">
            Open Full Dashboard →
          </a>
          <p style="margin:16px 0 0;font-size:12px;color:#94a3b8;">
            Showing top {TOP_N} of 50 — see all rankings, heatmap, and historical tracker at the dashboard.
          </p>
        </td>
      </tr>

      <!-- FOOTER -->
      <tr>
        <td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
          <p style="margin:0;font-size:12px;color:#94a3b8;">
            MomentumIQ · Updated every Sunday · Not financial advice
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def send_email(recipients, subject, html_body, dry_run=False):
    if dry_run:
        log.info("=== DRY RUN — email NOT sent ===")
        log.info(f"To: {', '.join(recipients)}")
        log.info(f"Subject: {subject}")
        log.info("HTML body written to: /tmp/momentum_email_preview.html")
        with open("/tmp/momentum_email_preview.html", "w") as f:
            f.write(html_body)
        return

    if not GMAIL_USER or not GMAIL_APP_PASS:
        raise ValueError(
            "GMAIL_USER and GMAIL_APP_PASS env vars must be set. "
            "Generate an App Password at https://myaccount.google.com/apppasswords"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"MomentumIQ <{GMAIL_USER}>"
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())

    log.info(f"✅ Email sent to {len(recipients)} recipient(s): {', '.join(recipients)}")


def main():
    parser = argparse.ArgumentParser(description="Send weekly MomentumIQ digest")
    parser.add_argument("--dry-run", action="store_true", help="Preview email without sending")
    args = parser.parse_args()

    data       = load_data()
    clients    = load_clients()
    week       = data.get("week", "—")
    year       = data.get("year", "—")
    subject    = f"MomentumIQ Weekly Digest — Week {week}, {year}"
    html_body  = build_html(data)

    if not clients:
        log.warning("No recipients found in clients.txt — add email addresses and re-run.")
        return

    log.info(f"Sending to {len(clients)} recipient(s): {', '.join(clients)}")
    send_email(clients, subject, html_body, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
