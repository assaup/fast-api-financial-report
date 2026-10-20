from app.models import Wallet
from decimal import Decimal
from sqlalchemy.orm import Session
from app.enum import CurrencyEnum

def get_wallet_balance_by_name(db: Session, user_id: int, wallet_name: str) -> Wallet | None:
    return db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()

def get_wallet_by_id(db: Session, user_id: int, wallet_id: int) -> Wallet | None:
    return db.query(Wallet).filter(Wallet.id == wallet_id, Wallet.user_id == user_id).first()

def get_all_wallets(db: Session, user_id: int) -> list[Wallet]:
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()

def create_wallet(db: Session, user_id: int, wallet_name: str, amount: float, currency: CurrencyEnum) -> Wallet:
    wallet = Wallet(name=wallet_name, balance=amount, user_id=user_id, currency=currency)
    db.add(wallet)
    db.flush()
    return wallet

def delete_wallet(db: Session,wallet: Wallet) -> None:
    db.delete(wallet)
    return 
