from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


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
