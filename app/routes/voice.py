# app/routes/voice.py  (replace your function with this handler)
from fastapi import APIRouter, Request, HTTPException
import logging
from app.telephony.provider_registry import get_provider
from app.telephony.webhook_parser import parse_incoming
from app.services.call_flow_service import CallFlowService
from app.schemas.voice import OutboundCallRequest

router = APIRouter(prefix="/voice", tags=["Voice"])
log = logging.getLogger("voice")

@router.post("/webhook")
async def inbound_webhook(request: Request):
    provider = get_provider()
    raw = await request.body()
    headers = dict(request.headers)

    # Parse form safely (Twilio sends x-www-form-urlencoded)
    form = {}
    try:
        f = await request.form()
        form = {k: v for k, v in f.items()}
    except Exception:
        form = {}

    full_url = str(request.url)

    # Enforce signature if configured
    if not provider.verify_signature(raw, headers, form, full_url):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = parse_incoming(
        provider_name=provider.name,
        query=request.query_params,
        form=form,
        raw=raw,
        headers=headers,
    )

    log.info("voice_event", extra={"event": dict(event), "provider": provider.name})
    response_xml = await CallFlowService.handle_incoming_event(event, provider)
    return provider.XMLResponse(response_xml)

@router.post("/outbound/initiate")
async def initiate_outbound(payload: OutboundCallRequest):
    provider = get_provider()
    call_sid = await provider.initiate_call(payload.to_number, payload.from_number)
    return {"status": "initiated", "provider_call_id": call_sid}
