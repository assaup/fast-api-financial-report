import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions import (
    AppError,
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError
)

logger = logging.getLogger(__name__)

STATUS_BY_CATEGORY: list[tuple[type[AppError], int]] = [
    (NotFoundError, 404),
    (ConflictError, 409),
    (BusinessRuleError, 400),
    (AuthenticationError, 401),
]

CODE_BY_HTTP_STATUS = {
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
}

def status_for(exc: AppError) -> int:
    for cls, status in STATUS_BY_CATEGORY:
        if isinstance(exc, cls):
            return status
    return 400

def error_response(status_code: int, code: str, message: str, details=None, headers=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or {} }},
        headers=headers
    )

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = status_for(exc)
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthenticationError) else None
    return error_response(status_code, exc.code, exc.message, exc.details, headers)

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = []
    for err in exc.errors():
        loc = [str(part) for part in err["loc"] if part not in ("body", "query", "path", "header")]
        fields.append({"field": ".".join(loc), "message": err["msg"], "type": err["type"]})
    return error_response(422, "VALIDATION_ERROR", "Request validation failed", {"fields": fields})

async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = CODE_BY_HTTP_STATUS.get(exc.status_code, f"HTTP_{exc.status_code}")
    return error_response(exc.status_code, code, str(exc.detail), headers=getattr(exc, "headers", None))

async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL_ERROR", "Something went wrong. Try again later")

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)