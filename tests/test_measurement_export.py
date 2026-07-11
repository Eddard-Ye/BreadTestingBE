from datetime import datetime
from io import BytesIO

from openpyxl import load_workbook

from app.schemas.measurement import MeasurementResponse
from app.services.measurement_export import (
    build_measurements_xlsx,
    format_recorded_at,
    sanitize_export_filename,
)


def test_sanitize_export_filename_replaces_illegal_chars() -> None:
    assert sanitize_export_filename('数据汇总:2026/7/11') == "数据汇总_2026_7_11.xlsx"


def test_sanitize_export_filename_converts_csv_suffix() -> None:
    assert sanitize_export_filename("数据汇总.csv") == "数据汇总.xlsx"


def test_build_measurements_xlsx_includes_headers_and_rows() -> None:
    records = [
        MeasurementResponse(
            id="1",
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-1",
            temperature="24.5",
            weight="128.3",
            length="101.2",
            width="49.5",
            height="29.8",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 32, 56),
        )
    ]
    content = build_measurements_xlsx(records)
    workbook = load_workbook(BytesIO(content))
    worksheet = workbook.active

    assert worksheet.title == "录入数据"
    assert [cell.value for cell in worksheet[1]] == [
        "名称",
        "温度(°C)",
        "重量(g)",
        "长(mm)",
        "宽(mm)",
        "高(mm)",
        "水切宽度(mm)",
        "时间",
    ]
    assert [cell.value for cell in worksheet[2]] == [
        "样品-1",
        "24.5",
        "128.3",
        "101.2",
        "49.5",
        "29.8",
        "0",
        "2026/06/22 16:32:56",
    ]


def test_format_recorded_at() -> None:
    assert format_recorded_at(datetime(2026, 6, 22, 16, 32, 56)) == "2026/06/22 16:32:56"
