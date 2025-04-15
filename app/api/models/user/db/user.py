import uuid
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from app.api.models.user.signup_request import SignUpRequest
from app.api.utils.password_utils import get_hashed_password


class User(SQLModel, table=True):
    __tablename__ = "User"
    id: uuid.UUID = Field(primary_key=True, default=uuid.uuid4())
    email: str = Field(min_length=3, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[A-Za-z]{2,}$', unique=True)
    hashed_password: str
    first_name: str = Field(min_length=2, max_length=26, regex=r"^[A-Za-z\\s'-]{1,100}$")
    last_name: str = Field(min_length=2, max_length=26, regex=r"^[A-Za-z\\s'-]{1,100}$")

    session: "Session" = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="reviewer")




def to_user(signup_request: SignUpRequest) -> User:
    return User(
        email=signup_request.email,
        hashed_password=get_hashed_password(signup_request.password),
        first_name=signup_request.first_name,
        last_name=signup_request.last_name
    )