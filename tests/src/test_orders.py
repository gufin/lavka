from datetime import datetime
from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_post_orders_valid(make_post_request, setup_database):
    await setup_database
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
    assert response.status == HTTPStatus.OK
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


@pytest.mark.parametrize(
    "params",
    [
        {
            "orders": [
                {
                    "weight": 100,
                    "regions": 1,
                    "delivery_hours": ["invalid"],
                }
            ]
        },
        {},
    ],
)
async def test_post_orders_invalid(params, make_post_request):
    response = await make_post_request("/orders", params=params)
    assert response.status == HTTPStatus.BAD_REQUEST


async def test_get_existing_order(make_get_request):
    response = await make_get_request("/orders/1")
    assert response.status == HTTPStatus.OK
    assert response.body == {
        "order_id": 1,
        "weight": 1.5,
        "regions": 1,
        "delivery_hours": ["09:00-12:00"],
        "cost": 150.0,
        "completed_time": None,
    }


async def test_get_non_existing_order(make_get_request):
    response = await make_get_request("/orders/999")
    assert response.status == HTTPStatus.NOT_FOUND


async def test_get_invalid_order(make_get_request):
    response = await make_get_request("/orders/e")
    assert response.status == 400


async def test_get_orders(make_get_request):
    response = await make_get_request("/orders")
    assert response.status == HTTPStatus.OK
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


async def test_get_orders_limit(make_get_request):
    response = await make_get_request("/orders?limit=2")
    assert response.status == HTTPStatus.OK
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


async def test_get_orders_offset(make_get_request):
    response = await make_get_request("/orders?offset=1")
    assert response.status == HTTPStatus.OK
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


async def test_get_orders_limit_offset(make_get_request):
    response = await make_get_request("/orders?limit=1&offset=1")
    assert response.status == HTTPStatus.OK
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


@pytest.mark.parametrize("limit", ["e", "-1"])
async def test_get_orders_invalid_limit(limit, make_get_request):
    response = await make_get_request(f"/orders?limit={limit}")
    assert response.status == 400


@pytest.mark.parametrize("offset", ["e", "-1"])
async def test_get_orders_invalid_offset(offset, make_get_request):
    response = await make_get_request(f"/orders?offset={offset}")
    assert response.status == 400


@pytest.mark.parametrize(
    "limit,offset",
    [
        ("-1", "-1"),
        ("e", "e"),
        ("1", "e"),
        ("e", "1"),
    ],
)
async def test_get_orders_invalid_limit_offset(
    limit, offset, make_get_request
):
    response = await make_get_request(f"/orders?limit={limit}&offset={offset}")
    assert response.status == 400


async def test_get_orders_limit_offset_out_of_range(make_get_request):
    response = await make_get_request("/orders?limit=1&offset=100")
    assert response.status == HTTPStatus.OK
    assert response.body == []


async def test_complete_orders(make_post_request, create_couriers):
    await create_couriers
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
    assert response.status == HTTPStatus.OK
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


async def test_repeat_complete_orders(make_post_request, complete_orders):
    await complete_orders
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
    assert response.status == HTTPStatus.OK
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


@pytest.mark.parametrize(
    "complete_info",
    [
        [
            {
                "courier_id": 1,
                "order_id": 1,
                "complete_time": "2023-04-01T12:00:00.000Z",
            }
        ],
        [
            {
                "courier_id": 2,
                "order_id": 1,
                "complete_time": "2023-04-01T12:00:00.000Z",
            }
        ],
    ],
)
async def test_invalid_data_complete_orders(
    complete_info, make_post_request, complete_orders
):
    await complete_orders
    response = await make_post_request(
        "/orders/complete",
        params={"complete_info": complete_info},
    )
    assert response.status == 400


async def test_assign_orders(
    make_post_request, setup_database, create_couriers, create_orders
):
    await setup_database
    await create_couriers
    await create_orders
    response = await make_post_request("/orders/assign")
    assert response.status == HTTPStatus.CREATED
    assert response.body == {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "couriers": [
            {
                "courier_id": 1,
                "orders": [
                    {
                        "group_order_id": 0,
                        "orders": [
                            {
                                "id": 1,
                                "weight": 1.5,
                                "regions": 1,
                                "delivery_hours": ["09:00-12:00"],
                                "cost": 150.0,
                                "completed_time": None,
                            }
                        ],
                    },
                    {
                        "group_order_id": 1,
                        "orders": [
                            {
                                "id": 3,
                                "weight": 0.8,
                                "regions": 1,
                                "delivery_hours": [
                                    "10:00-11:00",
                                    "13:00-14:00",
                                ],
                                "cost": 100.0,
                                "completed_time": None,
                            }
                        ],
                    },
                ],
            }
        ],
    }


async def test_assign_orders_with_param(
    make_post_request, setup_database, create_couriers, create_orders
):
    await setup_database
    await create_couriers
    await create_orders
    current_date = datetime.now().strftime("%Y-%m-%d")
    response = await make_post_request(f"/orders/assign?date={current_date}")
    assert response.status == HTTPStatus.CREATED
    assert response.body == {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "couriers": [
            {
                "courier_id": 1,
                "orders": [
                    {
                        "group_order_id": 0,
                        "orders": [
                            {
                                "id": 1,
                                "weight": 1.5,
                                "regions": 1,
                                "delivery_hours": ["09:00-12:00"],
                                "cost": 150.0,
                                "completed_time": None,
                            }
                        ],
                    },
                    {
                        "group_order_id": 1,
                        "orders": [
                            {
                                "id": 3,
                                "weight": 0.8,
                                "regions": 1,
                                "delivery_hours": [
                                    "10:00-11:00",
                                    "13:00-14:00",
                                ],
                                "cost": 100.0,
                                "completed_time": None,
                            }
                        ],
                    },
                ],
            }
        ],
    }


async def test_double_assign_orders(
    make_post_request,
    setup_database,
    create_couriers,
    create_orders,
    assign_orders,
):
    await setup_database
    await create_couriers
    await create_orders
    await assign_orders
    response = await make_post_request("/orders/assign")
    assert response.status == 400
