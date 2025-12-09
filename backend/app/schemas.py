from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    
    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    item_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: int
    item: ItemResponse
    
    class Config:
        from_attributes = True

class CheckoutRequest(BaseModel):
    user_id: str
    discount_code: Optional[str] = None

class CheckoutResponse(BaseModel):
    order_id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    discount_code: Optional[str] = None

class DiscountCodeResponse(BaseModel):
    id: int
    code: str
    discount_percentage: float
    is_used: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdminStatsResponse(BaseModel):
    total_items_purchased: int
    total_purchase_amount: float
    discount_codes: List[DiscountCodeResponse]
    total_discount_amount: float

