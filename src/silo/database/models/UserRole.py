from sqlalchemy import Column, ForeignKey, Integer, Table

from silo.database.models import Base

user_roles_association = Table(
    "user_roles_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)
