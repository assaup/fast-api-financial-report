from app.schemas import CreateWalletRequest
from app.service import wallets as wallets_service
from fastapi import Depends, Path, status, APIRouter
from sqlalchemy.orm import Session
from app.dependency import get_db, get_current_user
from app.models import User
from app.schemas import WalletResponse, WalletUpdateRequest
from typing import Annotated


router = APIRouter()

@router.get("/balance")
async def get_balance(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return await wallets_service.get_total_balance(db, current_user)

@router.post("/wallets", response_model=WalletResponse)
def create_wallet(wallet: CreateWalletRequest, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return wallets_service.create_wallet(db, current_user, wallet)
    
@router.get("/wallets", response_model=list[WalletResponse])
def get_all_wallets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return wallets_service.get_all_wallets(db, current_user)

@router.get('/wallets/{wallet_id}', response_model=WalletResponse)
def get_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return wallets_service.get_wallet(db, current_user, wallet_id)

@router.patch("/wallets/{wallet_id}", response_model=WalletResponse)
def update_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    payload: WalletUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return wallets_service.update_wallet(db, current_user, wallet_id, payload)

@router.delete("/wallets/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(
    wallet_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
)-> None:
    wallets_service.delete_wallet(db, current_user, wallet_id)
