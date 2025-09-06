from sqlalchemy import select
from silo.database import async_get_db
from silo.database.models import Role


async def add_default_roles() -> None:
    async for db in async_get_db():
        # user role
        result = await db.execute(select(Role).filter_by(name="user"))
        user_role = result.scalar_one_or_none()
        if user_role is None:
            db.add(Role(name="user", permissions={"/user/myinfo": ["GET"]}))
            await db.commit()
            print("[SILO] Added default role 'user'")
        # admin role
        result = await db.execute(select(Role).filter_by(name="admin"))
        admin_role = result.scalar_one_or_none()
        if admin_role is None:
            db.add(
                Role(
                    name="admin",
                    permissions={"*": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                )
            )
            await db.commit()
            print("[SILO] Added default role 'admin'")
