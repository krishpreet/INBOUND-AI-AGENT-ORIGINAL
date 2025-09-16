from pydantic import BaseModel
from typing import Optional

class CallEvent(BaseModel):
    provider_call_id: str
    event: str
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    digits: Optional[str] = None
