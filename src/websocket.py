from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

class WSConnectionManager:
    """Manages WebSocket connections for auction lots."""
    def __init__(self):
        """Initializes the manager with an empty connection map."""
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, lot_id: int, ws: WebSocket):
        """
        Accepts a WebSocket connection and registers it for a lot.

        Args:
            lot_id (int): The ID of the lot to subscribe to.
            ws (WebSocket): The WebSocket connection object.
        """
        await ws.accept()
        self.active_connections[lot_id].add(ws)

    def disconnect(self, lot_id: int, ws: WebSocket):
        """
        Unregisters a WebSocket connection from a lot.

        Args:
            lot_id (int): The ID of the lot to unsubscribe from.
            ws (WebSocket): The WebSocket connection object.
        """
        if lot_id in self.active_connections:
            self.active_connections[lot_id].discard(ws)
            if not self.active_connections[lot_id]:
                del self.active_connections[lot_id]

    async def broadcast(self, lot_id: int, message: dict):
        """
        Sends a JSON message to all clients subscribed to a specific lot.

        Args:
            lot_id (int): The ID of the lot to broadcast a message for.
            message (dict): The message data to send.
        """
        if lot_id not in self.active_connections:
            return

        for connection in list(self.active_connections[lot_id]):
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(lot_id, connection)