import enum
import uuid
from datetime import date as date_type
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, UniqueConstraint, Date, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class PeriodType(str, enum.Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"

class Fundamental(Base):
    """
    One row per (company, period_end_date, period_type).
    """

    __tablename__ = "fundamentals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    period_end_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    period_type: Mapped[PeriodType] = mapped_column(
        Enum(PeriodType, name="period_type_enum"), nullable=False
    )
    report_date: Mapped[date_type] = mapped_column(Date, nullable=False)

    # Raw P&L items (in INR Crores)
    revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    ebitda: Mapped[float | None] = mapped_column(Float, nullable=True)
    ebit: Mapped[float | None] = mapped_column(Float, nullable=True)
    interest_expense: Mapped[float | None] = mapped_column(Float, nullable=True)
    tax_expense: Mapped[float | None] = mapped_column(Float, nullable=True)
    pat: Mapped[float | None] = mapped_column(Float, nullable=True)  # Net profit after tax

    # Raw Balance Sheet items (in INR Crores)
    total_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_equity: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_debt: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_liabilities: Mapped[float | None] = mapped_column(Float, nullable=True)
    cash_and_equivalents: Mapped[float | None] = mapped_column(Float, nullable=True)
    shares_outstanding: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Raw Cash Flow items (in INR Crores)
    operating_cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)
    investing_cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)
    financing_cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)
    capex: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Derived / computed metrics (precomputed at ingestion time since
    # they only depend on the statement data above, not on daily price)
    eps: Mapped[float | None] = mapped_column(Float, nullable=True)
    book_value_per_share: Mapped[float | None] = mapped_column(Float, nullable=True)
    roe: Mapped[float | None] = mapped_column(Float, nullable=True)          # PAT / Equity
    roce: Mapped[float | None] = mapped_column(Float, nullable=True)         # EBIT / Capital Employed
    roa: Mapped[float | None] = mapped_column(Float, nullable=True)          # PAT / Total Assets
    debt_to_equity: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    operating_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    free_cash_flow: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", back_populates="fundamentals")

    __table_args__ = (
        UniqueConstraint(
            "company_id", "period_end_date", "period_type", name="uq_fundamentals_company_period"
        ),
        # Hot path: "latest row per company with report_date <= as_of_date"
        Index("ix_fundamentals_company_report_date", "company_id", "report_date"),
        Index("ix_fundamentals_report_date", "report_date"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Fundamental {self.company_id} {self.period_end_date} ({self.period_type})>"
