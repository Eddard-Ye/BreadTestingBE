from __future__ import annotations

import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.measurement import MeasurementRecord
from app.models.recipe import Recipe
from app.schemas.measurement import MeasurementCreate, MeasurementResponse

LOCAL_TZ = ZoneInfo("Asia/Shanghai")


class MeasurementService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_local_naive(dt: datetime) -> datetime:
        """统一为本地墙钟 naive 时间，便于与数据库中的录入时间比较。"""
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(LOCAL_TZ).replace(tzinfo=None)

    def _apply_filters(
        self,
        query,
        *,
        recipe_id: str | None,
        record_type: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
        has_preview: bool | None = None,
    ):
        if recipe_id is not None:
            query = query.where(MeasurementRecord.recipe_id == recipe_id)
        if record_type is not None:
            query = query.where(MeasurementRecord.record_type == record_type)
        if has_preview:
            query = query.where(MeasurementRecord.preview_name.isnot(None))
            query = query.where(MeasurementRecord.preview_name != "")
        if start_time is not None:
            query = query.where(
                MeasurementRecord.recorded_at >= self._to_local_naive(start_time)
            )
        if end_time is not None:
            query = query.where(
                MeasurementRecord.recorded_at <= self._to_local_naive(end_time)
            )
        return query

    def list_records(
        self,
        *,
        recipe_id: str | None = None,
        record_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
        has_preview: bool | None = None,
    ) -> tuple[list[MeasurementResponse], int]:
        if page < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="页码必须大于 0")
        if page_size < 1 or page_size > 500:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="每页条数必须在 1 到 500 之间")

        filters = {
            "recipe_id": recipe_id,
            "record_type": record_type,
            "start_time": start_time,
            "end_time": end_time,
            "has_preview": has_preview,
        }

        count_query = select(func.count()).select_from(MeasurementRecord)
        count_query = self._apply_filters(count_query, **filters)
        total = self.db.scalar(count_query) or 0

        query = select(MeasurementRecord).order_by(MeasurementRecord.recorded_at.desc())
        query = self._apply_filters(query, **filters)
        query = query.offset((page - 1) * page_size).limit(page_size)

        rows = self.db.scalars(query).all()
        return [self._to_response(row) for row in rows], total

    def list_all_records(
        self,
        *,
        recipe_id: str | None = None,
        record_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        has_preview: bool | None = None,
    ) -> list[MeasurementResponse]:
        """按筛选条件返回全部录入记录（不分页，供 CSV 导出）。"""
        filters = {
            "recipe_id": recipe_id,
            "record_type": record_type,
            "start_time": start_time,
            "end_time": end_time,
            "has_preview": has_preview,
        }

        query = select(MeasurementRecord).order_by(MeasurementRecord.recorded_at.desc())
        query = self._apply_filters(query, **filters)
        rows = self.db.scalars(query).all()
        return [self._to_response(row) for row in rows]

    def create_batch(self, records: list[MeasurementCreate]) -> list[MeasurementResponse]:
        if not records:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="批次数据不能为空")

        recipe_ids = {item.recipe_id for item in records}
        if len(recipe_ids) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="同一批次只能包含一个配方")

        recipe_id = next(iter(recipe_ids))
        recipe = self.db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在")

        saved_rows: list[MeasurementRecord] = []
        for payload in records:
            recorded_at = payload.recorded_at or datetime.now(LOCAL_TZ)
            recorded_at = self._to_local_naive(recorded_at)

            row = MeasurementRecord(
                id=str(uuid.uuid4()),
                recipe_id=payload.recipe_id,
                record_type=payload.record_type,
                slot_index=payload.slot_index,
                sample_name=payload.sample_name,
                temperature=payload.temperature,
                weight=payload.weight,
                length=payload.length,
                width=payload.width,
                height=payload.height,
                water_cut_width=payload.water_cut_width,
                preview_name=payload.preview_name,
                recorded_at=recorded_at,
            )
            self.db.add(row)
            saved_rows.append(row)

        self.db.commit()
        for row in saved_rows:
            self.db.refresh(row)
        return [self._to_response(row) for row in saved_rows]

    @staticmethod
    def _to_response(row: MeasurementRecord) -> MeasurementResponse:
        return MeasurementResponse(
            id=row.id,
            recipe_id=row.recipe_id,
            record_type=row.record_type,
            slot_index=row.slot_index,
            sample_name=row.sample_name,
            temperature=row.temperature,
            weight=row.weight,
            length=row.length,
            width=row.width,
            height=row.height,
            water_cut_width=row.water_cut_width,
            preview_name=row.preview_name,
            recorded_at=row.recorded_at,
        )


def get_measurement_service(db: Session) -> MeasurementService:
    return MeasurementService(db)
