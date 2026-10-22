from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import CurrencyEnum, OperationType
from app.models import Operation


async def create_operation(
    db: AsyncSession,
    wallet_id: int,
    type: str,
    amount: Decimal,
    currency: CurrencyEnum,
    category: str | None = None,
    subcategory: str | None = None,
) -> Operation:
    operation = Operation(
        wallet_id=wallet_id, type=type, amount=amount, currency=currency, category=category, subcategory=subcategory
    )
    db.add(operation)
    await db.flush()
    return operation


async def get_operations_list(
    db: AsyncSession,
    wallets_ids: list[int],
    limit: int,
    offset: int,
    date_from: datetime | None,
    date_to: datetime | None,
    type: OperationType | None = None,
    category: str | None = None,
) -> list[Operation]:
    stmt = select(Operation).where(Operation.wallet_id.in_(wallets_ids))

    if date_from is not None:
        stmt = stmt.where(Operation.created_at >= date_from)

    if date_to is not None:
        stmt = stmt.where(Operation.created_at <= date_to)

    if type is not None:
        stmt = stmt.where(Operation.type == type)

    if category is not None:
        stmt = stmt.where(Operation.category == category)

    stmt = stmt.order_by(Operation.created_at.desc(), Operation.id.desc()).limit(limit).offset(offset)
    return list((await db.scalars(stmt)).all())


async def delete_operations_by_wallet(db: AsyncSession, wallet_id: int) -> None:
    await db.execute(delete(Operation).where(Operation.wallet_id == wallet_id))


async def get_expenses_by_category(
    db: AsyncSession,
    wallets_ids: list[int],
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    total = func.sum(Operation.amount).label("total")
    count = func.count(Operation.id).label("count")

    stmt = select(Operation.category, Operation.currency, total, count).where(
        Operation.wallet_id.in_(wallets_ids), Operation.type == OperationType.EXPENSE
    )

    if date_from is not None:
        stmt = stmt.where(Operation.created_at >= date_from)
    if date_to is not None:
        stmt = stmt.where(Operation.created_at <= date_to)
    stmt = stmt.group_by(Operation.category, Operation.currency).order_by(total.desc())
    return list((await db.execute(stmt)).all())
