from datetime import date, datetime
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy import desc
from sqlalchemy.orm import Session

from auth.auth_handler import get_current_user
from database import get_db
from models.UserRating import UserRating
from models.Users import Gender, Users
from utils import is_valid_comment

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


# 用户评分请求模型
class RatingRequest(BaseModel):
    rating: int
    comment: str = None

    @field_validator("rating")
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("评分必须在1-5之间")
        return v


# 用户评分响应模型
class RatingResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: str = None
    created_at: datetime

    class Config:
        from_attributes = True


# 评分统计响应模型
class RatingStats(BaseModel):
    average_rating: float
    total_ratings: int


# 分页响应模型
class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    pages: int


# 分页评分响应模型
class PaginatedRatingResponse(PaginatedResponse):
    items: list[RatingResponse]


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


@router.post(
    "/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED
)
def create_rating(
    rating_data: RatingRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    添加用户评分和评论
    """
    # 检查评论内容是否有效（如果提供了评论）
    if rating_data.comment:
        is_valid, reason = is_valid_comment(rating_data.comment)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"评论无效: {reason}")

    # 创建新的评分记录
    new_rating = UserRating(
        user_id=current_user.id, rating=rating_data.rating, comment=rating_data.comment
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating


@router.get("/ratings/all", response_model=PaginatedRatingResponse)
def get_all_ratings(
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
):
    """
    分页获取所有用户的评论
    """

    # 查询总评论数
    total = db.query(UserRating).count()

    # 获取当前页的评论
    ratings = (
        db.query(UserRating)
        .order_by(desc(UserRating.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 返回分页结果
    return {
        "items": ratings,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": ceil(total / limit) if total > 0 else 1,
    }


@router.get("/ratings", response_model=list[RatingResponse])
def get_user_ratings(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    获取当前用户的所有评分记录
    """
    ratings = (
        db.query(UserRating)
        .filter(UserRating.user_id == current_user.id)
        .order_by(desc(UserRating.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return ratings


@router.get("/ratings/stats", response_model=RatingStats)
def get_rating_stats(db: Session = Depends(get_db)):
    """
    获取带有时间加权的平均评分统计
    """
    # 获取所有评分记录
    ratings = db.query(UserRating).order_by(desc(UserRating.created_at)).all()

    if not ratings:
        return {"average_rating": 0.0, "total_ratings": 0}

    # 计算时间加权评分
    total_weight = 0
    weighted_sum = 0
    current_time = datetime.now()

    for rating in ratings:
        # 计算时间差（以天为单位）
        days_diff = (current_time - rating.created_at).days
        # 使用指数衰减作为权重，最近的评分权重更大
        weight = max(0.1, 1.0 / (1 + 0.1 * days_diff))  # 确保权重最小为0.1

        weighted_sum += rating.rating * weight
        total_weight += weight

    # 计算加权平均分
    average_rating = weighted_sum / total_weight if total_weight > 0 else 0

    return {"average_rating": round(average_rating, 2), "total_ratings": len(ratings)}
