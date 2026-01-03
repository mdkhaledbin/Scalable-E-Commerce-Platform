from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price: int = Field(ge=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[int] = Field(default=None, ge=0)

class CartItemReplace(BaseModel):
    items: List[CartItemCreate] = Field(default_factory=list)

class CartItemRead(CartItemBase):
    id: int
    cart_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)




class CartBase(BaseModel):
    status: str = Field(default="PENDING", min_length=3, max_length=20)
    user_id: int = Field(gt=0)
    items: List[CartItemCreate] = Field(default_factory=list)


class CartCreate(CartBase):
    pass


class CartUpdate(BaseModel):
    status: Optional[str] = Field(default=None, min_length=3, max_length=20)


class CartRead(CartBase):
    id: int
    user_id: int
    items: List[CartItemRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)