from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import pool
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open(wait=True, timeout=10)
    yield
    await pool.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.environment}
