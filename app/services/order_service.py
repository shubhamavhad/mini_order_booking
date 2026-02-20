from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.product import Product
from app.models.order import Order, OrderItem


# ---------------- CREATE ORDER ----------------

def create_order(db, user_id, items):
    try:
        order = Order(customer_id=user_id)
        db.add(order)
        db.flush()

        total = 0

        for item in items:
            product = db.query(Product)\
                .filter(Product.id == item.product_id)\
                .with_for_update().first()

            if not product:
                raise HTTPException(404, "Product not found")

            if not product.is_active:
                raise HTTPException(400, "Inactive product")

            if product.stock_quantity < item.quantity:
                raise HTTPException(400, "Insufficient stock")

            product.stock_quantity -= item.quantity
            total += product.price * item.quantity

            db.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price
            ))

        order.total_amount = total
        db.commit()
        return order

    except Exception as e:
        db.rollback()
        raise e


# ---------------- CONFIRM ORDER ----------------

def confirm_order(db, order_id):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise HTTPException(404, "Order not found")

        if order.status == "CONFIRMED":
            raise HTTPException(400, "Order already confirmed")

        if order.status == "CANCELLED":
            raise HTTPException(400, "Cancelled order cannot be confirmed")

        order.status = "CONFIRMED"
        db.commit()
        return order

    except Exception as e:
        db.rollback()
        raise e


# ---------------- CANCEL ORDER ----------------

def cancel_order(db, order_id, user):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise HTTPException(404, "Order not found")

        # Customer can cancel only their order
        if user.role != "admin" and order.customer_id != user.id:
            raise HTTPException(403, "Not allowed")

        if order.status == "CANCELLED":
            raise HTTPException(400, "Order already cancelled")

        # Restore stock
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        for item in items:
            product = db.query(Product)\
                .filter(Product.id == item.product_id)\
                .with_for_update().first()

            product.stock_quantity += item.quantity

        order.status = "CANCELLED"
        db.commit()
        return order

    except Exception as e:
        db.rollback()
        raise e