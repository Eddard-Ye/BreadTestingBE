from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MeasurementRecord(Base):
    __tablename__ = "measurement_records"
    __table_args__ = (
        Index("ix_measurement_recipe_type_time", "recipe_id", "record_type", "recorded_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recipe_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    record_type: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    slot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_name: Mapped[str] = mapped_column(String(255), nullable=False)
    temperature: Mapped[str] = mapped_column(String(32), nullable=False)
    weight: Mapped[str] = mapped_column(String(32), nullable=False)
    length: Mapped[str] = mapped_column(String(32), nullable=False)
    width: Mapped[str] = mapped_column(String(32), nullable=False)
    height: Mapped[str] = mapped_column(String(32), nullable=False)
    water_cut_width: Mapped[str] = mapped_column(String(32), nullable=False)
    preview_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
