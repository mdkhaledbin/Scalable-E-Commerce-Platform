from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItemUpdate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)


class OrderBase(BaseModel):
    user_id: int = Field(gt=0)


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(default=None, min_length=1, max_length=20)
    items: Optional[List[OrderItemUpdate]] = None


class OrderRead(OrderBase):
    id: int
    status: str
    items: List[OrderItemRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
