from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
import logging

from app.api.models.user.signup_request import SignUpRequest, SignInRequest
from app.api.routes.user.user_service import (
    create_new_user,
    get_user_by_email,
    get_current_user,
    access_token_bearer
)
from app.api.utils.password_utils import validate_password, validate_email
from app.api.utils.token_utils import create_access_token, create_refresh_token
from app.api.models.products.response.product_response_models import BaseResponse
from app.core.config import Config
from app.core.db import get_db

logger = logging.getLogger(__name__)
user_router = APIRouter(prefix="/users", tags=["Users"])

def error_response(message: str, code: int):
    content = BaseResponse(status="error", message=message).model_dump()
    return JSONResponse(status_code=code, content=content)

@user_router.post("/signup", response_model=BaseResponse[dict], status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        valid_email, email_msg = validate_email(request.email)
        valid_pwd, pwd_msg = validate_password(request.password)
        if not valid_email:
            logger.warning("Invalid signup email: %s", request.email)
            return error_response(email_msg, status.HTTP_400_BAD_REQUEST)
        if not valid_pwd:
            logger.warning("Invalid signup password for user %s", request.email)
            return error_response(pwd_msg, status.HTTP_400_BAD_REQUEST)
        message = await create_new_user(request, db)
        return BaseResponse(data={"message": message})
    except ValueError as e:
        logger.warning("Validation error during signup: %s", e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        logger.error("Unexpected error during signup", exc_info=ex)
        return error_response(ex.statement, status.HTTP_500_INTERNAL_SERVER_ERROR)
    # except Exception as ex:
    #     logger.error("Unexpected error during signup", exc_info=ex)
    #     return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@user_router.post("/signin", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
async def signin(
    request: SignInRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        valid_email, email_msg = validate_email(request.email)
        valid_pwd, pwd_msg = validate_password(request.password)
        if not valid_email:
            logger.warning("Invalid signin email: %s", request.email)
            return error_response(email_msg, status.HTTP_400_BAD_REQUEST)
        if not valid_pwd:
            logger.warning("Invalid signin password for user %s", request.email)
            return error_response(pwd_msg, status.HTTP_400_BAD_REQUEST)
        user = await get_user_by_email(request.email, request.password, db)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return BaseResponse(data={
            "message": "User login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    except ValueError as e:
        logger.warning("Signin error for %s: %s", request.email, e)
        return error_response(str(e), status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Unexpected error during signin", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)

@user_router.post("/refresh-token", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
async def refresh_token(
    token_details: HTTPAuthorizationCredentials = Depends(access_token_bearer)
):
    try:
        payload = jwt.decode(
            token_details.credentials,
            Config.JWT_REFRESH_SECRET_KEY,
            algorithms=Config.ALGORITHM
        )
        exp = payload.get('exp')
        sub = payload.get('sub')
        if exp is None or sub is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Expired refresh token for subject %s", sub)
            return error_response("Token expired", status.HTTP_401_UNAUTHORIZED)
        new_refresh = create_refresh_token(sub)
        return BaseResponse(data={"refresh_token": new_refresh})
    except (jwt.JWTError, ValidationError) as e:
        logger.warning("Invalid refresh token: %s", e)
        return error_response("Could not validate credentials", status.HTTP_403_FORBIDDEN)
    except Exception as ex:
        logger.error("Unexpected error refreshing token", exc_info=ex)
        return error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)