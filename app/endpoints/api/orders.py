import datetime
from http import HTTPStatus

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.containers import Container
from infrastructure.rate_limiter import rate_limiter
from models import CompleteOrderList, OrdersList
from services.use_cases.order_service import OrderService

router = APIRouter()


@router.post("/orders", dependencies=[Depends(rate_limiter)])
@inject
async def create_orders(
    request: Request,
    order_service: OrderService = Depends(Provide[Container.order_service]),
):
    body = await request.json()
    try:
        orders_model = OrdersList.parse_obj(body)
        return await order_service.create_orders(orders_model=orders_model)
    except ValidationError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.get("/orders/{order_id}", dependencies=[Depends(rate_limiter)])
@inject
async def get_order(
    order_id,
    order_service: OrderService = Depends(Provide[Container.order_service]),
):
    try:
        correct_order_id = int(order_id)
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )

    result = await order_service.get_order(order_id=correct_order_id)
    return (
        JSONResponse(
            content={"detail": "Order not found."},
            status_code=HTTPStatus.NOT_FOUND,
        )
        if result is None
        else result
    )


@router.get("/orders", dependencies=[Depends(rate_limiter)])
@inject
async def get_orders(
    offset=0,
    limit=1,
    order_service: OrderService = Depends(Provide[Container.order_service]),
):
    try:
        correct_offset = int(offset)
        correct_limit = int(limit)
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )

    if correct_offset < 0 or correct_limit < 0:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )
    return await order_service.get_orders(offset=offset, limit=limit)


@router.post("/orders/complete", dependencies=[Depends(rate_limiter)])
@inject
async def complete_orders(
    request: Request,
    order_service: OrderService = Depends(Provide[Container.order_service]),
):
    body = await request.json()
    try:
        complete_orders_model = CompleteOrderList.parse_obj(body)
        result = await order_service.complete_orders(
            complete_orders_model=complete_orders_model
        )
        return (
            JSONResponse(
                content={"detail": "Invalid data provided."},
                status_code=HTTPStatus.BAD_REQUEST,
            )
            if result is None
            else result
        )
    except ValidationError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )


@router.post("/orders/assign", dependencies=[Depends(rate_limiter)])
@inject
async def assign_orders(
    date=None,
    order_service: OrderService = Depends(Provide[Container.order_service]),
):
    if date is None:
        date = datetime.datetime.now()

    if isinstance(date, datetime.datetime):
        correct_date = date
    else:
        try:
            correct_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValidationError:
            return JSONResponse(
                content={"detail": "Invalid data provided."},
                status_code=HTTPStatus.BAD_REQUEST,
            )

    result = await order_service.assign_orders(date=correct_date)
    return (
        JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST,
        )
        if result is None
        else JSONResponse(
            content=result.dict(), status_code=HTTPStatus.CREATED
        )
    )
