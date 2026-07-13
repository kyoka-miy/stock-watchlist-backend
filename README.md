# Stock Watchlist

Backend API for a stock watchlist app built with FastAPI.

**Live Demo:** https://stock-watchlist-frontend-gamma.vercel.app/home

---

## Overview

A backend that lets users sign in with Google account, manage watchlists, and view stock prices and financial indicators.

Key features:

- Google OAuth2 login / logout (JWT + Refresh Token)
- Add and remove symbols from a watchlist
- Fetch stock indicators per symbol (price, P/E, P/B, dividend yield, etc.)
- Chart data APIs for price history, dividend history, cash flow, and earnings
- Symbol search via yfinance
- Response caching with Redis

---

## Tech Stack

| Category    | Technology                               |
| ----------- | ---------------------------------------- |
| Language    | Python 3.13                              |
| Framework   | FastAPI                                  |
| ASGI Server | Uvicorn                                  |
| ORM         | SQLAlchemy                               |
| Migration   | Alembic                                  |
| Database    | PostgreSQL                               |
| Cache       | Redis                                    |
| Stock Data  | yfinance                                 |
| Auth        | Google OAuth2 / JWT (PyJWT, python-jose) |
| Validation  | Pydantic v2                              |
| Deploy      | Render                                   |

---

## Getting Started

### Prerequisites

- Python 3.13
- pipenv
- Docker

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/kyoka-miy/stock-watchlist-backend.git
cd stock-watchlist-backend

# 2. Install dependencies
pip install pipenv
pipenv install

# 3. Set up environment variables
cp .env.example .env
# Edit .env and fill in the required values

# 4. Start PostgreSQL and Redis with Docker
docker compose up -d

# 5. Run database migrations
pipenv run upgrade

# 6. Start the development server
pipenv run start
```

The server will be available at http://localhost:8000.  
Swagger UI is accessible at http://localhost:8000/docs.

### Environment Variables (.env)

```env
ENVIRONMENT=development
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_PORT=5432
YAHOO_FINANCE_URL=https://finance.yahoo.com
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL=3600
GOOGLE_CLIENT_ID=your_google_client_id
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
```

---

## Project Structure

```
stock-list-backend/
├── app/
│   ├── main.py                 # FastAPI app initialization and middleware
│   ├── config.py               # Environment variable and settings management (pydantic-settings)
│   ├── db/
│   │   ├── base_class.py       # SQLAlchemy declarative base
│   │   ├── session.py          # Database session
│   │   └── redis_cache.py      # Redis client
│   ├── domain/
│   │   ├── models/             # SQLAlchemy ORM models
│   │   └── schemas/            # Pydantic schemas (request / response)
│   ├── exceptions/
│   │   ├── app_exception.py    # Custom application exception
│   │   └── handlers.py         # Exception handlers (logging + JSON response conversion)
│   ├── presentation/           # FastAPI routers (controller layer)
│   ├── repository/             # Abstract repository interfaces
│   │   └── impl/               # Repository implementations
│   ├── service/                # Abstract service interfaces
│   │   └── impl/               # Service implementations (including yfinance)
│   ├── usecase/                # Use case layer (business logic)
│   └── util/                   # Shared utilities, constants, and enums
├── migration/
│   ├── env.py                  # Alembic environment configuration
│   └── versions/               # Migration files
├── docker-compose.yml          # Local PostgreSQL and Redis containers
├── alembic.ini                 # Alembic configuration
└── Pipfile                     # Dependency definitions
```
