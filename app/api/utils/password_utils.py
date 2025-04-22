import re

from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def validate_email(email: str) -> tuple[bool, str]:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(email_regex, email):
        return True, "Valid email"
    return False, "Invalid email format"


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password should be at least 6 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password should contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password should contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password should contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password should contain at least one special character"

    return True, "Valid password"



def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)