import os
import json
import urllib.request
import urllib.error

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")


def send_submission_notification(to_email: str, form_title: str, data: dict, sub_id: int) -> None:
    if not RESEND_API_KEY:
        return

    rows_html = "".join(
        f"""<tr>
          <td style="padding:8px 0;font-size:13px;color:#64748b;font-weight:500;vertical-align:top;border-bottom:1px solid #f1f5f9;padding-right:16px">{k}</td>
          <td style="padding:8px 0;font-size:13px;color:#0f172a;font-weight:600;vertical-align:top;border-bottom:1px solid #f1f5f9">{v}</td>
        </tr>"""
        for k, v in data.items()
        if not str(k).startswith("_")
    )

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:20px;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
  <div style="max-width:520px;margin:0 auto">
    <div style="background:linear-gradient(135deg,#1a56db 0%,#6c63ff 100%);padding:28px 28px 24px;border-radius:16px 16px 0 0">
      <div style="font-size:28px;margin-bottom:8px">📥</div>
      <h1 style="color:#fff;font-size:20px;font-weight:800;margin:0 0 4px">New Submission!</h1>
      <p style="color:rgba(255,255,255,.8);font-size:14px;margin:0">{form_title}</p>
    </div>
    <div style="background:#fff;padding:28px;border:1.5px solid #e2e8f0;border-top:none;border-radius:0 0 16px 16px;box-shadow:0 4px 16px rgba(15,23,42,.08)">
      <table style="width:100%;border-collapse:collapse">
        {rows_html}
      </table>
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:12px;color:#94a3b8">Submission #{sub_id}</span>
        <span style="font-size:12px;color:#94a3b8">FormCraft</span>
      </div>
    </div>
  </div>
</body>
</html>"""

    payload = json.dumps({
        "from": f"FormCraft <{FROM_EMAIL}>",
        "to": [to_email],
        "subject": f"New submission on \"{form_title}\"",
        "html": html,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass  # never fail a submission because of email
