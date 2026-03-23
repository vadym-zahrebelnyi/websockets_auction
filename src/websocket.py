import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect, status


class WSConnectionManager:
    """Manages WebSocket connections for auction lots."""

    def __init__(self):
        """Initializes the manager with an empty connection map."""
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, lot_id: int, ws: WebSocket):
        """Accepts and registers a WebSocket connection."""
        await ws.accept()
        self.active_connections[lot_id].add(ws)

    def disconnect(self, lot_id: int, ws: WebSocket):
        """Unregisters a WebSocket connection."""
        if lot_id in self.active_connections:
            self.active_connections[lot_id].discard(ws)
            if not self.active_connections[lot_id]:
                del self.active_connections[lot_id]

    async def _send_to_connection(
        self, lot_id: int, connection: WebSocket, message: dict
    ):
        """Helper to send a message to a single connection and handle disconnect."""
        try:
            await connection.send_json(message)
        except (WebSocketDisconnect, Exception):
            self.disconnect(lot_id, connection)

    async def broadcast(self, lot_id: int, message: dict):
        """Sends a JSON message to all clients subscribed to a specific lot concurrently."""
        connections = list(self.active_connections.get(lot_id, []))
        if not connections:
            return

        tasks = [
            self._send_to_connection(lot_id, conn, message) for conn in connections
        ]
        await asyncio.gather(*tasks)

    async def subscribe(self, lot_id: int, websocket: WebSocket, lot_exists: bool = True):
        """
        Handles the entire WebSocket lifecycle: validation, connection, listening, and cleanup.
        
        Args:
            lot_id (int): The ID of the lot.
            websocket (WebSocket): The WebSocket connection object.
            lot_exists (bool): Whether the lot exists to allow subscription.
        """
        if not lot_exists:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await self.connect(lot_id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            self.disconnect(lot_id, websocket)
            try:
                await websocket.close()
            except Exception:
                pass

    async def close_all(self):
        """Closes all active WebSocket connections concurrently."""
        await asyncio.gather(
            *(
                conn.close()
                for conns in self.active_connections.values()
                for conn in conns
            ),
            return_exceptions=True,
        )
        self.active_connections.clear()
