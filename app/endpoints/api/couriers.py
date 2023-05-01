from datetime import datetime

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.containers import Container
from infrastructure.rate_limiter import rate_limiter
from models import CouriersList
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.post("/couriers", dependencies=[Depends(rate_limiter)])
@inject
async def create_couriers(
    request: Request,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    body = await request.json()
    try:
        couriers_model = CouriersList.parse_obj(body)
        return await courier_service.create_couriers(
            couriers_model=couriers_model
        )
    except ValidationError:
        return JSONResponse(content={}, status_code=400)


@router.get("/couriers/{courier_id}", dependencies=[Depends(rate_limiter)])
@inject
async def get_courier(
    courier_id,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    try:
        correct_courier_id = int(courier_id)
        result = await courier_service.get_courier(
            courier_id=correct_courier_id
        )
        return (
            JSONResponse(content={}, status_code=404)
            if result is None
            else result
        )
    except ValueError:
        return JSONResponse(content={}, status_code=400)


@router.get("/couriers", dependencies=[Depends(rate_limiter)])
@inject
async def get_couriers(
    offset=0,
    limit=1,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    try:
        correct_offset = int(offset)
        correct_limit = int(limit)
        if correct_offset >= 0 and correct_limit > 0:
            return await courier_service.get_couriers(
                offset=correct_offset, limit=correct_limit
            )
        return JSONResponse(content={}, status_code=400)
    except ValueError:
        return JSONResponse(content={}, status_code=400)


@router.get(
    "/couriers/meta-info/{courier_id}", dependencies=[Depends(rate_limiter)]
)
@inject
async def get_courier_meta_info(
    courier_id,
    start_date,
    end_date,
    courier_service: CourierService = Depends(
        Provide[Container.courier_service]
    ),
):
    try:
        correct_courier_id = int(courier_id)
        correct_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        correct_end_date = datetime.strptime(end_date, "%Y-%m-%d")
        result = await courier_service.get_courier_meta_info(
            courier_id=correct_courier_id,
            start_date=correct_start_date,
            end_date=correct_end_date,
        )
        return (
            JSONResponse(content={}, status_code=404)
            if result is None
            else result
        )
    except ValueError:
        return JSONResponse(content={}, status_code=400)
