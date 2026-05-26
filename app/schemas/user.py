# app/schemas/user.py

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UserBase(BaseModel):
    """
    Shared fields. Neither password nor privileged fields here.
    Both UserCreate and UserResponse inherit from this.
    """

    email: EmailStr # Pydantic validates this is a real email format

class UserCreate(UserBase):
    """
    What the API accepts when registering a new user. (Create)
    Password is the plain text here - it gets hashed in the service layer.
    We NEVER store plain text passwords.
    """
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Must be at least 8 characters"
    )

    @field_validator("password") # A Pydantic decorator that says: "run this method to validate the password field before accepting it." The "password" in quotes tells it which specific field to watch. Whenever someone submits a password, Pydantic automatically calls this method first.
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Basic password rules. In production you'd use  
        a library like zxcvbn for real strength checking.
        """
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserUpdate(BaseModel):
    """
    All fields optional - PATCH semantics.
    Only send what you want to change.

    Why Optional for everything?
    PATCH /users/me with {"email": "new@email.com"}
    should only update email, not touch password.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    What the API returns to clients.
    Notice: NO hashed_password, NO internal flags.
    """
    id: uuid.UUID
    is_active: bool
    is_superviser: bool
    created_at: datetime

    model_config = {
        # Tells Pydantic to read data from SQLAlchemy model attributes.
        # Without this, Pydantic only reads plain dicts, not ORM objects.
        "from_attributes": True
    }

class UserWithProfile(UserResponse):
    """
    Extended response that includes profile data.
    Used when you need the full user + their display info.
    The Optional here means a user might not have a profile yet.
    """
    profile: Optional["ProfileResponse"] = None

    model_config = {"from_atributes": True}


# -- Token schemas (used in auth routes) ---------------------

class Token(BaseModel):
    """What the login endpoint returns."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    What we extract FROM a JWT after decoding it
    This is internal - never sent to clients directly.
    """
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None

    
# Needed because UserWithProfile references ProfileResponse
# which is defined in another file - forward reference resolution
from app.schemas.profile import ProfileResponse # noqa: E402
UserWithProfile.model_rebuild()
