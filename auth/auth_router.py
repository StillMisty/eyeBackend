from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.auth_handler import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from database import get_db
from models.Users import Gender, Users

router = APIRouter(prefix="/auth", tags=["认证"])


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    account: str
    password: str


class UserCreate(BaseModel):
    account: str
    password: str
    birth_date: datetime = None
    gender: Gender = None

    class Config:
        use_enum_values = True


class UserResponse(BaseModel):
    id: int
    account: str
    birth_date: date = None
    gender: str = None

    class Config:
        from_attributes = True


@router.post("/login", response_model=Token)
def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.account, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.account}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.account == user.account).first()
    if db_user:
        raise HTTPException(status_code=400, detail="账号已存在")

    hashed_password = get_password_hash(user.password)
    db_user = Users(
        account=user.account,
        password=hashed_password,
        birth_date=user.birth_date,
        gender=user.gender,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.account}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
