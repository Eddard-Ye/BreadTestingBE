from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import MeasurementRecord
from app.models.measurement_batch import MeasurementBatch
from app.models.recipe import Recipe
from app.services.measurement_batch_backfill import (
    backfill_measurement_batch_ids,
    expected_batch_size,
    rebuild_measurement_batch_ids,
)


def _recipe_config(batch_size: int = 6) -> dict:
    section = {
        "batchSize": 3,
        "temperature": {"min": 20, "max": 26},
        "weight": {"min": 80, "max": 100},
        "length": {"min": 90, "max": 110},
        "width": {"min": 40, "max": 55},
        "height": {"min": 25, "max": 35},
        "waterCutWidth": {"min": 40, "max": 50},
    }
    return {
        "name": "测试配方",
        "batchSize": batch_size,
        "temperature": {"min": 22, "max": 28},
        "weight": {"min": 120, "max": 140},
        "length": {"min": 98, "max": 108},
        "width": {"min": 48, "max": 52},
        "height": {"min": 28, "max": 32},
        "waterCutWidth": {"min": 42, "max": 48},
        "enableWaterCut": False,
        "enableRoundBread": False,
        "enableBottomMeasurement": True,
        "bottomParams": section,
        "enableMiddleMeasurement": True,
        "middleParams": section,
    }


def _insert_record(
    session: Session,
    *,
    recipe_id: str,
    slot_index: int,
    recorded_at: datetime,
    record_type: str = "product",
) -> MeasurementRecord:
    row = MeasurementRecord(
        id=f"{recipe_id}-{record_type}-{slot_index}-{recorded_at.isoformat()}",
        recipe_id=recipe_id,
        record_type=record_type,
        slot_index=slot_index,
        sample_name=f"测试配方-成品-{slot_index + 1}",
        temperature="24.5",
        weight="128.3",
        length="101.2",
        width="49.5",
        height="29.8",
        water_cut_width="0",
        recorded_at=recorded_at,
    )
    session.add(row)
    return row


@pytest.fixture
def db_session(client):
    from app.db.session import get_session_factory

    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def test_expected_batch_size_uses_recipe_section(db_session: Session) -> None:
    config = _recipe_config(batch_size=6)
    assert expected_batch_size(config, "product") == 6
    assert expected_batch_size(config, "bottom") == 3
    assert expected_batch_size(config, "middle") == 3


def test_backfill_groups_records_by_batch_size_and_time(db_session: Session) -> None:
    recipe_id = "standardC"
    db_session.add(
        Recipe(
            id=recipe_id,
            name="标准配方C",
            config=_recipe_config(batch_size=6),
        )
    )
    db_session.flush()

    base = datetime(2026, 7, 1, 20, 37, 0)
    for index in range(6):
        _insert_record(
            db_session,
            recipe_id=recipe_id,
            slot_index=index,
            recorded_at=base.replace(second=index * 5),
        )
    for index in range(6):
        _insert_record(
            db_session,
            recipe_id=recipe_id,
            slot_index=index,
            recorded_at=datetime(2026, 7, 1, 23, 19, index * 8),
        )
    db_session.commit()

    assigned = backfill_measurement_batch_ids(db_session)
    db_session.commit()

    rows = db_session.scalars(
        select(MeasurementRecord).order_by(MeasurementRecord.recorded_at)
    ).all()
    batches = db_session.scalars(
        select(MeasurementBatch)
        .where(MeasurementBatch.recipe_id == recipe_id)
        .order_by(MeasurementBatch.batch_seq)
    ).all()

    assert assigned == 12
    assert [batch.batch_seq for batch in batches] == [1, 2]
    assert {row.batch_id for row in rows[:6]} == {batches[0].id}
    assert {row.batch_id for row in rows[6:]} == {batches[1].id}


def test_backfill_splits_on_large_time_gap(db_session: Session) -> None:
    recipe_id = "standardC"
    db_session.add(
        Recipe(
            id=recipe_id,
            name="标准配方C",
            config=_recipe_config(batch_size=6),
        )
    )
    db_session.flush()

    _insert_record(
        db_session,
        recipe_id=recipe_id,
        slot_index=0,
        recorded_at=datetime(2026, 7, 1, 10, 0, 0),
    )
    _insert_record(
        db_session,
        recipe_id=recipe_id,
        slot_index=1,
        recorded_at=datetime(2026, 7, 1, 10, 20, 0),
    )
    db_session.commit()

    backfill_measurement_batch_ids(db_session)
    db_session.commit()

    batches = db_session.scalars(
        select(MeasurementBatch)
        .where(MeasurementBatch.recipe_id == recipe_id)
        .order_by(MeasurementBatch.batch_seq)
    ).all()
    assert [batch.batch_seq for batch in batches] == [1, 2]


def test_rebuild_uses_independent_batch_seq_per_recipe(db_session: Session) -> None:
    db_session.add_all(
        [
            Recipe(id="recipeA", name="配方A", config=_recipe_config(batch_size=1)),
            Recipe(id="recipeB", name="配方B", config=_recipe_config(batch_size=1)),
        ]
    )
    db_session.flush()

    _insert_record(
        db_session,
        recipe_id="recipeA",
        slot_index=0,
        recorded_at=datetime(2026, 7, 1, 10, 0, 0),
    )
    _insert_record(
        db_session,
        recipe_id="recipeB",
        slot_index=0,
        recorded_at=datetime(2026, 7, 1, 10, 5, 0),
    )
    _insert_record(
        db_session,
        recipe_id="recipeA",
        slot_index=0,
        recorded_at=datetime(2026, 7, 1, 11, 0, 0),
    )
    db_session.commit()

    rebuild_measurement_batch_ids(db_session)
    db_session.commit()

    batches = db_session.scalars(
        select(MeasurementBatch).order_by(
            MeasurementBatch.recipe_id,
            MeasurementBatch.batch_seq,
        )
    ).all()
    assert [(batch.recipe_id, batch.batch_seq) for batch in batches] == [
        ("recipeA", 1),
        ("recipeA", 2),
        ("recipeB", 1),
    ]
