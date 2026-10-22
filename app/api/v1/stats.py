from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import AUTH_ERRORS, error_responses
from app.dependency import get_current_user, get_db
from app.exceptions import InvalidDateRangeError, WalletNotFoundError
from app.models import User
from app.schemas import ExpenseStatsItem
from app.service import stats as stats_service

router = APIRouter(responses=error_responses(*AUTH_ERRORS))


@router.get(
    "/stats/expenses",
    response_model=list[ExpenseStatsItem],
    responses=error_responses(InvalidDateRangeError(), WalletNotFoundError(5)),
)
async def get_expenses_by_category(
    wallet_id: int | None = Query(None, gt=0),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await stats_service.get_expenses_by_category(
        db, current_user, wallet_id=wallet_id, date_from=date_from, date_to=date_to
    )
