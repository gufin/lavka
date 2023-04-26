from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query

from core.containers import Container
from models import CourierModel, CouriersList, CouriersListResponse
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/couriers")
@inject
async def create_couriers(
    couriers_model: CouriersList,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> CouriersList:
    return await courier_service.create_couriers(couriers_model=couriers_model)


@router.get("/couriers/{courier_id}")
@inject
async def get_courier(
    courier_id: int,
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> CourierModel:
    return await courier_service.get_courier(courier_id=courier_id)


@router.get("/couriers")
@inject
async def get_courier(
    offset: int = Query(0, ge=0),
    limit: int = Query(1, ge=1),
    courier_service: CourierService = Depends(Provide[Container.courier_service]),
) -> CouriersListResponse:
    return await courier_service.get_couriers(offset=offset, limit=limit)
