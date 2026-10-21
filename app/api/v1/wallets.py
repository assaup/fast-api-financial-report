from app.schemas import CreateWalletRequest
from app.service import wallets as wallets_service
from fastapi import Depends, Path, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependency import get_db, get_current_user, Pagination
from app.models import User
from app.schemas import WalletResponse, WalletUpdateRequest
from typing import Annotated


router = APIRouter()

@router.get("/balance")
async def get_balance(db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return await wallets_service.get_total_balance(db, current_user)

@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(wallet: CreateWalletRequest, db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return await wallets_service.create_wallet(db, current_user, wallet)
    
@router.get("/wallets", response_model=list[WalletResponse])
async def get_all_wallets(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        pagination: Pagination = Depends(),
    ):
    return await wallets_service.get_all_wallets(db, current_user, pagination)

@router.get('/wallets/{wallet_id}', response_model=WalletResponse)
async def get_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await wallets_service.get_wallet(db, current_user, wallet_id)

@router.patch("/wallets/{wallet_id}", response_model=WalletResponse)
async def update_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    payload: WalletUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await wallets_service.update_wallet(db, current_user, wallet_id, payload)

@router.delete("/wallets/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
)-> None:
    await wallets_service.delete_wallet(db, current_user, wallet_id)
