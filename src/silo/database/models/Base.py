from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Base(DeclarativeBase, MappedAsDataclass):
    ...