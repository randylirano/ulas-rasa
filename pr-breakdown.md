# Ulas Rasa — PR Breakdown

## Current State
- ✅ Backend folder scaffolded with FastAPI project structure
- ✅ Poetry set up with FastAPI + Uvicorn + Pydantic Settings
- ✅ `config.py` with environment variable management
- ✅ `main.py` with root and health check endpoints
- ✅ `businesses` router scaffolded with placeholder endpoints

---

## PR 1 — Backend Foundation & Configuration

### What this PR is about
Establishes the foundational backend setup. This includes finalizing the project structure, environment configuration, CORS middleware, and a working health check endpoint. This PR has no business logic or database — it is purely about getting a clean, well-configured FastAPI app running locally.

### Changes
- Finalize `app/config.py` with all required settings (app name, environment, CORS origins)
- Update `app/main.py` to register CORS middleware using `allowed_origins` from config
- Add `GET /health` endpoint that returns environment info
- Add `GET /` root endpoint
- Create `.env` file for local development (not committed)
- Create `.env.example` file with placeholder values (committed as reference for other developers)
- Add `.gitignore` for `backend/` covering `.env`, `.venv`, `__pycache__`

### Testing Strategy
- Manually visit `http://localhost:8000` and `http://localhost:8000/health`
- Verify `/health` returns correct environment value from `.env`
- Verify `/docs` and `/redoc` are accessible locally
- Test CORS by making a `fetch` call from browser console on a different port

### Reading Materials

**Official**
- FastAPI Bigger Applications: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- FastAPI CORS Middleware: https://fastapi.tiangolo.com/tutorial/cors/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

**Community**
- Real Python — Python dotenv guide: https://realpython.com/python-dotenv/

---

## PR 2 — Database Connection & Schema

### What this PR is about
Sets up the PostgreSQL connection and defines the initial database schema with raw SQL. No ORM — tables are created manually using SQL migration files. This PR is about establishing the database layer and understanding the schema before writing any application logic.

### Changes
- Install `psycopg` (PostgreSQL driver for Python)
- Create `app/database/connection.py` — manages PostgreSQL connection pool
- Create `migrations/` folder at the root of `backend/`
- Write `migrations/001_initial_schema.sql` with the following tables:
  - `users` — id, name, email, password_hash, created_at
  - `businesses` — id, name, address, city, state, phone, website, created_at
  - `categories` — id, name
  - `business_categories` — business_id, category_id (join table)
  - `reviews` — id, user_id, business_id, rating, body, created_at
- Update `.env` with `DATABASE_URL=postgresql://localhost:5432/ulas_rasa`
- Create the local database: `createdb ulas_rasa`
- Run the migration manually: `psql ulas_rasa < migrations/001_initial_schema.sql`

### Testing Strategy
- Connect to the database with `psql ulas_rasa` and verify tables were created with `\dt`
- Verify foreign key constraints work by attempting to insert an invalid reference
- Verify the connection pool initializes correctly when the FastAPI app starts

### Reading Materials

**Official**
- PostgreSQL Tutorial: https://www.postgresql.org/docs/current/tutorial.html
- PostgreSQL Data Types: https://www.postgresql.org/docs/current/datatype.html
- psycopg3 Connection docs: https://www.psycopg.org/psycopg3/docs/basic/usage.html

**Community**
- Full Stack Python — PostgreSQL: https://www.fullstackpython.com/postgresql.html

---

## PR 3 — Businesses Endpoints

### What this PR is about
Implements the first full feature — the businesses resource. This is the first PR that touches all layers: router, service, and database. The goal is to establish the full request lifecycle from HTTP request to database query and back.

### Changes
- Create `app/models/business.py` — Pydantic models for request/response shapes:
  - `BusinessCreate` — input model for creating a business
  - `BusinessResponse` — output model returned to the client
  - `BusinessListResponse` — paginated list response
- Create `app/database/businesses.py` — raw SQL queries:
  - `get_all_businesses()`
  - `get_business_by_id(id)`
  - `create_business(data)`
- Create `app/services/businesses.py` — business logic:
  - Validate that a business name is not a duplicate in the same city
  - Calculate average rating from reviews (join query)
- Update `app/routers/businesses.py` — wire up real endpoints:
  - `GET /businesses` — list all businesses with pagination
  - `GET /businesses/{id}` — get a single business
  - `POST /businesses` — create a new business

### Testing Strategy
- Use `/docs` Swagger UI to test each endpoint interactively
- Test `GET /businesses` returns an empty array on a fresh database
- Test `POST /businesses` creates a record and returns the correct shape
- Test `GET /businesses/{id}` with a valid and invalid ID
- Verify Pydantic rejects malformed request bodies (e.g. missing required fields)

### Reading Materials

**Official**
- FastAPI Path Parameters: https://fastapi.tiangolo.com/tutorial/path-params/
- FastAPI Request Body: https://fastapi.tiangolo.com/tutorial/body/
- FastAPI Response Model: https://fastapi.tiangolo.com/tutorial/response-model/

**Community**
- TestDriven.io — FastAPI with Postgres: https://testdriven.io/blog/fastapi-crud/

---

## PR 4 — Reviews Endpoints

### What this PR is about
Implements the reviews resource. This PR introduces more complex database queries involving JOINs and aggregations — a user leaves a review for a business, and the business average rating updates accordingly. This is where the relational nature of the database becomes meaningful.

### Changes
- Create `app/models/review.py` — Pydantic models:
  - `ReviewCreate` — input model (rating, body, business_id, user_id)
  - `ReviewResponse` — output model
- Create `app/database/reviews.py` — raw SQL queries:
  - `get_reviews_by_business(business_id)`
  - `create_review(data)`
  - `get_average_rating(business_id)` — uses `AVG()` aggregation
- Create `app/services/reviews.py` — business logic:
  - Validate rating is between 1 and 5
  - Prevent a user from reviewing the same business twice
  - Update business average rating after a new review
- Create `app/routers/reviews.py`:
  - `GET /businesses/{id}/reviews` — get all reviews for a business
  - `POST /businesses/{id}/reviews` — create a review for a business
- Register reviews router in `main.py`

### Testing Strategy
- Test creating a review and verify the business average rating updates
- Test that creating a duplicate review (same user, same business) returns an error
- Test that a rating outside 1-5 is rejected
- Verify the JOIN query returns reviewer name alongside review data

### Reading Materials

**Official**
- PostgreSQL Aggregate Functions: https://www.postgresql.org/docs/current/functions-aggregate.html
- PostgreSQL Joins: https://www.postgresql.org/docs/current/tutorial-joins.html
- FastAPI Body Validation: https://fastapi.tiangolo.com/tutorial/body-fields/

---

## PR 5 — Users & Authentication

### What this PR is about
Implements user registration, login, and JWT-based authentication. This PR introduces security concepts — password hashing, token generation, and protecting endpoints so only authenticated users can create businesses or write reviews.

### Changes
- Install `python-jose` (JWT), `passlib` (password hashing), `bcrypt`
- Create `app/models/user.py` — Pydantic models:
  - `UserCreate` — registration input (name, email, password)
  - `UserResponse` — safe output (never return password hash)
  - `Token` — JWT token response
- Create `app/database/users.py` — raw SQL queries:
  - `get_user_by_email(email)`
  - `create_user(data)`
- Create `app/services/auth.py` — authentication logic:
  - `hash_password(password)`
  - `verify_password(plain, hashed)`
  - `create_access_token(data)`
  - `get_current_user()` — FastAPI dependency for protected routes
- Create `app/routers/users.py`:
  - `POST /auth/register` — create a new user
  - `POST /auth/login` — returns JWT token
  - `GET /users/me` — returns current authenticated user (protected)
- Add auth dependency to `POST /businesses` and `POST /reviews`
- Add `SECRET_KEY` and `ACCESS_TOKEN_EXPIRE_MINUTES` to `config.py` and `.env`

### Testing Strategy
- Test registration creates a user with a hashed password (never plain text)
- Test login returns a valid JWT token
- Test accessing a protected endpoint without a token returns 401
- Test accessing a protected endpoint with a valid token succeeds
- Verify `/users/me` returns the correct user from the token

### Reading Materials

**Official**
- FastAPI Security & JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- passlib docs: https://passlib.readthedocs.io/en/stable/

**Community**
- TestDriven.io — FastAPI JWT Auth: https://testdriven.io/blog/fastapi-jwt-auth/

---

## PR 6 — Search Endpoint

### What this PR is about
Implements search — the core feature of a Yelp-like app. This PR introduces PostgreSQL full-text search using native `tsvector`/`tsquery` so you can search businesses by name, category, and city without an external search engine.

### Changes
- Add full-text search index to `businesses` table via a new migration:
  - `migrations/002_add_search_index.sql`
- Create `app/routers/search.py`:
  - `GET /search?q=pizza&city=seattle&rating=4` — search with filters
- Create `app/database/search.py` — raw SQL queries using:
  - `tsvector` and `tsquery` for full-text search
  - `WHERE city = $1` for city filtering
  - `HAVING AVG(rating) >= $2` for rating filtering
  - `ORDER BY` relevance ranking
- Create `app/services/search.py` — sanitize and validate query parameters
- Register search router in `main.py`

### Testing Strategy
- Test searching for a business by partial name
- Test filtering by city returns only businesses in that city
- Test filtering by minimum rating returns correct results
- Test empty search query returns all businesses
- Test search with no results returns empty array, not an error

### Reading Materials

**Official**
- PostgreSQL Full Text Search: https://www.postgresql.org/docs/current/textsearch.html
- PostgreSQL tsvector/tsquery: https://www.postgresql.org/docs/current/datatype-textsearch.html
- FastAPI Query Parameters: https://fastapi.tiangolo.com/tutorial/query-params/

**Community**
- Postgres full-text search in practice: https://rachbelaid.com/postgres-full-text-search-is-good-enough/

---

## PR 7 — Frontend Foundation

### What this PR is about
Scaffolds the Next.js frontend and establishes the base structure. This PR is the frontend equivalent of PR 1 — no features, just a clean, well-configured Next.js app that can successfully communicate with the FastAPI backend.

### Changes
- Scaffold Next.js app inside `frontend/` using `create-next-app`
- Install and configure Tailwind CSS
- Create `lib/api.ts` — base fetch wrapper that points to FastAPI backend URL
- Create environment variables:
  - `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - `.env.example` as reference
- Add `.gitignore` for `frontend/`
- Create a simple homepage that calls `GET /health` and displays the response
- Verify CORS works end-to-end between Next.js (port 3000) and FastAPI (port 8000)

### Testing Strategy
- Verify `npm run dev` starts without errors
- Verify homepage renders and successfully fetches from FastAPI `/health`
- Open browser network tab and confirm no CORS errors
- Verify `/health` response displays on the page

### Reading Materials

**Official**
- Next.js Installation: https://nextjs.org/docs/getting-started/installation
- Next.js Environment Variables: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
- Next.js Data Fetching: https://nextjs.org/docs/app/building-your-application/data-fetching

---

## PR 8 — Frontend Business Pages

### What this PR is about
Builds the core frontend pages for browsing and viewing businesses. This PR deepens your understanding of Next.js App Router — layouts, dynamic routes, Server Components, and data fetching patterns.

### Changes
- Create `app/businesses/page.tsx` — business listing page
  - Fetches `GET /businesses` from FastAPI
  - Displays list of business cards
- Create `app/businesses/[id]/page.tsx` — individual business page
  - Fetches `GET /businesses/{id}` and `GET /businesses/{id}/reviews`
  - Displays business details and review list
- Create reusable components:
  - `components/BusinessCard.tsx`
  - `components/ReviewCard.tsx`
  - `components/RatingStars.tsx`
- Style with Tailwind CSS

### Testing Strategy
- Verify business listing page renders correctly with seeded data
- Verify clicking a business navigates to the correct detail page
- Verify dynamic route `[id]` renders correct business data
- Test with an invalid business ID — should show a not found state

### Reading Materials

**Official**
- Next.js App Router: https://nextjs.org/docs/app/building-your-application/routing
- Next.js Dynamic Routes: https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes
- Next.js Server Components: https://nextjs.org/docs/app/building-your-application/rendering/server-components

---

## PR 9 — Frontend Auth & Protected Pages

### What this PR is about
Implements login, registration, and protecting frontend routes so only authenticated users can write reviews or add businesses. This PR introduces JWT handling on the frontend and Next.js Middleware for route protection.

### Changes
- Create `app/auth/login/page.tsx` — login form
- Create `app/auth/register/page.tsx` — registration form
- Create `lib/auth.ts` — handles JWT token storage and retrieval
- Create `components/AuthForm.tsx` — reusable form component
- Update `lib/api.ts` — attach JWT token to authenticated requests
- Add Next.js Middleware (`middleware.ts`) to protect routes:
  - `/businesses/new` — requires auth
  - `/reviews/new` — requires auth
- Create `app/businesses/new/page.tsx` — add a new business (protected)

### Testing Strategy
- Test login form submits and stores JWT token
- Test accessing a protected page without being logged in redirects to login
- Test accessing a protected page while logged in renders correctly
- Test logout clears the token and redirects to home

### Reading Materials

**Official**
- Next.js Middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware
- Next.js Authentication Guide: https://nextjs.org/docs/app/building-your-application/authentication
- MDN — localStorage: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

---

## PR 10 — Dockerize Backend

### What this PR is about
Packages the FastAPI backend into a Docker container. This PR is purely infrastructure — no new features. The goal is to understand how Docker works by containerizing something you already know is working.

### Changes
- Create `backend/Dockerfile`:
  - Multi-stage build — builder stage and runtime stage
  - Install Poetry dependencies
  - Copy app code
  - Expose port 8000
  - Set entrypoint to uvicorn
- Create `backend/.dockerignore`
- Test building and running the container locally:
  - `docker build -t ulas-rasa-backend .`
  - `docker run -p 8000:8000 ulas-rasa-backend`
- Verify all endpoints work from the container

### Testing Strategy
- Build the image and verify it builds without errors
- Run the container and verify `/health` responds correctly
- Verify environment variables can be passed into the container via `-e` flag
- Verify the container stops cleanly with `Ctrl+C`

### Reading Materials

**Official**
- Dockerfile reference: https://docs.docker.com/reference/dockerfile/
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Docker best practices: https://docs.docker.com/build/building/best-practices/

---

## PR 11 — Docker Compose (Full Local Stack)

### What this PR is about
Creates a `docker-compose.yml` that runs the entire stack — Next.js, FastAPI, and PostgreSQL — with a single command. This is the culmination of the Docker phase and represents a fully containerized local development environment.

### Changes
- Create `docker-compose.yml` at the monorepo root:
  - `db` service — PostgreSQL container with persistent volume
  - `backend` service — FastAPI container, depends on `db`
  - `frontend` service — Next.js container, depends on `backend`
- Create `frontend/Dockerfile`
- Update `backend/app/config.py` to read `DATABASE_URL` from environment
- Update `frontend/.env` to point `NEXT_PUBLIC_API_URL` to backend container
- Add `volumes:` for PostgreSQL data persistence
- Add `networks:` so containers can talk to each other

### Testing Strategy
- Run `docker compose up` and verify all three services start
- Verify frontend is accessible at `http://localhost:3000`
- Verify backend is accessible at `http://localhost:8000`
- Verify frontend can successfully call the backend
- Stop and restart with `docker compose down` and `docker compose up` — verify data persists

### Reading Materials

**Official**
- Docker Compose getting started: https://docs.docker.com/compose/gettingstarted/
- Docker Compose file reference: https://docs.docker.com/reference/compose-file/
- Docker networking: https://docs.docker.com/engine/network/

---

## PR 12 — Deployment

### What this PR is about
Deploys the full stack to production. Frontend on Vercel, backend on Fly.io, database on Neon. This PR introduces CI/CD with GitHub Actions so every push to `main` automatically deploys.

### Changes
- Set up Neon PostgreSQL — get production `DATABASE_URL`
- Run migrations against production database
- Deploy backend to Fly.io:
  - Create `fly.toml` configuration
  - Set production environment variables on Fly.io
  - `fly deploy`
- Deploy frontend to Vercel:
  - Connect GitHub repo to Vercel
  - Set `NEXT_PUBLIC_API_URL` to Fly.io backend URL
- Create `.github/workflows/deploy.yml` — GitHub Actions CI/CD:
  - Run on push to `main`
  - Deploy backend to Fly.io
  - Deploy frontend to Vercel
- Update CORS in `config.py` to allow production frontend domain

### Testing Strategy
- Verify production `/health` endpoint responds correctly
- Verify frontend loads at the Vercel URL
- Verify frontend can call the production backend
- Test the full flow end-to-end in production: register, login, create business, write review
- Verify `/docs` is disabled in production

### Reading Materials

**Official**
- Fly.io getting started: https://fly.io/docs/getting-started/
- Vercel deployment docs: https://vercel.com/docs/deployments/overview
- GitHub Actions docs: https://docs.github.com/en/actions

**Community**
- Neon getting started: https://neon.tech/docs/get-started-with-neon/signing-up

---

## Summary

| PR | Focus | Layer |
|---|---|---|
| PR 1 | Backend foundation & config | Backend |
| PR 2 | Database connection & schema | Database |
| PR 3 | Businesses endpoints | Backend |
| PR 4 | Reviews endpoints | Backend |
| PR 5 | Users & authentication | Backend |
| PR 6 | Search endpoint | Backend |
| PR 7 | Frontend foundation | Frontend |
| PR 8 | Frontend business pages | Frontend |
| PR 9 | Frontend auth & protected pages | Frontend |
| PR 10 | Dockerize backend | Infrastructure |
| PR 11 | Docker Compose full stack | Infrastructure |
| PR 12 | Deployment | Infrastructure |
