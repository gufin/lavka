from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.entities import Courier, engine
from models import CouriersList
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class LavkaPostgresRepository(LavkaAbstractRepository):
    def __init__(self, *, config: dict):
        self.config = config

    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        async with AsyncSession(engine) as session:
            for courier in couriers_model.couriers:
                new_courier = Courier(**courier.dict())
                async with session.begin():
                    session.add(new_courier)
            await session.commit()
        return couriers_model
