from abc import ABC, abstractmethod

from models import CourierModel, CouriersList, CouriersListResponse


class LavkaAbstractRepository(ABC):
    @abstractmethod
    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        pass

    @abstractmethod
    async def get_courier(self, *, courier_id: str) -> CourierModel:
        pass

    @abstractmethod
    async def get_couriers(self, offset: int, limit: int) -> CouriersListResponse:
        pass
