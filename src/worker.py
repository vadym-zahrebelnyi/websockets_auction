import asyncio

from src.config import get_settings
from src.db import AsyncSessionLocal
from src.service import AuctionService


settings = get_settings()

async def run_auction_worker():
    while True:
        async with AsyncSessionLocal() as session:
            service = AuctionService(session)
            await service.end_expired_lots()

        await asyncio.sleep(settings.auction.lots_check_interval_seconds)
