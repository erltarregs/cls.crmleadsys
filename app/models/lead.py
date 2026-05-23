# app/models/lead.py

import uuid
import enum
from datetime import datetime, date
from sqlalchemy import (
    String, Text, DateTime, Date,
    ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# -- Python Enums -> PostgreSQL ENUM types --------------------
# Defining status as an enum (not a plain string) gives you:
#   1. DB-level constraint - invalid values are rejected at insert
#   2. IDE autocomplete - LeadStatus.NEW instead of "new"
#   3. Easy to extend - add a new status in one place

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    TRADE_SHOW = "trade_show"
    OTHER = "other"

class Lead(Base):
    """
    A sales lead - the core entity of the CRM.

    Contains:
    - Contract information (name, email, phone, company)
    - Pipeline status (where in the sales process)
    - Important dates (follow-up date, close date)
    - File attachment (photo/document path)
    - Ownership (which user owns this lead)
    """

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # -- Contact Info --------------------
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True, # That related Mapped[str | None] above says that this field accepts either a string OR None 
    )
    company: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    job_title: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    
    # -- Pipeline -------------------
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"),
        default=LeadStatus.NEW,
        nullable=False,
        index=True, # we filter by status constantly
    )
    source: Mapped[LeadSource | None] = mapped_column(
        SAEnum(LeadSource, name="lead_source"),
        nullable=True,
    )

    # -- Notes -----------------
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # -- Date Fields ------------------
    # follow_up_date: shown as a date picker in the React frontend
    # expected_close_date: shown in calendar view
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- File Attachment --------------
    # Same pattern as profile avatar = store path, not binary data
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # -- Ownership -------------------------
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, # lead can exist without an owner (unassigned)
        index=True,
    )

    # -- Timestamps ---------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column( # Mapped[type] tells Python what type it is; = mapped_column(...) tells the database how to store it.
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -- Relationships ---------------------------
    owner: Mapped["User"] = relationship("User", back_populates="leads")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Lead id={self.id} name={self.full_name} status={self.status}>"
        