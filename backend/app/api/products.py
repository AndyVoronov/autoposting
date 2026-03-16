from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.analytics import AffiliateProduct, AffiliateClick

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    ref_url: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    image_url: Optional[str] = None
    price: Optional[str] = None


class ProductResponse(ProductCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(AffiliateProduct)
    if category:
        query = query.where(AffiliateProduct.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = AffiliateProduct(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AffiliateProduct).where(AffiliateProduct.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        return {"error": "Product not found"}

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AffiliateProduct).where(AffiliateProduct.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        return {"error": "Product not found"}

    await db.delete(product)
    await db.commit()
    return {"status": "deleted"}
