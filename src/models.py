from datetime import datetime
from enum import StrEnum
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Numeric,
    String,
    Enum,
    CheckConstraint,
    func,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LotStatusEnum(StrEnum):
    RUNNING = "running"
    ENDED = "ended"


class Lot(Base):
    __tablename__ = "lots"
    __table_args__ = (CheckConstraint("price > 0", name="check_price_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[LotStatusEnum] = mapped_column(
        Enum(LotStatusEnum), default=LotStatusEnum.RUNNING, nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    bids: Mapped[list["Bid"]] = relationship(
        back_populates="lot", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lot(id={self.id}, title='{self.title}', status={self.status})>"


class Bid(Base):
    __tablename__ = "bids"
    __table_args__ = (CheckConstraint("amount > 0", name="check_amount_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"), nullable=False)
    bidder: Mapped[str] = mapped_column(String(63), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lot: Mapped["Lot"] = relationship(back_populates="bids")

    def __repr__(self) -> str:
        return f"<Bid(id={self.id}, lot={self.lot.title}, bidder='{self.bidder}')>"
