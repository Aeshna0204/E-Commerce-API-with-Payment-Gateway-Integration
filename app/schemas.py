from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from enum import Enum

class UserCreate(BaseModel):
    username: str
    email: str
    password:str
    role:str

class UserResponse(BaseModel):
    id: int           # Unique identifier for the user
    username: str     # The username of the user
    email: str        # The email of the user, if applicable
    role:str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        orm_mode = True   

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"

class OrderItem(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True
    
class OrderCreate(BaseModel):
    # user_id :int
    items: List[OrderItem]
    

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    payment_id: Optional[str]
    items: List[OrderItemResponse]
    status: str

    class Config:
        orm_mode = True

class OrderUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[OrderStatus] = None

class PaymentResponse(BaseModel):
    payment_id: str
    approval_url: str
   

