import asyncio
from collections.abc import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, close_db
from app.models.identity import Permission, Role, User
from app.models.seed import SeedRecord

SeedFunction = Callable[[AsyncSession], Awaitable[None]]

ROLE_DEFINITIONS = {
    "TCG_ADMIN": "TCG Admin",
    "TCG_SALES": "TCG Sales",
    "PARTNER_ADMIN": "Partner Admin",
    "PARTNER_SALES": "Partner Sales",
    "PARTNER_PRESALES": "Partner Pre-Sales",
    "PARTNER_DELIVERY": "Partner Delivery",
}

PERMISSION_DEFINITIONS = {
    "platform.manage": "Manage platform configuration and identity",
    "partners.manage": "Create, review, and manage partners",
    "partners.view": "View authorized partner data",
    "sales.manage": "Manage deals, quotes, and orders",
    "sales.view": "View authorized sales data",
    "documents.manage": "Publish and administer documents",
    "documents.view": "View authorized documents",
}


async def seed_identity(session: AsyncSession) -> None:
    permissions: dict[str, Permission] = {}
    for code, description in PERMISSION_DEFINITIONS.items():
        existing = await session.scalar(select(Permission).where(Permission.code == code))
        permission = existing or Permission(code=code, description=description)
        if existing is None:
            session.add(permission)
        permissions[code] = permission

    await session.flush()
    roles: dict[str, Role] = {}
    for code, name in ROLE_DEFINITIONS.items():
        existing = await session.scalar(
            select(Role).where(Role.code == code).options(selectinload(Role.permissions))
        )
        role = existing or Role(code=code, name=name, permissions=[])
        role.name = name
        if existing is None:
            session.add(role)
        roles[code] = role

    await session.flush()
    roles["TCG_ADMIN"].permissions = list(permissions.values())
    roles["TCG_SALES"].permissions = [
        permissions["partners.view"],
        permissions["sales.manage"],
        permissions["documents.view"],
    ]
    roles["PARTNER_ADMIN"].permissions = [
        permissions["partners.view"],
        permissions["sales.manage"],
        permissions["documents.view"],
    ]
    for code in ("PARTNER_SALES", "PARTNER_PRESALES", "PARTNER_DELIVERY"):
        roles[code].permissions = [permissions["sales.view"], permissions["documents.view"]]

    email = settings.SEED_ADMIN_EMAIL.lower()
    admin = await session.scalar(
        select(User).where(User.email == email).options(selectinload(User.roles))
    )
    if admin is None:
        admin = User(
            email=email,
            full_name=settings.SEED_ADMIN_NAME,
            hashed_password=hash_password(settings.SEED_ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
            roles=[],
        )
        session.add(admin)
    if roles["TCG_ADMIN"] not in admin.roles:
        admin.roles.append(roles["TCG_ADMIN"])


SEEDS: tuple[tuple[str, SeedFunction], ...] = (("foundation-identity-v1", seed_identity),)


async def run_seeds() -> None:
    async with SessionLocal() as session:
        for key, seed_function in SEEDS:
            if await session.get(SeedRecord, key):
                print(f"Skipped seed {key} (already applied)")
                continue
            async with session.begin_nested():
                await seed_function(session)
                session.add(SeedRecord(key=key))
            await session.commit()
            print(f"Applied seed {key}")


async def async_main() -> None:
    try:
        await run_seeds()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(async_main())
