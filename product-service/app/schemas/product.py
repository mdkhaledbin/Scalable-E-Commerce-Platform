from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(min_length=3,max_length=50)
    price: int
    description: str = Field(min_length=5, max_length=200)
    category: str = Field(min_length=3, max_length=50)
    stock: int = Field(default=0)
    
class ProductRead(ProductBase):
    id:int
    created_at:datetime
    updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
    
class ProductUpdate(BaseModel):
    name: str | None = Field(min_length=3,max_length=50, default=None)
    price: int | None = Field(default=None)
    description: str | None = Field(min_length=5, max_length=200, default=None)
    category: str | None = Field(min_length=3, max_length=50, default=None)
    stock: int | None = Field(default=None)
    
    