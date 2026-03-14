import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.routes import router
from src.worker import run_auction_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(run_auction_worker())
    
    yield
    
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        return


app = FastAPI(lifespan=lifespan)

app.include_router(router)
