#!/usr/bin/env python3
"""Download Rapid Electronics invoice PDFs from Gmail."""

import base64
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = Path.home() / ".config/gcloud/gmail-token.json"
OUT_DIR = Path(__file__).parent / "rapid_invoices"

QUERY = "from:accounts@rapidelec.co.uk has:attachment"


def get_credentials():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def download_attachments(service, msg_id, out_dir):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    subject = headers.get("Subject", "unknown")

    def process_parts(parts):
        for part in parts:
            filename = part.get("filename", "")
            if filename.endswith(".pdf"):
                att_id = part["body"].get("attachmentId")
                if att_id:
                    att = service.users().messages().attachments().get(
                        userId="me", messageId=msg_id, id=att_id
                    ).execute()
                    data = base64.urlsafe_b64decode(att["data"])
                    out_path = out_dir / filename
                    out_path.write_bytes(data)
                    print(f"  Saved: {filename}  ({len(data)//1024} KB)")
            if part.get("parts"):
                process_parts(part["parts"])

    print(f"\n{subject}")
    process_parts(msg["payload"].get("parts", []))


def main():
    OUT_DIR.mkdir(exist_ok=True)
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", q=QUERY, maxResults=20).execute()
    messages = results.get("messages", [])
    print(f"Found {len(messages)} invoice email(s) with attachments.")

    for msg_ref in messages:
        download_attachments(service, msg_ref["id"], OUT_DIR)

    print(f"\nPDFs saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
