from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException


from app.models import User
from app.repository import operations as operations_repository
from app.schemas import ExpenseStatsItem
from app.service.wallets import get_wallet_ids


def get_expenses_by_category(
    db: Session,
    current_user: User,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[ExpenseStatsItem]:
    
    wallets_ids = get_wallet_ids(db, current_user.id, wallet_id)

    if date_to and date_from and date_to < date_from:
        raise HTTPException(400, detail="date_from must be earlier than or equal to date_to")

    rows = operations_repository.get_expenses_by_category(
        db,
        wallets_ids=wallets_ids,
        date_from=date_from,
        date_to=date_to
    )
    return [ExpenseStatsItem.model_validate(row) for row in rows]


