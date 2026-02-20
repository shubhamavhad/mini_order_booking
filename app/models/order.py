from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="PENDING")
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Float)