from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from app.database import get_db
from app.models.post import PublishQueue
from app.schemas.post import PublishQueueCreate, PublishQueueResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("", response_model=List[PublishQueueResponse])
async def get_queue(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(PublishQueue).order_by(desc(PublishQueue.scheduled_at))

    if status:
        query = query.where(PublishQueue.status == status)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PublishQueueResponse)
async def add_to_queue(
    data: PublishQueueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    queue_item = PublishQueue(**data.model_dump())
    db.add(queue_item)
    await db.commit()
    await db.refresh(queue_item)
    return queue_item


@router.delete("/{queue_id}")
async def remove_from_queue(
    queue_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(PublishQueue).where(PublishQueue.id == queue_id))
    item = result.scalar_one_or_none()

    if not item:
        return {"error": "Queue item not found"}

    await db.delete(item)
    await db.commit()
    return {"status": "removed"}
