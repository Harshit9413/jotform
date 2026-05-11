# Telegram & Twilio SMS Integration — Design Spec

**Date:** 2026-05-11
**Project:** FormCraft (JotForm clone)
**Scope:** Add Telegram Bot and Twilio SMS as new integration types for form submission notifications

---

## Overview

Extend the existing integration system with two new types:

- **`telegram`** — sends a formatted notification to an admin Telegram chat/group when a form is submitted
- **`twilio_sms`** — sends an SMS to the admin on every submission, and to the user if a phone number is found in the form data

Both follow the existing pattern: new handler files, registered in `engine.py` and `router.py`, no new DB models required.

---

## Architecture

No structural changes to the database. `Integration` and `IntegrationLog` tables remain unchanged. The `type` field simply accepts two new values.

```
backend/integrations/
├── engine.py             ← add telegram + twilio_sms dispatch
├── router.py             ← add to ALLOWED_TYPES
├── telegram_handler.py   ← NEW
└── twilio_handler.py     ← NEW
```

**Data flow:**
```
Form Submit → trigger_all_integrations()
                ├── google_sheets  (existing)
                ├── email          (existing)
                ├── telegram       ← NEW: admin only
                └── twilio_sms     ← NEW: admin + user
```

---

## Telegram Integration

### Config
```json
{
  "bot_token": "123456:ABC-xyz...",
  "chat_id": "-1001234567890"
}
```

| Field | Description |
|-------|-------------|
| `bot_token` | From BotFather |
| `chat_id` | Admin personal chat ID or group/channel ID |

### Behavior
- Sends one message per submission to the configured `chat_id`
- Uses `requests.post()` to `https://api.telegram.org/bot{token}/sendMessage`
- `parse_mode="HTML"` (avoids MarkdownV2 escaping complexity)
- Timeout: 10 seconds
- Raises exception if Telegram returns `ok: false`

### Message Format
```
📋 <b>New Form Submission</b>
Form: Contact Us
Submitted At: 2026-05-11 10:30 UTC

• Name: Harshit Sharma
• Email: harshit@example.com
• Message: Hello there...
```

### Security
- `bot_token` is masked in API responses (shows last 2 chars only)

---

## Twilio SMS Integration

### Config
```json
{
  "account_sid": "ACxxxxxxx",
  "auth_token": "xxxxxxx",
  "from_number": "+15551234567",
  "admin_number": "+919876543210"
}
```

| Field | Description |
|-------|-------------|
| `account_sid` | Twilio account SID |
| `auth_token` | Twilio auth token |
| `from_number` | Twilio sender number |
| `admin_number` | Admin's phone number (always notified) |

### Behavior
- Admin SMS is always sent on every submission
- User SMS is sent if a phone number is auto-detected in form data
- Phone detection: checks keys containing `phone`, `mobile`, `contact`, `number` (case-insensitive); value must have 10+ digits
- Uses `twilio` Python SDK: `Client(account_sid, auth_token).messages.create()`

### Message Format — Admin
```
[FormCraft] New submission on "Contact Us"
Name: Harshit, Email: harshit@ex.com
View dashboard for full details.
```

### Message Format — User
```
[FormCraft] Thank you for submitting "Contact Us"!
We received your response and will get back to you soon.
```

### Security
- `auth_token` is masked in API responses (shows last 2 chars only)

---

## Changes to Existing Files

### `router.py`
```python
ALLOWED_TYPES = {"google_sheets", "email", "telegram", "twilio_sms"}
```

Add masking in `_mask_config()`:
- `telegram`: mask `bot_token`
- `twilio_sms`: mask `auth_token`

### `engine.py`
```python
from .telegram_handler import run_telegram
from .twilio_handler import run_twilio_sms

# in dispatch block:
elif itg.type == "telegram":
    run_telegram(itg.config, data, form_title)
elif itg.type == "twilio_sms":
    run_twilio_sms(itg.config, data, form_title)
```

### `requirements.txt`
Add:
```
twilio
```
(`requests` is already installed)

---

## Frontend

No changes required. The existing integration UI accepts any `type` string with a JSON config object — `telegram` and `twilio_sms` will work automatically.

---

## Out of Scope

- Telegram user notifications (requires user to `/start` the bot first — impractical via form)
- WhatsApp via Twilio (separate integration, future work)
- SMS templates / customization UI
