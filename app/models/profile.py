# app/models/profile.py

import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Profile(Base):
    """
    Extended user information - separated from User intentionally.

    Why split User and Profile?
    - User = authentication data (email, password, active status)
    - Profile = personal/display data (name, avatar, phone, etc)
    - Keeps the auth/authentication (not authz/authorization) table lean and fast
    - Profile data can be updated without touching auth logic
    - Common pattern in production systems (Django does this too)
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -- Foreign Key to User -----------------------
    # ondelete="CASCADE" means: if the User row is deleted,
    # this Profile row is automatically deleted too.
    # This is enfored at the DATABASE level - not just Python.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,    # enforces one-to-one at DB level
        nullable=False,
        index=True,
    )

    # -- Personal Info -----------------------------
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=False
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=False
    )

    # -- Date field example -----------------------
    # Date (no time) vs DateTime (date + time) - choose intentionally.
    # date_of_birth doesn't need a time component.
    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # -- Photo Upload -----------------------------------
    # We store the FILE PATH, not the file itself.
    # e.g., "uploads/photos/abc123.jpg"
    # The actual file lives on disk (or the cloud server such as S3 later).
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # -- Timestamps -------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -- Relationships ----------------------------
    user: Mapped["User"] = relationship("User", back_populates="profile")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id} name={self.full_name}>"
        