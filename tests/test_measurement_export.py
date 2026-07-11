from datetime import datetime

from app.schemas.measurement import MeasurementResponse
from app.services.measurement_export import (
    build_measurements_csv,
    format_recorded_at,
    sanitize_export_filename,
)


def test_sanitize_export_filename_replaces_illegal_chars() -> None:
    assert sanitize_export_filename('数据汇总:2026/7/11') == "数据汇总_2026_7_11.csv"


def test_build_measurements_csv_includes_bom_and_headers() -> None:
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
    content = build_measurements_csv(records)
    assert content.startswith("\ufeff".encode("utf-8"))
    text = content.decode("utf-8-sig")
    assert "名称,温度(°C)" in text.splitlines()[0]
    assert "样品-1,24.5,128.3" in text.splitlines()[1]


def test_format_recorded_at() -> None:
    assert format_recorded_at(datetime(2026, 6, 22, 16, 32, 56)) == "2026/06/22 16:32:56"
