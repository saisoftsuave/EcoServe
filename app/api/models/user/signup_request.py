from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: str = "test1@gmail.com"
    password: str = "Test@123"
    first_name: str = "Test"
    last_name: str = "User"
    profile_image: str | None = None


class SignInRequest(BaseModel):
    email: str = "test1@gmail.com"
    password: str = "Test@123"


class User(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    profile_image: str | None = None