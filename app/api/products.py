from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.product import Product
from app.api.deps import get_db, admin_required

router = APIRouter(prefix="/products", tags=["Products"])



# Create Product (Admin Only)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db=Depends(get_db),
    user=Depends(admin_required)
):
    try:
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "status": True,
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price
            }
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )



# List Products (Pagination)
@router.get("/", status_code=status.HTTP_200_OK)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db=Depends(get_db)
):
    try:
        query = db.query(Product)
        total = query.count()

        skip = (page - 1) * limit
        products = query.offset(skip).limit(limit).all()

        return {
            "status": True,
            "message": "Products fetched successfully",
            "data": products,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total // limit) + (1 if total % limit else 0)
            }
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )
    
# ============================
# Update Product (Admin Only)
# ============================

@router.patch("/{product_id}", status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db=Depends(get_db),
    user=Depends(admin_required)
):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "Product not found"}
            )

        update_fields = product_data.dict(exclude_unset=True)

        # Prevent negative stock
        if "stock_quantity" in update_fields:
            if update_fields["stock_quantity"] < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"status": False, "message": "Stock cannot be negative"}
                )

        for key, value in update_fields.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return {
            "status": True,
            "message": "Product updated successfully",
            "data": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "is_active": product.is_active
            }
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )