"""
DSE Dividend Tracker — WhatsApp Bot

Uses WhatsApp Business API (Cloud API via Meta).
Handles incoming messages and responds with dividend data.

Commands:
  DIVIDENDS       → Show all recent dividend announcements
  YIELDS          → Show dividend yields ranked highest to lowest
  TAX <shares> <dividend> [resident|non_resident]  → Calculate tax
  UPCOMING        → Show upcoming dividends
  HELP            → Show available commands
"""

import hashlib
import hmac
import logging
import os

import httpx
from fastapi import APIRouter, Request, Response

logger = logging.getLogger("dse.whatsapp")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "dse-dividend-verify")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

router = APIRouter(prefix="/webhook", tags=["whatsapp"])


# ─── Signature verification ───────────────────────────────────────

def verify_signature(payload: bytes, signature_header: str) -> bool:
    """Verify Meta webhook payload signature (X-Hub-Signature-256)."""
    if not APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not set — skipping signature verification")
        return True

    if not signature_header:
        return False

    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


# ─── Webhook verification (GET) ────────────────────────────────────

@router.get("/whatsapp")
def verify_webhook(request: Request):
    """Meta sends a GET request to verify the webhook URL."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    logger.warning("Webhook verification failed — invalid token")
    return Response(status_code=403)


# ─── Incoming messages (POST) ──────────────────────────────────────

@router.post("/whatsapp")
async def receive_message(request: Request):
    """Process incoming WhatsApp messages."""
    body_bytes = await request.body()

    # Verify payload signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body_bytes, signature):
        logger.warning("Invalid webhook signature — rejecting request")
        return Response(status_code=403)

    body = await request.json()

    # Extract message data
    entry = body.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    messages = value.get("messages", [])

    if not messages:
        return {"status": "no message"}

    msg = messages[0]
    from_number = msg.get("from", "")
    text = msg.get("text", {}).get("body", "").strip().upper()

    logger.info("Message from %s: %s", from_number[:6] + "***", text[:50])

    # Route commands
    if text in ("HELP", "HI", "HABARI"):
        response = format_help()
    elif text in ("DIVIDENDS", "GAWIO"):
        response = await get_dividends()
    elif text == "YIELDS":
        response = await get_yields()
    elif text.startswith("TAX"):
        response = await handle_tax_command(text)
    elif text == "UPCOMING":
        response = await get_upcoming()
    else:
        response = (
            "Samahani, sijaelewa amri yako.\n"
            "(Sorry, I didn't understand.)\n\n"
            "Andika *HELP* kuona amri zote."
        )

    await send_message(from_number, response)
    return {"status": "ok"}


# ─── Command handlers ──────────────────────────────────────────────

def format_help() -> str:
    return (
        "*DSE Dividend Tracker*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*DIVIDENDS* — Tangazo za gawio zote\n"
        "  (All dividend announcements)\n\n"
        "*YIELDS* — Dividend yield kwa kila hisa\n"
        "  (Dividend yield per stock)\n\n"
        "*UPCOMING* — Gawio zinazokuja\n"
        "  (Upcoming dividends)\n\n"
        "*TAX 5000 818 resident*\n"
        "  Hesabu kodi ya gawio\n"
        "  (Calculate dividend tax)\n"
        "  Format: TAX <shares> <dividend_per_share> [resident|non_resident]\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Powered by DSE Dividend Tracker"
    )


async def get_dividends() -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API_BASE}/api/dividends/")
        if resp.status_code != 200:
            return "Samahani, tatizo la mtandao. Jaribu tena."

    dividends = resp.json()[:10]  # Latest 10
    if not dividends:
        return "Hakuna tangazo za gawio kwa sasa."

    lines = ["*Tangazo za Gawio (Dividends)*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for d in dividends:
        status_icon = "✅" if d["status"] == "paid" else "⏳"
        lines.append(
            f"{status_icon} *{d['symbol']}* — TZS {d['dividend_per_share']}/share\n"
            f"   Year: {d['financial_year']}\n"
            f"   Books close: {d['books_closure_date'] or 'TBD'}\n"
            f"   Payment: {d['payment_date'] or 'TBD'}\n"
        )

    return "\n".join(lines)


async def get_yields() -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API_BASE}/api/dividends/yields")
        if resp.status_code != 200:
            return "Samahani, tatizo la mtandao. Jaribu tena."

    yields_data = resp.json()[:10]
    if not yields_data:
        return "Hakuna data ya dividend yield kwa sasa."

    lines = ["*Dividend Yields (Ranked)*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for i, y in enumerate(yields_data, 1):
        bar = "🟢" if float(y["dividend_yield"]) > 5 else "🟡" if float(y["dividend_yield"]) > 2 else "🔴"
        lines.append(
            f"{i}. {bar} *{y['symbol']}* — {y['dividend_yield']}%\n"
            f"   Price: TZS {y['current_price']} | Div: TZS {y['last_dividend']}\n"
        )

    return "\n".join(lines)


async def get_upcoming() -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API_BASE}/api/dividends/upcoming?days=90")
        if resp.status_code != 200:
            return "Samahani, tatizo la mtandao. Jaribu tena."

    upcoming = resp.json()
    if not upcoming:
        return "Hakuna gawio zinazokuja katika siku 90 zijazo.\n(No upcoming dividends in the next 90 days.)"

    lines = ["*Gawio Zinazokuja (Upcoming)*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for d in upcoming:
        lines.append(
            f"⏳ *{d['symbol']}* — TZS {d['dividend_per_share']}/share\n"
            f"   Books close: {d['books_closure_date']}\n"
            f"   Nunua kabla ya tarehe hii kupata gawio!\n"
        )

    return "\n".join(lines)


async def handle_tax_command(text: str) -> str:
    """Parse: TAX 5000 818 resident"""
    parts = text.split()
    if len(parts) < 3:
        return (
            "Format: *TAX <shares> <dividend_per_share> [resident|non_resident]*\n\n"
            "Mfano: TAX 5000 818 resident\n"
            "(Calculate tax on 5000 shares at TZS 818 dividend)"
        )

    try:
        shares = int(parts[1])
        dps = float(parts[2])
    except ValueError:
        return "Tafadhali ingiza nambari sahihi.\n(Please enter valid numbers.)"

    if shares <= 0 or dps <= 0:
        return "Tafadhali ingiza nambari chanya.\n(Please enter positive numbers.)"

    residency = parts[3].lower() if len(parts) > 3 else "resident"
    if residency not in ("resident", "non_resident"):
        residency = "resident"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{API_BASE}/api/tax/calculate",
            json={
                "shares": shares,
                "dividend_per_share": dps,
                "residency": residency,
            },
        )
        if resp.status_code != 200:
            return "Tatizo la kuhesabu kodi. Jaribu tena."

    result = resp.json()
    tax_pct = float(result["tax_rate"]) * 100

    return (
        f"*Hesabu ya Kodi ya Gawio*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hisa: {shares:,}\n"
        f"Gawio/hisa: TZS {dps:,.2f}\n"
        f"Residency: {residency}\n\n"
        f"💰 Gross: *TZS {result['gross_dividend']}*\n"
        f"🏛️ Kodi ({tax_pct:.0f}%): *TZS {result['tax_amount']}*\n"
        f"✅ Net (unapata): *TZS {result['net_dividend']}*\n"
    )


# ─── Send message via WhatsApp Cloud API ───────────────────────────

async def send_message(to: str, text: str):
    """Send a text message via WhatsApp Business Cloud API."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print(f"[DEV MODE] Would send to {to}:\n{text}")
        return

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            logger.error("Failed to send WhatsApp message: %s %s", resp.status_code, resp.text)
