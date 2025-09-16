# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    email: EmailStr
    company: Optional[str] = None
    api_key: Optional[str] = None
