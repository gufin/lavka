from models import (
    CompleteOrderList,
    CourierModel,
    CouriersList,
    CouriersListResponse,
    OrderModel,
    OrdersList,
)
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class CourierService:
    def __init__(self, repository: LavkaAbstractRepository):
        self.repository = repository

    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        return await self.repository.create_couriers(couriers_model=couriers_model)

    async def get_courier(self, *, courier_id: int) -> CourierModel:
        return await self.repository.get_courier(courier_id=courier_id)

    async def get_couriers(self, offset: int, limit: int) -> CouriersListResponse:
        return await self.repository.get_couriers(offset=offset, limit=limit)

    async def create_orders(self, *, orders_model: OrdersList) -> list[OrderModel]:
        return await self.repository.create_orders(orders_model=orders_model)

    async def get_order(self, *, order_id: int) -> OrderModel:
        return await self.repository.get_order(order_id=order_id)

    async def get_orders(self, offset: int, limit: int) -> list[OrderModel]:
        return await self.repository.get_orders(offset=offset, limit=limit)

    async def complete_orders(
        self, complete_orders_model: CompleteOrderList
    ) -> list[OrderModel]:
        return await self.repository.complete_orders(
            complete_orders_model=complete_orders_model
        )
