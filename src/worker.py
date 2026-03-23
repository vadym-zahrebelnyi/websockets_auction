import asyncio

from src.config import get_settings
from src.db import AsyncSessionLocal
from src.service import AuctionService


settings = get_settings()


async def run_auction_worker():
    """
    Background worker that periodically checks for and closes expired auction lots.
    Runs in an infinite loop until the application is shut down.
    """
    while True:
        async with AsyncSessionLocal() as session:
            service = AuctionService(session, None)
            await service.end_expired_lots()

        await asyncio.sleep(settings.auction.lots_check_interval_seconds)
