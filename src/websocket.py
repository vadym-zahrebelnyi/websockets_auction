from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

class WSConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, lot_id: int, ws: WebSocket):
        await ws.accept()
        self.active_connections[lot_id].add(ws)

    def disconnect(self, lot_id: int, ws: WebSocket):
        if lot_id in self.active_connections:
            self.active_connections[lot_id].discard(ws)
            if not self.active_connections[lot_id]:
                del self.active_connections[lot_id]

    async def broadcast(self, lot_id: int, message: dict):
        if lot_id not in self.active_connections:
            return
            
        for connection in list(self.active_connections[lot_id]):
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(lot_id, connection)