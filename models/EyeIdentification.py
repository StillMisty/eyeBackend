import json
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class EyeIdentification(Base):
    """眼部识别记录模型"""

    __tablename__ = "eye_identifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_path = Column(String, nullable=False)
    results = Column(Text, nullable=False)  # JSON格式存储识别结果
    created_at = Column(DateTime, default=datetime.now)

    # 关联用户
    user = relationship("Users", back_populates="eye_identifications")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "results": json.loads(self.results),
            "created_at": self.created_at.isoformat(),
        }
