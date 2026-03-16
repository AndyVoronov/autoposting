import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.post import Post


class Platform(str, enum.Enum):
    TELEGRAM = "telegram"
    VK = "vk"
    WORDPRESS = "wordpress"


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform), default=Platform.TELEGRAM)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="channel")
    content_types: Mapped[list["ChannelContent"]] = relationship(
        "ChannelContent", back_populates="channel"
    )

    def __repr__(self) -> str:
        return f"<Channel {self.name}>"


class ContentType(str, enum.Enum):
    REDDIT = "reddit"
    HOROSCOPE = "horoscope"
    ANIMAL_FACTS = "animal_facts"
    NEWS = "news"
    CITY = "city"
    AFFILIATE = "affiliate"
    CUSTOM = "custom"


class ContentTypeModel(Base):
    __tablename__ = "content_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    channels: Mapped[list["ChannelContent"]] = relationship(
        "ChannelContent", back_populates="content_type"
    )

    def __repr__(self) -> str:
        return f"<ContentType {self.name}>"


class ChannelContent(Base):
    __tablename__ = "channel_content"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), index=True)
    content_type_id: Mapped[int] = mapped_column(ForeignKey("content_types.id"), index=True)
    schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    channel: Mapped["Channel"] = relationship("Channel", back_populates="content_types")
    content_type: Mapped["ContentTypeModel"] = relationship(
        "ContentTypeModel", back_populates="channels"
    )

    def __repr__(self) -> str:
        return f"<ChannelContent channel={self.channel_id} type={self.content_type_id}>"
