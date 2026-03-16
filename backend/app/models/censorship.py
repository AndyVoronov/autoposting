from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CensorshipType(str):
    BANNED = "banned"
    WARN = "warn"
    REVIEW = "review"
    AUTO_EDIT = "auto_edit"


class CensorshipRule(Base):
    __tablename__ = "censorship_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pattern: Mapped[str] = mapped_column(String(500), index=True)
    pattern_type: Mapped[str] = mapped_column(String(20), default="word")  # word, regex
    rule_type: Mapped[str] = mapped_column(
        String(20), default="banned"
    )  # banned, warn, review, auto_edit
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    replacement: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<CensorshipRule {self.pattern}>"


class CensorshipLog(Base):
    __tablename__ = "censorship_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("posts.id"), nullable=True, index=True
    )
    text: Mapped[str] = mapped_column(Text)
    rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("censorship_rules.id"), nullable=True)
    matched_pattern: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    action: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CensorshipLog {self.action}>"
