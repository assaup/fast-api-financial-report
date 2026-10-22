from collections import defaultdict
from typing import Any

from app.exception_handlers import status_for
from app.exceptions import AppError, AuthenticationError, InvalidTokenError
from app.schemas import ErrorResponse

VALIDATION_EXAMPLE = {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"fields": [{"field": "amount", "message": "Input should be greater than 0", "type": "greater_than"}]},
}


def error_responses(*errors: AppError, validation: bool = True) -> dict[int | str, dict[str, Any]]:
    grouped: dict[int, dict[str, dict]] = defaultdict(dict)
    for exc in errors:
        grouped[status_for(exc)][exc.code] = {"code": exc.code, "message": exc.message, "details": exc.details}
    if validation:
        grouped[422]["VALIDATION_ERROR"] = VALIDATION_EXAMPLE

    return {
        status: {
            "model": ErrorResponse,
            "description": ", ".join(examples),
            "content": {
                "application/json": {
                    "examples": {code: {"summary": code, "value": {"error": body}} for code, body in examples.items()}
                }
            },
        }
        for status, examples in grouped.items()
    }


AUTH_ERRORS = (AuthenticationError("Not authenticated"), InvalidTokenError())