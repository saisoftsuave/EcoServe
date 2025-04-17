import uuid

from sqlmodel import SQLModel, Field, Relationship


class Session(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    user_id: uuid.UUID = Field(foreign_key="User.id")
    session_token: str = Field(unique=True)

    user: "User" = Relationship(back_populates="session", sa_relationship_kwargs={"lazy": "selectin"})