# API'nin kullanacağı modeller

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str
    brand: str
    image_url: str
    is_active: bool = True


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    brand: str
    image_url: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    status: str

    model_config = ConfigDict(from_attributes=True)

