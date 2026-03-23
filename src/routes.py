from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, WebSocket

from src.dependencies import get_auction_service, get_ws_manager
from src.schemas import LotReadSchema, LotCreateSchema, BidCreateSchema, BidReadSchema
from src.service import AuctionService
from src.exceptions import (
    AuctionException,
    LotNotFoundException,
)


router = APIRouter()

AService = Annotated[AuctionService, Depends(get_auction_service)]


@router.get(
    "/lots",
    response_model=list[LotReadSchema],
    summary="Get active lots",
    description="Returns a list of all auction lots available in the database.",
)
async def read_lots(service: AService):
    """
    Retrieves all auction lots from the database.

    Args:
        service (AuctionService): The injected auction service instance.

    Returns:
        list[LotReadSchema]: A list of all lot objects.
    """
    return await service.get_lots()


@router.post(
    "/lots",
    response_model=LotReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lot",
    description="Creates a new auction lot with the specified title, starting price, and duration.",
)
async def open_lot(lot_data: LotCreateSchema, service: AService):
    """
    Creates a new auction lot.

    Args:
        lot_data (LotCreateSchema): The input data for the new lot.
        service (AuctionService): The injected auction service instance.

    Returns:
        LotReadSchema: The created lot details.
    """
    try:
        return await service.create_lot(lot_data)
    except AuctionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/lots/{lot_id:int}/bids",
    response_model=BidReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Place a bid",
    description="Places a bid on a specific lot. Extends the auction time if the bid is placed near the end.",
)
async def place_bid(lot_id: int, bid_data: BidCreateSchema, service: AService):
    """
    Places a bid on a specific lot.

    Args:
        lot_id (int): The ID of the lot.
        bid_data (BidCreateSchema): The bid details.
        service (AuctionService): The injected auction service instance.

    Returns:
        Bid: The recorded bid object.
    """
    try:
        return await service.place_bid(lot_id, bid_data)
    except LotNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except AuctionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.websocket("/ws/lots/{lot_id:int}")
async def lot_subscription(
    lot_id: int,
    websocket: WebSocket,
    service: AService
):
    """
    Subscribes to real-time updates for a specific lot via WebSocket.
    Clients receive notifications about new bids and time extensions.

    Args:
        lot_id (int): The ID of the lot to monitor.
        websocket (WebSocket): The WebSocket connection instance.
        service (AuctionService): The injected auction service instance.
    """
    await service.subscribe_to_lot(lot_id, websocket)
