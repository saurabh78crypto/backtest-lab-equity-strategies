import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Exchange(str, enum.Enum):
    NSE = "NSE"
    BSE = "BSE"

class Company(Base):
    """
    Master reference table for every tradeable instrument in the universe,
    including the benchmark index itself (is_benchmark=True), so that prices
    for the benchmark live in the exact same `stock_prices` table/schema as
    every other equity and can be queried identically.
    """

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Ticker as used against the data provider, e.g. "RELIANCE.NS" or "^NSEI"
    symbol: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    # Clean trading symbol without provider suffix, e.g. "RELIANCE"
    trading_symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    exchange: Mapped[Exchange] = mapped_column(
        Enum(Exchange, name="exchange_enum"), default=Exchange.NSE, nullable=False
    )
    isin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_benchmark: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    prices = relationship("StockPrice", back_populates="company", cascade="all, delete-orphan")
    fundamentals = relationship("Fundamental", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_companies_sector", "sector"),
        Index("ix_companies_active_benchmark", "is_active", "is_benchmark"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Company {self.symbol}>"
