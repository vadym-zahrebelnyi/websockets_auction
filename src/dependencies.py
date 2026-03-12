from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import AsyncSessionLocal
from src.service import AuctionService

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_auction_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuctionService:
    return AuctionService(db)
