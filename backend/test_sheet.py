import gspread
from google.oauth2.service_account import Credentials
import sys
import os

SPREADSHEET_ID = "136UiZdhW8P7w9gA0tL0Jy9kFr1DWiD6HYzo_QN8eCFs"
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "service-account.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: service-account.json not found at: {SERVICE_ACCOUNT_FILE}")
        print("Please download your service account JSON key from Google Cloud Console")
        print("and place it at the above path.")
        sys.exit(1)

    print("Connecting to Google Sheets...")
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"ERROR: Failed to load credentials: {e}")
        print("\nFix: Make sure your service-account.json is a valid Google service account key file.")
        sys.exit(1)

    print("Opening spreadsheet...")
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet not found: {SPREADSHEET_ID}")
        print("\nFix: Share your Google Sheet with the service account email (Editor access).")
        print("Open the sheet → Share → paste the client_email from service-account.json")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not open spreadsheet: {e}")
        sys.exit(1)

    print("Appending row...")
    try:
        sheet.append_row(["Harshit", "Form Test"])
    except Exception as e:
        print(f"ERROR: Failed to append row: {e}")
        sys.exit(1)

    print("Data added successfully")

if __name__ == "__main__":
    main()
