from datetime import datetime, timedelta
from typing import Any, Optional

from core.constants import COURIER_SETTINGS
from models import (
    CompleteOrderList,
    OrderModel,
    OrdersList,
)
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class OrderService:
    def __init__(self, repository: LavkaAbstractRepository):
        self.repository = repository

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

    async def assign_orders(self, date: datetime):
        if await self.repository.get_count_of_schedule(date=date) > 0:
            return None

        couriers = await self.repository.get_all_couriers()

        if not couriers:
            return None

        orders_to_assign = await self.repository.get_orders_to_assign(
            date=date
        )
        if not orders_to_assign:
            return None

        sorted_orders = sorted(
            orders_to_assign,
            key=lambda current_order: current_order.weight,
            reverse=True,
        )

        time_slots, available_slots = self.get_time_slots(
            couriers=couriers,
            current_courier_settings=COURIER_SETTINGS,
            date=date,
        )

        for order in sorted_orders:
            for courier in couriers:
                settings = COURIER_SETTINGS[courier.courier_type]

                if (
                    order.regions
                    not in courier.regions[: settings["max_regions"]]
                    or order.weight > settings["max_weight"]
                    or available_slots[courier.id] <= 0
                ):
                    continue

                timeslot_id = self.get_timeslot_id(
                    order_delivery_hours=order.delivery_hours,
                    time_slots=time_slots[courier.id],
                    max_orders=settings["max_orders"],
                    weight=order.weight,
                    max_weight=settings["max_weight"],
                )

                if timeslot_id is None:
                    continue

                time_slot = time_slots[courier.id][timeslot_id]
                time_slot[1].append(order.id)
                time_slot[2] += order.weight

                time_slot[3] += (
                    order.cost
                    if len(time_slot[1]) == 1
                    else order.cost * settings["next_delivery_cost"]
                )
                available_slots[courier.id] -= 1
                break

        return await self.repository.save_schedule(
            time_slots=time_slots, date=date
        )

    def get_time_slots(
        self, couriers, current_courier_settings, date
    ) -> tuple[dict[Any, list[Any]], dict[Any, int]]:
        time_slots = {}
        available_slots = {}
        for courier in couriers:
            time_slots[courier.id] = []
            available_slots[courier.id] = 0
            settings = current_courier_settings[courier.courier_type]
            max_time_slot_time = settings["first_order_time"] + settings[
                "next_order_time"
            ] * (settings["max_orders"] - 1)
            for time_interval in courier.working_hours:
                duration_minutes = (
                    self.get_duration_minutes(time_interval)
                    + max_time_slot_time
                )
                start_date = self.get_start_date(
                    time_interval=time_interval, date=date
                )
                while duration_minutes >= max_time_slot_time:
                    time_slots[courier.id].append(([start_date, [], 0, 0]))
                    start_date += timedelta(minutes=max_time_slot_time)
                    available_slots[courier.id] += 1
                    duration_minutes -= max_time_slot_time
        return time_slots, available_slots

    def get_timeslot_id(
        self,
        order_delivery_hours: list,
        time_slots: list,
        max_orders: int,
        weight: float,
        max_weight: float,
    ) -> Optional[int]:
        return next(
            (
                pos
                for pos, time_slot in enumerate(time_slots)
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

    @staticmethod
    def get_start_date(time_interval: str, date: datetime) -> datetime:
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
