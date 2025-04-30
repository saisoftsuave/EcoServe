from datetime import datetime
from uuid import UUID

import stripe
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.orders.db.payments import Payment, PaymentStatus
from app.api.models.orders.payment_request import PaymentUpdate, PaymentCreate


async def create_payment_service(db: AsyncSession, payment_data: PaymentCreate) -> dict:
    payment_intent = stripe.PaymentIntent.create(
        amount=int(payment_data.amount * 100),  # Convert to cents
        currency="usd",
        payment_method_types=[payment_data.payment_method],
        metadata={"order_id": str(payment_data.order_id)},
    )

    payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        status=PaymentStatus.PENDING,
        transaction_id=payment_intent.id
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return {
            **payment.dict(),
            "client_secret": payment_intent.client_secret
        }

async def get_payment_service(db: AsyncSession, payment_id: UUID) -> Payment:
    return await db.get(Payment, payment_id)

async def update_payment_service(db: AsyncSession, payment_id: UUID, payment_update: PaymentUpdate) -> Payment:
    payment = await db.get(Payment, payment_id)
    if payment:
        update_data = payment_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)
        if update_data:
            payment.updated_at = datetime.utcnow()
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
    return payment

async def delete_payment_service(db: AsyncSession, payment_id: UUID) -> bool:
    payment = await db.get(Payment, payment_id)
    if payment:
        await db.delete(payment)
        await db.commit()
        return True
    return False