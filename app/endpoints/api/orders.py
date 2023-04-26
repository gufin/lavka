from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query

from core.containers import Container
from models import OrderModel, OrdersList
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/orders")
@inject
async def create_orders(
    orders_model: OrdersList,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> list[OrderModel]:
    return await courier_service.create_orders(orders_model=orders_model)


@router.get("/orders/{order_id}")
@inject
async def get_order(
    order_id: int,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> OrderModel:
    return await courier_service.get_order(order_id=order_id)
