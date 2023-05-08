from datetime import datetime

from models import (
    CourierMetaInfo,
    CourierModel,
    CouriersList,
    CouriersListResponse,
    CourierType,
)
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class CourierService:
    def __init__(self, repository: LavkaAbstractRepository):
        self.repository = repository
        self.salary_coefficients = {
            CourierType.AUTO: 4,
            CourierType.BIKE: 3,
            CourierType.FOOT: 2,
        }

        self.rating_coefficients = {
            CourierType.AUTO: 1,
            CourierType.BIKE: 2,
            CourierType.FOOT: 3,
        }

    async def create_couriers(
        self, *, couriers_model: CouriersList
    ) -> CouriersList:
        return await self.repository.create_couriers(
            couriers_model=couriers_model
        )

    async def get_courier(self, *, courier_id: int) -> CourierModel:
        return await self.repository.get_courier(courier_id=courier_id)

    async def get_couriers(
        self, offset: int, limit: int
    ) -> CouriersListResponse:
        return await self.repository.get_couriers(offset=offset, limit=limit)

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
        if completed_orders == 0:
            rating = None
            earnings = None
        else:
            earnings = (
                sum_of_orders * self.salary_coefficients[courier.courier_type]
            )

            working_hours = self.get_working_hours(
                time_ranges=courier.working_hours
            )
            rating = (
                completed_orders
                / working_hours
                * self.rating_coefficients[courier.courier_type]
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
    def get_working_hours(time_ranges: list) -> float:
        start_times, end_times = [], []
        for time_range in time_ranges:
            start, end = time_range.split("-")
            start_times.append(datetime.strptime(start, "%H:%M").time())
            end_times.append(datetime.strptime(end, "%H:%M").time())

        min_start_time = min(start_times)
        max_end_time = max(end_times)

        start_datetime = datetime.combine(datetime.min, min_start_time)
        end_datetime = datetime.combine(datetime.min, max_end_time)
        time_difference = end_datetime - start_datetime

        return time_difference.total_seconds() / 3600

    async def get_couriers_assignments(self, courier_id: int, date: datetime):
        return await self.repository.get_couriers_assignments(
            courier_id=courier_id, date=date
        )
