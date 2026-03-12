from fastapi import FastAPI, WebSocket

from src.routes import lot_router


app = FastAPI()

app.include_router(lot_router)
