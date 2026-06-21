from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.serializers import build_run_detail
from app.backtest_engine.engine import BacktestEngine
from app.db.session import get_db
from app.schemas.backtest import BacktestRunDetail
from app.strategies.prebuilt import get_prebuilt_strategy, list_prebuilt_strategies

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("/prebuilt")
def get_prebuilt_list():
    return list_prebuilt_strategies()

@router.post("/prebuilt/{key}/run", response_model=BacktestRunDetail)
def run_prebuilt_strategy(key: str, db: Session = Depends(get_db)):
    config = get_prebuilt_strategy(key)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Unknown prebuilt strategy '{key}'")

    engine = BacktestEngine(db, config)
    try:
        run = engine.run()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.refresh(run)
    return build_run_detail(run)
