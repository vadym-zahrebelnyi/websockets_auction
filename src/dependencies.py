from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import AsyncSessionLocal
from src.service import AuctionService
from src.websocket import WSConnectionManager

ws_manager = WSConnectionManager()

async def get_db():
    """Provides an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_ws_manager() -> WSConnectionManager:
    """Provides the singleton instance of the WebSocket connection manager."""
    return ws_manager

async def get_auction_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    ws: Annotated[WSConnectionManager, Depends(get_ws_manager)]
) -> AuctionService:
    """Provides an AuctionService instance initialized with its dependencies."""
    return AuctionService(db, ws)

