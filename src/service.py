from datetime import datetime, timezone, timedelta
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.config import get_settings
from src.exceptions import (
    LotCreateException,
    LotEndedException,
    LotNotFoundException,
    BidTooLowException,
    BidCreateException,
)
from src.models import Lot, LotStatusEnum, Bid
from src.schemas import LotCreateSchema, BidCreateSchema

settings = get_settings()

class AuctionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_lots(self) -> Sequence[Lot]:
        result = await self.db.execute(select(Lot))
        return result.scalars().all()

    async def create_lot(self, lot_data: LotCreateSchema) -> Lot:
        lot = Lot(
            title=lot_data.title,
            price=lot_data.price,
            end_time=datetime.now(timezone.utc)
            + timedelta(minutes=lot_data.duration_minutes),
        )
        try:
            self.db.add(lot)
            await self.db.commit()
            await self.db.refresh(lot)
            return lot
        except IntegrityError as e:
            await self.db.rollback()
            raise LotCreateException()

    async def place_bid(self, lot_id: int, bid_data: BidCreateSchema) -> Bid:
        lot = await self.db.get(Lot, lot_id)
        if not lot:
            raise LotNotFoundException()

        time_remaining = (lot.end_time - datetime.now(timezone.utc)).total_seconds()
        if time_remaining <= 0:
            lot.status = LotStatusEnum.ENDED
            try:
                self.db.add(lot)
                await self.db.commit()
            except IntegrityError:
                await self.db.rollback()
                raise BidCreateException()

        if lot.status == LotStatusEnum.ENDED:
            raise LotEndedException()
        
        if lot.price >= bid_data.amount:
            raise BidTooLowException()

        if time_remaining < settings.auction.time_extension_seconds:
            lot.end_time += timedelta(seconds=settings.auction.time_extension_seconds)

        lot.price = bid_data.amount
        
        bid = Bid(
            lot_id=lot_id,
            bidder=bid_data.bidder,
            amount=bid_data.amount
        )

        try:
            self.db.add(bid)
            self.db.add(lot)
            await self.db.commit()
            await self.db.refresh(bid)
            return bid
        except IntegrityError:
            await self.db.rollback()
            raise BidCreateException()


    async def end_expired_lots(self) -> None:
        stmt = (
            update(Lot)
            .where(Lot.status == LotStatusEnum.RUNNING)
            .where(Lot.end_time <= func.now())
            .values(status=LotStatusEnum.ENDED)
        )

        await self.db.execute(stmt)
        await self.db.commit()
