from typing import Optional

from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    stock_quantity: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None