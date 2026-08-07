from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MeasurementBatch(Base):
    __tablename__ = "measurement_batches"
    __table_args__ = (
        Index(
            "uq_measurement_batch_recipe_type_seq",
            "recipe_id",
            "record_type",
            "batch_seq",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    recipe_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    record_type: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
