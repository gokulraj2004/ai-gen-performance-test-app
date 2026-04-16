# Performance Test App

A full-stack web application scaffold built with React (TypeScript), FastAPI (Python), and PostgreSQL. This project provides a production-ready framework with authentication, example CRUD entities, and Docker orchestration.

---

## Tech Stack

| Layer      | Technology                                      |
|------------|------------------------------------------------|
| Frontend   | React 18, TypeScript, Vite, TailwindCSS        |
| Backend    | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2   |
| Database   | PostgreSQL 15                                   |
| Auth       | JWT (access + refresh tokens), bcrypt           |
| DevOps     | Docker, Docker Compose, nginx                   |

---

## Prerequisites

- **Docker** >= 24.0 and **Docker Compose** >= 2.20 (for containerized setup)
- **Node.js** >= 20.0 and **npm** >= 10.0 (for local frontend development)
- **Python** >= 3.11 (for local backend development)
- **PostgreSQL** >= 15 (for local database, or use the Docker service)

---

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd performance-test-app
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set secure values for SECRET_KEY, JWT_SECRET_KEY, DB_PASSWORD
```

### 3. Start with Docker Compose

```bash
docker-compose up --build
```

This starts three services:
- **Frontend** → [http://localhost:3000](http://localhost:3000)
- **Backend API** → [http://localhost:8000](http://localhost:8000)
- **PostgreSQL** → `localhost:5432`

### 4. Run database migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Explore the API

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## Environment Variables

All configuration is managed via environment variables. See [`.env.example`](.env.example) for a complete list with descriptions.

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Application secret key | `change-me-to-a-random-secret-key` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `performance_test_app` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `JWT_SECRET_KEY` | JWT signing secret | `change-me-to-a-random-jwt-secret` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:8000/api/v1` |

---

## Project Structure

```
performance-test-app/
├── frontend/               # React + TypeScript SPA
│   ├── src/
│   │   ├── api/            # Axios client and API call modules
│   │   ├── components/     # Reusable UI, layout, auth, and example components
│   │   ├── context/        # React context providers (Auth)
│   │   ├── hooks/          # Custom React hooks
│   │   ├── pages/          # Route-level page components
│   │   ├── router/         # React Router v6 configuration
│   │   ├── types/          # TypeScript interfaces
│   │   └── utils/          # Helper functions
│   ├── Dockerfile          # Multi-stage build (Node + nginx)
│   └── nginx.conf          # SPA routing configuration
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/            # Route handlers (auth, examples)
│   │   ├── core/           # Security, exceptions, pagination
│   │   ├── middleware/      # CORS configuration
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   └── services/       # Business logic layer
│   ├── alembic/            # Database migrations
│   ├── tests/              # Pytest test suite
│   └── Dockerfile          # Python slim image
│
├── docker-compose.yml      # Multi-service orchestration
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server (with hot reload)
npm run dev
```

The Vite dev server runs on [http://localhost:5173](http://localhost:5173) and proxies API requests to the backend.

---

## Testing

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run linter
ruff check .

# Run type checker
mypy app/
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run tests with coverage
npm run test -- --coverage
```

---

## API Documentation

The FastAPI backend auto-generates interactive API documentation:

- **Swagger UI:** `GET /docs`
- **ReDoc:** `GET /redoc`
- **OpenAPI JSON:** `GET /openapi.json`

### Key Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/v1/auth/register` | Register new user | No |
| `POST` | `/api/v1/auth/login` | Login | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Refresh Token |
| `POST` | `/api/v1/auth/logout` | Logout (blocklist token) | Access Token |
| `GET` | `/api/v1/auth/me` | Get current user | Access Token |
| `PUT` | `/api/v1/auth/me` | Update current user | Access Token |
| `GET` | `/api/v1/items` | List items (paginated) | Access Token |
| `POST` | `/api/v1/items` | Create item | Access Token |
| `GET` | `/api/v1/items/{id}` | Get item | Access Token |
| `PUT` | `/api/v1/items/{id}` | Update item (owner) | Access Token |
| `DELETE` | `/api/v1/items/{id}` | Delete item (owner) | Access Token |
| `GET` | `/api/v1/tags` | List tags | No |
| `POST` | `/api/v1/tags` | Create tag | Access Token |
| `GET` | `/api/health` | Health check | No |

---

## Customizing This Scaffold

This project includes **example entities** (Item, Tag) to demonstrate patterns. To build your own application:

1. **Backend:** Delete `app/models/examples.py`, `app/schemas/examples.py`, `app/api/v1/examples.py`, `app/services/example_service.py`
2. **Frontend:** Delete `src/components/examples/`, `src/types/examples.ts`, `src/api/items.ts`, `src/hooks/useItems.ts`, `src/pages/ItemsPage.tsx`, `src/pages/ItemDetailPage.tsx`
3. Create your own domain models, schemas, services, and components following the same patterns.
4. Keep the authentication system — it's production-ready.

---

## Deployment

### Production Considerations

1. **Environment:** Set `APP_ENV=production` and `DEBUG=false`
2. **Secrets:** Use strong, unique values for `SECRET_KEY`, `JWT_SECRET_KEY`, and `DB_PASSWORD`
3. **HTTPS:** Configure TLS termination at your load balancer or reverse proxy
4. **Database:** Use a managed PostgreSQL service with backups enabled
5. **CORS:** Restrict `CORS_ORIGINS` to your production domain(s)

### CI/CD Pipeline (Suggested)

```
Push → Lint & Type Check → Run Tests → Build Docker Images → Push to Registry → Deploy
```

---

## License

This project is provided as a scaffold. Apply your own license as needed.