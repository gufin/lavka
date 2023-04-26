from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.entities import Courier, engine
from models import CourierModel, CouriersList, CouriersListResponse
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

    async def get_courier(self, *, courier_id: str) -> CourierModel:
        async with AsyncSession(engine) as session:
            stmt = select(Courier).where(Courier.id == int(courier_id))
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
