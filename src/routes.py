from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.dependencies import get_auction_service
from src.schemas import LotReadSchema, LotCreateSchema, BidCreateSchema
from src.service import AuctionService
from src.exceptions import (
    AuctionException,
    LotNotFoundException,
)


router = APIRouter(
    tags=["lots"],
)

AService = Annotated[AuctionService, Depends(get_auction_service)]

@router.get(
    "/lots",
    response_model=list[LotReadSchema],
)
async def read_lots(service: AService):
    return await service.get_lots()


@router.post(
    "/lots",
    response_model=LotReadSchema,
    status_code=status.HTTP_201_CREATED,
)
async def open_lot(lot_data: LotCreateSchema, service: AService):
    try:
        return await service.create_lot(lot_data)
    except AuctionException as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=e.message)


@router.post(
    "/lots/{lot_id}/bids",
    status_code=status.HTTP_201_CREATED,
)
async def place_bid(lot_id: int, bid_data: BidCreateSchema, service: AService):
    try:
        return await service.place_bid(lot_id, bid_data)
    except LotNotFoundException as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message)
    except AuctionException as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=e.message)
