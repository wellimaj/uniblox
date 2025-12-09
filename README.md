# Ecommerce Store

A full-stack ecommerce application built with FastAPI (Python), React (TypeScript), and PostgreSQL, all containerized with Docker.

## Features

- **Product Catalog**: Browse available items
- **Shopping Cart**: Add/remove items from cart
- **Checkout**: Complete orders with optional discount codes
- **Discount System**: Every 5th order automatically generates a 10% discount code
- **Admin Panel**: View statistics and generate discount codes

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Project Structure

```
uniblox/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── database.py      # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── routers/         # API route handlers
│   │       ├── cart.py
│   │       ├── checkout.py
│   │       ├── admin.py
│   │       └── items.py
│   ├── tests/               # Unit tests
│   ├── requirements.txt
│   └── seed_data.py         # Database seeding script
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types
│   │   └── index.css        # Styles
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Backend Dockerfile
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Docker daemon running
- Git

### Installation & Running

1. **Ensure Docker is running**:
   ```bash
   docker ps
   ```
   If you get an error, start Docker:
   - **Docker Desktop**: Open the Docker Desktop application
   - **Docker service (Linux)**: `sudo systemctl start docker`

2. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd uniblox
   ```

3. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```
   
   Or use the provided script:
   ```bash
   ./start.sh
   ```

4. **Restart services** (if already running):
   ```bash
   ./start.sh restart
   ```
   
   Or manually:
   ```bash
   docker-compose restart
   ```

5. **Stop services**:
   ```bash
   ./start.sh stop
   ```
   
   Or manually:
   ```bash
   docker-compose stop
   ```

   This will:
   - Start PostgreSQL database
   - Start FastAPI backend on port 8000
   - Start React frontend on port 3000
   - Seed the database with sample products

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Troubleshooting

**Docker Connection Error**:
If you see `Connection refused` errors:
- **Docker Desktop not running**: The script will automatically try to use the system Docker socket (`/var/run/docker.sock`) if Docker Desktop isn't available
- **Manual fix**: Export `DOCKER_HOST=unix:///var/run/docker.sock` before running commands
- **Verify Docker is accessible**: `docker ps` should list running containers
- **Start Docker service (Linux)**: `sudo systemctl start docker`

**Port Already in Use**:
If ports 3000, 8000, or 5432 are already in use:
- The PostgreSQL container uses port **5433** on the host (mapped from 5432 in container)
- To change ports, modify the port mappings in `docker-compose.yml`
- Example: Change `"5433:5432"` to `"5434:5432"` if 5433 is also in use

**ContainerConfig Error**:
If you see `KeyError: 'ContainerConfig'` errors:
- Clean up old containers: `./start.sh clean` or `docker-compose down -v`
- This usually happens when containers were created with incompatible Docker versions

### Running Tests

To run the backend unit tests:

```bash
docker-compose exec backend pytest
```

Or run tests locally (requires Python 3.11+):

```bash
cd backend
pip install -r requirements.txt
pytest
```

## API Endpoints

### Items
- `GET /api/items/` - Get all items
- `POST /api/items/` - Create a new item (admin)

### Cart
- `POST /api/cart/add?user_id={user_id}` - Add item to cart
- `GET /api/cart/{user_id}` - Get user's cart
- `DELETE /api/cart/{user_id}/item/{item_id}` - Remove item from cart
- `DELETE /api/cart/{user_id}/clear` - Clear entire cart

### Checkout
- `POST /api/checkout/` - Process checkout
  ```json
  {
    "user_id": "user_123",
    "discount_code": "SAVE10_1" // optional
  }
  ```

### Admin
- `GET /api/admin/stats` - Get store statistics
- `POST /api/admin/discount/generate` - Generate discount code (if conditions met)

## Discount Code System

- Every 5th order automatically generates a 10% discount code
- Discount codes can be used only once
- Discount applies to the entire order
- Admin can manually generate discount codes when conditions are met (every 5th order)

## Development

### Backend Development

The backend uses FastAPI with SQLAlchemy ORM. The database models are defined in `app/models.py` and API routes are in `app/routers/`.

Key files:
- `app/main.py` - FastAPI app initialization
- `app/database.py` - Database connection and session management
- `app/models.py` - SQLAlchemy models
- `app/schemas.py` - Pydantic models for request/response validation

### Frontend Development

The frontend is built with React and TypeScript using Vite as the build tool.

Key files:
- `src/App.tsx` - Main application component
- `src/api.ts` - API client functions
- `src/types.ts` - TypeScript type definitions

### Database

The application uses PostgreSQL. Tables are automatically created on startup. To seed sample data, the `seed_data.py` script runs automatically in Docker.

## Testing

Unit tests are located in `backend/tests/`. They test:
- Cart operations (add, remove, get)
- Checkout functionality (with and without discount codes)
- Admin statistics

Run tests with:
```bash
pytest backend/tests/
```

## Assumptions & Design Decisions

1. **User ID**: Currently using a simple string user ID. In production, this would be replaced with proper authentication.

2. **Nth Order**: Set to 5 orders. This can be easily changed in `backend/app/routers/checkout.py` and `backend/app/routers/admin.py`.

3. **Discount Percentage**: Fixed at 10% for all discount codes.

4. **Database**: Uses PostgreSQL in Docker. Data persists in a Docker volume.

5. **CORS**: Backend allows requests from `http://localhost:3000` for development.

## Future Improvements

- User authentication and authorization
- Payment integration
- Order history for users
- Product search and filtering
- Inventory management
- Email notifications for orders and discount codes
- More comprehensive error handling
- API rate limiting
- Logging and monitoring

## License

This project is created for demonstration purposes.
