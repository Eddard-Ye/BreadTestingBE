from __future__ import annotations

import time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.schemas.recipe import RecipeBase, RecipeCreate, RecipeUpdate


class RecipeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_recipes(self) -> dict[str, RecipeBase]:
        rows = self.db.scalars(select(Recipe).order_by(Recipe.id)).all()
        return {row.id: RecipeBase.model_validate(row.config) for row in rows}

    def get_recipe(self, recipe_id: str) -> RecipeBase:
        row = self.db.get(Recipe, recipe_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在")
        return RecipeBase.model_validate(row.config)

    def create_recipe(self, payload: RecipeCreate) -> tuple[str, RecipeBase]:
        recipe = RecipeBase.model_validate(payload.model_dump(by_alias=True))
        recipe_id = f"custom_{int(time.time() * 1000)}"
        row = Recipe(
            id=recipe_id,
            name=recipe.name,
            config=recipe.model_dump(by_alias=True),
        )
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="配方名称已存在",
            ) from exc
        return recipe_id, recipe

    def update_recipe(self, recipe_id: str, payload: RecipeUpdate) -> RecipeBase:
        row = self.db.get(Recipe, recipe_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在")

        recipe = RecipeBase.model_validate(payload.model_dump(by_alias=True))
        row.name = recipe.name
        row.config = recipe.model_dump(by_alias=True)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="配方名称已存在",
            ) from exc
        return recipe

    def delete_recipe(self, recipe_id: str) -> None:
        row = self.db.get(Recipe, recipe_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配方不存在")

        total = self.db.scalar(select(func.count()).select_from(Recipe)) or 0
        if total <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="至少保留一个配方")

        self.db.delete(row)
        self.db.commit()


def get_recipe_service(db: Session) -> RecipeService:
    return RecipeService(db)
