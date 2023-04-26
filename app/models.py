from enum import Enum

from pydantic import BaseModel, Field


class CourierType(str, Enum):
    FOOT = "FOOT"
    BIKE = "BIKE"
    AUTO = "AUTO"


class CourierModel(BaseModel):
    id: int = Field(default=None, alias="courier_id")
    courier_type: CourierType
    regions: list[int]
    working_hours: list[str]


class CouriersList(BaseModel):
    couriers: list[CourierModel]


class CouriersListResponse(BaseModel):
    couriers: list[CourierModel]
    limit: int
    offset: int
