# app/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class User(Base):
    """
    Represents a CRM system user (sales rep, admin, etc.)
    This is the authentication identity - NOT the lead/contact.

    Mapped[] and mapped_column() are SQLAlchemy 2.0 style.
    They give you full type hints and IDE autocomplete.
    Avoid the old Column() style - it has no type safety.
    """

    __tablename__ = "users"

    # -- Primary Key ----------------------
    # UUID instead of integer:
    #   - can be generated client-side (no DB roundtrip needed)
    #   - doesn't leak record count ("user 3" tells attackers you have 2 others)
    #   - safe to expose in URLs
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # -- Identity Fields -----------------
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,         # we query users by email constantly (login)
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # -- Status ---------------------------
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -- Timestamps ----------------------------
    # server_default=faunc.now() means PostgreSQL sets the value,
    # not Python. More reliable accross timezones and server restarts.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), # auto-updates on every UPDATE query
        nullable = False,
    )

    # -- Relationships --------------------------
    # "back_populates" creates a two-way link:
    #   user.profile <-> profile.user
    #   user.leads <-> lead.owner
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False, # one-to-one: a user has exactly one profile
        cascade="all, delete-orphan",
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
    