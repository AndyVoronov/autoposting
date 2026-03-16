from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.channel import ContentTypeModel
from app.schemas.channel import (
    ContentTypeCreate,
    ContentTypeUpdate,
    ContentTypeResponse,
)
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/content-types", tags=["content-types"])


@router.get("", response_model=List[ContentTypeResponse])
async def get_content_types(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ContentTypeModel).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{content_type_id}", response_model=ContentTypeResponse)
async def get_content_type(
    content_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentTypeModel).where(ContentTypeModel.id == content_type_id)
    )
    content_type = result.scalar_one_or_none()

    if not content_type:
        raise HTTPException(status_code=404, detail="Content type not found")

    return content_type


@router.post("", response_model=ContentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_content_type(
    data: ContentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = ContentTypeModel(**data.model_dump())
    db.add(content_type)
    await db.commit()
    await db.refresh(content_type)
    return content_type


@router.patch("/{content_type_id}", response_model=ContentTypeResponse)
async def update_content_type(
    content_type_id: int,
    data: ContentTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentTypeModel).where(ContentTypeModel.id == content_type_id)
    )
    content_type = result.scalar_one_or_none()

    if not content_type:
        raise HTTPException(status_code=404, detail="Content type not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content_type, field, value)

    await db.commit()
    await db.refresh(content_type)
    return content_type


@router.delete("/{content_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_type(
    content_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentTypeModel).where(ContentTypeModel.id == content_type_id)
    )
    content_type = result.scalar_one_or_none()

    if not content_type:
        raise HTTPException(status_code=404, detail="Content type not found")

    await db.delete(content_type)
    await db.commit()
