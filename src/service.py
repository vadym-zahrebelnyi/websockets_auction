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
from src.schemas import LotCreateSchema, BidCreateSchema, BidPlacedReadSchema

from src.websocket import WSConnectionManager

settings = get_settings()


class AuctionService:
    """Business logic for auction management."""

    def __init__(self, db: AsyncSession, ws: WSConnectionManager):
        """Initializes the service with database session and websocket manager."""
        self.db = db
        self.ws = ws

    async def get_lots(self) -> Sequence[Lot]:
        """
        Retrieves all auction lots from the database.

        Returns:
            Sequence[Lot]: A list of all lot objects found in the database.
        """
        result = await self.db.execute(select(Lot))
        return result.scalars().all()

    async def get_lot(self, lot_id: int) -> Lot | None:
        """
        Retrieves a single lot by its ID.

        Args:
            lot_id (int): The ID of the lot to retrieve.

        Returns:
            Lot | None: The lot object if found, otherwise None.
        """
        return await self.db.get(Lot, lot_id)

    async def subscribe_to_lot(self, lot_id: int, websocket: WebSocket) -> None:
        """
        Starts a WebSocket subscription for a lot after checking its existence.

        Args:
            lot_id (int): The ID of the lot.
            websocket (WebSocket): The WebSocket connection object.
        """
        lot = await self.get_lot(lot_id)
        await self.ws.subscribe(lot_id, websocket, lot_exists=lot is not None)

    async def create_lot(self, lot_data: LotCreateSchema) -> Lot:
        """
        Creates a new auction lot and saves it to the database.

        Args:
            lot_data (LotCreateSchema): The data required to create a new lot (title, price, duration).

        Returns:
            Lot: The newly created lot object with its generated ID and calculated end time.

        Raises:
            LotCreateException: If there is a database integrity error during creation.
        """
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
        except IntegrityError:
            await self.db.rollback()
            raise LotCreateException()

    async def place_bid(self, lot_id: int, bid_data: BidCreateSchema) -> Bid:
        """
        Processes a new bid on a lot.
        Validates lot status, price, and time remaining.
        Broadcasts the new bid to WebSocket subscribers.

        Args:
            lot_id (int): The unique identifier of the lot to bid on.
            bid_data (BidCreateSchema): The bid details (bidder name and amount).

        Returns:
            Bid: The recorded bid object.

        Raises:
            LotNotFoundException: If the lot ID does not exist.
            LotEndedException: If the auction for the lot has already closed.
            BidTooLowException: If the bid amount is not higher than the current price.
            BidCreateException: If there is a database error during processing.
        """
        stmt = select(Lot).where(Lot.id == lot_id).with_for_update()
        result = await self.db.execute(stmt)
        lot = result.scalar_one_or_none()

        if not lot:
            raise LotNotFoundException()

        if lot.status == LotStatusEnum.ENDED:
            raise LotEndedException()

        time_remaining = (lot.end_time - datetime.now(timezone.utc)).total_seconds()
        is_expired = time_remaining <= 0

        bid = None
        if is_expired:
            lot.status = LotStatusEnum.ENDED
        else:
            if lot.price >= bid_data.amount:
                raise BidTooLowException()

            if time_remaining < settings.auction.time_extension_seconds:
                lot.end_time += timedelta(
                    seconds=settings.auction.time_extension_seconds
                )

            lot.price = bid_data.amount
            bid = Bid(lot_id=lot_id, bidder=bid_data.bidder, amount=bid_data.amount)
            self.db.add(bid)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise BidCreateException()

        if is_expired:
            raise LotEndedException()

        await self.db.refresh(bid)
        if self.ws:
            message = BidPlacedReadSchema.model_validate(bid).model_dump(mode="json")
            await self.ws.broadcast(lot_id, message)

        return bid

    async def end_expired_lots(self) -> None:
        """Updates the status of all expired lots to 'ended'."""
        stmt = (
            update(Lot)
            .where(Lot.status == LotStatusEnum.RUNNING)
            .where(Lot.end_time <= func.now())
            .values(status=LotStatusEnum.ENDED)
        )

        await self.db.execute(stmt)
        await self.db.commit()
