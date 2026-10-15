from decimal import Decimal
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Wallet(Base):
    __tablename__ = "wallet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[Decimal]