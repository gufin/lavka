from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.entities import Courier, engine, Order
from models import (
    CompleteOrderList,
    CourierModel,
    CouriersList,
    CouriersListResponse,
    OrderModel,
    OrdersList,
)
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class LavkaPostgresRepository(LavkaAbstractRepository):
    def __init__(self, *, config: dict):
        self.config = config

    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        created_couriers = []
        async with AsyncSession(engine) as session:
            for courier in couriers_model.couriers:
                new_courier = Courier(**courier.dict())
                async with session.begin():
                    session.add(new_courier)
                    await session.flush()
                    created_couriers.append(
                        CourierModel(
                            courier_id=new_courier.id,
                            courier_type=new_courier.courier_type,
                            regions=new_courier.regions,
                            working_hours=new_courier.working_hours,
                        )
                    )
            await session.commit()
        return CouriersList(couriers=created_couriers)

    async def get_courier(self, *, courier_id: int) -> CourierModel:
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

    async def get_couriers(self, offset: int, limit: int) -> CouriersListResponse:
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

    async def create_orders(self, *, orders_model: OrdersList) -> list[OrderModel]:
        created_orders = []
        async with AsyncSession(engine) as session:
            for order in orders_model.orders:
                new_order = Order(**order.dict())
                async with session.begin():
                    session.add(new_order)
                    await session.flush()
                    created_orders.append(
                        OrderModel(
                            order_id=new_order.id,
                            weight=new_order.weight,
                            regions=new_order.regions,
                            delivery_hours=new_order.delivery_hours,
                            cost=new_order.cost,
                            completed_time=new_order.completed_time,
                        )
                    )
            await session.commit()
        return created_orders

    async def get_order(self, *, order_id: int) -> OrderModel:
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

    async def complete_orders(self, *, complete_orders_model: CompleteOrderList):
        async with AsyncSession(engine) as session:
            order_ids = [info.order_id for info in complete_orders_model.complete_info]
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
