from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_db

router = APIRouter(tags=["Auth"])

#register the user
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db=Depends(get_db)):
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"status": False, "message": "Username already exists"}
            )

        db_user = User(
            username=user.username,
            password=hash_password(user.password),
            role=user.role
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {
            "status": True,
            "message": "User created successfully",
            "data": {
                "id": db_user.id,
                "username": db_user.username,
                "role": db_user.role
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Database error"}
        )


#login the user and return access token
@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: LoginRequest, db=Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == data.username).first()

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = create_access_token({"id": user.id})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )