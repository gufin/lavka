from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.entities import Courier, engine
from models import CourierModel, CouriersList
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
