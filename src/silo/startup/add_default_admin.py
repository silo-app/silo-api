from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound

from silo import config
from silo.database import async_get_db
from silo.database.models import Role, User


async def add_default_admin() -> None:
    async for db in async_get_db():
        result = await db.execute(
            select(User).where(User.roles.any(Role.name == "admin"))
        )
        try:
            admin_user = result.scalar_one_or_none()
            if admin_user is None:
                if config.first_admin_user is None:
                    raise RuntimeError(
                        "[SILO] Error: Cannot startup SILO. Define a first admin user with the environment variable FIRST_ADMIN_USER"
                    )
                new_user = User(username=config.first_admin_user)
                resultr = await db.execute(select(Role).where(Role.name == "admin"))
                admin_role = resultr.scalar_one_or_none()

                new_user.roles.append(admin_role)
                db.add(new_user)
                await db.commit()

                print(f"[SILO] Added default admin user '{config.first_admin_user}'")
        except MultipleResultsFound:
            pass
