import asyncio

import pytest
from pytest import approx

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


async def test_post_courier_invalid(
    make_post_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
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


async def test_get_existing_courier(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request("/couriers/1")
    assert response.status == 200
    assert response.body == {
        "courier_id": 1,
        "courier_type": "FOOT",
        "regions": [1, 2, 9],
        "working_hours": ["10:00-14:00", "16:00-20:00"],
    }
    await asyncio.sleep(1)


async def test_get_non_existing_courier(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request("/couriers/999")
    assert response.status == 404
    await asyncio.sleep(1)


async def test_get_invalid_courier(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request("/couriers/e")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers(make_get_request, setup_database, create_couriers):
    await setup_database
    await create_couriers
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


async def test_get_couriers_limit(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
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


async def test_get_couriers_offset(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
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


async def test_get_couriers_limit_offset(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
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


@pytest.mark.parametrize("limit", ["e", "-1"])
async def test_get_couriers_invalid_limit(
    limit, make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request(f"/couriers?limit={limit}")
    assert response.status == 400
    await asyncio.sleep(1)


@pytest.mark.parametrize("offset", ["e", "-1"])
async def test_get_couriers_invalid_offset(
    offset, make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request(f"/couriers?offset={offset}")
    assert response.status == 400
    await asyncio.sleep(1)


@pytest.mark.parametrize(
    "limit,offset",
    [
        ("-1", "-1"),
        ("e", "e"),
        ("1", "e"),
        ("e", "1"),
    ],
)
async def test_get_couriers_invalid_limit_offset(
    limit, offset, make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request(
        f"/couriers?limit={limit}&offset={offset}"
    )
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_couriers_limit_offset_out_of_range(
    make_get_request, setup_database, create_couriers
):
    await setup_database
    await create_couriers
    response = await make_get_request("/couriers?limit=1&offset=100")
    assert response.status == 200
    assert response.body == {"couriers": [], "limit": 1, "offset": 100}
    await asyncio.sleep(1)


async def test_get_courier_meta_info(
    make_get_request,
    setup_database,
    create_couriers,
    create_orders,
    complete_orders,
):
    await setup_database
    await create_couriers
    await create_orders
    await complete_orders
    response = await make_get_request(
        "/couriers/meta-info/1?start_date=2023-04-01&end_date=2023-05-02"
    )
    assert response.status == 200
    assert response.body == {
        "courier_id": 1,
        "courier_type": "FOOT",
        "regions": [1, 2, 9],
        "working_hours": ["10:00-14:00", "16:00-20:00"],
        "earnings": 300,
        "rating": approx(0.3),
    }
    await asyncio.sleep(1)


async def test_get_courier_meta_info_different_period(
    make_get_request,
    setup_database,
    create_couriers,
    create_orders,
    complete_orders,
):
    await setup_database
    await create_couriers
    await create_orders
    await complete_orders
    response = await make_get_request(
        "/couriers/meta-info/1?start_date=2023-04-01&end_date=2023-05-01"
    )
    assert response.status == 200
    assert response.body == {
        "courier_id": 1,
        "courier_type": "FOOT",
        "regions": [1, 2, 9],
        "working_hours": ["10:00-14:00", "16:00-20:00"],
        "earnings": None,
        "rating": None,
    }
    await asyncio.sleep(1)


@pytest.mark.parametrize(
    "query_params",
    [
        "?start_date=2023-04-01",
        "?end_date=2023-05-01",
        "",
    ],
)
async def test_get_courier_meta_info_missing_params(
    query_params,
    make_get_request,
    setup_database,
    create_couriers,
    create_orders,
    complete_orders,
):
    await setup_database
    await create_couriers
    await create_orders
    await complete_orders
    response = await make_get_request(f"/couriers/meta-info/1{query_params}")
    assert response.status == 422
    await asyncio.sleep(1)


@pytest.mark.parametrize(
    "path, start_date, end_date",
    [
        ("/couriers/meta-info/1", "e", "2023-05-01"),
        ("/couriers/meta-info/1", "2023-04-01", "e"),
        ("/couriers/meta-info/e", "2023-04-01", "2023-05-01"),
        ("/couriers/meta-info/e", "e", "e"),
    ],
)
async def test_get_courier_meta_info_invalid_params(
    path,
    start_date,
    end_date,
    make_get_request,
    setup_database,
    create_couriers,
    create_orders,
    complete_orders,
):
    await setup_database
    await create_couriers
    await create_orders
    await complete_orders
    response = await make_get_request(
        f"{path}?start_date={start_date}&end_date={end_date}"
    )
    assert response.status == 400
    await asyncio.sleep(1)
