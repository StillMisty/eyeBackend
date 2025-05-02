from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database import Base


class UserRating(Base):
    """用户评分实体类，用于存储用户评论和打分信息"""

    # 表名
    __tablename__ = "user_ratings"

    # 表字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment="评分ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    rating = Column(Integer, nullable=False, comment="评分(1-5)")
    comment = Column(Text, nullable=True, comment="评论内容")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联用户
    user = relationship("Users", back_populates="ratings")

    def __init__(self, user_id, rating, comment=None):
        """
        初始化用户评分
        :param user_id: 用户ID
        :param rating: 评分(1-5)
        :param comment: 评论内容
        """
        self.user_id = user_id
        self.rating = rating
        self.comment = comment

    def __repr__(self):
        """
        字符串表示
        :return: 用户评分信息字符串
        """
        return f"<UserRating(user_id={self.user_id}, rating={self.rating}, created_at='{self.created_at}')>"

    def to_dict(self):
        """
        将对象转换为字典
        :return: 包含用户评分信息的字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
