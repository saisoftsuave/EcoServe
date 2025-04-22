from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from typing import List

from app.api.models.products import Review
from app.api.services.review_service import ReviewCreate, create_review_service, \
    get_review_service, update_review_service, delete_review_service, ReviewUpdate
from app.core.db import get_db

reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])

@reviews_router.post("/", response_model=Review, status_code=201)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_review_service(db, review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@reviews_router.get("/{review_id}", response_model=Review)
async def read_review(review_id: str, db: AsyncSession = Depends(get_db)):
    review = get_review_service(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

# @reviews_router.get("/", response_model=List[Review])
# async def read_reviews(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
#     return get_reviews_service(db, skip=skip, limit=limit)

@reviews_router.put("/{review_id}", response_model=Review)
async def update_review(review_id: str, review_update: ReviewUpdate, db: AsyncSession = Depends(get_db)):
    try:
        review = update_review_service(db, review_id, review_update)
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@reviews_router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: str, db: AsyncSession = Depends(get_db)):
    if delete_review_service(db, review_id) is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return None