import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import Product, Order
from schemas import ProductCreate, ProductResponse, OrderCreate, OrderResponse

from kafka_producer import send_order_event
from redis_client import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()

    try:
        yield db    # Fonksiyon veritabanını get_products fonksiyonuna teslim eder ve çalışmasını dondurur. Bitirmez dondurur. Amaç finally'yi çalıştırmak
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "E-Commerce API çalışıyor!"}


# Ürün okuma
@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):

    cached_products = redis_client.get("products")

    if cached_products:
        print("Cache HIT - Dosya bulundu.")

        return json.loads(cached_products)

    print("Cache MISS - Dosya bulunamadı veritabanına istek gönderilecek.")

    products = db.query(Product).all()

    products_data = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "brand": product.brand,
            "image_url": product.image_url,
            "is_active": product.is_active
        }
        for product in products
    ]

    # Önbellek güncelleme
    redis_client.set(
        "products",
        json.dumps(products_data)
    )

    return products_data


# Ürün yazma
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db) ):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category=product.category,
        brand=product.brand,
        image_url=product.image_url,
        is_active=product.is_active
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

#Sipariş oluştur
@app.post("/orders", response_model=OrderResponse)
def create_order( order: OrderCreate, db: Session = Depends(get_db) ):
    product = db.query(Product).filter(
        Product.id == order.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Ürün satışa kapalı"
        )

    # if product.stock < order.quantity:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Yeterli stok bulunmuyor"
    #     )

    total_price = product.price * order.quantity
    # product.stock -= order.quantity


    new_order = Order(
        product_id=product.id,
        quantity=order.quantity,
        total_price=total_price,
        status="pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    order_event = {
        "event": "OrderCreated",
        "order_id": new_order.id,
        "product_id": new_order.product_id,
        "quantity": new_order.quantity
    }

    send_order_event(order_event)

    return new_order


# Oluşturulan siparişleri görme
@app.get("/orders", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()

    return orders

