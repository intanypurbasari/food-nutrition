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


# Nutrients absent from both TKPI and MyFCD, filled from USDA SR Legacy by
# scripts/fill_usda_nutrients.py after Stage 3. Kept out of NUTRIENT_FIELDS so
# they neither act as Stage 3 imputation predictors nor count toward
# missing_nutrient_count / completeness_score of the source data.
USDA_NUTRIENT_FIELDS = [
    "magnesium_mg",
    "sugars_total_g",
    "saturated_fat_g",
    "cholesterol_mg",
    "vitamin_b6_mg",
    "vitamin_b12_mcg",
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
    magnesium_mg: Optional[float] = None
    sugars_total_g: Optional[float] = None
    saturated_fat_g: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    vitamin_b6_mg: Optional[float] = None
    vitamin_b12_mcg: Optional[float] = None
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
