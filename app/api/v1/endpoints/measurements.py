from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_measurement_service_dep
from app.schemas.measurement import (
    MeasurementBatchCreate,
    MeasurementListResponse,
    MeasurementResponse,
)
from app.services.measurement_service import MeasurementService

router = APIRouter()


@router.get("", response_model=MeasurementListResponse)
async def list_measurements(
    service: Annotated[MeasurementService, Depends(get_measurement_service_dep)],
    recipe_id: Annotated[str | None, Query(alias="recipeId")] = None,
    record_type: Annotated[str | None, Query(alias="recordType")] = None,
    start_time: Annotated[datetime | None, Query(alias="startTime")] = None,
    end_time: Annotated[datetime | None, Query(alias="endTime")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=500)] = 10,
) -> MeasurementListResponse:
    """按配方、数据类型和时间范围分页查询录入数据，按录入时间降序。"""
    records, total = service.list_records(
        recipe_id=recipe_id,
        record_type=record_type,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )
    return MeasurementListResponse(
        records=records,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/batch", response_model=list[MeasurementResponse], status_code=201)
async def create_measurement_batch(
    payload: MeasurementBatchCreate,
    service: Annotated[MeasurementService, Depends(get_measurement_service_dep)],
) -> list[MeasurementResponse]:
    """整批录入完成后一次性写入数据库。"""
    return service.create_batch(payload.records)
