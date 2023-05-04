from datetime import datetime, timedelta
from typing import Optional

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

    async def create_orders(
        self, *, orders_model: OrdersList
    ) -> list[OrderModel]:
        return await self.repository.create_orders(orders_model=orders_model)

    async def get_order(self, *, order_id: int) -> OrderModel:
        return await self.repository.get_order(order_id=order_id)

    async def get_orders(self, offset: int, limit: int) -> list[OrderModel]:
        return await self.repository.get_orders(offset=offset, limit=limit)

    async def complete_orders(self, complete_orders_model: CompleteOrderList):
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
        earnings = (
            None
            if completed_orders == 0
            else sum_of_orders * salary_coefficient
        )

        if completed_orders == 0:
            rating = None
        else:
            working_hours = self.get_working_hours(
                time_ranges=courier.working_hours
            )
            rating = completed_orders / working_hours * rating__coefficient

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

    async def assign_orders(self, date: datetime):
        count_of_schedule = await self.repository.get_count_of_schedule(
            date=date
        )
        if count_of_schedule == 0:
            couriers_response = await self.repository.get_couriers(
                offset=0, limit=1000
            )
            orders_to_assign = await self.repository.get_orders_to_assign(
                date=date
            )
            courier_type_settings = self.get_courier_type_settings()

            sorted_orders = sorted(
                orders_to_assign, key=lambda order: order.weight, reverse=True
            )

            (
                courier_time_slots,
                courier_available_slots,
            ) = self.get_courier_time_slots(
                couriers_response=couriers_response,
                courier_type_settings=courier_type_settings,
                date=date,
            )
            for order in sorted_orders:
                for courier in couriers_response.couriers:
                    settings = courier_type_settings[courier.courier_type]

                    if (
                        order.regions
                        in courier.regions[: settings["max_regions"]]
                        and order.weight <= settings["max_weight"]
                        and courier_available_slots[courier.id] > 0
                    ):
                        timeslot_id = self.get_timeslot_id(
                            order_delivery_hours=order.delivery_hours,
                            courier_time_slots=courier_time_slots[courier.id],
                            max_orders=settings["max_orders"],
                            weight=order.weight,
                            max_weight=settings["max_weight"],
                        )
                        if timeslot_id is not None:
                            courier_time_slots[courier.id][timeslot_id][
                                1
                            ].append(order.id)
                            courier_time_slots[courier.id][timeslot_id][
                                2
                            ] += order.weight
                            if (
                                len(
                                    courier_time_slots[courier.id][
                                        timeslot_id
                                    ][1]
                                )
                                == 1
                            ):
                                courier_time_slots[courier.id][timeslot_id][
                                    3
                                ] += order.cost
                            else:
                                courier_time_slots[courier.id][timeslot_id][
                                    3
                                ] += (
                                    order.cost * settings["delivery_cost"][1]
                                )
                            courier_available_slots[courier.id] -= 1
                            break

            return await self.repository.save_schedule(
                courier_time_slots=courier_time_slots, date=date
            )
        return None

    def get_courier_time_slots(
        self, couriers_response, courier_type_settings, date
    ):
        courier_time_slots = {}
        courier_available_slots = {}
        for courier in couriers_response.couriers:
            courier_time_slots[courier.id] = []
            courier_available_slots[courier.id] = 0
            settings = courier_type_settings[courier.courier_type]
            max_time_slot_time = settings["order_time"][0] + settings[
                "order_time"
            ][1] * (settings["max_orders"] - 1)
            for time_interval in courier.working_hours:
                duration_minutes = (
                    self.get_duration_minutes(time_interval)
                    + max_time_slot_time
                )
                start_date = self.get_start_date(
                    time_interval=time_interval, date=date
                )
                while duration_minutes >= max_time_slot_time:
                    courier_time_slots[courier.id].append(
                        ([start_date, [], 0, 0])
                    )
                    start_date += timedelta(minutes=max_time_slot_time)
                    courier_available_slots[courier.id] += 1
                    duration_minutes -= max_time_slot_time
        return courier_time_slots, courier_available_slots

    def get_timeslot_id(
        self,
        order_delivery_hours: list,
        courier_time_slots: list,
        max_orders: int,
        weight: float,
        max_weight: float,
    ) -> Optional[int]:
        return next(
            (
                pos
                for pos, time_slot in enumerate(courier_time_slots)
                if len(time_slot[1]) < max_orders
                and time_slot[2] + weight <= max_weight
                and self.is_time_in_intervals(
                    time=time_slot[0], intervals=order_delivery_hours
                )
            ),
            None,
        )

    def is_time_in_intervals(self, time: datetime, intervals: list):
        time_minutes = time.hour * 60 + time.minute
        for interval in intervals:
            start_str, end_str = interval.split("-")
            start_minutes = self.time_to_minutes(start_str)
            end_minutes = self.time_to_minutes(end_str)
            if start_minutes <= time_minutes < end_minutes:
                return True
        return False

    @staticmethod
    def time_to_minutes(time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def check_overlap_exist(
        self, courier_working_hours: list, order_delivery_hours: list
    ) -> bool:
        def intervals_overlap(start1, end1, start2, end2):
            return start1 < end2 and start2 < end1

        overlap_found = False

        for courier_interval in courier_working_hours:
            courier_start, courier_end = courier_interval.split("-")
            courier_start_minutes = self.time_to_minutes(courier_start)
            courier_end_minutes = self.time_to_minutes(courier_end)

            for order_interval in order_delivery_hours:
                order_start, order_end = order_interval.split("-")
                order_start_minutes = self.time_to_minutes(order_start)
                order_end_minutes = self.time_to_minutes(order_end)

                if intervals_overlap(
                    courier_start_minutes,
                    courier_end_minutes,
                    order_start_minutes,
                    order_end_minutes,
                ):
                    overlap_found = True
                    break

            if overlap_found:
                break
        return overlap_found

    @staticmethod
    def get_start_date(time_interval: str, date: datetime) -> int:
        start_time_str, end_time_str = time_interval.split("-")
        start_hours, start_minutes = map(int, start_time_str.split(":"))
        start_time_delta = timedelta(hours=start_hours, minutes=start_minutes)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_of_day + start_time_delta

    @staticmethod
    def get_duration_minutes(time_interval: str) -> int:
        start_time_str, end_time_str = time_interval.split("-")
        start_hours, start_minutes = map(int, start_time_str.split(":"))
        end_hours, end_minutes = map(int, end_time_str.split(":"))
        start_minutes_total = start_hours * 60 + start_minutes
        end_minutes_total = end_hours * 60 + end_minutes
        return end_minutes_total - start_minutes_total

    @staticmethod
    def get_courier_type_settings() -> dict:
        return {
            CourierType.FOOT: {
                "max_weight": 10,
                "max_orders": 2,
                "max_regions": 1,
                "order_time": [25, 10],
                "delivery_cost": [1.0, 0.8],
            },
            CourierType.BIKE: {
                "max_weight": 20,
                "max_orders": 4,
                "max_regions": 2,
                "order_time": [12, 8],
                "delivery_cost": [1.0, 0.8],
            },
            CourierType.AUTO: {
                "max_weight": 40,
                "max_orders": 7,
                "max_regions": 3,
                "order_time": [8, 4],
                "delivery_cost": [1.0, 0.8],
            },
        }

    async def get_couriers_assignments(self, courier_id: int, date: datetime):
        return await self.repository.get_couriers_assignments(courier_id=courier_id, date=date)
