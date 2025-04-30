from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from stripe import StripeError

from app.api.models.orders.db.payments import Payment
from app.api.models.orders.payment_request import PaymentCreate, PaymentUpdate
from app.api.routes.user.user_service import get_current_user
from app.api.services.payment_service import (
    create_payment_service,
    get_payment_service,
    update_payment_service,
    delete_payment_service
)
from app.core.db import get_db

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.post("", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        payment = await create_payment_service(session, payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.get("/{payment_id}", response_model=Payment)
async def read_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    payment = await get_payment_service(session, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@payment_router.put("/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: UUID,
    payment_update: PaymentUpdate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        payment = await update_payment_service(session, payment_id, payment_update)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@payment_router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    success = await delete_payment_service(session, payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment not found")


@payment_router.get("/intent/{transaction_id}", response_model=dict)
async def get_payment_intent(
    transaction_id: str,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        # Verify the payment exists in the database
        statement = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await session.execute(statement)
        payment = result.first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Retrieve the Payment Intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(transaction_id)
        return {
            "transaction_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            # "amount": str(payment.amount),
            # "order_id": str(payment.order_id)
        }
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")