from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict


def run_google_sheets(config: Dict[str, Any], form_data: Dict[str, Any], form_title: str) -> Dict[str, Any]:
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "google-api-python-client is not installed. "
            "Run: pip install google-api-python-client google-auth"
        )

    spreadsheet_id = config.get("spreadsheet_id", "").strip()
    sheet_name     = config.get("sheet_name", "Sheet1").strip() or "Sheet1"
    sa_info        = config.get("service_account_json")

    if not spreadsheet_id:
        raise ValueError("spreadsheet_id is required")
    if not sa_info:
        raise ValueError("service_account_json is required")

    if isinstance(sa_info, str):
        sa_info = json.loads(sa_info)

    try:
        credentials = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
    except Exception as exc:
        raise ValueError(
            f"Invalid service account JSON: {exc}. "
            "Paste the full contents of your downloaded service-account.json file."
        ) from exc

    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    sheets  = service.spreadsheets()

    # ── Ensure sheet tab exists, create if missing ────────────────────────
    try:
        meta = sheets.get(spreadsheetId=spreadsheet_id, fields="sheets.properties.title").execute()
    except Exception as exc:
        err = str(exc)
        if "403" in err or "PERMISSION_DENIED" in err:
            sa_email = sa_info.get("client_email", "the service account email")
            raise ValueError(
                f"Permission denied. Open your Google Sheet → Share → add '{sa_email}' as Editor."
            ) from exc
        if "404" in err or "NOT_FOUND" in err:
            raise ValueError(
                f"Spreadsheet not found. Check that the Spreadsheet ID is correct "
                f"(the long string in the URL between /d/ and /edit)."
            ) from exc
        raise ValueError(f"Google Sheets API error: {exc}") from exc
    existing_tabs = [s["properties"]["title"] for s in meta.get("sheets", [])]
    if sheet_name not in existing_tabs:
        sheets.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]},
        ).execute()

    # ── Pull existing headers (row 1) ──────────────────────────────────────
    result          = sheets.values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!1:1",
    ).execute()
    existing_headers: list[str] = (result.get("values") or [[]])[0]

    # ── Build canonical column list from form data ─────────────────────────
    data_keys   = [k for k in form_data if not str(k).startswith("_")]
    want_headers = ["Submission ID", "Form Title", "Submitted At (UTC)"] + data_keys

    if not existing_headers:
        # Write header row
        sheets.values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1",
            valueInputOption="RAW",
            body={"values": [want_headers]},
        ).execute()
        col_order = want_headers
    else:
        col_order = existing_headers
        # Add any new columns that appeared in this submission
        missing = [h for h in want_headers if h not in col_order]
        if missing:
            col_order = col_order + missing
            sheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'!A1",
                valueInputOption="RAW",
                body={"values": [col_order]},
            ).execute()

    # ── Build data row aligned to col_order ───────────────────────────────
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    row = []
    for col in col_order:
        if col == "Submission ID":
            row.append("")          # filled by caller if needed
        elif col == "Form Title":
            row.append(form_title)
        elif col == "Submitted At (UTC)":
            row.append(now)
        else:
            val = form_data.get(col, "")
            if isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            row.append(str(val) if val is not None else "")

    sheets.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    return {"rows_added": 1, "sheet": sheet_name}
