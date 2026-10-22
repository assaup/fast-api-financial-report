from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import AUTH_ERRORS, error_responses
from app.dependency import Pagination, get_current_user, get_db
from app.enum import OperationType
from app.exceptions import InsufficientFundsError, WalletNotFoundError
from app.models import User
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
from app.service import operations as operations_service

router = APIRouter(responses=error_responses(*AUTH_ERRORS))


@router.post(
    "/operation/income", response_model=OperationResponse, responses=error_responses(WalletNotFoundError("card"))
)
async def add_income(
    operation: OperationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await operations_service.add_income(db, current_user, operation)


@router.post(
    "/operation/expense",
    response_model=OperationResponse,
    responses=error_responses(WalletNotFoundError("card"), InsufficientFundsError(100, 200, "rub")),
)
async def add_expense(
    operation: OperationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await operations_service.add_expense(db, current_user, operation)


@router.get("/operations", response_model=list[OperationResponse], responses=error_responses(WalletNotFoundError(5)))
async def get_operations_list(
    pagination: Annotated[Pagination, Depends()],
    wallet_id: int | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    type: OperationType | None = Query(None),
    category: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await operations_service.get_operations_list(
        db, user, pagination, wallet_id, date_from, date_to, type, category
    )


@router.post(
    "/operation/transfer",
    response_model=OperationResponse,
    responses=error_responses(WalletNotFoundError("100"), InsufficientFundsError(100, 200, "rub")),
)
async def create_transfer(
    payload: TransferCreateSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await operations_service.transfer_between_wallets(
        db, user.id, payload.from_wallet_id, payload.to_wallet_id, payload.amount
    )
