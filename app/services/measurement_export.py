from __future__ import annotations

import io
import re
from datetime import datetime

from openpyxl import Workbook

from app.schemas.measurement import MeasurementResponse

_EXPORT_HEADERS = [
    "名称",
    "温度(°C)",
    "重量(g)",
    "长(mm)",
    "宽(mm)",
    "高(mm)",
    "水切宽度(mm)",
    "时间",
]

_WINDOWS_ILLEGAL_FILENAME = re.compile(r'[<>:"/\\|?*]')


def sanitize_export_filename(filename: str) -> str:
    cleaned = _WINDOWS_ILLEGAL_FILENAME.sub("_", filename.strip())
    if cleaned.lower().endswith(".csv"):
        cleaned = cleaned[:-4]
    if not cleaned.lower().endswith(".xlsx"):
        cleaned = f"{cleaned}.xlsx"
    return cleaned


def format_recorded_at(dt: datetime) -> str:
    """近似前端 toLocaleString('zh-CN') 的展示格式。"""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def build_measurements_xlsx(records: list[MeasurementResponse]) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "录入数据"
    worksheet.append(_EXPORT_HEADERS)
    for record in records:
        worksheet.append(
            [
                record.sample_name,
                record.temperature,
                record.weight,
                record.length,
                record.width,
                record.height,
                record.water_cut_width,
                format_recorded_at(record.recorded_at),
            ]
        )
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
