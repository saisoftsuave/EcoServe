from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app.api.models.user.signup_request import SignUpRequest, SignInRequest
from app.api.routes.user.user_service import create_new_user, get_user_by_email, get_current_user, access_token_bearer
from app.api.utils.password_utils import validate_password, validate_email
from app.api.utils.token_utils import create_access_token, create_refresh_token
from app.core.config import Config
from app.core.db import get_db

user_router = APIRouter()


@user_router.post("/signup")
async def signup(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    is_vaild_email, email_message = validate_email(request.email)
    is_vaild_password, password_message = validate_password(request.password)
    if not is_vaild_email:
        raise HTTPException(status_code=400, detail=email_message)
    if not is_vaild_password:
        raise HTTPException(status_code=400, detail=password_message)
    message = await create_new_user(request, db)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={
        "message": message
    })


@user_router.post("/signin")
async def signup(request: SignInRequest, db: AsyncSession = Depends(get_db)):
    is_vaild_email, email_message = validate_email(request.email)
    is_vaild_password, password_message = validate_password(request.password)
    if not is_vaild_email:
        raise HTTPException(status_code=400, detail=email_message)
    if not is_vaild_password:
        raise HTTPException(status_code=400, detail=password_message)
    user = await get_user_by_email(email=request.email, password=request.password, db=db)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "message": "User login successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@user_router.post("/refresh-token",
                  summary="Refresh user token", status_code=status.HTTP_200_OK
                  )
async def refresh_token(token_details: HTTPAuthorizationCredentials = Depends(access_token_bearer)):
    try:
        print("token_details " + token_details.credentials)
        payload = jwt.decode(token_details.credentials, Config.JWT_REFRESH_SECRET_KEY, algorithms=Config.ALGORITHM)
        user_id = payload.get('sub')
        if datetime.fromtimestamp(payload.get('exp')) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    refresh_token = create_refresh_token(user_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "refresh_token": refresh_token
    })
