from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core.containers import Container
from models import CouriersList

from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/couriers")
@inject
async def progress(
    couriers_model: CouriersList,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> CouriersList:
    return await courier_service.create_couriers(couriers_model=couriers_model)
