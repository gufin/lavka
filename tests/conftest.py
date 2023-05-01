import asyncio
from dataclasses import dataclass

import aiohttp
import pytest
from multidict import CIMultiDictProxy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

service_api_url = "http://127.0.0.1:8080"


@pytest.fixture(autouse=True)
async def setup_database():
    DATABASE_URL = "postgresql+asyncpg://postgres:example@127.0.0.1/postgres"

    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE couriers CASCADE;"))
            await session.execute(
                text("ALTER SEQUENCE couriers_id_seq RESTART WITH 1;")
            )
            await session.execute(text("TRUNCATE TABLE orders CASCADE;"))
            await session.execute(text("ALTER SEQUENCE orders_id_seq RESTART WITH 1;"))
            await session.commit()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def make_get_request(session):
    async def inner(endpoint: str, params: dict | None = None) -> HTTPResponse:
        params = params or {}
        url = f"{service_api_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=params) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner


@pytest.fixture
def make_post_request(session):
    async def inner(endpoint: str, params: dict | None = None) -> HTTPResponse:
        params = params or {}
        url = f"{service_api_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )

    return inner
