from fastapi import FastAPI
from app.db.database import engine
from app.db.base import Base
from app.api import auth, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Order System")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)