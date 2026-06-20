from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_recipe_service_dep, require_auth
from app.schemas.recipe import (
    RecipeCreate,
    RecipeListResponse,
    RecipeOption,
    RecipeOptionsResponse,
    RecipeResponse,
    RecipeUpdate,
)
from app.services.recipe_service import RecipeService

router = APIRouter()


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> RecipeListResponse:
    """获取全部配方，供下拉框与页面初始化使用。"""
    return RecipeListResponse(recipes=service.list_recipes())


@router.get("/options", response_model=RecipeOptionsResponse)
async def list_recipe_options(
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> RecipeOptionsResponse:
    """获取配方下拉选项（id + name）。"""
    recipes = service.list_recipes()
    options = [
        RecipeOption(id=recipe_id, name=recipe.name)
        for recipe_id, recipe in recipes.items()
    ]
    return RecipeOptionsResponse(options=options)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> RecipeResponse:
    """查看指定配方配置（查看配置 / 当前选中配方）。"""
    recipe = service.get_recipe(recipe_id)
    return RecipeResponse(id=recipe_id, **recipe.model_dump())


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate,
    _: Annotated[str, Depends(require_auth)],
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> RecipeResponse:
    """添加配方（需登录）。"""
    recipe_id, recipe = service.create_recipe(payload)
    return RecipeResponse(id=recipe_id, **recipe.model_dump())


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    payload: RecipeUpdate,
    _: Annotated[str, Depends(require_auth)],
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> RecipeResponse:
    """编辑配方（需登录）。"""
    recipe = service.update_recipe(recipe_id, payload)
    return RecipeResponse(id=recipe_id, **recipe.model_dump())


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str,
    _: Annotated[str, Depends(require_auth)],
    service: Annotated[RecipeService, Depends(get_recipe_service_dep)],
) -> None:
    """删除配方（需登录）。"""
    service.delete_recipe(recipe_id)
