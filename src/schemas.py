from decimal import Decimal
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.models import LotStatusEnum
from src.config import get_settings


settings = get_settings()


class LotReadSchema(BaseModel):
    """Schema for reading lot information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: LotStatusEnum
    price: Annotated[Decimal, Field(examples=["100.00"])]
    end_time: datetime


class LotCreateSchema(BaseModel):
    """Schema for creating a new lot."""

    title: Annotated[str, Field(min_length=3, max_length=255, examples=["Lot title"])]
    price: Annotated[
        Decimal, Field(gt=0, max_digits=12, decimal_places=2, examples=["100.00"])
    ]
    duration_minutes: Annotated[
        int, Field(ge=settings.auction.min_duration_minutes, examples=["15"])
    ]


class BidCreateSchema(BaseModel):
    """Schema for placing a bid."""

    bidder: Annotated[str, Field(min_length=3, max_length=63, examples=["John"])]
    amount: Annotated[
        Decimal,
        Field(
            ge=settings.auction.min_bid_step,
            max_digits=12,
            decimal_places=2,
            examples=["120"],
        ),
    ]


class BidReadSchema(BaseModel):
    """Schema for reading bid information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    bidder: str
    amount: Decimal
    timestamp: datetime


class BidPlacedReadSchema(BaseModel):
    """Schema for bid notification message via WebSocket."""

    model_config = ConfigDict(from_attributes=True)

    type: str = "bid_placed"
    lot_id: int
    bidder: str
    amount: Annotated[Decimal, Field(examples=["100.00"])]
