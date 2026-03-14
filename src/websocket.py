from collections import defaultdict

from fastapi import WebSocket


class WSConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = defaultdict()

    async def connect(self, lot_id: int, ws: WebSocket):
        await ws.accept()
        self.active_connections[lot_id].add(ws)

    def disconnect(self, lot_id: int, ws: WebSocket):
        self.active_connections[lot_id].discard(ws)

        if not self.active_connections[lot_id]:
            del self.active_connections[lot_id]

    async def broadcast(self, lot_id: int, message: dict):
        for connection in self.active_connections[lot_id]:
            await connection.send_json(message)