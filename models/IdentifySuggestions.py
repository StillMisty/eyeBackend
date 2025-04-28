from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy import Enum as SQLAEnum

from database import Base
from models.Users import Gender


class IdentifySuggestions(Base):
    """眼部疾病识别建议记录表"""

    # 表名
    __tablename__ = "identify_suggestions"

    # 表字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    age = Column(Integer, comment="用户年龄")
    gender = Column(SQLAEnum(Gender), default=None, comment="用户性别")
    disease = Column(String, comment="疾病名称")
    suggestion = Column(String, comment="识别建议")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def __init__(self, age: int, gender: Gender, disease: str, suggestion: str):
        self.age = age
        self.gender = gender
        self.disease = disease
        self.suggestion = suggestion

    def to_dict(self):
        """
        将对象转换为字典
        :return: 包含识别建议信息的字典
        """
        return {
            "id": self.id,
            "age": self.age,
            "gender": self.gender,
            "disease": self.disease,
            "suggestion": self.suggestion,
            "created_at": self.created_at.isoformat(),
        }
