from __future__ import annotations

import csv
import io
import re
from datetime import datetime

from app.schemas.measurement import MeasurementResponse

_CSV_HEADERS = [
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
    if not cleaned.lower().endswith(".csv"):
        cleaned = f"{cleaned}.csv"
    return cleaned


def format_recorded_at(dt: datetime) -> str:
    """近似前端 toLocaleString('zh-CN') 的展示格式。"""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def build_measurements_csv(records: list[MeasurementResponse]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(_CSV_HEADERS)
    for record in records:
        writer.writerow(
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
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")
