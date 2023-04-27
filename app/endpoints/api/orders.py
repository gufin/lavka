from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.containers import Container
from models import CompleteOrderList, OrderModel, OrdersList
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/orders")
@inject
async def create_orders(
    request: Request,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
):
    body = await request.json()
    try:
        orders_model = OrdersList.parse_obj(body)
        return await courier_service.create_orders(orders_model=orders_model)
    except ValidationError:
        return JSONResponse(content={}, status_code=400)

@router.get("/orders/{order_id}")
@inject
async def get_order(
    order_id,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
):
    try:
        correct_order_id = int(order_id)
        result = await courier_service.get_order(order_id=correct_order_id)
        return JSONResponse(content={},
                        status_code=404) if result is None else result
    except:
        return JSONResponse(content={}, status_code=400)

@router.get("/orders")
@inject
async def get_orders(
    offset: int = Query(0, ge=0),
    limit: int = Query(1, ge=1),
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> list[OrderModel]:
    return await courier_service.get_orders(offset=offset, limit=limit)


@router.post("/orders/complete")
@inject
async def complete_orders(
    complete_orders_model: CompleteOrderList,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> list[OrderModel]:
    return await courier_service.complete_orders(
        complete_orders_model=complete_orders_model
    )
