"""Pytest configuration and shared async test fixtures."""

import asyncio
import os
import sys
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Ensure api directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.facility import Facility
from app.db.models.safety_report import SafetyReport
from app.db.models.action_item import ActionItem

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create in-memory SQLite schema per test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        # Seed minimum facility and user for test foreign keys
        u = User(
            user_id="USR-001",
            name="Alok Sharma",
            email="alok.sharma@oilindia.in",
            role="HSE Manager",
            title="Chief General Manager",
            facility_id="FAC-DUL-01",
        )
        f = Facility(
            facility_id="FAC-DUL-01",
            name="Duliajan Central Hub",
            short_name="Duliajan Hub",
            region="Upper Assam Basin",
            type="Central Operational Hub",
            active_personnel=1200,
        )
        session.add(u)
        session.add(f)
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide AsyncClient with overridden database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
