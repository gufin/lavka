import datetime

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.containers import Container
from infrastructure.rate_limiter import rate_limiter
from models import CompleteOrderList, OrdersList
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/orders", dependencies=[Depends(rate_limiter)])
@inject
async def create_orders(
    request: Request,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    body = await request.json()
    try:
        orders_model = OrdersList.parse_obj(body)
        return await courier_service.create_orders(orders_model=orders_model)
    except ValidationError:
        return JSONResponse(content={}, status_code=400)


@router.get("/orders/{order_id}", dependencies=[Depends(rate_limiter)])
@inject
async def get_order(
    order_id,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    try:
        correct_order_id = int(order_id)
        result = await courier_service.get_order(order_id=correct_order_id)
        return (
            JSONResponse(content={}, status_code=404)
            if result is None
            else result
        )
    except ValueError:
        return JSONResponse(content={}, status_code=400)


@router.get("/orders", dependencies=[Depends(rate_limiter)])
@inject
async def get_orders(
    offset=0,
    limit=1,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    try:
        correct_offset = int(offset)
        correct_limit = int(limit)
        if correct_offset >= 0 and correct_limit > 0:
            return await courier_service.get_orders(offset=offset, limit=limit)
        return JSONResponse(content={}, status_code=400)
    except ValueError:
        return JSONResponse(content={}, status_code=400)


@router.post("/orders/complete", dependencies=[Depends(rate_limiter)])
@inject
async def complete_orders(
    request: Request,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    body = await request.json()
    try:
        complete_orders_model = CompleteOrderList.parse_obj(body)
        result = await courier_service.complete_orders(
            complete_orders_model=complete_orders_model
        )
        return (
            JSONResponse(content={}, status_code=400)
            if result is None
            else result
        )
    except ValidationError:
        return JSONResponse(content={}, status_code=400)


@router.post("/orders/assign", dependencies=[Depends(rate_limiter)])
@inject
async def assign_orders(
    date=datetime.datetime.now(),
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    if type(date) != datetime.datetime:
        try:
            correct_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValidationError:
            return JSONResponse(content={}, status_code=400)
    else:
        correct_date = date
    result = await courier_service.assign_orders(date=correct_date)
    return (
        JSONResponse(content={}, status_code=400)
        if result is None
        else JSONResponse(content=result.dict(), status_code=201)
    )
