from enum import Enum

from pydantic import BaseModel


class CourierType(str, Enum):
    FOOT = "FOOT"
    BIKE = "BIKE"
    AUTO = "AUTO"


class CourierModel(BaseModel):
    courier_type: CourierType
    regions: list[int]
    working_hours: list[str]


class CouriersList(BaseModel):
    couriers: list[CourierModel]
