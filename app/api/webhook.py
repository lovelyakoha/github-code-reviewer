from fastapi import APIRouter, Request
from app.services.github_service import process_github_event

router = APIRouter()

@router.post("/webhook")
async def webhook_post(request: Request):
    payload = await request.json()

    
    event_type = request.headers.get("X-GitHub-Event")

    print("EVENT TYPE :", event_type)
    print("PAYLOAD REÇU :", payload)

    
    result = process_github_event(event_type, payload)

    return {
        "message": "Données reçues",
        "service": result
    }