import uuid

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "User"
    id: uuid.UUID = Field(primary_key=True, default=uuid.uuid4())
    email: str = Field(min_length=3, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[A-Za-z]{2,}$', unique=True)
    hashed_password: str
    first_name: str = Field(min_length=2, max_length=26, regex=r"^[A-Za-z\\s'-]{1,100}$")
    last_name: str = Field(min_length=2, max_length=26, regex=r"^[A-Za-z\\s'-]{1,100}$")

    session: "Session" = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})