from fastapi import APIRouter
from fastapi.responses import Response

from app.schemas.capture import CaptureMeasurementRequest, CaptureMeasurementResponse
from app.services.stream_capture_service import capture_measurement, fetch_capture_preview

router = APIRouter()


@router.post("/measurement", response_model=CaptureMeasurementResponse)
async def capture_measurement_for_entry(
    payload: CaptureMeasurementRequest,
) -> CaptureMeasurementResponse:
    """录入数据时触发视觉采集：读取传感器并转发至 capture_2d_stream /capture。"""
    return capture_measurement(name=payload.name, water_cut=payload.water_cut)


@router.get("/preview/{file_name}")
async def get_capture_preview(file_name: str) -> Response:
    """代理视觉服务 /captures/{fileName}，供确认录入弹窗展示抓拍图。"""
    content, content_type = fetch_capture_preview(file_name)
    return Response(content=content, media_type=content_type)
