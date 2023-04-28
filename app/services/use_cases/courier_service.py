from datetime import datetime

from models import (
    CompleteOrderList,
    CourierMetaInfo,
    CourierModel,
    CouriersList,
    CouriersListResponse,
    CourierType,
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

    async def get_courier_meta_info(
        self, *, courier_id: int, start_date: datetime, end_date: datetime
    ):
        courier = await self.repository.get_courier(courier_id=courier_id)
        (
            sum_of_orders,
            completed_orders,
        ) = await self.repository.get_cost_sum_and_order_count(
            courier_id=courier_id, start_date=start_date, end_date=end_date
        )
        salary_coefficient = self.get_courier_type_salary_coefficient(
            courier_type=courier.courier_type
        )
        rating__coefficient = self.get_courier_type_rating_coefficient(
            courier_type=courier.courier_type
        )
        earnings = None if completed_orders == 0 else sum_of_orders * salary_coefficient

        if completed_orders == 0:
            rating = None
        else:
            rating = (
                completed_orders
                / ((end_date - start_date).days * 24)
                * rating__coefficient
            )

        return CourierMetaInfo(
            courier_id=courier.id,
            courier_type=courier.courier_type,
            regions=courier.regions,
            working_hours=courier.working_hours,
            rating=rating,
            earnings=earnings,
        )

    @staticmethod
    def get_courier_type_salary_coefficient(courier_type: CourierType) -> int:
        if courier_type == CourierType.AUTO:
            return 4
        elif courier_type == CourierType.BIKE:
            return 3
        elif courier_type == CourierType.FOOT:
            return 2

    @staticmethod
    def get_courier_type_rating_coefficient(courier_type: CourierType) -> int:
        if courier_type == CourierType.AUTO:
            return 1
        elif courier_type == CourierType.BIKE:
            return 2
        elif courier_type == CourierType.FOOT:
            return 3
