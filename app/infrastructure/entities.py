from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    func,
    Integer,
    String,
    Enum,
    ARRAY,
    DateTime,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from core.settings import settings

engine = create_async_engine(settings.storage_url, echo=True)
Base = declarative_base()
metadata = Base.metadata


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True)
    courier_type = Column(
        Enum("FOOT", "BIKE", "AUTO", name="courier_types"), nullable=False
    )
    regions = Column(ARRAY(Integer), nullable=False)
    working_hours = Column(ARRAY(String), nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=True)
    weight = Column(Float, nullable=False)
    regions = Column(Integer, nullable=False)
    delivery_hours = Column(ARRAY(String), nullable=False)
    cost = Column(Float, nullable=False)
    completed_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())


class OrderDeliverySchedule(Base):
    __tablename__ = "orders_delivery_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    group_order_id = Column(Integer, nullable=False)
    group_time = Column(DateTime, nullable=True)
    group_weight = Column(Float, nullable=False)
    group_cost = Column(Float, nullable=False)
