# app/schemas/profile.py

import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class ProfileBase(BaseModel):
    """ Shared profile fields."""
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    bio: Optional[str] = Field(default=None, max_length=1000)
    date_of_birth: Optional[date] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional [str]:
        """
        Basic phone validation --allows international formats.
        e.g., +1-555-0100, +44 20 7946 0958
        In production, use the 'phonenumbers' library for full validation.
        """
        if v is None:
            return v
        # Strip spaces and dashes for checking
        clened = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[\d]{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return v
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        """
        Date validation example.
        The frontend sends ISO 8601: "1990-06-15"
        Pydantic auto parses this string into a Python date object.
        We just add a sanity check here.
        """
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year
        if age < 18:
            raise ValueError("User must be at least 18 years old")
        if age > 120:
            raise ValueError("Please enter a valid date of birth")
        return v

    
class ProfileCreate(ProfileBase):
    """
    Used when creating a profile.
    user_id is NOT here - it comes from the JWT token,
    not from what the user sends. Users can't create
    profiles for other users.
    """
    pass

class ProfileUpdate(BaseModel):
    """
    All optional for PATCH updates.
    avatar_url is handled separately via file upload endpoint,
    not through this schema.
    """
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    bio: Optional[str] = Field(default=None, max_length=1000)
    date_of_birth: Optional[date] = None

class ProfileResponse(ProfileBase):
    """
    What the API returns
    Includes computed full_name and the avatar path.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Computed field - derived from first_name + last_name
    # We add it manually since it's a @property on the model
    full_name: Optional[str] = None

    model_config = {"from attributes": True}

    @classmethod
    def from_orm_with_full_name(cls, profile) -> "ProfileResponse":
        """
        Custom constructor that calls the mode's @property.
        Usage: ProfileResponse.from_orm_with_full_name(profile_obj)
        """
        data = cls.model_validate(profile)
        data.full_name = profile.full_name
        return data
        