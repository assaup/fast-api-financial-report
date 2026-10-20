from decimal import Decimal
from sqlalchemy.orm import Session
from app.enum import CurrencyEnum, OperationType
from app.models import Operation
from datetime import datetime
from sqlalchemy import func

def create_operation(
    db: Session,
    wallet_id: int,
    type: str,
    amount: Decimal,
    currency: CurrencyEnum, 
    category: str | None = None,
    subcategory: str | None =None,
) -> Operation:
    operation = Operation(
        wallet_id=wallet_id,
        type=type,
        amount=amount,
        currency=currency,
        category=category,
        subcategory=subcategory
    )
    db.add(operation)
    db.flush()
    return operation

def get_operations_list(
    db: Session,
    wallets_ids: list[int],
    limit: int,
    offset: int,
    date_from: datetime | None,
    date_to: datetime | None,
    type: OperationType | None = None,
    category: str | None = None
) -> list[Operation]:
    query = db.query(Operation).filter(Operation.wallet_id.in_(wallets_ids))

    if date_from is not None:
        query = query.filter(Operation.created_at >= date_from)

    if date_to is not None:
        query = query.filter(Operation.created_at <= date_to)

    if type is not None:
        query = query.filter(Operation.type == type)

    if category is not None:
        query = query.filter(Operation.category == category)

    return (query
            .order_by(Operation.created_at.desc(), Operation.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
            )

def delete_operations_by_wallet(db: Session, wallet_id: int) -> None:
    db.query(Operation).filter(Operation.wallet_id == wallet_id).delete()

def get_expenses_by_category(
    db: Session,
    wallets_ids: list[int],
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    total = func.sum(Operation.amount).label('total')
    count = func.count(Operation.id).label('count')

    query = (
        db.query(Operation.category, Operation.currency, total, count)
        .filter(
            Operation.wallet_id.in_(wallets_ids),
            Operation.type == OperationType.EXPENSE
        )
    )

    if date_from is not None:
        query = query.filter(Operation.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Operation.created_at <= date_to)

    return (
        query
        .group_by(Operation.category, Operation.currency)
        .order_by(total.desc())
        .all()
    )