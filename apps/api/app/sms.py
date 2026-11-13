"""The new-order SMS to the store phone.

Two modes:

* **Demo (default).** Nothing is sent. The message is stored and served by the
  staff feed/notifications endpoint, which is what the site has always done.
* **Live.** Set ``SMS_PROVIDER`` (``termii`` or ``africastalking``), ``SMS_API_KEY``,
  ``SMS_SENDER_ID`` (an approved sender ID) and ``STORE_PHONE`` (the shop's number
  in international form, e.g. +2348031234567). The same message is then texted
  to the shop as well as stored.

Sending is best effort and never raises: an order must not fail because a
gateway is slow or down.
"""

from __future__ import annotations

import asyncio
import json
import logging
import urllib.parse
import urllib.request

from . import config

log = logging.getLogger("freshmart.sms")

TIMEOUT_SECONDS = 6
PROVIDERS = ("termii", "africastalking")

TERMII_URL = "https://api.ng.termii.com/api/sms/send"
AFRICASTALKING_URL = "https://api.africastalking.com/version1/messaging"


def configured() -> tuple[bool, str]:
    """(ready, reason) — ready is False until every required setting exists."""
    provider = config.SMS_PROVIDER
    if provider not in PROVIDERS:
        return False, "SMS_PROVIDER is not set to termii or africastalking"
    if not config.SMS_API_KEY:
        return False, "SMS_API_KEY is not set"
    if not config.SMS_SENDER_ID:
        return False, "SMS_SENDER_ID is not set"
    if not config.STORE_PHONE:
        return False, "STORE_PHONE is not set"
    if provider == "africastalking" and not config.AT_USERNAME:
        return False, "AFRICASTALKING_USERNAME is not set"
    return True, ""


def _post(url: str, body: bytes, headers: dict[str, str]) -> tuple[int, str]:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:  # noqa: S310 - fixed https URL
        return resp.status, resp.read().decode("utf-8", "replace")[:300]


def _deliver(text: str) -> tuple[bool, str]:
    """Blocking gateway call. Returns (sent, detail)."""
    provider = config.SMS_PROVIDER
    if provider == "termii":
        body = json.dumps(
            {
                "to": config.STORE_PHONE,
                "from": config.SMS_SENDER_ID,
                "sms": text,
                "type": "plain",
                "channel": "generic",
                "api_key": config.SMS_API_KEY,
            }
        ).encode()
        status, detail = _post(TERMII_URL, body, {"Content-Type": "application/json"})
    else:
        body = urllib.parse.urlencode(
            {
                "username": config.AT_USERNAME,
                "to": config.STORE_PHONE,
                "from": config.SMS_SENDER_ID,
                "message": text,
            }
        ).encode()
        status, detail = _post(
            AFRICASTALKING_URL,
            body,
            {
                "apiKey": config.SMS_API_KEY,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
    return (200 <= status < 300), detail


async def send(text: str) -> dict:
    """Text the store, if a gateway is configured. Never raises."""
    ready, why = configured()
    if not ready:
        return {"sent": False, "provider": "demo", "error": why}
    try:
        sent, detail = await asyncio.to_thread(_deliver, text)
    except Exception as exc:  # noqa: BLE001 - a gateway problem must not break checkout
        log.warning("Store SMS failed via %s: %s", config.SMS_PROVIDER, exc)
        return {"sent": False, "provider": config.SMS_PROVIDER, "error": str(exc)[:200]}
    if not sent:
        log.warning("Store SMS rejected by %s: %s", config.SMS_PROVIDER, detail)
    return {"sent": sent, "provider": config.SMS_PROVIDER, "error": "" if sent else detail}
