from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.post import PostStatus
from app.models.channel import Platform


class PostBase(BaseModel):
    channel_id: int
    content_type_id: Optional[int] = None
    title: Optional[str] = None
    body: str
    media_urls: Optional[List[str]] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None


class PostCreate(PostBase):
    status: PostStatus = PostStatus.DRAFT


class PostUpdate(BaseModel):
    channel_id: Optional[int] = None
    content_type_id: Optional[int] = None
    title: Optional[str] = None
    body: Optional[str] = None
    media_urls: Optional[List[str]] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    status: Optional[PostStatus] = None
    scheduled_at: Optional[datetime] = None


class PostResponse(PostBase):
    id: int
    status: PostStatus
    censorship_flags: Optional[dict] = None
    censorship_passed: bool
    ai_metadata: Optional[dict] = None
    generated_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublishQueueBase(BaseModel):
    post_id: int
    platform: Platform
    scheduled_at: datetime
    priority: int = 5


class PublishQueueCreate(PublishQueueBase):
    pass


class PublishQueueResponse(PublishQueueBase):
    id: int
    attempts: int
    max_attempts: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
