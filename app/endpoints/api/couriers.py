from datetime import datetime
from http import HTTPStatus

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.containers import Container
from infrastructure.rate_limiter import rate_limiter
from models import CouriersList
from services.use_cases.courier_service import CourierService

router = APIRouter()


@router.get("/couriers/assignments", dependencies=[Depends(rate_limiter)])
@inject
async def get_couriers_assignments(
        courier_id=-1,
        date=None,
        courier_service: CourierService = Depends(
            Provide[Container.courier_service]
        ),
):
    if date is None:
        date = datetime.combine(datetime.now(), datetime.min.time())
    try:
        correct_courier_id = int(courier_id)
        if isinstance(date, datetime):
            correct_date = date
        else:
            correct_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST
        )

    result = await courier_service.get_couriers_assignments(
        courier_id=correct_courier_id, date=correct_date
    )
    return (
        JSONResponse(
            content={"detail": "Assignments not found."},
            status_code=HTTPStatus.NOT_FOUND
        )
        if result is None
        else result
    )


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
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST
        )


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
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST
        )
    result = await courier_service.get_courier(courier_id=correct_courier_id)
    return (
        JSONResponse(content={"detail": "Courier not found."},
                     status_code=HTTPStatus.NOT_FOUND)
        if result is None
        else result
    )


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
        if correct_offset < 0 or correct_limit < 0:
            return JSONResponse(
                content={"detail": "Invalid data provided."},
                status_code=HTTPStatus.BAD_REQUEST
            )
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST
        )
    return await courier_service.get_couriers(
        offset=correct_offset, limit=correct_limit
    )


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
    except ValueError:
        return JSONResponse(
            content={"detail": "Invalid data provided."},
            status_code=HTTPStatus.BAD_REQUEST
        )

    result = await courier_service.get_courier_meta_info(
        courier_id=correct_courier_id,
        start_date=correct_start_date,
        end_date=correct_end_date,
    )
    return (
        JSONResponse(content={"detail": "Courier not found."},
                     status_code=HTTPStatus.NOT_FOUND)
        if result is None
        else result
    )
