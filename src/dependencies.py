from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import AsyncSessionLocal
from src.service import AuctionService
from src.websocket import WSConnectionManager

ws_manager = WSConnectionManager()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_ws_manager() -> WSConnectionManager:
    return ws_manager

def get_auction_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    ws: Annotated[WSConnectionManager, Depends(get_ws_manager)] | None = None
) -> AuctionService:
    return AuctionService(db, ws)

