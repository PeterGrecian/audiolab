#!/usr/bin/env python3
"""Fetch emails from/about Rapid Electronics via Gmail API.

Usage:
    python3 fetch_rapid_emails.py
"""

import base64
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path.home() / "gcp/credentials/workspace-client.json"
TOKEN_FILE = Path.home() / ".config/gcloud/gmail-token.json"

QUERY = "from:rapid OR subject:rapid rapid electronics"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def decode_body(part):
    data = part.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def get_text(payload):
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        return decode_body(payload)
    if mime.startswith("multipart/"):
        for part in payload.get("parts", []):
            text = get_text(part)
            if text:
                return text
    return ""


def main():
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    print(f"Searching: {QUERY!r}\n")
    results = service.users().messages().list(
        userId="me", q=QUERY, maxResults=50
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print("No messages found.")
        return

    print(f"Found {len(messages)} message(s).\n")
    print("=" * 70)

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "(no subject)")
        sender  = headers.get("From", "?")
        date    = headers.get("Date", "?")

        # Attachments
        attachments = []
        def collect_attachments(part):
            filename = part.get("filename", "")
            if filename:
                attachments.append(filename)
            for sub in part.get("parts", []):
                collect_attachments(sub)
        collect_attachments(msg["payload"])

        print(f"Date:    {date}")
        print(f"From:    {sender}")
        print(f"Subject: {subject}")
        if attachments:
            print(f"Attachments: {', '.join(attachments)}")

        # Print first 800 chars of body
        body = get_text(msg["payload"]).strip()
        if body:
            preview = body[:800]
            print(f"\n{preview}")
            if len(body) > 800:
                print("... [truncated]")

        print("=" * 70)


if __name__ == "__main__":
    main()
