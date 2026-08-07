from datetime import datetime
from io import BytesIO

from openpyxl import load_workbook

from app.schemas.measurement import MeasurementResponse
from app.services.measurement_export import (
    build_measurements_xlsx,
    format_recorded_at,
    sanitize_export_filename,
    sanitize_sheet_title,
)


def _row_values(sheet, row: int, last_col: int) -> list:
    return [sheet.cell(row=row, column=col).value for col in range(1, last_col + 1)]


def test_sanitize_export_filename_replaces_illegal_chars() -> None:
    assert sanitize_export_filename('数据汇总:2026/7/11') == "数据汇总_2026_7_11.xlsx"


def test_sanitize_export_filename_converts_csv_suffix() -> None:
    assert sanitize_export_filename("数据汇总.csv") == "数据汇总.xlsx"


def test_sanitize_sheet_title() -> None:
    assert sanitize_sheet_title("成品-温度") == "成品-温度"
    assert len(sanitize_sheet_title("x" * 40)) == 31


def test_build_measurements_xlsx_creates_metric_sheets_per_type() -> None:
    records = [
        MeasurementResponse(
            id="1",
            batch_id=1,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-1",
            temperature="24.5",
            weight="128.3",
            length="101.2",
            width="49.5",
            height="29.8",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 32, 56),
        ),
        MeasurementResponse(
            id="2",
            batch_id=1,
            recipe_id="standardC",
            record_type="bottom",
            slot_index=0,
            sample_name="样品-底片-1",
            temperature="22.1",
            weight="88.3",
            length="91.2",
            width="45.5",
            height="28.8",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 33, 10),
        ),
    ]
    content = build_measurements_xlsx(records, enable_water_cut=False)
    workbook = load_workbook(BytesIO(content))

    assert workbook.sheetnames[0] == "底稿"
    draft = workbook["底稿"]
    assert _row_values(draft, 1, 8) == [
        "批次号",
        "名称",
        "温度(°C)",
        "重量(g)",
        "长(mm)",
        "宽(mm)",
        "高(mm)",
        "时间",
    ]
    assert draft.max_row == 3
    assert _row_values(draft, 2, 8) == [
        1,
        "样品-底片-1",
        "22.1",
        "88.3",
        "91.2",
        "45.5",
        "28.8",
        "2026/06/22 16:33:10",
    ]
    assert _row_values(draft, 3, 8) == [
        1,
        "样品-成品-1",
        "24.5",
        "128.3",
        "101.2",
        "49.5",
        "29.8",
        "2026/06/22 16:32:56",
    ]

    assert "成品-温度" in workbook.sheetnames
    assert "成品-重量" in workbook.sheetnames
    assert "底片-温度" in workbook.sheetnames
    assert "底片-重量" in workbook.sheetnames
    assert "成品-水切宽度" not in workbook.sheetnames

    product_temperature = workbook["成品-温度"]
    assert _row_values(product_temperature, 1, 4) == [
        "批次号",
        "开始时间",
        "温度1",
        "单批温度",
    ]
    assert _row_values(product_temperature, 2, 4) == [
        1,
        "2026/06/22 16:32:56",
        "24.5",
        24.5,
    ]


def test_build_measurements_xlsx_groups_batch_into_one_row_with_sum() -> None:
    records = [
        MeasurementResponse(
            id="1",
            batch_id=1,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-1",
            temperature="24.5",
            weight="100",
            length="0",
            width="0",
            height="0",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 32, 56),
        ),
        MeasurementResponse(
            id="2",
            batch_id=1,
            recipe_id="standardC",
            record_type="product",
            slot_index=1,
            sample_name="样品-成品-2",
            temperature="25.5",
            weight="110",
            length="0",
            width="0",
            height="0",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 33, 10),
        ),
        MeasurementResponse(
            id="3",
            batch_id=2,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-3",
            temperature="20",
            weight="90",
            length="0",
            width="0",
            height="0",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 17, 0, 0),
        ),
    ]
    workbook = load_workbook(BytesIO(build_measurements_xlsx(records, enable_water_cut=False)))
    temperature_sheet = workbook["成品-温度"]
    weight_sheet = workbook["成品-重量"]

    assert _row_values(temperature_sheet, 1, 5) == [
        "批次号",
        "开始时间",
        "温度1",
        "温度2",
        "单批温度",
    ]
    assert _row_values(temperature_sheet, 2, 5) == [
        1,
        "2026/06/22 16:32:56",
        "24.5",
        "25.5",
        50,
    ]
    assert _row_values(temperature_sheet, 3, 5) == [
        2,
        "2026/06/22 17:00:00",
        "20",
        None,
        20,
    ]

    assert _row_values(weight_sheet, 1, 5) == [
        "批次号",
        "开始时间",
        "重量1",
        "重量2",
        "单批重量",
    ]
    assert _row_values(weight_sheet, 2, 5) == [
        1,
        "2026/06/22 16:32:56",
        "100",
        "110",
        210,
    ]


def test_build_measurements_xlsx_includes_water_cut_for_product_when_enabled() -> None:
    records = [
        MeasurementResponse(
            id="1",
            batch_id=1,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-1",
            temperature="24.5",
            weight="128.3",
            length="101.2",
            width="49.5",
            height="29.8",
            water_cut_width="42.5",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 32, 56),
        )
    ]
    workbook = load_workbook(
        BytesIO(build_measurements_xlsx(records, enable_water_cut=True))
    )
    assert "成品-水切宽度" in workbook.sheetnames
    assert workbook.sheetnames[0] == "底稿"
    draft = workbook["底稿"]
    assert _row_values(draft, 1, 9) == [
        "批次号",
        "名称",
        "温度(°C)",
        "重量(g)",
        "长(mm)",
        "宽(mm)",
        "高(mm)",
        "水切宽度(mm)",
        "时间",
    ]
    assert _row_values(draft, 2, 9) == [
        1,
        "样品-成品-1",
        "24.5",
        "128.3",
        "101.2",
        "49.5",
        "29.8",
        "42.5",
        "2026/06/22 16:32:56",
    ]
    assert _row_values(workbook["成品-水切宽度"], 1, 4) == [
        "批次号",
        "开始时间",
        "水切宽度1",
        "单批水切宽度",
    ]
    assert _row_values(workbook["成品-水切宽度"], 2, 4) == [
        1,
        "2026/06/22 16:32:56",
        "42.5",
        42.5,
    ]


def test_format_recorded_at() -> None:
    assert format_recorded_at(datetime(2026, 6, 22, 16, 32, 56)) == "2026/06/22 16:32:56"


def test_build_measurements_xlsx_appends_stats_table_with_formulas() -> None:
    records = [
        MeasurementResponse(
            id="1",
            batch_id=1,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-1",
            temperature="24.5",
            weight="100",
            length="0",
            width="0",
            height="0",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 16, 32, 56),
        ),
        MeasurementResponse(
            id="2",
            batch_id=2,
            recipe_id="standardC",
            record_type="product",
            slot_index=0,
            sample_name="样品-成品-2",
            temperature="26.5",
            weight="110",
            length="0",
            width="0",
            height="0",
            water_cut_width="0",
            preview_name=None,
            recorded_at=datetime(2026, 6, 22, 17, 0, 0),
        ),
    ]
    workbook = load_workbook(BytesIO(build_measurements_xlsx(records, enable_water_cut=False)))
    sheet = workbook["成品-重量"]

    stats_start = 5  # header + 2 data rows + blank row
    stats_label_col = 6  # batch_total_col(4) + 2
    stats_input_col = 7
    stats_value_col = 8
    assert sheet.cell(row=stats_start, column=stats_label_col).value == "公差上限 USL"
    assert sheet.cell(row=stats_start, column=stats_input_col).value is None
    assert sheet.cell(row=stats_start, column=stats_value_col).value == "=G5"
    assert sheet.cell(row=stats_start + 2, column=stats_input_col).value == "(USL + LSL) / 2"
    assert sheet.cell(row=stats_start + 2, column=stats_value_col).value == "=(G5+G6)/2"
    assert sheet.cell(row=stats_start + 4, column=stats_value_col).value == "=AVERAGE(D2:D3)"
    assert sheet.cell(row=stats_start + 5, column=stats_value_col).value == "=STDEV(D2:D3)"
    assert sheet.cell(row=stats_start + 8, column=stats_value_col).value == "=(G5-H9)/(3*H10)"
    assert sheet.cell(row=stats_start + 10, column=stats_label_col).value == "CPK"
    assert sheet.cell(row=stats_start + 10, column=stats_value_col).value == "=MIN(H13,H14)"
    assert sheet.cell(row=stats_start + 14, column=stats_value_col).value == "=H17*(1-ABS(H18))"
