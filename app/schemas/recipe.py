from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

HeightCalcMode = Literal["peak", "average", "percentile"]
DEFAULT_HEIGHT_CALC_MODE: HeightCalcMode = "peak"
DEFAULT_HEIGHT_PERCENTILE: float = 50.0


class RangeSpec(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    min: float
    max: float

    @model_validator(mode="after")
    def validate_range(self) -> "RangeSpec":
        if self.min > self.max:
            raise ValueError("min must be less than or equal to max")
        return self


class SectionParams(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    batch_size: int = Field(ge=0)
    temperature: RangeSpec
    weight: RangeSpec
    length: RangeSpec
    width: RangeSpec
    height: RangeSpec
    water_cut_width: RangeSpec
    height_calc_mode: HeightCalcMode = DEFAULT_HEIGHT_CALC_MODE
    # 物理高度百分位（0=最低，50=中位，100=最高）；仅 percentile 模式参与计算。
    height_percentile: float = Field(
        default=DEFAULT_HEIGHT_PERCENTILE, ge=0, le=100
    )
    # LxW 测量工作高度（mm），capture 时转发给视频后端；不影响物体高度 H。
    lw_height_mm: float = Field(default=0.0)


class RecipeBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(min_length=1)
    batch_size: int = Field(ge=0)
    temperature: RangeSpec
    weight: RangeSpec
    length: RangeSpec
    width: RangeSpec
    height: RangeSpec
    water_cut_width: RangeSpec
    enable_water_cut: bool = False
    enable_round_bread: bool = False
    height_calc_mode: HeightCalcMode = DEFAULT_HEIGHT_CALC_MODE
    # 物理高度百分位（0=最低，50=中位，100=最高）；仅 percentile 模式参与计算。
    height_percentile: float = Field(
        default=DEFAULT_HEIGHT_PERCENTILE, ge=0, le=100
    )
    # LxW 测量工作高度（mm），capture 时转发给视频后端；不影响物体高度 H。
    lw_height_mm: float = Field(default=0.0)
    enable_bottom_measurement: bool = False
    bottom_params: SectionParams
    enable_middle_measurement: bool = False
    middle_params: SectionParams


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class RecipeResponse(RecipeBase):
    id: str


class RecipeListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    recipes: dict[str, RecipeBase]


class RecipeOption(BaseModel):
    id: str
    name: str


class RecipeOptionsResponse(BaseModel):
    options: list[RecipeOption]
