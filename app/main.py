import stripe
from fastapi import FastAPI, Request, Header
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.services.payment_service import update_payment_service
from app.core.config import Settings, Config
from app.core.errors import register_all_errors
from app.main_router import main_router

app = FastAPI()

register_all_errors(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Frontend URL
        "http://localhost",       # Add other origins if needed
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


@app.post("/webhook")
async def webhook_received(request: Request, stripe_signature: str = Header(str)):
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=Config.STRIPE_WEBHOOK_SECRET
        )
        event_data = event[data]
    except Exception as e:
        return {"error": e}

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        update_payment_service()
        return {"payment_intent": payment_intent}
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        return {"payment_intent": payment_intent}

    return {"status": "success"}