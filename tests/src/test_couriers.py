import asyncio

import pytest

pytestmark = pytest.mark.asyncio


async def test_post_courier_valid(make_post_request, setup_database):
    await setup_database
    response = await make_post_request(
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
    assert response.status == 200
    assert response.body == {
        "couriers": [
            {
                "courier_id": 1,
                "courier_type": "FOOT",
                "regions": [1, 2, 9],
                "working_hours": ["10:00-14:00", "16:00-20:00"],
            },
            {
                "courier_id": 2,
                "courier_type": "BIKE",
                "regions": [4, 5, 6],
                "working_hours": ["09:00-13:00", "15:00-19:00"],
            },
            {
                "courier_id": 3,
                "courier_type": "AUTO",
                "regions": [7, 8, 17],
                "working_hours": ["08:00-12:00", "14:00-18:00"],
            },
        ]
    }
    await asyncio.sleep(1)


async def test_post_courier_invalid(make_post_request):
    response = await make_post_request(
        "/couriers",
        params={
            "couriers": [
                {
                    "courier_type": "foot",
                    "regions": [1, 2, 3],
                    "working_hours": ["invalid"],
                }
            ]
        },
    )
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_existing_courier(make_get_request):
    response = await make_get_request("/couriers/1")
    assert response.status == 200
    assert response.body == {
        "courier_id": 1,
        "courier_type": "FOOT",
        "regions": [1, 2, 9],
        "working_hours": ["10:00-14:00", "16:00-20:00"],
    }
    await asyncio.sleep(1)


async def test_get_non_existing_courier(make_get_request):
    response = await make_get_request("/couriers/999")
    assert response.status == 404
    await asyncio.sleep(1)


async def test_get_invalid_courier(make_get_request):
    response = await make_get_request("/couriers/e")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers(make_get_request):
    response = await make_get_request("/couriers")
    assert response.status == 200
    assert response.body == {
        "couriers": [
            {
                "courier_id": 1,
                "courier_type": "FOOT",
                "regions": [1, 2, 9],
                "working_hours": ["10:00-14:00", "16:00-20:00"],
            }
        ],
        "limit": 1,
        "offset": 0,
    }
    await asyncio.sleep(1)


async def test_get_couriers_limit(make_get_request):
    response = await make_get_request("/couriers?limit=2")
    assert response.status == 200
    assert response.body == {
        "couriers": [
            {
                "courier_id": 1,
                "courier_type": "FOOT",
                "regions": [1, 2, 9],
                "working_hours": ["10:00-14:00", "16:00-20:00"],
            },
            {
                "courier_id": 2,
                "courier_type": "BIKE",
                "regions": [4, 5, 6],
                "working_hours": ["09:00-13:00", "15:00-19:00"],
            },
        ],
        "limit": 2,
        "offset": 0,
    }
    await asyncio.sleep(1)


async def test_get_couriers_offset(make_get_request):
    response = await make_get_request("/couriers?offset=1")
    assert response.status == 200
    assert response.body == {
        "couriers": [
            {
                "courier_id": 2,
                "courier_type": "BIKE",
                "regions": [4, 5, 6],
                "working_hours": ["09:00-13:00", "15:00-19:00"],
            }
        ],
        "limit": 1,
        "offset": 1,
    }
    await asyncio.sleep(1)


async def test_get_couriers_limit_offset(make_get_request):
    response = await make_get_request("/couriers?limit=1&offset=1")
    assert response.status == 200
    assert response.body == {
        "couriers": [
            {
                "courier_id": 2,
                "courier_type": "BIKE",
                "regions": [4, 5, 6],
                "working_hours": ["09:00-13:00", "15:00-19:00"],
            }
        ],
        "limit": 1,
        "offset": 1,
    }
    await asyncio.sleep(1)


async def test_get_couriers_invalid_limit(make_get_request):
    response = await make_get_request("/couriers?limit=e")
    assert response.status == 400
    response = await make_get_request("/couriers?limit=-1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers_invalid_offset(make_get_request):
    response = await make_get_request("/couriers?offset=e")
    assert response.status == 400
    response = await make_get_request("/couriers?offset=-1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers_invalid_limit_offset(make_get_request):
    response = await make_get_request("/couriers?limit=-1&offset=-1")
    assert response.status == 400
    response = await make_get_request("/couriers?limit=e&offset=e")
    assert response.status == 400
    response = await make_get_request("/couriers?limit=1&offset=e")
    assert response.status == 400
    response = await make_get_request("/couriers?limit=e&offset=1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers_limit_offset_out_of_range(make_get_request):
    response = await make_get_request("/couriers?limit=1&offset=100")
    assert response.status == 200
    assert response.body == {"couriers": [], "limit": 1, "offset": 100}
    await asyncio.sleep(1)
