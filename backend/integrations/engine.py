from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

from formcraft.database import SessionLocal
from .models import Integration, IntegrationLog
from .google_sheets import run_google_sheets
from .email_handler import run_email
from .telegram_handler import run_telegram
from .twilio_handler import run_twilio_sms


def trigger_all_integrations(
    submission_id: int,
    form_id: str,
    form_title: str,
    data: Dict[str, Any],
) -> None:
    """
    Called as a FastAPI background task after every submission.
    Opens its own DB session so it never blocks the HTTP response.
    Each integration runs independently — one failure never stops the others.
    """
    db = SessionLocal()
    try:
        integrations = (
            db.query(Integration)
            .filter(Integration.form_id == form_id, Integration.is_active.is_(True))
            .all()
        )

        for itg in integrations:
            status        = "success"
            error_message = None
            try:
                if itg.type == "google_sheets":
                    run_google_sheets(itg.config, data, form_title)
                elif itg.type == "email":
                    run_email(itg.config, data, form_title)
                elif itg.type == "telegram":
                    run_telegram(itg.config, data, form_title)
                elif itg.type == "twilio_sms":
                    run_twilio_sms(itg.config, data, form_title)
                else:
                    raise ValueError(f"Unknown integration type: {itg.type}")
            except Exception as exc:
                status        = "failed"
                error_message = str(exc)[:800]

            log = IntegrationLog(
                integration_id=itg.id,
                submission_id=submission_id,
                status=status,
                error_message=error_message,
                triggered_at=datetime.now(timezone.utc),
            )
            db.add(log)

        db.commit()
    except Exception:
        pass   # never crash the background worker
    finally:
        db.close()
