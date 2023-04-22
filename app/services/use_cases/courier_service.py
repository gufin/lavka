from models import CouriersList
from services.use_cases.abstract_repositories import LavkaAbstractRepository


class CourierService:
    def __init__(self, repository: LavkaAbstractRepository):
        self.repository = repository

    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        return await self.repository.create_couriers(couriers_model=couriers_model)
