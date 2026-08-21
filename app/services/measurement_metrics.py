"""Shared rules for which measurement metrics are recorded/shown."""

from __future__ import annotations

from typing import Iterable

from app.schemas.measurement import RecordType

# Canonical metric field names (API / DB / export).
ALL_METRICS: tuple[str, ...] = (
    "temperature",
    "weight",
    "length",
    "width",
    "height",
    "water_cut_width",
)

# Frontend camelCase aliases.
_FRONTEND_ALIASES: dict[str, str] = {
    "waterCutWidth": "water_cut_width",
    "water_cut_width": "water_cut_width",
}


def normalize_metric_field(field: str) -> str:
    return _FRONTEND_ALIASES.get(field, field)


def visible_metrics(
    record_type: RecordType,
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> frozenset[str]:
    """Return metric fields that should be recorded/shown for a slot."""
    if enable_round_bread:
        if record_type == "product":
            fields = {"temperature", "weight", "height"}
            if enable_water_cut:
                fields.add("water_cut_width")
            return frozenset(fields)
        # bottom / middle: diameter (length) + height
        return frozenset({"length", "height"})

    if record_type == "product":
        fields = {"temperature", "weight", "height"}
        if enable_water_cut:
            fields.add("water_cut_width")
        return frozenset(fields)
    if record_type == "bottom":
        return frozenset({"length", "width", "height"})
    # middle: no restrictions (water cut remains product-only)
    return frozenset(
        {
            "temperature",
            "weight",
            "length",
            "width",
            "height",
        }
    )


def is_metric_visible(
    record_type: RecordType,
    field: str,
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> bool:
    field = normalize_metric_field(field)
    return field in visible_metrics(
        record_type,
        enable_round_bread=enable_round_bread,
        enable_water_cut=enable_water_cut,
    )


def mask_metric_value(
    record_type: RecordType,
    field: str,
    value: str | None,
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> str:
    if not is_metric_visible(
        record_type,
        field,
        enable_round_bread=enable_round_bread,
        enable_water_cut=enable_water_cut,
    ):
        return "-"
    if value is None or str(value).strip() == "":
        return "-"
    return str(value)


def required_metrics_for_completion(
    record_type: RecordType,
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> frozenset[str]:
    """Fields that must be non-empty (and not '-') for a slot to count as complete."""
    return visible_metrics(
        record_type,
        enable_round_bread=enable_round_bread,
        enable_water_cut=enable_water_cut,
    )


def is_record_complete(
    values: dict[str, str | None],
    record_type: RecordType,
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> bool:
    for field in required_metrics_for_completion(
        record_type,
        enable_round_bread=enable_round_bread,
        enable_water_cut=enable_water_cut,
    ):
        raw = values.get(field)
        if raw is None:
            # also accept camelCase from frontend-shaped dicts
            if field == "water_cut_width":
                raw = values.get("waterCutWidth")
        text = "" if raw is None else str(raw).strip()
        if not text or text == "-":
            return False
    return True


def iter_visible_metric_fields(
    record_type: RecordType,
    fields: Iterable[tuple[str, str, str]],
    *,
    enable_round_bread: bool,
    enable_water_cut: bool,
) -> list[tuple[str, str, str]]:
    visible = visible_metrics(
        record_type,
        enable_round_bread=enable_round_bread,
        enable_water_cut=enable_water_cut,
    )
    result: list[tuple[str, str, str]] = []
    for field, short_label, header in fields:
        if field not in visible:
            continue
        if enable_round_bread and field == "length":
            result.append((field, "直径", "直径(mm)"))
        else:
            result.append((field, short_label, header))
    return result
