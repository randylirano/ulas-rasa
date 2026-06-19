from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import get_pool

# Define pool before everything else
# Ensuring DB connection pool established before our App start processing request
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB connection pool on app startup
    await get_pool()
    yield
    # Close DB connection pool on app shutdown
    p = await get_pool()
    await p.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": f"{settings.app_name} is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment}