import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import create_all_tables
from app.db.session import engine

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Ensuring database tables exist...")
    create_all_tables(engine)
    logger.info("Database ready.")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Backtesting platform for equity-based fundamental strategies on the Indian market.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"status": "ok", "service": settings.APP_NAME}

@app.get("/health")
def health():
    return {"status": "healthy"}