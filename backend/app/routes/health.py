from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple status endpoint."""
    return {"status": "ok"}