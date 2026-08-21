"""Unit tests for measurement metric visibility rules."""

from app.services.measurement_metrics import (
    is_metric_visible,
    is_record_complete,
    mask_metric_value,
    visible_metrics,
)


def test_round_product_metrics() -> None:
    assert visible_metrics(
        "product", enable_round_bread=True, enable_water_cut=False
    ) == frozenset({"temperature", "weight", "height"})
    assert visible_metrics(
        "product", enable_round_bread=True, enable_water_cut=True
    ) == frozenset({"temperature", "weight", "height", "water_cut_width"})


def test_round_bottom_middle_metrics() -> None:
    expected = frozenset({"length", "height"})
    assert (
        visible_metrics("bottom", enable_round_bread=True, enable_water_cut=True)
        == expected
    )
    assert (
        visible_metrics("middle", enable_round_bread=True, enable_water_cut=True)
        == expected
    )


def test_non_round_product_and_bottom() -> None:
    assert visible_metrics(
        "product", enable_round_bread=False, enable_water_cut=True
    ) == frozenset({"temperature", "weight", "height", "water_cut_width"})
    assert visible_metrics(
        "bottom", enable_round_bread=False, enable_water_cut=True
    ) == frozenset({"length", "width", "height"})


def test_non_round_middle_unrestricted() -> None:
    assert visible_metrics(
        "middle", enable_round_bread=False, enable_water_cut=False
    ) == frozenset({"temperature", "weight", "length", "width", "height"})


def test_mask_and_complete() -> None:
    assert (
        mask_metric_value(
            "product",
            "length",
            "100",
            enable_round_bread=True,
            enable_water_cut=False,
        )
        == "-"
    )
    assert is_record_complete(
        {"temperature": "25", "weight": "100", "height": "30", "length": "90"},
        "product",
        enable_round_bread=True,
        enable_water_cut=False,
    )
    assert not is_record_complete(
        {"temperature": "25", "weight": "-", "height": "30"},
        "product",
        enable_round_bread=False,
        enable_water_cut=False,
    )
    assert is_metric_visible(
        "bottom", "width", enable_round_bread=False, enable_water_cut=False
    )
    assert not is_metric_visible(
        "bottom", "width", enable_round_bread=True, enable_water_cut=False
    )
