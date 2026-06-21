import uuid
from datetime import date as date_type
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, UniqueConstraint, BigInteger, Date, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class StockPrice(Base):
    """
    Daily OHLCV time series. One row per (company, date).

    Kept as a narrow, append-only table (no fundamental/ratio columns) so it
    stays fast to scan and index for the heavy time-series reads the backtest
    engine performs (mark-to-market valuation across the full date range).
    """

    __tablename__ = "stock_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    adj_close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_stock_prices_company_date"),
        # Composite index covers the engine's primary access pattern:
        # "give all prices for company X between date A and B"
        Index("ix_stock_prices_company_date", "company_id", "date"),
        # Supports "all prices on date D across companies" (e.g. universe mark-to-market)
        Index("ix_stock_prices_date", "date"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<StockPrice {self.company_id} {self.date} close={self.close}>"
