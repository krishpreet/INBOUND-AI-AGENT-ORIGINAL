# app/services/user_service.py
from app.core.db import db
from app.models.user import User

async def create_user(user: User):
    result = await db.database["users"].insert_one(user.dict(by_alias=True))
    return str(result.inserted_id)

async def get_user_by_email(email: str):
    return await db.database["users"].find_one({"email": email})
