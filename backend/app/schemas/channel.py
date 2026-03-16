from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.channel import Platform, ContentType


class ChannelBase(BaseModel):
    name: str
    slug: str
    platform: Platform = Platform.TELEGRAM
    config: Optional[dict] = None
    is_active: bool = True


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    platform: Optional[Platform] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class ChannelResponse(ChannelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentTypeBase(BaseModel):
    name: str
    type: ContentType
    description: Optional[str] = None
    config: Optional[dict] = None
    is_active: bool = True


class ContentTypeCreate(ContentTypeBase):
    pass


class ContentTypeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ContentType] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class ContentTypeResponse(ContentTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelContentBase(BaseModel):
    channel_id: int
    content_type_id: int
    schedule: Optional[str] = None
    config: Optional[dict] = None
    is_active: bool = True


class ChannelContentCreate(ChannelContentBase):
    pass


class ChannelContentUpdate(BaseModel):
    schedule: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class ChannelContentResponse(ChannelContentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
