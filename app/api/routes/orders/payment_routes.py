from uuid import UUID

import stripe
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from app.api.models.orders.db.payments import Payment
from app.api.models.orders.payment_request import PaymentCreate, PaymentUpdate
from app.api.routes.user.user_service import get_current_user
from app.api.services.order_service import get_orders_service, get_order_service
from app.api.services.payment_service import (
    create_payment_service,
    get_payment_service,
    update_payment_service
)
from app.core.db import get_db
from app.api.models.products.response.product_response_models import BaseResponse

logger = logging.getLogger(__name__)
payment_router = APIRouter(prefix="/payments", tags=["Payments"])


def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)


@payment_router.post("", status_code=status.HTTP_201_CREATED)
async def create_payment(
        payment_data: PaymentCreate,
        session: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        order_details = await get_order_service(session, order_id=payment_data.order_id)
        payment = await create_payment_service(session, payment_data, order_details.total_amount, user_id=user.id)
        return BaseResponse(data=payment)
    except ValueError as e:
        logger.warning("Validation error creating payment: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except stripe.error.StripeError as e:
        logger.error("Stripe error creating payment: %s", e, exc_info=e)
        return error_response(f"Stripe error: {str(e)}", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating payment", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@payment_router.get("/{payment_id}", response_model=BaseResponse[Payment])
async def read_payment(
        payment_id: UUID,
        session: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        payment = await get_payment_service(session, payment_id)
        if not payment:
            return error_response("Payment not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=payment)
    except Exception as ex:
        logger.error("Error reading payment %s", payment_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@payment_router.put("/{payment_id}", response_model=BaseResponse[Payment])
async def update_payment(
        payment_id: UUID,
        payment_update: PaymentUpdate,
        session: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    try:
        payment = await update_payment_service(session, payment_id, payment_update)
        if not payment:
            return error_response("Payment not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=payment)
    except ValueError as e:
        logger.warning("Validation error updating payment %s: %s", payment_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except stripe.error.StripeError as e:
        logger.error("Stripe error updating payment %s: %s", payment_id, e, exc_info=e)
        return error_response(f"Stripe error: {str(e)}", status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Error updating payment %s", payment_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


# @payment_router.delete("/{payment_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
# async def delete_payment(
#         payment_id: UUID,
#         session: AsyncSession = Depends(get_db),
#         user=Depends(get_current_user)
# ):
#     try:
#         success = await delete_payment_service(session, payment_id)
#         if not success:
#             return error_response("Payment not found", status.HTTP_404_NOT_FOUND)
#         return BaseResponse(message="Payment deleted successfully")
#     except Exception as ex:
#         logger.error("Error deleting payment %s", payment_id, exc_info=ex)
#         return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


# @payment_router.get("/intent/{transaction_id}", response_model=BaseResponse[dict])
# async def get_payment_intent(
#         transaction_id: str,
#         session: AsyncSession = Depends(get_db),
#         user=Depends(get_current_user)
# ):
#     from sqlmodel import select
#     try:
#         statement = select(Payment).where(Payment.transaction_id == transaction_id)
#         result = await session.execute(statement)
#         payment = result.scalar_one_or_none()
#         if not payment:
#             return error_response("Payment not found", status.HTTP_404_NOT_FOUND)
#
#         intent = stripe.PaymentIntent.retrieve(transaction_id)
#         return BaseResponse(data={
#             "transaction_id": intent.id,
#             "client_secret": intent.client_secret
#         })
#     except stripe.error.StripeError as e:
#         logger.error("Stripe error retrieving intent %s: %s", transaction_id, e, exc_info=e)
#         return error_response(f"Stripe error: {str(e)}", status.HTTP_400_BAD_REQUEST)
#     except Exception as ex:
#         logger.error("Error retrieving intent %s", transaction_id, exc_info=ex)
#         return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
