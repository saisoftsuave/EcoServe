"""
This file consist of custom Exceptions for bustle spot application
"""
from typing import Callable, Any

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class BustleSoptException(Exception):
    """
    Application Global Exception
    """


class UserAlreadyExists(BustleSoptException):
    """
    if UserAlreadyExists in DB
    """


class DataBaseException(BustleSoptException):
    """
     Database exception
     """

    def __init__(self, detail):
        super().__init__(detail)


class UserNotFound(BustleSoptException):
    """
    UserNotFound in DB
    """


class UserEmailNotVerified(BustleSoptException):
    """
    User Email is not verified before sign in
    """


class TokenNotFound(BustleSoptException):
    """
    Token not found in request
    """


class InvalidTokenException(BustleSoptException):
    """
    Token is invalid because not present session db
    """


class InvalidCredentials(BustleSoptException):
    """
    Provided incorrect Credentials
    """


class OrganisationNotFound(BustleSoptException):
    """
    if organisation not found in database
    """


class InsufficientPermission(BustleSoptException):
    """
    if current_user not have permission to access or modify
    """

    def __init__(self, detail):
        super().__init__(detail)


class TeamNotFound(BustleSoptException):
    """
    if current_user not have permission to access or modify
    """


class SessionNotFound(BustleSoptException):
    """
    if session not found in database
    """


class TokenMissing(BustleSoptException):
    """
    if token is missing
    """


class TaskNotFound(BustleSoptException):
    """
    Task not found in database (Invalid task ID)
    """


def create_exception_handler(
        status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    """
    Reusable function to create a custom exception
    :param status_code:
    :param initial_detail:
    :return:
    """

    async def exception_handler(request: Request, exc: BustleSoptException):
        detail = initial_detail.copy()
        if hasattr(exc, "detail") and exc.detail:
            detail["message"] = f"{detail['message']} {str(exc.detail)}"
        elif str(exc):
            detail["message"] = f"{detail['message']} {str(exc)}"

        return JSONResponse(content=detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    """
    This function register all custom exception with fastAPi application instance
    :param app:
    :return:
    """
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )
    app.add_exception_handler(
        DataBaseException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": f"data base execution failed:",
                "error_code": "database_exception",
            },
        )
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND, initial_detail={
                "message": "User not found, please check the details",
                "error_code": "user_not_found"
            }
        )
    )
    app.add_exception_handler(
        UserEmailNotVerified,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "User not verified email, please verify your email",
                "error_code": "user_not_verified"
            }
        )
    )
    app.add_exception_handler(
        TokenNotFound,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Token is missing in request",
                "error_code": "token_mission"
            }
        )
    )
    app.add_exception_handler(
        InvalidTokenException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Token is invalid",
                "error_code": "token_invalid"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Invalid Credentials",
                "error_code": "invalid_creds"
            }
        )
    )
    app.add_exception_handler(
        OrganisationNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Organisation not found",
                "error_code": "invalid_org_id"
            }
        )
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        TeamNotFound,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Team not found",
                "error_code": "team_not_found",
            },
        ),
    )
    app.add_exception_handler(
        TokenMissing,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Token is not provided",
                "error_code": "token_missing",
            },
        ),
    )
    app.add_exception_handler(
        TaskNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Invalid task ID provided",
                "error_code": "404"
            }
        )
    )
    app.add_exception_handler(
        SessionNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Session not found",
                "error_code": "session_not_found"
            }
        )
    )
