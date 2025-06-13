from fastapi import APIRouter, Request
import logging

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", status_code=200)
async def handle_webhook(request: Request):
    """
    Handles incoming webhook requests.
    Accepts any JSON payload.
    """
    payload = await request.json()
    logger.info(f"Received webhook payload: {payload}")
    # In a real application, you would process the payload here.
    # For example, based on the event type, you might update a database,
    # send a notification, or trigger other actions.
    return {"status": "success", "message": "Webhook received successfully"}
