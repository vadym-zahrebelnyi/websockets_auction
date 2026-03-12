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
    price: Annotated[Decimal, Field(examples=["100.0"])]
    end_time: datetime


class LotCreateSchema(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=255)]
    price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    duration_minutes: Annotated[int, Field(ge=settings.auction.min_duration_minutes)]


class BidCreateSchema(BaseModel):
    bidder: Annotated[str, Field(min_length=3, max_length=63)]
    amount: Annotated[
        Decimal,
        Field(ge=settings.auction.min_bid_step, max_digits=12, decimal_places=2),
    ]
