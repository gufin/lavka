import asyncio

import pytest

pytestmark = pytest.mark.asyncio


async def test_post_orders_valid(make_post_request, setup_database):
    response = await make_post_request(
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
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": ["09:00-12:00"],
            "cost": 150.0,
            "completed_time": None,
        },
        {
            "order_id": 2,
            "weight": 3.2,
            "regions": 2,
            "delivery_hours": ["14:00-18:00", "19:00-22:00"],
            "cost": 250.0,
            "completed_time": None,
        },
        {
            "order_id": 3,
            "weight": 0.8,
            "regions": 1,
            "delivery_hours": ["10:00-11:00", "13:00-14:00"],
            "cost": 100.0,
            "completed_time": None,
        },
    ]
    await asyncio.sleep(1)


async def test_post_orders_invalid(make_post_request):
    response = await make_post_request(
        "/orders",
        params={
            "orders": [
                {
                    "weight": 100,
                    "regions": 1,
                    "delivery_hours": ["invalid"],
                }
            ]
        },
    )
    assert response.status == 400
    response = await make_post_request("/orders", params={})
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_existing_order(make_get_request):
    response = await make_get_request("/orders/1")
    assert response.status == 200
    assert response.body == {
        "order_id": 1,
        "weight": 1.5,
        "regions": 1,
        "delivery_hours": ["09:00-12:00"],
        "cost": 150.0,
        "completed_time": None,
    }
    await asyncio.sleep(1)


async def test_get_non_existing_order(make_get_request):
    response = await make_get_request("/orders/999")
    assert response.status == 404
    await asyncio.sleep(1)


async def test_get_invalid_order(make_get_request):
    response = await make_get_request("/orders/e")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_orders(make_get_request):
    response = await make_get_request("/orders")
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": ["09:00-12:00"],
            "cost": 150.0,
            "completed_time": None,
        }
    ]
    await asyncio.sleep(1)


async def test_get_orders_limit(make_get_request):
    response = await make_get_request("/orders?limit=2")
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": ["09:00-12:00"],
            "cost": 150.0,
            "completed_time": None,
        },
        {
            "order_id": 2,
            "weight": 3.2,
            "regions": 2,
            "delivery_hours": ["14:00-18:00", "19:00-22:00"],
            "cost": 250.0,
            "completed_time": None,
        },
    ]
    await asyncio.sleep(1)


async def test_get_orders_offset(make_get_request):
    response = await make_get_request("/orders?offset=1")
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 2,
            "weight": 3.2,
            "regions": 2,
            "delivery_hours": ["14:00-18:00", "19:00-22:00"],
            "cost": 250.0,
            "completed_time": None,
        }
    ]
    await asyncio.sleep(1)


async def test_get_orders_limit_offset(make_get_request):
    response = await make_get_request("/orders?limit=1&offset=1")
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 2,
            "weight": 3.2,
            "regions": 2,
            "delivery_hours": ["14:00-18:00", "19:00-22:00"],
            "cost": 250.0,
            "completed_time": None,
        }
    ]
    await asyncio.sleep(1)


async def test_get_orders_invalid_limit(make_get_request):
    response = await make_get_request("/orders?limit=e")
    assert response.status == 400
    response = await make_get_request("/orders?limit=-1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_orders_invalid_offset(make_get_request):
    response = await make_get_request("/orders?offset=e")
    assert response.status == 400
    response = await make_get_request("/orders?offset=-1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_orders_invalid_limit_offset(make_get_request):
    response = await make_get_request("/orders?limit=-1&offset=-1")
    assert response.status == 400
    response = await make_get_request("/orders?limit=e&offset=e")
    assert response.status == 400
    response = await make_get_request("/orders?limit=1&offset=e")
    assert response.status == 400
    response = await make_get_request("/orders?limit=e&offset=1")
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_orders_limit_offset_out_of_range(make_get_request):
    response = await make_get_request("/orders?limit=1&offset=100")
    assert response.status == 200
    assert response.body == []
    await asyncio.sleep(1)


async def test_complete_orders(make_post_request):
    response = await make_post_request(
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
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": ["09:00-12:00"],
            "cost": 150.0,
            "completed_time": "2023-05-01T12:00:00",
        }
    ]
    await asyncio.sleep(1)


async def test_invalid_complete_orders(make_post_request):
    response = await make_post_request(
        "/orders/complete",
        params={
            "complete_info": [
                {
                    "courier_id": 1,
                    "order_id": 1,
                }
            ]
        },
    )
    assert response.status == 400
    await asyncio.sleep(1)


async def test_repeat_complete_orders(make_post_request):
    response = await make_post_request(
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
    assert response.status == 200
    assert response.body == [
        {
            "order_id": 1,
            "weight": 1.5,
            "regions": 1,
            "delivery_hours": ["09:00-12:00"],
            "cost": 150.0,
            "completed_time": "2023-05-01T12:00:00",
        }
    ]
    await asyncio.sleep(1)


async def test_invalid_data_complete_orders(make_post_request):
    response = await make_post_request(
        "/orders/complete",
        params={
            "complete_info": [
                {
                    "courier_id": 1,
                    "order_id": 1,
                    "complete_time": "2023-04-01T12:00:00.000Z",
                }
            ]
        },
    )
    assert response.status == 400
    response = await make_post_request(
        "/orders/complete",
        params={
            "complete_info": [
                {
                    "courier_id": 2,
                    "order_id": 1,
                    "complete_time": "2023-04-01T12:00:00.000Z",
                }
            ]
        },
    )
    assert response.status == 400
    await asyncio.sleep(1)


async def test_get_courier_meta_info(make_get_request):
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
        "rating": 0.004032258064516129,
    }
    await asyncio.sleep(1)


async def test_get_courier_meta_info_different_period(make_get_request):
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


async def test_get_courier_meta_info_missing_params(make_get_request):
    response = await make_get_request("/couriers/meta-info/1?start_date=2023-04-01")
    assert response.status == 422
    response = await make_get_request("/couriers/meta-info/1?end_date=2023-05-01")
    assert response.status == 422
    response = await make_get_request("/couriers/meta-info/1")
    assert response.status == 422
    await asyncio.sleep(1)


async def test_get_courier_meta_info_invalid_params(make_get_request):
    response = await make_get_request(
        "/couriers/meta-info/1?start_date=e&end_date=2023-05-01"
    )
    assert response.status == 400
    response = await make_get_request(
        "/couriers/meta-info/1?start_date=2023-04-01&end_date=e"
    )
    assert response.status == 400
    response = await make_get_request(
        "/couriers/meta-info/e?start_date=2023-04-01&end_date=2023-05-01"
    )
    assert response.status == 400
    response = await make_get_request("/couriers/meta-info/e?start_date=e&end_date=e")
    assert response.status == 400
    await asyncio.sleep(1)
