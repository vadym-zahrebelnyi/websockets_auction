from functools import lru_cache
from typing import Annotated
from decimal import Decimal

from pydantic import BaseModel, Field, PostgresDsn, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


NonEmptyStr = Annotated[str, Field(min_length=1)]
Port = Annotated[PositiveInt, Field(le=65535)]
BidDecimal = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class DatabaseSettings(BaseModel):
    user: NonEmptyStr
    password: NonEmptyStr
    host: NonEmptyStr
    port: Port
    name: NonEmptyStr

    @property
    def url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.name,
        )


class AuctionSettings(BaseModel):
    time_extension: PositiveInt
    min_bid_step: BidDecimal
    min_duration_minutes: PositiveInt


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )

    auction: AuctionSettings
    db: DatabaseSettings


@lru_cache
def get_settings() -> Settings:
    return Settings()
