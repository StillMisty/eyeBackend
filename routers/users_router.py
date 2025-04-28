from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.auth_handler import get_current_user
from database import get_db
from models.Users import Gender, Users

# 创建路由
router = APIRouter(
    prefix="/users",
    tags=["用户"],
)


class UserInfoUpdate(BaseModel):
    birth_date: date = None
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


@router.put("/update", response_model=UserResponse)
def update_user_info(
    user_data: UserInfoUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新当前登录用户的性别和出生日期信息
    """
    # 只更新提供的字段
    if user_data.birth_date is not None:
        current_user.birth_date = user_data.birth_date
    if user_data.gender is not None:
        current_user.gender = user_data.gender

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserResponse)
def get_user_info(current_user: Users = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    """
    return current_user
