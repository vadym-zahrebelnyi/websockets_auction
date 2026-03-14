# Auction Service (FastAPI + WebSocket)

A real-time auction service implementation.

## Features
- **Create Lots**: Define starting price and auction duration.
- **Place Bids**: Submit bids via REST API.
- **Real-time Updates**: Subscribe to lot events via WebSockets to receive instant notifications about new bids and time extensions.
- **Auto-extension**: The auction time extends automatically if a bid is placed near the end.

## Tech Stack
- **FastAPI**: Main web framework.
- **WebSocket**: Real-time communication.
- **PostgreSQL**: Database for persistence.
- **SQLAlchemy (Async)**: Modern async ORM.
- **Alembic**: Database migrations.
- **Docker**: Containerized deployment.

## Getting Started

1. Create a `.env` file from the provided sample:
   ```bash
   cp .env.sample .env
   ```
   *Note: Ensure the values in `.env` match your local or Docker environment.*

2. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at: `http://localhost:8000`

## API Documentation
Once the server is running, you can explore the interactive API documentation (Swagger UI) at:
- [http://localhost:8000/docs](http://localhost:8000/docs)

## Key Endpoints
- `GET /lots`: List all active auction lots.
- `POST /lots`: Create a new auction lot.
- `POST /lots/{lot_id}/bids`: Place a bid on a specific lot.
- `WS /ws/lots/{lot_id}`: Subscribe to real-time updates for a specific lot.

## WebSocket Message Format
When a bid is placed, all subscribed clients receive a notification in the following format:
```json
{
  "type": "bid_placed",
  "lot_id": 1,
  "bidder": "John",
  "amount": 105
}
```
