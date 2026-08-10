from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


NUTRIENT_FIELDS = [
    "water_g",
    "energy_kcal",
    "protein_g",
    "fat_g",
    "carbohydrate_g",
    "fiber_g",
    "ash_g",
    "calcium_mg",
    "phosphorus_mg",
    "iron_mg",
    "sodium_mg",
    "potassium_mg",
    "copper_mg",
    "zinc_mg",
    "retinol_mcg",
    "beta_carotene_mcg",
    "carotene_total_mcg",
    "vitamin_a_mcg",
    "vitamin_b1_mg",
    "vitamin_b2_mg",
    "niacin_mg",
    "vitamin_c_mg",
]


class NutritionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    food_id: str
    food_name_original: str
    food_name_normalized: str
    source: str
    source_url: Optional[str] = None
    category_original: Optional[str] = None
    category_normalized: Optional[str] = None
    water_g: Optional[float] = None
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None
    carbohydrate_g: Optional[float] = None
    fiber_g: Optional[float] = None
    ash_g: Optional[float] = None
    calcium_mg: Optional[float] = None
    phosphorus_mg: Optional[float] = None
    iron_mg: Optional[float] = None
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    copper_mg: Optional[float] = None
    zinc_mg: Optional[float] = None
    retinol_mcg: Optional[float] = None
    beta_carotene_mcg: Optional[float] = None
    carotene_total_mcg: Optional[float] = None
    vitamin_a_mcg: Optional[float] = None
    vitamin_b1_mg: Optional[float] = None
    vitamin_b2_mg: Optional[float] = None
    niacin_mg: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    unit_basis: str = "per 100g"
    scraped_at: datetime
    cleaned_at: Optional[datetime] = None
    missing_nutrient_count: int = Field(ge=0)
    completeness_score: float = Field(ge=0, le=1)
    notes: Optional[str] = None

    @field_validator("food_id", "food_name_original", "food_name_normalized", "source", "unit_basis")
    @classmethod
    def required_strings_are_not_blank(cls, value: str) -> str:
        if value is None or not str(value).strip():
            raise ValueError("required string field cannot be blank")
        return str(value).strip()

    @field_validator("source")
    @classmethod
    def source_is_known(cls, value: str) -> str:
        normalized = str(value).strip()
        if normalized not in {"TKPI", "MyFCD"}:
            raise ValueError("source must be TKPI or MyFCD")
        return normalized


SCHEMA: list[dict[str, Any]] = [
    {"name": name, "required": field.is_required(), "annotation": str(field.annotation)}
    for name, field in NutritionRecord.model_fields.items()
]


def schema_columns() -> list[str]:
    return list(NutritionRecord.model_fields.keys())
