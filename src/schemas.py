from decimal import Decimal
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.models import LotStatusEnum
from src.config import get_settings


settings = get_settings()


class LotReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: LotStatusEnum
    price: Annotated[Decimal, Field(examples=["100.00"])]
    end_time: datetime


class LotCreateSchema(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=255, examples=["Lot title"])]
    price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2, examples=["100.00"])]
    duration_minutes: Annotated[int, Field(ge=settings.auction.min_duration_minutes, examples=["15"])]


class BidCreateSchema(BaseModel):
    bidder: Annotated[str, Field(min_length=3, max_length=63, examples=["John"])]
    amount: Annotated[
        Decimal,
        Field(ge=settings.auction.min_bid_step, max_digits=12, decimal_places=2, examples=["120"]),
    ]



class BidPlacedReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = "bid_placed"
    lot_id: int
    bidder: str
    amount: Annotated[Decimal, Field(examples=["100.00"])]