import pytest
from httpx import AsyncClient

from main import app  # замените на ваше приложение FastAPI

HOST = '127.0.0.1'


@pytest.mark.asyncio
async def test_post_courier_valid():
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.post("/couriers", json={
            "couriers": [
                {
                    "courier_type": "FOOT",
                    "regions": [1, 2, 9],
                    "working_hours": ["10:00-14:00", "16:00-20:00"]
                },
                {
                    "courier_type": "BIKE",
                    "regions": [4, 5, 6],
                    "working_hours": ["09:00-13:00", "15:00-19:00"]
                },
                {
                    "courier_type": "AUTO",
                    "regions": [7, 8, 17],
                    "working_hours": ["08:00-12:00", "14:00-18:00"]
                }
            ]
        })
    assert response.status_code == 200
    assert response.json() == {
        "couriers": [
            {
                "courier_id": 1,
                "courier_type": "FOOT",
                "regions": [
                    1,
                    2,
                    9
                ],
                "working_hours": [
                    "10:00-14:00",
                    "16:00-20:00"
                ]
            },
            {
                "courier_id": 2,
                "courier_type": "BIKE",
                "regions": [
                    4,
                    5,
                    6
                ],
                "working_hours": [
                    "09:00-13:00",
                    "15:00-19:00"
                ]
            },
            {
                "courier_id": 3,
                "courier_type": "AUTO",
                "regions": [
                    7,
                    8,
                    17
                ],
                "working_hours": [
                    "08:00-12:00",
                    "14:00-18:00"
                ]
            }
        ]
    }


@pytest.mark.asyncio
async def test_post_courier_invalid():
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.post("/couriers", json={
            "couriers": [
                {
                    "courier_type": "foot",
                    "regions": [1, 2, 3],
                    "working_hours": ["invalid"]
                }
            ]
        })
    assert response.status_code == 400
    # Проверьте сообщение об ошибке в ответе


@pytest.mark.asyncio
async def test_get_existing_courier():
    # Предположим, что курьер с id 1 существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        await ac.post("/couriers", json={
            "couriers": [
                {
                    "courier_type": "FOOT",
                    "regions": [1, 2, 9],
                    "working_hours": ["10:00-14:00", "16:00-20:00"]
                }
            ]
        })
        response = await ac.get("/couriers/1")
    assert response.status_code == 200
    assert response.json() == {
        "courier_id": 1,
        "courier_type": "FOOT",
        "regions": [
            1,
            2,
            9
        ],
        "working_hours": [
            "10:00-14:00",
            "16:00-20:00"
        ]
    }


@pytest.mark.asyncio
async def test_get_non_existing_courier():
    # Предположим, что курьера с id 999 не существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.get("/couriers/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_invalid_courier():
    # Предположим, что курьера с id 999 не существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.get("/couriers/e")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_post_orders_valid():
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.post("/orders", json={
            "orders": [
                {
                    "weight": 1.5,
                    "regions": 1,
                    "delivery_hours": [
                        "09:00-12:00"
                    ],
                    "cost": 150
                },
                {
                    "weight": 3.2,
                    "regions": 2,
                    "delivery_hours": [
                        "14:00-18:00",
                        "19:00-22:00"
                    ],
                    "cost": 250
                },
                {
                    "weight": 0.8,
                    "regions": 1,
                    "delivery_hours": [
                        "10:00-11:00",
                        "13:00-14:00"
                    ],
                    "cost": 100
                }
            ]
        })
    assert response.status_code == 200
    assert response.json() == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": [
                "09:00-12:00"
            ],
            "cost": 150.0,
            "completed_time": None
        },
        {
            "order_id": 2,
            "weight": 3.2,
            "regions": 2,
            "delivery_hours": [
                "14:00-18:00",
                "19:00-22:00"
            ],
            "cost": 250.0,
            "completed_time": None
        },
        {
            "order_id": 3,
            "weight": 0.8,
            "regions": 1,
            "delivery_hours": [
                "10:00-11:00",
                "13:00-14:00"
            ],
            "cost": 100.0,
            "completed_time": None
        }
    ]


@pytest.mark.asyncio
async def test_post_orders_invalid():
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.post("/orders", json={
            "orders": [
                {
                    "weight": 100,
                    "regions": 1,
                    "delivery_hours": ["invalid"],
                }
            ]
        })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_existing_order():
    # Предположим, что заказ с id 1 существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.get("/orders/1")
    assert response.status_code == 200
    assert response.json() == {
        "order_id": 1,
        "weight": 1.5,
        "regions": 1,
        "delivery_hours": [
            "09:00-12:00"
        ],
        "cost": 150.0,
        "completed_time": None
    }


@pytest.mark.asyncio
async def test_get_non_existing_order():
    # Предположим, что заказа с id 999 не существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.get("/orders/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_invalid_order():
    # Предположим, что заказа с id 999 не существует
    async with AsyncClient(app=app, base_url=f"http://{HOST}") as ac:
        response = await ac.get("/orders/e")
    assert response.status_code == 400
