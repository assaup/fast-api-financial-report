from fastapi import HTTPException
from app.schemas import CreateWalletRequest, WalletResponse, TotalBalance, WalletUpdateRequest
from app.repository import wallets as wallets_repository
from app.models import User, Wallet
from decimal import Decimal
from app.enum import CurrencyEnum
from app.service import exchange_service
from app.repository import operations as operations_repository
from app.dependency import Pagination
from sqlalchemy.ext.asyncio import AsyncSession


async def get_total_balance(db: AsyncSession, current_user: User) -> TotalBalance:
    wallets = await wallets_repository.get_all_wallets(db, current_user.id)
    total_balance = Decimal(0)
    for wallet in wallets:
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            exchange_rate = await exchange_service.get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
            total_balance += exchange_rate * wallet.balance
            
    return TotalBalance(total_balance=total_balance)


async def create_wallet(db: AsyncSession, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:
    if await wallets_repository.get_wallet_balance_by_name(db, current_user.id, wallet.name):
        raise HTTPException(
            status_code=400,
            detail=f"Wallet '{wallet.name}' already exists"
        )
    wallet = await wallets_repository.create_wallet(db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency)

    await db.commit()

    return WalletResponse.model_validate(wallet)

async def get_all_wallets(db: AsyncSession, current_user: User, pagination: Pagination) -> list[WalletResponse]:
    wallets = await wallets_repository.get_all_wallets(db, current_user.id, pagination.limit, pagination.offset)
    return [WalletResponse.model_validate(wallet) for wallet in wallets]

async def _get_wallet_or_404(db: AsyncSession, user_id: int, wallet_id: int) -> Wallet:
    wallet = await wallets_repository.get_wallet_by_id(db, user_id, wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found")
    return wallet

async def get_wallet(db: AsyncSession, current_user: User, wallet_id: int) -> WalletResponse:
    wallet = await _get_wallet_or_404(db, current_user.id, wallet_id)
    return WalletResponse.model_validate(wallet)

async def update_wallet(db: AsyncSession, current_user: User, wallet_id: int, payload: WalletUpdateRequest) -> WalletResponse:
    wallet = await _get_wallet_or_404(db, current_user.id, wallet_id)
    if payload.name is not None:
        wallet.name = payload.name
    await db.commit()
    return WalletResponse.model_validate(wallet)

async def delete_wallet(db: AsyncSession, current_user: User, wallet_id: int) -> None:
    wallet = await _get_wallet_or_404(db, current_user.id, wallet_id)
    if wallet.balance > 0:
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' has non-zero balance: {wallet.balance}. Withdraw or transfer it first",)
    await operations_repository.delete_operations_by_wallet(db, wallet_id)
    await wallets_repository.delete_wallet(db, wallet)
    await db.commit()


async def get_wallet_ids(db: AsyncSession, user_id: int, wallet_id: int | None = None) -> list[int]:
    if wallet_id is not None:
        wallet = await _get_wallet_or_404(db, user_id, wallet_id)
        return [wallet.id]
    wallets = await wallets_repository.get_all_wallets(db, user_id)
    return [wallet.id for wallet in wallets]