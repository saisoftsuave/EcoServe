from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.models.user.db.user import to_user, User
from app.api.models.user.signup_request import SignUpRequest
from app.api.utils.password_utils import verify_password
from app.core.access_token_barrier import AccessTokenBearer
from app.core.config import Config
from app.core.db import get_db
from app.core.errors import UserNotFound, InvalidCredentials, DataBaseException

access_token_bearer = AccessTokenBearer()


async def create_new_user(user: SignUpRequest, db: AsyncSession):
    db_user = to_user(user)
    try:
        db.add(db_user)
        await db.commit()
        return f"Account created successfully with the email {user.email}"
    except IntegrityError as e:
        raise DataBaseException(detail=e.detail)
    except SQLAlchemyError as e:
        raise DataBaseException(detail=e)


async def get_user_by_email(email: str, password: str, db: AsyncSession) -> User | str:
    try:
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        user_db = result.scalars().first()
        if user_db is None:
            raise UserNotFound()
        verify_user_password = verify_password(password, user_db.hashed_password)
        if not verify_user_password:
            raise InvalidCredentials()
        return user_db
    except SQLAlchemyError as e:
        raise DataBaseException(detail=e)


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


async def get_current_user(token_details: HTTPAuthorizationCredentials = Depends(access_token_bearer),
                           db: AsyncSession = Depends(get_db)):
    try:
        print("token_details " + token_details.credentials)
        payload = jwt.decode(token_details.credentials, Config.JWT_SECRET_KEY, algorithms=Config.ALGORITHM)
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
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    return user
