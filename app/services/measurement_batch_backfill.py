from __future__ import annotations

from datetime import timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.models.measurement import MeasurementRecord
from app.models.measurement_batch import MeasurementBatch
from app.models.recipe import Recipe

# 组内相邻记录超过该间隔时，即使未满 batch_size 也视为新批次。
_BATCH_TIME_GAP = timedelta(minutes=10)


def expected_batch_size(recipe_config: dict, record_type: str) -> int:
    if record_type == "bottom":
        size = recipe_config.get("bottomParams", {}).get("batchSize", 0)
    elif record_type == "middle":
        size = recipe_config.get("middleParams", {}).get("batchSize", 0)
    else:
        size = recipe_config.get("batchSize", 0)
    return max(int(size or 0), 1)


def next_batch_seq(session: Session, recipe_id: str, record_type: str) -> int:
    max_seq = session.scalar(
        select(func.max(MeasurementBatch.batch_seq)).where(
            MeasurementBatch.recipe_id == recipe_id,
            MeasurementBatch.record_type == record_type,
        )
    )
    return int(max_seq or 0) + 1


def _split_into_batches(
    records: list[MeasurementRecord],
    batch_size: int,
) -> list[list[MeasurementRecord]]:
    if not records:
        return []

    groups: list[list[MeasurementRecord]] = []
    current: list[MeasurementRecord] = []

    for record in records:
        if current:
            gap = record.recorded_at - current[-1].recorded_at
            if len(current) >= batch_size or gap > _BATCH_TIME_GAP:
                groups.append(current)
                current = []
        current.append(record)

    if current:
        groups.append(current)
    return groups


def _group_records(
    rows: list[MeasurementRecord],
) -> dict[tuple[str, str], list[MeasurementRecord]]:
    grouped: dict[tuple[str, str], list[MeasurementRecord]] = {}
    for row in rows:
        key = (row.recipe_id, row.record_type)
        grouped.setdefault(key, []).append(row)
    return grouped


def _assign_batch(
    session: Session,
    group: list[MeasurementRecord],
    batch_seq: int,
) -> None:
    if not group:
        return

    batch = MeasurementBatch(
        recipe_id=group[0].recipe_id,
        record_type=group[0].record_type,
        batch_seq=batch_seq,
    )
    session.add(batch)
    session.flush()
    for record in group:
        record.batch_id = batch.id


def _assign_records(session: Session, rows: list[MeasurementRecord]) -> int:
    if not rows:
        return 0

    assigned = 0
    for (_recipe_id, record_type), records in _group_records(rows).items():
        recipe = session.get(Recipe, _recipe_id)
        if recipe is None:
            batch_size = 1
        else:
            batch_size = expected_batch_size(recipe.config, record_type)

        batch_seq = 0
        for group in _split_into_batches(records, batch_size):
            batch_seq += 1
            _assign_batch(session, group, batch_seq)
            assigned += len(group)
    return assigned


def backfill_measurement_batch_ids(session: Session) -> int:
    """为缺少 batch_id 的历史记录按配方 batch_size 与时间顺序回填批次号。"""
    rows = session.scalars(
        select(MeasurementRecord)
        .where(MeasurementRecord.batch_id.is_(None))
        .order_by(
            MeasurementRecord.recipe_id,
            MeasurementRecord.record_type,
            MeasurementRecord.recorded_at,
            MeasurementRecord.slot_index,
        )
    ).all()
    return _assign_records(session, rows)


def rebuild_measurement_batch_ids(session: Session) -> int:
    """清空并按配方独立批次号重建全部录入数据的批次关联。"""
    session.execute(update(MeasurementRecord).values(batch_id=None))
    session.execute(delete(MeasurementBatch))
    session.flush()

    rows = session.scalars(
        select(MeasurementRecord).order_by(
            MeasurementRecord.recipe_id,
            MeasurementRecord.record_type,
            MeasurementRecord.recorded_at,
            MeasurementRecord.slot_index,
        )
    ).all()
    return _assign_records(session, rows)
