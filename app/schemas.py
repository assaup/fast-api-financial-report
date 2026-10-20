from pydantic import BaseModel, Field, StringConstraints, model_validator
from decimal import Decimal
from app.enum import CurrencyEnum
from datetime import datetime
from typing import Annotated, Self


PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
NonNegativeMoney = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
WalletName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=127)]


class OperationRequest(BaseModel):
    wallet_name: WalletName
    amount: PositiveMoney
    description: str | None = Field(None, max_length=255)


class CreateWalletRequest(BaseModel):
    name: WalletName
    initial_balance: NonNegativeMoney = Decimal(0)
    currency: CurrencyEnum = CurrencyEnum.RUB


Login = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=127)]
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]

class UserCreateRequest(BaseModel):
    login: Login
    password: Password

class LoginRequest(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    login: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class WalletResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    balance: Decimal
    currency: CurrencyEnum


class OperationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    wallet_id: int
    type: str
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    subcategory: str | None
    created_at: datetime


class TransferCreateSchema(BaseModel):
    from_wallet_id: int = Field(gt=0)
    to_wallet_id: int = Field(gt=0)
    amount: PositiveMoney

    # Запрет перевода самому себе
    @model_validator(mode='after')
    def wallet_must_differ(self) -> Self:
        if self.from_wallet_id == self.to_wallet_id:
            raise ValueError("Cannot transfer to the same wallet")
        return self

class TotalBalance(BaseModel):
    total_balance: Decimal

class WalletUpdateRequest(BaseModel):
    name: WalletName | None = None

class ExpenseStatsItem(BaseModel):
    model_config = {'from_attributes': True}

    category: str | None
    currency: CurrencyEnum
    total: Decimal
    count: int