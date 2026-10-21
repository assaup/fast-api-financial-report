from app.models import Wallet
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enum import CurrencyEnum

async def get_wallet_balance_by_name(db: AsyncSession, user_id: int, wallet_name: str) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.name == wallet_name, Wallet.user_id == user_id)
    return await db.scalar(stmt)

async def get_wallet_by_id(db: AsyncSession, user_id: int, wallet_id: int) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
    return await db.scalar(stmt)

async def get_all_wallets(db: AsyncSession, user_id: int, limit: int | None = None, offset: int | None = None) -> list[Wallet]:
    stmt = (
        select(Wallet)
        .where(Wallet.user_id == user_id)
        .order_by(Wallet.id.desc())
        .limit(limit)
        .offset(offset)
        )
    res = await db.scalars(stmt)
    return list(res.all())

async def create_wallet(db: AsyncSession, user_id: int, wallet_name: str, amount: float, currency: CurrencyEnum) -> Wallet:
    wallet = Wallet(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    db.add(wallet)
    await db.flush()
    return wallet

async def delete_wallet(db: AsyncSession, wallet: Wallet) -> None:
    await db.delete(wallet)
