from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.api.deps import get_current_user, get_db, admin_required
from app.services.order_service import (
    create_order,
    confirm_order,
    cancel_order
)
from app.schemas.order import OrderCreate
from app.models.order import Order

router = APIRouter(prefix="/orders", tags=["Orders"])



# CREATE ORDER
@router.post("/", status_code=status.HTTP_201_CREATED)
def place_order(
    order: OrderCreate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        result = create_order(db, user.id, order.items)

        return {
            "status": True,
            "message": "Order placed successfully",
            "data": result
        }

    except HTTPException as e:
        raise e

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )


# LIST ORDERS (Pagination + Filter)
@router.get("/", status_code=status.HTTP_200_OK)
def list_orders(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        query = db.query(Order)

        # Normal users see only their orders
        if user.role != "admin":
            query = query.filter(Order.customer_id == user.id)

        if status:
            query = query.filter(Order.status == status)

        total = query.count()
        skip = (page - 1) * limit

        orders = query.offset(skip).limit(limit).all()

        return {
            "status": True,
            "message": "Orders fetched successfully",
            "data": orders,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total // limit) + (1 if total % limit > 0 else 0)
            }
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )


# CONFIRM ORDER (Admin Only)
@router.patch("/{order_id}/confirm", status_code=status.HTTP_200_OK)
def confirm(
    order_id: int,
    db=Depends(get_db),
    user=Depends(admin_required)
):
    try:
        order = confirm_order(db, order_id)

        return {
            "status": True,
            "message": "Order confirmed successfully",
            "data": {
                "order_id": order.id,
                "status": order.status
            }
        }

    except HTTPException as e:
        raise e

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )


# CANCEL ORDER (Customer/Admin)
@router.patch("/{order_id}/cancel", status_code=status.HTTP_200_OK)
def cancel(
    order_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        order = cancel_order(db, order_id, user)

        return {
            "status": True,
            "message": "Order cancelled successfully",
            "data": {
                "order_id": order.id,
                "status": order.status
            }
        }

    except HTTPException as e:
        raise e

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )