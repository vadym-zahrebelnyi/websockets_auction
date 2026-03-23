import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.routes import router
from src.worker import run_auction_worker
from src.dependencies import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(run_auction_worker())
    
    yield
    
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    await ws_manager.close_all()


app = FastAPI(
    title="Auction Service API",
    description="Real-time auction service with WebSocket support for live bid updates.",
    lifespan=lifespan,
)

app.include_router(router)
