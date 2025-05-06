import stripe
from fastapi import FastAPI, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.models.orders.db.payments import PaymentStatus
from app.api.models.orders.order_request import OrderUpdate
from app.api.models.orders.payment_request import PaymentUpdate
from app.api.routes.user.user_service import get_current_user
from app.api.services.order_service import update_order_item_service, update_order_service
from app.api.services.payment_service import update_payment_service
from app.api.utils.order_status import OrderStatus
from app.core.config import Settings, Config
from app.core.db import get_db
from app.core.errors import register_all_errors
from app.main_router import main_router
import traceback
import logging
from fastapi import APIRouter, Request, Header, Depends
from fastapi.responses import JSONResponse
import stripe
from sqlmodel.ext.asyncio.session import AsyncSession

app = FastAPI()

register_all_errors(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Frontend URL
        "http://localhost",  # Add other origins if needed
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],  # Allow all headers, including Authorization
)
app.include_router(main_router)

stripe.api_key = Config.STRIPE_API_KEY


@app.get("/")
async def root():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"currently server is running"})




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/webhook")
async def webhook_received(
    request: Request,
    stripe_signature: str = Header(...),
    session: AsyncSession = Depends(get_db)
):
    data = await request.body()
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=Config.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Received Stripe event: {event['type']}")

        # Handle specific event types
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            metadata = payment_intent.get("metadata", {})
            payment_id = metadata.get("payment_id")
            order_id = metadata.get("order_id")

            if not payment_id or not order_id:
                logger.error("Missing payment_id or order_id in metadata")
                return JSONResponse(status_code=400, content={"error": "Missing metadata"})

            # Update payment and order status
            await update_payment_service(
                session,
                payment_id=payment_id,
                payment_update=PaymentUpdate(status=PaymentStatus.COMPLETED)
            )
            await update_order_service(
                session,
                order_id=order_id,
                order_update=OrderUpdate(status=OrderStatus.PROCESSING)
            )
            logger.info(f"Processed payment_intent.succeeded for order_id: {order_id}")
            return {"payment_intent": payment_intent}

        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            metadata = payment_intent.get("metadata", {})
            payment_id = metadata.get("payment_id")

            if not payment_id:
                logger.error("Missing payment_id in metadata")
                return JSONResponse(status_code=400, content={"error": "Missing payment_id"})

            await update_payment_service(
                session,
                payment_id=payment_id,
                payment_update=PaymentUpdate(status=PaymentStatus.FAILED)
            )
            logger.info(f"Processed payment_intent.payment_failed for payment_id: {payment_id}")
            return {"payment_intent": payment_intent}

        else:
            logger.info(f"Unhandled event type: {event['type']}")
            return {"status": "success"}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})