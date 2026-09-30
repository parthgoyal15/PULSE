"""
WhatsApp Cloud API client.
Set WHATSAPP_TOKEN and WHATSAPP_PHONE_ID in .env to send real messages.
Without credentials, messages are logged to console (demo mode).
"""

import os
import json
import httpx

GRAPH_API_URL = "https://graph.facebook.com/v18.0"


async def send_alert_message(recipient_phone: str, transfer: dict, message_text: str) -> dict:
    """Send an interactive WhatsApp message with Approve/Modify/Escalate buttons."""
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_ID")

    if not token or not phone_id:
        print(f"\n[WhatsApp DEMO] Would send to {recipient_phone}:\n{message_text}\n")
        return {"status": "demo_mode", "message": message_text}

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": message_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"approve_{transfer['id']}", "title": "✅ Approve"}},
                    {"type": "reply", "reply": {"id": f"modify_{transfer['id']}", "title": "✏️ Modify"}},
                    {"type": "reply", "reply": {"id": f"escalate_{transfer['id']}", "title": "⬆️ Escalate"}},
                ]
            },
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_API_URL}/{phone_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        return resp.json()


async def send_text_message(recipient_phone: str, text: str) -> dict:
    """Send a plain text WhatsApp message."""
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_ID")

    if not token or not phone_id:
        print(f"\n[WhatsApp DEMO] Would send to {recipient_phone}:\n{text}\n")
        return {"status": "demo_mode", "message": text}

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_API_URL}/{phone_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        return resp.json()


def parse_webhook_event(body: dict) -> dict | None:
    """Extract message data from a WhatsApp webhook payload."""
    try:
        changes = body["entry"][0]["changes"][0]["value"]
        if "messages" not in changes:
            return None
        message = changes["messages"][0]
        contact = changes["contacts"][0]
        return {
            "phone": message["from"],
            "name": contact["profile"]["name"],
            "type": message["type"],
            "text": message.get("text", {}).get("body", ""),
            "button_id": message.get("interactive", {}).get("button_reply", {}).get("id", ""),
        }
    except (KeyError, IndexError):
        return None
