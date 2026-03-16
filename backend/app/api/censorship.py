from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.censorship import CensorshipRule
from app.services.censorship import check_censorship

router = APIRouter(prefix="/censorship", tags=["censorship"])


class CensorshipRuleCreate(BaseModel):
    pattern: str
    pattern_type: str = "word"
    rule_type: str = "banned"
    category: Optional[str] = None
    replacement: Optional[str] = None


class CensorshipRuleResponse(CensorshipRuleCreate):
    id: int
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class CensorshipCheckRequest(BaseModel):
    text: str


class CensorshipCheckResponse(BaseModel):
    passed: bool
    action: str
    matched_rules: List[dict]
    ai_check: Optional[dict] = None


@router.get("/rules", response_model=List[CensorshipRuleResponse])
async def get_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CensorshipRule).order_by(CensorshipRule.category))
    return result.scalars().all()


@router.post("/rules", response_model=CensorshipRuleResponse)
async def create_rule(
    data: CensorshipRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = CensorshipRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CensorshipRule).where(CensorshipRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    await db.delete(rule)
    await db.commit()
    return {"status": "deleted"}


@router.post("/check", response_model=CensorshipCheckResponse)
async def check_text(
    data: CensorshipCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await check_censorship(db, data.text)
    return CensorshipCheckResponse(**result)
