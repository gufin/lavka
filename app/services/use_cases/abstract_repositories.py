from abc import ABC, abstractmethod

from models import CouriersList


class LavkaAbstractRepository(ABC):
    @abstractmethod
    async def create_couriers(self, *, couriers_model: CouriersList) -> CouriersList:
        pass
