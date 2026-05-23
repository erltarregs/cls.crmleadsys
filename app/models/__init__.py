# app/models/__init__.py
# Import all models here so Alembic can discover them in one import.
# If you add a new model, add it to this file.

from app.models.user import User
from app.models.profile import Profile
from app.models.lead import Lead

__all__ = ["User", "Profile", "Lead"]
