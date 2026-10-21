from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db, get_current_user
from app.models import User
from app.schemas import ExpenseStatsItem
from app.service import stats as stats_service

router = APIRouter()

@router.get('/stats/expenses', response_model=list[ExpenseStatsItem])
async def get_expenses_by_category(
    wallet_id: int | None = Query(None, gt=0),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await stats_service.get_expenses_by_category(
        db,
        current_user,
        wallet_id=wallet_id,
        date_from=date_from,
        date_to=date_to
    )