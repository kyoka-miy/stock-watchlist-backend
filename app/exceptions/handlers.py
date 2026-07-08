import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.app_exception import AppException


logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "Request validation error: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    errors = [
        {
            "field": e["loc"][-1],
            "message": e["msg"]
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": errors
        }
    )


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(
        "AppException: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    content = {"message": exc.message}
    if getattr(exc, "details", None) is not None:
        content["details"] = exc.details

    return JSONResponse(
        status_code=400,
        content=content
    )


async def system_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "details": str(exc)}
    )
