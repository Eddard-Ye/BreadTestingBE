from __future__ import annotations

import io
import re
from collections.abc import Callable
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.schemas.measurement import MeasurementResponse, RecordType

DRAFT_SHEET_TITLE = "底稿"

RECORD_TYPE_LABELS: dict[RecordType, str] = {
    "product": "成品",
    "bottom": "底片",
    "middle": "中片",
}

METRIC_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("temperature", "温度", "温度(°C)"),
    ("weight", "重量", "重量(g)"),
    ("length", "长", "长(mm)"),
    ("width", "宽", "宽(mm)"),
    ("height", "高", "高(mm)"),
    ("water_cut_width", "水切宽度", "水切宽度(mm)"),
)

_WINDOWS_ILLEGAL_FILENAME = re.compile(r'[<>:"/\\|?*]')
_SHEET_ILLEGAL_CHARS = re.compile(r"[\\/*?:\[\]]")


def sanitize_export_filename(filename: str) -> str:
    cleaned = _WINDOWS_ILLEGAL_FILENAME.sub("_", filename.strip())
    if cleaned.lower().endswith(".csv"):
        cleaned = cleaned[:-4]
    if not cleaned.lower().endswith(".xlsx"):
        cleaned = f"{cleaned}.xlsx"
    return cleaned


def sanitize_sheet_title(title: str) -> str:
    cleaned = _SHEET_ILLEGAL_CHARS.sub("_", title.strip())
    return cleaned[:31] or "Sheet"


def format_recorded_at(dt: datetime) -> str:
    """近似前端 toLocaleString('zh-CN') 的展示格式。"""
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def _record_sort_key(record: MeasurementResponse) -> tuple[int, int, datetime]:
    return (
        record.batch_id or 0,
        record.slot_index,
        record.recorded_at,
    )


def _metric_value(record: MeasurementResponse, field: str) -> str:
    return getattr(record, field)


def _parse_numeric(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_sum(total: float) -> str | int | float:
    if total.is_integer():
        return int(total)
    return round(total, 4)


def _group_records_by_batch(
    records: list[MeasurementResponse],
) -> list[tuple[int, list[MeasurementResponse]]]:
    batches: dict[int, list[MeasurementResponse]] = {}
    for record in records:
        batch_key = record.batch_id or 0
        batches.setdefault(batch_key, []).append(record)

    grouped: list[tuple[int, list[MeasurementResponse]]] = []
    for batch_id in sorted(batches):
        batch_records = sorted(
            batches[batch_id],
            key=lambda record: (record.slot_index, record.recorded_at),
        )
        grouped.append((batch_id, batch_records))
    return grouped


def _should_include_metric(
    record_type: RecordType,
    field: str,
    *,
    enable_water_cut: bool,
) -> bool:
    if field != "water_cut_width":
        return True
    return enable_water_cut and record_type == "product"


def _batch_start_time(batch_records: list[MeasurementResponse]) -> str:
    earliest = min(record.recorded_at for record in batch_records)
    return format_recorded_at(earliest)


def _cell_ref(row: int, column: int) -> str:
    return f"{get_column_letter(column)}{row}"


def _append_stats_table(
    worksheet: Worksheet,
    *,
    last_data_row: int,
    batch_total_col: int,
) -> None:
    """在数据区右下方追加 SPC 统计表（含 Excel 公式）。"""
    stats_start_row = last_data_row + 2
    stats_start_col = batch_total_col + 2
    label_col = stats_start_col
    input_col = stats_start_col + 1
    value_col = stats_start_col + 2
    red_label = Font(color="FF0000")

    batch_col = get_column_letter(batch_total_col)
    batch_range = f"{batch_col}2:{batch_col}{last_data_row}"

    usl_row = stats_start_row
    lsl_row = stats_start_row + 1
    u_row = stats_start_row + 2
    t_row = stats_start_row + 3
    mean_row = stats_start_row + 4
    stdev_row = stats_start_row + 5
    max_row = stats_start_row + 6
    min_row = stats_start_row + 7
    cpku_row = stats_start_row + 8
    cpkl_row = stats_start_row + 9
    cpk_row = stats_start_row + 10
    cp_row = stats_start_row + 12
    ca_row = stats_start_row + 13
    cpk2_row = stats_start_row + 14

    usl_input_ref = _cell_ref(usl_row, input_col)
    lsl_input_ref = _cell_ref(lsl_row, input_col)
    u_ref = _cell_ref(u_row, value_col)
    t_ref = _cell_ref(t_row, value_col)
    mean_ref = _cell_ref(mean_row, value_col)
    stdev_ref = _cell_ref(stdev_row, value_col)
    cpku_ref = _cell_ref(cpku_row, value_col)
    cpkl_ref = _cell_ref(cpkl_row, value_col)
    cp_ref = _cell_ref(cp_row, value_col)
    ca_ref = _cell_ref(ca_row, value_col)

    rows: list[tuple[str, str | None, str | None, bool]] = [
        ("公差上限 USL", None, f"={usl_input_ref}", False),
        ("公差下限 LSL", None, f"={lsl_input_ref}", False),
        ("规格中心 U", "(USL + LSL) / 2", f"=({usl_input_ref}+{lsl_input_ref})/2", False),
        ("规格公差 T", "USL - LSL", f"={usl_input_ref}-{lsl_input_ref}", False),
        ("X 平均值", "na", f"=AVERAGE({batch_range})", False),
        ("标准差 σ", "STDEV", f"=STDEV({batch_range})", False),
        ("最大值", "MAX", f"=MAX({batch_range})", False),
        ("最小值", "Min", f"=MIN({batch_range})", False),
        ("CPKU", "(USL - X) / 3σ", f"=({usl_input_ref}-{mean_ref})/(3*{stdev_ref})", False),
        ("CPKL", "(X - LSL) / 3σ", f"=({mean_ref}-{lsl_input_ref})/(3*{stdev_ref})", False),
        ("CPK", "Min(CPKU, CPKL)", f"=MIN({cpku_ref},{cpkl_ref})", True),
        ("", None, None, False),
        ("Cp 离散趋势精确度", "(USL - LSL) / 6σ", f"=({usl_input_ref}-{lsl_input_ref})/(6*{stdev_ref})", False),
        ("Ca 集中趋势精确度", "(X - U) / (T / 2)", f"=({mean_ref}-{u_ref})/({t_ref}/2)", False),
        ("Cpk", "Cp * (1 - |Ca|)", f"={cp_ref}*(1-ABS({ca_ref}))", True),
    ]

    current_row = stats_start_row
    for label, hint, formula, is_red in rows:
        label_cell = worksheet.cell(row=current_row, column=label_col, value=label or None)
        if is_red:
            label_cell.font = red_label
        if hint is not None:
            worksheet.cell(row=current_row, column=input_col, value=hint)
        if formula is not None:
            worksheet.cell(row=current_row, column=value_col, value=formula)
        current_row += 1


def _draft_sheet_header(*, enable_water_cut: bool) -> list[str]:
    header = [
        "批次号",
        "名称",
        "温度(°C)",
        "重量(g)",
        "长(mm)",
        "宽(mm)",
        "高(mm)",
    ]
    if enable_water_cut:
        header.append("水切宽度(mm)")
    header.append("时间")
    return header


def _draft_sheet_row(record: MeasurementResponse, *, enable_water_cut: bool) -> list[object]:
    row: list[object] = [
        record.batch_id,
        record.sample_name,
        record.temperature,
        record.weight,
        record.length,
        record.width,
        record.height,
    ]
    if enable_water_cut:
        row.append(
            record.water_cut_width
            if record.record_type == "product"
            else ""
        )
    row.append(format_recorded_at(record.recorded_at))
    return row


def _append_draft_sheet(
    workbook: Workbook,
    records: list[MeasurementResponse],
    *,
    enable_water_cut: bool,
) -> None:
    """追加与数据汇总页表格一致的底稿 Sheet，置于 workbook 首位。"""
    worksheet = workbook.create_sheet(
        title=sanitize_sheet_title(DRAFT_SHEET_TITLE),
        index=0,
    )
    worksheet.append(_draft_sheet_header(enable_water_cut=enable_water_cut))
    for record in sorted(records, key=lambda item: item.recorded_at, reverse=True):
        worksheet.append(_draft_sheet_row(record, enable_water_cut=enable_water_cut))


def _append_metric_sheet(
    workbook: Workbook,
    *,
    sheet_title: str,
    metric_label: str,
    records: list[MeasurementResponse],
    value_getter: Callable[[MeasurementResponse], str],
) -> None:
    grouped = _group_records_by_batch(records)
    max_samples = max((len(batch_records) for _, batch_records in grouped), default=0)

    worksheet: Worksheet = workbook.create_sheet(title=sheet_title)
    header = ["批次号", "开始时间"]
    header.extend(f"{metric_label}{index}" for index in range(1, max_samples + 1))
    header.append(f"单批{metric_label}")
    worksheet.append(header)

    for batch_id, batch_records in grouped:
        values = [value_getter(record) for record in batch_records]
        total = sum(_parse_numeric(value) for value in values)
        row: list[object] = [
            batch_id or None,
            _batch_start_time(batch_records),
            *values,
        ]
        if len(values) < max_samples:
            row.extend([""] * (max_samples - len(values)))
        row.append(_format_sum(total))
        worksheet.append(row)

    last_data_row = worksheet.max_row
    batch_total_col = 2 + max_samples + 1
    _append_stats_table(
        worksheet,
        last_data_row=last_data_row,
        batch_total_col=batch_total_col,
    )


def build_measurements_xlsx(
    records: list[MeasurementResponse],
    *,
    enable_water_cut: bool = False,
) -> bytes:
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    records_by_type: dict[RecordType, list[MeasurementResponse]] = {
        "product": [],
        "bottom": [],
        "middle": [],
    }
    for record in records:
        records_by_type[record.record_type].append(record)

    if records:
        _append_draft_sheet(
            workbook,
            records,
            enable_water_cut=enable_water_cut,
        )

    for record_type in ("product", "bottom", "middle"):
        typed_records = sorted(records_by_type[record_type], key=_record_sort_key)
        if not typed_records:
            continue

        type_label = RECORD_TYPE_LABELS[record_type]
        for field, short_label, _metric_header in METRIC_FIELDS:
            if not _should_include_metric(record_type, field, enable_water_cut=enable_water_cut):
                continue

            sheet_title = sanitize_sheet_title(f"{type_label}-{short_label}")
            _append_metric_sheet(
                workbook,
                sheet_title=sheet_title,
                metric_label=short_label,
                records=typed_records,
                value_getter=lambda record, metric_field=field: _metric_value(record, metric_field),
            )

    if not workbook.sheetnames:
        summary = workbook.create_sheet(title="录入数据")
        summary.append(["提示"])
        summary.append(["当前筛选条件下没有可导出的数据"])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
