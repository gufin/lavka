# TODO исправить flake8
import asyncio
from dataclasses import dataclass

import aiohttp
import pytest
from multidict import CIMultiDictProxy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

service_api_url = "http://127.0.0.1:8080"  # TODO заменить на настройки


@pytest.fixture(autouse=True)
async def setup_database():
    DATABASE_URL = "postgresql+asyncpg://postgres:example@127.0.0.1/postgres"
    # TODO заменить на настройки
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE couriers CASCADE;"))
            await session.execute(
                text("ALTER SEQUENCE couriers_id_seq RESTART WITH 1;")
            )
            await session.execute(text("TRUNCATE TABLE orders CASCADE;"))
            await session.execute(
                text("ALTER SEQUENCE orders_id_seq RESTART WITH 1;")
            )
            await session.commit()


@pytest.fixture(autouse=True)
async def create_couriers(make_post_request):
    await make_post_request(
        "/couriers",
        params={
            "couriers": [
                {
                    "courier_type": "FOOT",
                    "regions": [1, 2, 9],
                    "working_hours": ["10:00-14:00", "16:00-20:00"],
                },
                {
                    "courier_type": "BIKE",
                    "regions": [4, 5, 6],
                    "working_hours": ["09:00-13:00", "15:00-19:00"],
                },
                {
                    "courier_type": "AUTO",
                    "regions": [7, 8, 17],
                    "working_hours": ["08:00-12:00", "14:00-18:00"],
                },
            ]
        },
    )


@pytest.fixture(autouse=True)
async def create_orders(make_post_request):
    await make_post_request(
        "/orders",
        params={
            "orders": [
                {
                    "weight": 1.5,
                    "regions": 1,
                    "delivery_hours": ["09:00-12:00"],
                    "cost": 150,
                },
                {
                    "weight": 3.2,
                    "regions": 2,
                    "delivery_hours": ["14:00-18:00", "19:00-22:00"],
                    "cost": 250,
                },
                {
                    "weight": 0.8,
                    "regions": 1,
                    "delivery_hours": ["10:00-11:00", "13:00-14:00"],
                    "cost": 100,
                },
            ]
        },
    )


@pytest.fixture(autouse=True)
async def complete_orders(make_post_request):
    await make_post_request(
        "/orders/complete",
        params={
            "complete_info": [
                {
                    "courier_id": 1,
                    "order_id": 1,
                    "complete_time": "2023-05-01T12:00:00.000Z",
                }
            ]
        },
    )


@pytest.fixture(autouse=True)
async def assign_orders(make_post_request):
    await make_post_request("/orders/assign")


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
