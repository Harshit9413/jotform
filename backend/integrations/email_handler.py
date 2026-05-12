from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List


def _html_table(data: Dict[str, Any]) -> str:
    rows = "".join(
        f"""<tr>
          <td style="padding:9px 14px;font-size:13px;font-weight:600;color:#374151;
                     background:#f8fafc;border-bottom:1px solid #e2e8f0;
                     white-space:nowrap;vertical-align:top">{k}</td>
          <td style="padding:9px 14px;font-size:13px;color:#0f172a;
                     border-bottom:1px solid #e2e8f0;vertical-align:top">{v}</td>
        </tr>"""
        for k, v in data.items()
        if not str(k).startswith("_") and v not in ("", None)
    )
    return f"""<table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;
                              border-radius:10px;overflow:hidden">{rows}</table>"""


def _admin_html(form_title: str, table_html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:24px;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
  <div style="max-width:580px;margin:0 auto">
    <div style="background:linear-gradient(135deg,#1a56db 0%,#6c63ff 100%);
                padding:28px 28px 24px;border-radius:16px 16px 0 0">
      <div style="font-size:28px;margin-bottom:10px">📥</div>
      <h1 style="color:#fff;font-size:20px;font-weight:800;margin:0 0 4px">
        New Form Submission</h1>
      <p style="color:rgba(255,255,255,.8);font-size:14px;margin:0">{form_title}</p>
    </div>
    <div style="background:#fff;padding:28px;border:1.5px solid #e2e8f0;
                border-top:none;border-radius:0 0 16px 16px">
      <p style="font-size:13px;color:#64748b;margin:0 0 18px">
        A new response has been submitted. Here are the details:</p>
      {table_html}
      <p style="font-size:11px;color:#94a3b8;margin:20px 0 0;text-align:center">
        Sent by FormCraft · Integration System</p>
    </div>
  </div>
</body>
</html>"""


def _confirm_html(form_title: str, table_html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:24px;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
  <div style="max-width:580px;margin:0 auto">
    <div style="background:linear-gradient(135deg,#059669 0%,#0891b2 100%);
                padding:28px 28px 24px;border-radius:16px 16px 0 0">
      <div style="font-size:32px;margin-bottom:10px">✅</div>
      <h1 style="color:#fff;font-size:20px;font-weight:800;margin:0 0 4px">
        Thank you for your submission!</h1>
      <p style="color:rgba(255,255,255,.8);font-size:14px;margin:0">{form_title}</p>
    </div>
    <div style="background:#fff;padding:28px;border:1.5px solid #e2e8f0;
                border-top:none;border-radius:0 0 16px 16px">
      <p style="font-size:14px;color:#374151;margin:0 0 18px;line-height:1.6">
        We have received your response and will get back to you as soon as possible.
        Here is a summary of what you submitted:</p>
      {table_html}
      <p style="font-size:11px;color:#94a3b8;margin:24px 0 0;text-align:center">
        Sent by FormCraft · You are receiving this because you submitted a form.</p>
    </div>
  </div>
</body>
</html>"""


def run_email(config: Dict[str, Any], form_data: Dict[str, Any], form_title: str) -> Dict[str, Any]:
    smtp_host   = config.get("smtp_host", "smtp.gmail.com").strip()
    smtp_port   = int(config.get("smtp_port", 587))
    from_email  = config.get("from_email", "").strip()
    password    = config.get("password", "").strip()
    admin_email = config.get("admin_email", "").strip()

    if not from_email or not password or not admin_email:
        raise ValueError("Email config incomplete — from_email, password, and admin_email are required.")

    table_html = _html_table(form_data)
    sent: List[str] = []

    try:
        smtp_conn = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
    except (OSError, TimeoutError) as exc:
        raise ValueError(
            f"Cannot connect to SMTP server {smtp_host}:{smtp_port}. "
            f"Check host/port. Detail: {exc}"
        ) from exc

    with smtp_conn as server:
        server.ehlo()
        try:
            server.starttls()
        except smtplib.SMTPException:
            pass
        try:
            server.login(from_email, password)
        except smtplib.SMTPAuthenticationError:
            raise ValueError(
                "SMTP login failed. For Gmail: generate a 16-character App Password at "
                "Google Account → Security → App Passwords. Do not use your regular password."
            )

        # ── Email 1: Admin notification ────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Submission — {form_title}"
        msg["From"]    = f"FormCraft <{from_email}>"
        msg["To"]      = admin_email
        msg.attach(MIMEText(_admin_html(form_title, table_html), "html"))
        server.sendmail(from_email, [admin_email], msg.as_string())
        sent.append("admin_notification")

        # ── Email 2: User confirmation (if email found in form data) ───────
        user_email = None
        for k, v in form_data.items():
            if "email" in str(k).lower() and "@" in str(v) and "." in str(v):
                user_email = str(v).strip()
                break

        if user_email and user_email != admin_email:
            msg2 = MIMEMultipart("alternative")
            msg2["Subject"] = f"Thank you for submitting — {form_title}"
            msg2["From"]    = f"FormCraft <{from_email}>"
            msg2["To"]      = user_email
            msg2.attach(MIMEText(_confirm_html(form_title, table_html), "html"))
            server.sendmail(from_email, [user_email], msg2.as_string())
            sent.append("user_confirmation")

    return {"emails_sent": sent}
