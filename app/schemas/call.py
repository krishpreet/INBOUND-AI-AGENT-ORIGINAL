from pydantic import BaseModel

class CallCreate(BaseModel):
    caller: str
    receiver: str
    status: str = "initiated"

class CallResponse(CallCreate):
    id: int
    class Config:
        orm_mode = True