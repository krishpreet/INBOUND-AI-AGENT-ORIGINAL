from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"status": "ok"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
