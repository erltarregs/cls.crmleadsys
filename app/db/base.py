# app/db/base.py

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this class.

    The __tablename__ is auto-generated from the class name:
        class User(Base)  -> table name: "user"
        class LeadNote(Base) -> table name: "lead_note"

    We'll override __tablename__ explicitly in each model anyway,
    but this gives us a safe default.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Converts CamelCase class name to snake_case table name
        # UserProfile -> user_profile
        import re
        name = cls.__name__
        # Insert underscore before each capital letter (except the first)
        snake = re.sub(r'(?<!^)?=[A-Z])', '_', name).lower()
        return snake
        