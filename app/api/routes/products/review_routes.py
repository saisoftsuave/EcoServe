from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from starlette.responses import JSONResponse

from app.api.models.products import Review
from app.api.routes.user.user_service import get_current_user
from app.api.services.review_service import (
    ReviewCreate,
    create_review_service,
    get_review_service,
    update_review_service,
    delete_review_service,
    ReviewUpdate,
    get_reviews_service
)
from app.api.models.products.response.product_response_models import BaseResponse
from app.core.base_response import BaseResponse
from app.core.db import get_db

logger = logging.getLogger(__name__)
reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)


@reviews_router.post("/", response_model=BaseResponse[Review], status_code=201)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> BaseResponse | JSONResponse:
    try:
        created_review = await create_review_service(db, review, user.id)
        return BaseResponse(data=created_review)
    except ValueError as e:
        logger.warning("Validation error creating review: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error creating review", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@reviews_router.get("/{review_id}", response_model=BaseResponse[Review])
async def read_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse | BaseResponse:
    try:
        review = await get_review_service(db, review_id)
        if not review:
            return error_response("Review not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=review)
    except Exception as ex:
        logger.error("Error reading review %s", review_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@reviews_router.get("/", response_model=BaseResponse[List[Review]])
async def read_reviews(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse | JSONResponse:
    try:
        reviews = await get_reviews_service(db, skip=skip, limit=limit)
        return BaseResponse(data=reviews)
    except Exception as ex:
        logger.error("Error reading reviews list", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@reviews_router.put("/{review_id}", response_model=BaseResponse[Review])
async def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> JSONResponse | BaseResponse:
    try:
        review = await update_review_service(db, review_id, review_update)
        if not review:
            return error_response("Review not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=review)
    except ValueError as e:
        logger.warning("Validation error updating review %s: %s", review_id, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error updating review %s", review_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@reviews_router.delete("/{review_id}", response_model=BaseResponse[None], status_code=200)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> JSONResponse | BaseResponse:
    try:
        deleted = await delete_review_service(db, review_id)
        if not deleted:
            return error_response("Review not found", status.HTTP_404_NOT_FOUND)
        return BaseResponse(data=None, message="Review deleted successfully")
    except Exception as ex:
        logger.error("Error deleting review %s", review_id, exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)
