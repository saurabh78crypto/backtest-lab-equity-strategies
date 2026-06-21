from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Company, Fundamental, StockPrice
from app.schemas.company import CompanyOut, UniverseStats

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    companies = db.execute(
        select(Company).where(Company.is_active.is_(True)).order_by(Company.trading_symbol)
    ).scalars().all()
    return companies

@router.get("/stats", response_model=UniverseStats)
def universe_stats(db: Session = Depends(get_db)):
    total_companies = db.scalar(select(func.count(Company.id)).where(Company.is_benchmark.is_(False)))
    total_price_rows = db.scalar(select(func.count(StockPrice.id)))
    total_fundamental_rows = db.scalar(select(func.count(Fundamental.id)))
    earliest = db.scalar(select(func.min(StockPrice.date)))
    latest = db.scalar(select(func.max(StockPrice.date)))
    sectors = db.execute(
        select(Company.sector).where(Company.sector.is_not(None)).distinct()
    ).scalars().all()

    return UniverseStats(
        total_companies=total_companies or 0,
        total_price_rows=total_price_rows or 0,
        total_fundamental_rows=total_fundamental_rows or 0,
        earliest_price_date=str(earliest) if earliest else None,
        latest_price_date=str(latest) if latest else None,
        sectors=sorted(sectors),
    )
