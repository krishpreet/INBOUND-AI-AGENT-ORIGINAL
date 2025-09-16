from pydantic import BaseModel

class OutboundCallRequest(BaseModel):
    to_number: str
    from_number: str | None = None
