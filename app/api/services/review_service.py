from typing import Optional, List

from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.models.products import Product, Review
from app.api.models.user.db import User



# class Review(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     product_id: int = Field(foreign_key="product.id")
#     reviewer_id: int = Field(foreign_key="user.id")
#     rating: int
#     review_message: Optional[str] = None

class ReviewCreate(SQLModel):
    product_id: str
    reviewer_id: str
    rating: int
    review_message: Optional[str] = None

class ReviewUpdate(SQLModel):
    product_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    rating: Optional[int] = None
    review_message: Optional[str] = None


# Create
async def create_review_service(db: AsyncSession, review: ReviewCreate) -> Review:
    if not await db.get(Product, review.product_id):
        raise ValueError("Product not found")
    if not await db.get(User, review.reviewer_id):
        raise ValueError("User not found")
    if not 1 <= review.rating <= 5:
        raise ValueError("Rating must be between 1 and 5")
    review_model = Review(**review.dict())
    db.add(review_model)
    await db.commit()
    await db.refresh(review_model)
    return review_model

# Read One
async def get_review_service(db: AsyncSession, review_id: str) -> Optional[Review]:
    return await db.get(Review, review_id)

# # Read All
# async def get_reviews_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Review]:
#     return db.query(Review).offset(skip).limit(limit).all()

# Update
async def update_review_service(db: AsyncSession, review_id: str, review_update: ReviewUpdate) -> Optional[Review]:
    review = await db.get(Review, review_id)
    if review:
        for key, value in review_update.dict(exclude_unset=True).items():
            if key == "product_id" and value is not None:
                if not await db.get(Product, value):
                    raise ValueError("Product not found")
            elif key == "reviewer_id" and value is not None:
                if not await db.get(User, value):
                    raise ValueError("User not found")
            elif key == "rating" and value is not None:
                if not 1 <= value <= 5:
                    raise ValueError("Rating must be between 1 and 5")
            setattr(review, key, value)
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    return None

# Delete
async def delete_review_service(db: AsyncSession, review_id: str) -> Optional[Review]:
    review = await db.get(Review, review_id)
    if review:
        await db.delete(review)
        await db.commit()
        return review
    return None