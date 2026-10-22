from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import InvalidDateRangeError, InsufficientFundsError, WalletNotEmptyError
from app.models import User
from app.repository import operations as operations_repository
from app.schemas import ExpenseStatsItem
from app.service.wallets import get_wallet_ids


async def get_expenses_by_category(
    db: AsyncSession,
    current_user: User,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[ExpenseStatsItem]:
    
    wallets_ids = await get_wallet_ids(db, current_user.id, wallet_id)

    if date_to and date_from and date_to < date_from:
        raise InvalidDateRangeError()

    rows = await operations_repository.get_expenses_by_category(
        db,
        wallets_ids=wallets_ids,
        date_from=date_from,
        date_to=date_to
    )
    return [ExpenseStatsItem.model_validate(row) for row in rows]


