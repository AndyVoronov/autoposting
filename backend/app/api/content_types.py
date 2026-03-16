from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.channel import ContentTypeModel, ChannelContent, Channel
from app.schemas.channel import (
    ContentTypeCreate,
    ContentTypeUpdate,
    ContentTypeResponse,
)
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/content-types", tags=["content-types"])


class ChannelBindingCreate(BaseModel):
    channel_id: int
    schedule: str | None = None


class ChannelBindingResponse(BaseModel):
    id: int
    channel_id: int
    channel_name: str
    schedule: str | None
    is_active: bool

    class Config:
        from_attributes = True


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


@router.get("/{content_type_id}/channels", response_model=List[ChannelBindingResponse])
async def get_content_type_channels(
    content_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChannelContent)
        .where(ChannelContent.content_type_id == content_type_id)
        .options(selectinload(ChannelContent.channel))
    )
    bindings = result.scalars().all()

    return [
        ChannelBindingResponse(
            id=b.id,
            channel_id=b.channel_id,
            channel_name=b.channel.name if b.channel else f"Channel {b.channel_id}",
            schedule=b.schedule,
            is_active=b.is_active,
        )
        for b in bindings
    ]


@router.post(
    "/{content_type_id}/channels",
    response_model=ChannelBindingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bind_channel_to_content_type(
    content_type_id: int,
    data: ChannelBindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ct_result = await db.execute(
        select(ContentTypeModel).where(ContentTypeModel.id == content_type_id)
    )
    if not ct_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Content type not found")

    channel_result = await db.execute(select(Channel).where(Channel.id == data.channel_id))
    channel = channel_result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    existing = await db.execute(
        select(ChannelContent).where(
            and_(
                ChannelContent.content_type_id == content_type_id,
                ChannelContent.channel_id == data.channel_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Channel already bound to this content type")

    binding = ChannelContent(
        content_type_id=content_type_id,
        channel_id=data.channel_id,
        schedule=data.schedule,
        is_active=True,
    )
    db.add(binding)
    await db.commit()
    await db.refresh(binding)

    return ChannelBindingResponse(
        id=binding.id,
        channel_id=binding.channel_id,
        channel_name=channel.name,
        schedule=binding.schedule,
        is_active=binding.is_active,
    )


@router.delete("/{content_type_id}/channels/{binding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unbind_channel_from_content_type(
    content_type_id: int,
    binding_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChannelContent).where(
            and_(
                ChannelContent.id == binding_id,
                ChannelContent.content_type_id == content_type_id,
            )
        )
    )
    binding = result.scalar_one_or_none()

    if not binding:
        raise HTTPException(status_code=404, detail="Binding not found")

    await db.delete(binding)
    await db.commit()
