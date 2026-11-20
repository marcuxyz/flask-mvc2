"""Optional base class for models using reflection. Requires SQLAlchemy."""

try:
    from sqlalchemy.orm import DeferredReflection  # SQLAlchemy 2.x
except ImportError:  # SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import DeferredReflection


class BaseModel(DeferredReflection):
    """``class Message(BaseModel, db.Model): __tablename__ = "messages"``

    Columns are discovered in the database when ``FlaskMVC(app, db=db)`` initializes.
    """

    __abstract__ = True
