from enum import Enum
from typing import Optional
from datetime import datetime

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


class OrderModel(BaseModel):
    id: int = Field(default=None, alias="order_id")
    weight: float
    regions: int
    delivery_hours: list[str]
    cost: float
    completed_time: Optional[datetime] = None


class OrdersList(BaseModel):
    orders: list[OrderModel]
