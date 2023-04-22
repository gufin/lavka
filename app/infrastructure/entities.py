from sqlalchemy import Column, Integer, String, Enum, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from core.settings import settings

engine = create_async_engine(settings.storage_url, echo=True)
Base = declarative_base()
metadata = Base.metadata


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True)
    courier_type = Column(Enum("FOOT", "BIKE", "AUTO", name="courier_types"),
                          nullable=False)
    regions = Column(ARRAY(Integer), nullable=False)
    working_hours = Column(ARRAY(String), nullable=False)
