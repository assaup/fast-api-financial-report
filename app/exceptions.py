from decimal import Decimal


class AppError(Exception):
    """Базовая ошибка приложения. Ничего не знает про HTTP."""

    code = "APP_ERROR"
    message = "Application error"

    def __init__(self, message: str | None = None, **details):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    message = "Resource not found"


class ConflictError(AppError):
    code = "CONFLICT"
    message = "Conflict with the current state"


class BusinessRuleError(AppError):
    code = "BUSINESS_RULE_VIOLATION"
    message = "Business rule violated"


class AuthenticationError(AppError):
    code = "UNAUTHORIZED"
    message = "Authentication required"


# конретные ошибки
class WalletNotFoundError(NotFoundError):
    code = "WALLET_NOT_FOUND"

    def __init__(self, wallet: int | str):
        super().__init__(f"Wallet '{wallet}' not found", wallet=wallet)


class WalletAlreadyExistsError(ConflictError):
    code = "WALLET_ALREADY_EXISTS"

    def __init__(self, name: str):
        super().__init__(f"Wallet '{name}' already exists", name=name)


class WalletNotEmptyError(ConflictError):
    code = "WALLET_NOT_EMPTY"

    def __init__(self, name: str, balance: Decimal):
        super().__init__(
            f"Wallet '{name}' has non-zero balance: {balance}. Withdraw or transfer it first",
            name=name,
            balance=str(balance),
        )


class InsufficientFundsError(BusinessRuleError):
    code = "INSUFFICIENT_FUNDS"

    def __init__(self, available: Decimal, requested: Decimal, currency: str):
        super().__init__(
            f"Insufficient funds: available {available} {currency}, requested {requested}",
            available=str(available),
            requested=str(requested),
            currency=str(currency),
        )


class InvalidDateRangeError(BusinessRuleError):
    code = "INVALID_DATE_RANGE"
    message = "date_from must be earlier than or equal to date_to"


class InvalidTokenError(AuthenticationError):
    code = "INVALID_TOKEN"
    message = "Invalid or expired token"


class UserAlreadyExistsError(ConflictError):
    code = "USER_ALREADY_EXISTS"

    def __init__(self, login: str):
        super().__init__(f"User '{login}' already exists", login=login)


class InvalidCredentialsError(AuthenticationError):
    code = "INVALID_CREDENTIALS"
    message = "Incorrect login or password"
