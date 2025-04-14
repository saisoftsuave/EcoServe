from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    profile_image: str | None = None


class SignInRequest(BaseModel):
    email: str
    password: str


class User(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    profile_image: str | None = None