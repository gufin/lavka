from abc import ABC, abstractmethod
from datetime import datetime

from models import (
    CompleteOrderList,
    CourierModel,
    CouriersList,
    CouriersListResponse,
    OrderModel,
    OrdersList,
)


class LavkaAbstractRepository(ABC):
    @abstractmethod
    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        pass

    @abstractmethod
    async def get_courier(self, *, courier_id: int) -> CourierModel:
        pass

    @abstractmethod
    async def get_couriers(self, offset: int, limit: int) -> CouriersListResponse:
        pass

    @abstractmethod
    async def create_orders(self, orders_model: OrdersList) -> list[OrderModel]:
        pass

    @abstractmethod
    async def get_order(self, *, order_id: int) -> OrderModel:
        pass

    @abstractmethod
    async def get_orders(self, offset: int, limit: int) -> list[OrderModel]:
        pass

    @abstractmethod
    async def complete_orders(self, complete_orders_model: CompleteOrderList):
        pass

    @abstractmethod
    async def get_cost_sum_and_order_count(
        self, courier_id: int, start_date: datetime, end_date: datetime
    ):
        pass
