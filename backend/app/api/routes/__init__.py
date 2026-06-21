from fastapi import APIRouter

from app.api.routes.backtest import router as backtest_router
from app.api.routes.companies import router as companies_router
from app.api.routes.metadata import router as metadata_router
from app.api.routes.strategies import router as strategies_router

api_router = APIRouter()
api_router.include_router(metadata_router)
api_router.include_router(companies_router)
api_router.include_router(backtest_router)
api_router.include_router(strategies_router)
