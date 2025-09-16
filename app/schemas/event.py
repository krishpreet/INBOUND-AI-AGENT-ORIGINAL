from pydantic import BaseModel

class EventCreate(BaseModel):
    name: str
    description: str | None = None

class EventResponse(EventCreate):
    id: int
    class Config:
        orm_mode = True