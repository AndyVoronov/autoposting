from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_current_user
from app.models.user import User
from app.services.ai import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


class TextRequest(BaseModel):
    text: str
    max_chars: Optional[int] = 500


class TextResponse(BaseModel):
    result: Optional[str]
    success: bool


@router.post("/improve", response_model=TextResponse)
async def improve_text(
    data: TextRequest,
    current_user: User = Depends(get_current_user),
):
    result = await ai_service.improve_text(data.text)
    return TextResponse(result=result, success=result is not None)


@router.post("/shorten", response_model=TextResponse)
async def shorten_text(
    data: TextRequest,
    current_user: User = Depends(get_current_user),
):
    result = await ai_service.shorten_text(data.text, data.max_chars or 500)
    return TextResponse(result=result, success=result is not None)


@router.post("/rewrite", response_model=TextResponse)
async def rewrite_text(
    data: TextRequest,
    current_user: User = Depends(get_current_user),
):
    result = await ai_service.rewrite_text_for_post(data.text)
    return TextResponse(result=result, success=result is not None)
