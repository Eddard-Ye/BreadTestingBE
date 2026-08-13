from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.recipe import DEFAULT_HEIGHT_CALC_MODE, HeightCalcMode


class CaptureMeasurementRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(min_length=1)
    water_cut: bool = False
    height_calc_mode: HeightCalcMode = DEFAULT_HEIGHT_CALC_MODE
    # LxW 针孔换算工作高度（mm）；与物体高度 H 的校准参数相互独立。
    lw_height_mm: float = Field(default=0.0)


class CaptureMeasurementResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    ok: bool = True
    temperature: str
    weight: str
    height: str
    length: str
    width: str
    water_cut_mm: str
    file_name: str
    image_preview_url: str
