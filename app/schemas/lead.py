# app/schemas/lead.py

import uuid
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

# Import the Python enums from the model
# Schemas reuse the same enum definitions - no duplication
from app.models.lead import LeadStatus, LeadSource

class LeadBase(BaseModel):
    """
    Core lead fields shared across Create/Update/Response
    """
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    company: Optional[str] = Field(default=None, max_length=200)
    job_title: Optional[str] = Field(default=None, max_lenth=200)
    notes: Optional[str] = None

    # -- Enum fields ------------------------
    # Pydantic validates that the value is one of the enum members.
    # The frontend sends: "new", "contacted", "won", etc.
    # Pydantic converts the string to the enum object automatically.
    status: LeadStatus = LeadStatus.NEW
    source: Optional[LeadSource] = None

    # -- Date fields --------------------
    # Frontend sends ISO 8601 date strings: "2026-06"
    # Pydantic auto-;arses them into Python data objects.
    # No manual strptime() needed - this is one of Pydantic's best features.
    follow_up_date: Optional[date] = None
    expected_close_date: Optional[date] = None

    @field_validator("follow_up_date", "expected_close_date", mode = "before")
    @classmethod
    def parse_flexible_data(cls, v):
        """
        Handles multiple date formats the frontend might send:
            "2026-06-15"            -> standard ISO 8601 (preferred)
            "06/15/2026"            -> US format
            "2026-06-15T00:00:00"   -> datetime string (strips time part)
        
        This is the kind of real-world data handling that
        tutorials skip but production apps always need.
        """
        if v is None:
            return v
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Try ISO format first (fastest)
            try:
                return date.fromisoformat(v[:10]) # handles datetime strings too
            except ValueError:
                pass
            # Try US format
            from datetime import datetime as dt
            try:
                return dt.strptime(v, "%m/%d/%Y").date()
            except ValueError:
                pass
            raise ValueError(f"Cannot parse date '{v}'. Use YYYY-MM-DD format.")
        return v


class LeadCreate(LeadBase):
    """
    What the API accepts to create a lead

    owner_id is NOT here - it's taken from the JWT token.
    The logged-in user automatically becomes the owner.
    Prevents one user from creating leads on behalf of another.
    """
    pass


class LeadUpdate(BaseModel):
    """
    All fields optional - supports partial updates (PATCH)

    Example: Moving a lead from "contacted" to "qualified"
    only needs {"status": "qualified"} - no other fields required
    """
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    company: Optional[str] = Field(default=None, max_length=200)
    job_title: Optional[str] = Field(default=None, max_lenth=200)
    notes: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    follow_up_date: Optional[date] = None
    expected_close_date: Optional[date] = None


class LeadResponse(LeadBase):
    """
    Full lead response including system-generated fields.
    photo_url is the saved file path from uploads.
    """
    id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Nested owner info - instead of just an ID, return
    # enough user info for the frontend to display "Assigned to: John Smith"
    owner: Optional["LeadOwnerInfo"] = None
    
    model_config = {"from_attributes": True}


class LeadOwnerInfo(BaseModel):
    """
    Minimal user info embedded in LeadResponse
    We don't embed the full UserResponse (that would expose too much).
    Just enough for display purposes
    """
    id: uuid.UUID
    email: str

    model_config = {"from_attributes": True}


class LeadListResponse():
    """
    Paginated list response.
    Always paginate list endpoints - never return unbounded lists.
    """
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


# Resolve forward reference
LeadResponse.model_rebuild()
