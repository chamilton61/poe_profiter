# poe_profiter
FastAPI application to assist with keeping tabs on difficult to track items and their prices.

## Features

- FastAPI web framework
- PostgreSQL database with SQLAlchemy ORM
- Repository pattern for clean separation of concerns
- Docker and Docker Compose for easy deployment
- RESTful API endpoints for items and prices

## Project Structure

```
app/
├── core/           # Core configuration and database setup
├── models/         # SQLAlchemy models
├── repositories/   # Repository pattern implementation
├── schemas/        # Pydantic schemas for validation
└── main.py         # FastAPI application and routes
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running with Docker Compose

1. Clone the repository
2. Run the application:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

### API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

- `GET /` - Hello World endpoint
- `GET /health` - Health check endpoint
- `POST /items/` - Create a new item
- `GET /items/` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `GET /items/category/{category}` - Get items by category
- `POST /items/{item_id}/prices/` - Add a price for an item
- `GET /items/{item_id}/prices/` - Get all prices for an item
