from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import Pagination
from app.enum import OperationType
from app.exceptions import InsufficientFundsError, WalletNotFoundError
from app.models import User, Wallet
from app.repository import operations as operations_repository
from app.repository import wallets as wallets_repository
from app.schemas import OperationRequest, OperationResponse
from app.service.exchange_service import get_exchange_rate
from app.service.wallets import get_wallet_ids


async def _get_wallet_or_404(db: AsyncSession, user_id: int, wallet_name: str) -> Wallet:
    wallet = await wallets_repository.get_wallet_balance_by_name(db, user_id, wallet_name)
    if wallet is None:
        raise WalletNotFoundError(wallet_name)
    return wallet


async def add_income(db: AsyncSession, current_user: User, operation: OperationRequest):
    wallet = await _get_wallet_or_404(db, current_user.id, operation.wallet_name)

    wallet.balance += operation.amount

    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
    )
    await db.commit()
    return OperationResponse.model_validate(operation)


async def add_expense(db: AsyncSession, current_user: User, operation: OperationRequest):
    wallet = await _get_wallet_or_404(db, current_user.id, operation.wallet_name)

    if wallet.balance < operation.amount:
        raise InsufficientFundsError(wallet.balance, operation.amount, wallet.currency)

    wallet.balance -= operation.amount
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
    )
    await db.commit()
    return OperationResponse.model_validate(operation)


async def get_operations_list(
    db: AsyncSession,
    current_user: User,
    pagination: Pagination,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    type: OperationType | None = None,
    category: str | None = None,
) -> list[OperationResponse]:

    wallets_ids = await get_wallet_ids(db, current_user.id, wallet_id)

    operations = await operations_repository.get_operations_list(
        db,
        wallets_ids,
        pagination.limit,
        pagination.offset,
        date_from,
        date_to,
        type,
        category,
    )
    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))
    return result


async def transfer_between_wallets(
    db: AsyncSession,
    user_id: int,
    from_wallet_id: int,
    to_wallet_id: int,
    amount: Decimal,
) -> OperationResponse:
    from_wallet = await wallets_repository.get_wallet_by_id(db, user_id, from_wallet_id)
    to_wallet = await wallets_repository.get_wallet_by_id(db, user_id, to_wallet_id)

    if not from_wallet:
        raise WalletNotFoundError(from_wallet_id)
    if not to_wallet:
        raise WalletNotFoundError(to_wallet_id)

    if from_wallet.balance < amount:
        raise InsufficientFundsError(from_wallet.balance, amount, from_wallet.currency)

    target_amount = amount
    exchange_rate = 1.0
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = await get_exchange_rate(from_wallet.currency, to_wallet.currency)
        target_amount = round(amount * exchange_rate, 2)

    from_wallet.balance = round(from_wallet.balance - amount, 2)
    to_wallet.balance = round(to_wallet.balance + target_amount, 2)
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=from_wallet.id,
        type=OperationType.TRANSFER,
        amount=target_amount,
        currency=to_wallet.currency,
        category="перевод",
    )
    db.add(from_wallet)
    db.add(to_wallet)
    db.add(operation)
    await db.commit()
    return OperationResponse.model_validate(operation)
