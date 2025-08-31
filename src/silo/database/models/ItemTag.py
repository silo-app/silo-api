from sqlalchemy import Column, ForeignKey, Table
from silo.database.models import Base

item_tag_association = Table(
    "item_tag_association",
    Base.metadata,
    Column("item_id", ForeignKey("item.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)
