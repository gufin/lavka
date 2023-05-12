import itertools
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func, null, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.entities import (
    Courier,
    engine,
    Order,
    OrderDeliverySchedule,
)
from models import (
    CompleteOrderList,
    CourierModel,
    CourierScheduleModel,
    CouriersList,
    CouriersListResponse,
    DeliveryScheduleModel,
    GroupOrderModel,
    OrderModel,
    OrdersList,
)
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class LavkaPostgresRepository(LavkaAbstractRepository):
    def __init__(self, *, config: dict):
        self.config = config

    async def create_couriers(self, *,
                              couriers_model: CouriersList) -> CouriersList:
        couriers = [Courier(**courier.dict()) for courier in
                    couriers_model.couriers]
        async with AsyncSession(engine) as session:
            async with session.begin():
                session.add_all(couriers)
                await session.flush()
                created_couriers = [
                    CourierModel(
                        courier_id=courier.id,
                        courier_type=courier.courier_type,
                        regions=courier.regions,
                        working_hours=courier.working_hours,
                    )
                    for courier in couriers
                ]
            await session.commit()
        return CouriersList(couriers=created_couriers)

    async def get_courier(self, *, courier_id: int) -> Optional[CourierModel]:
        async with AsyncSession(engine) as session:
            stmt = select(Courier).where(Courier.id == courier_id)
            result = await session.execute(stmt)
            courier = result.scalar_one_or_none()

            if courier is None:
                return None

            return CourierModel(
                courier_id=courier.id,
                courier_type=courier.courier_type,
                regions=courier.regions,
                working_hours=courier.working_hours,
            )

    async def get_couriers(
            self, offset: int, limit: int
    ) -> CouriersListResponse:
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(Courier).offset(offset).limit(limit)
                result = await session.execute(stmt)
                couriers = result.scalars().all()
                couriers_models = [
                    CourierModel(
                        courier_id=courier.id,
                        courier_type=courier.courier_type,
                        regions=courier.regions,
                        working_hours=courier.working_hours,
                    )
                    for courier in couriers
                ]
                return CouriersListResponse(
                    couriers=couriers_models, limit=limit, offset=offset
                )

    @staticmethod
    async def get_all_couriers() -> list[CourierModel]:
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(Courier)
                result = await session.execute(stmt)
                couriers = result.scalars().all()
                return [
                    CourierModel(
                        courier_id=courier.id,
                        courier_type=courier.courier_type,
                        regions=courier.regions,
                        working_hours=courier.working_hours,
                    )
                    for courier in couriers
                ]

    async def create_orders(self, *, orders_model: OrdersList) -> list[OrderModel]:
        orders = [Order(**order.dict()) for order in orders_model.orders]
        async with AsyncSession(engine) as session:
            async with session.begin():
                session.add_all(orders)
                await session.flush()
                created_orders = [
                    OrderModel(
                        order_id=order.id,
                        weight=order.weight,
                        regions=order.regions,
                        delivery_hours=order.delivery_hours,
                        cost=order.cost,
                        completed_time=order.completed_time,
                    )
                    for order in orders
                ]
            await session.commit()
        return created_orders

    async def get_order(self, *, order_id: int) -> Optional[OrderModel]:
        async with AsyncSession(engine) as session:
            stmt = select(Order).where(Order.id == order_id)
            result = await session.execute(stmt)
            order = result.scalar_one_or_none()

            if order is None:
                return None

            return OrderModel(
                order_id=order.id,
                weight=order.weight,
                regions=order.regions,
                delivery_hours=order.delivery_hours,
                cost=order.cost,
                completed_time=order.completed_time,
            )

    async def get_orders(self, *, offset: int, limit: int) -> list[OrderModel]:
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(Order).offset(offset).limit(limit)
                result = await session.execute(stmt)
                orders = result.scalars().all()
                return [
                    OrderModel(
                        order_id=order.id,
                        weight=order.weight,
                        regions=order.regions,
                        delivery_hours=order.delivery_hours,
                        cost=order.cost,
                        completed_time=order.completed_time,
                    )
                    for order in orders
                ]

    async def complete_orders(
            self, *, complete_orders_model: CompleteOrderList
    ):
        async with AsyncSession(engine) as session:
            order_ids = [
                info.order_id for info in complete_orders_model.complete_info
            ]
            async with session.begin():
                stmt = select(Order).filter(Order.id.in_(order_ids))
                result = await session.execute(stmt)
                orders = {order.id: order for order in result.scalars().all()}
                for info in complete_orders_model.complete_info:
                    order = orders.get(info.order_id)
                    if order is None:
                        return None
                    if order.courier_id is None:
                        current_courier = await self.get_courier(
                            courier_id=info.courier_id
                        )
                        if current_courier is not None:
                            order.completed_time = info.complete_time.replace(
                                tzinfo=None
                            )
                            order.courier_id = info.courier_id
                    elif (
                            order.courier_id != info.courier_id
                            or order.completed_time
                            != info.complete_time.replace(tzinfo=None)
                    ):
                        return None
                await session.commit()

            async with session.begin():
                stmt = select(Order).filter(Order.id.in_(order_ids))
                result = await session.execute(stmt)
                orders = result.scalars().all()
                return [
                    OrderModel(
                        order_id=order.id,
                        weight=order.weight,
                        regions=order.regions,
                        delivery_hours=order.delivery_hours,
                        cost=order.cost,
                        completed_time=order.completed_time,
                    )
                    for order in orders
                ]

    async def get_cost_sum_and_order_count(
            self, courier_id: int, start_date: datetime, end_date: datetime
    ):
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = (
                    select(func.sum(Order.cost), func.count(Order.id))
                    .where(Order.courier_id == courier_id)
                    .where(Order.completed_time >= start_date)
                    .where(Order.completed_time < end_date)
                )
                result = await session.execute(stmt)
                cost_sum, order_count = result.one_or_none()
                return cost_sum, order_count

    async def get_orders_to_assign(self, date: datetime) -> list[OrderModel]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = (
                    select(Order)
                    .filter(
                        and_(
                            Order.created_at >= start_of_day,
                            Order.created_at <= end_of_day,
                        )
                    )
                    .filter(Order.courier_id == null())
                )
                result = await session.execute(stmt)
                orders = result.scalars().all()
                return [
                    OrderModel(
                        order_id=order.id,
                        weight=order.weight,
                        regions=order.regions,
                        delivery_hours=order.delivery_hours,
                        cost=order.cost,
                        completed_time=order.completed_time,
                    )
                    for order in orders
                ]

    async def save_schedule(self, time_slots: dict, date: datetime):
        schedule_records = []
        for courier, value in time_slots.items():
            for schedule_record in value:
                for group_order_id, order in enumerate(schedule_record[1]):
                    new_schedule_record = OrderDeliverySchedule(
                        courier_id=courier,
                        date=date,
                        order_id=order,
                        group_order_id=group_order_id,
                        group_time=schedule_record[0],
                        group_weight=schedule_record[2],
                        group_cost=schedule_record[3],
                    )
                    schedule_records.append(new_schedule_record)
        async with AsyncSession(engine) as session:
            async with session.begin():
                session.add_all(schedule_records)
                await session.commit()
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = (
                    select(OrderDeliverySchedule, Courier, Order)
                    .select_from(
                        OrderDeliverySchedule.__table__.join(
                            Courier,
                            OrderDeliverySchedule.courier_id == Courier.id,
                        ).join(
                            Order, OrderDeliverySchedule.order_id == Order.id
                        )
                    )
                    .order_by(
                        OrderDeliverySchedule.date,
                        OrderDeliverySchedule.courier_id,
                        OrderDeliverySchedule.group_order_id,
                    )
                )
                result_proxy = await session.execute(stmt)
                result = self.transform_assignment_result(
                    result_proxy=result_proxy
                )

                return result[0] if result else None

    async def get_count_of_schedule(self, date: datetime) -> int:
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = select(func.count(OrderDeliverySchedule.id)).filter(
                    func.date(OrderDeliverySchedule.date) == date.date()
                )

                result_proxy = await session.execute(stmt)
                return result_proxy.scalar()

    async def get_couriers_assignments(self, courier_id: int, date: datetime):
        async with AsyncSession(engine) as session:
            async with session.begin():
                stmt = (
                    select(OrderDeliverySchedule, Courier, Order)
                    .select_from(
                        OrderDeliverySchedule.__table__.join(
                            Courier,
                            OrderDeliverySchedule.courier_id == Courier.id,
                        ).join(
                            Order, OrderDeliverySchedule.order_id == Order.id
                        )
                    )
                    .filter(
                        and_(
                            func.date(OrderDeliverySchedule.date) == date,
                            Courier.id == courier_id
                            if courier_id > -1
                            else True,
                        )
                    )
                    .order_by(
                        OrderDeliverySchedule.date,
                        OrderDeliverySchedule.courier_id,
                        OrderDeliverySchedule.group_order_id,
                    )
                )
                result_proxy = await session.execute(stmt)
                result = self.transform_assignment_result(
                    result_proxy=result_proxy
                )
                return result[0] if result else None

    @staticmethod
    def transform_assignment_result(result_proxy):
        schedules = result_proxy.fetchall()
        result_proxy.close()
        result = []
        for date, courier_schedule in itertools.groupby(
                schedules,
                key=lambda x: x.OrderDeliverySchedule.date.date(),
        ):
            couriers = []
            for courier_id, group_orders in itertools.groupby(
                    courier_schedule,
                    key=lambda x: x.OrderDeliverySchedule.courier_id,
            ):
                groups = []
                for group_id, orders in itertools.groupby(
                        group_orders,
                        key=lambda x: x.OrderDeliverySchedule.group_order_id,
                ):
                    order_models = [
                        OrderModel(
                            order_id=order.Order.id,
                            weight=order.Order.weight,
                            regions=order.Order.regions,
                            delivery_hours=order.Order.delivery_hours,
                            cost=order.Order.cost,
                            completed_time=order.Order.completed_time,
                        )
                        for order in orders
                    ]
                    groups.append(
                        GroupOrderModel(
                            group_order_id=group_id,
                            orders=order_models,
                        )
                    )
                couriers.append(
                    CourierScheduleModel(courier_id=courier_id, orders=groups)
                )
            result.append(
                DeliveryScheduleModel(date=date.isoformat(), couriers=couriers)
            )
            return result
