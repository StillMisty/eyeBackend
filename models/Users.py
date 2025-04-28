from enum import Enum

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import relationship

from database import Base


class Gender(str, Enum):
    """性别枚举"""

    MALE = "male"
    FEMALE = "female"


class Users(Base):
    """用户实体类，用于存储用户信息"""

    # 表名
    __tablename__ = "users"

    # 表字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    account = Column(String(50), unique=True, nullable=False, comment="用户账号")
    password = Column(String(100), nullable=False, comment="用户密码")
    birth_date = Column(Date, comment="用户出生日期")
    gender = Column(SQLAEnum(Gender), default=None, comment="用户性别")

    # 关联眼部识别记录
    eye_identifications = relationship("EyeIdentification", back_populates="user")

    def __init__(self, account, password, birth_date=None, gender=None):
        """
        初始化用户
        :param account: 用户账号
        :param password: 用户密码
        :param birth_date: 用户出生日期
        :param gender: 用户性别 (Gender枚举类型)
        """
        self.account = account
        self.password = password
        self.birth_date = birth_date
        self.gender = gender

    def __repr__(self):
        """
        字符串表示
        :return: 用户信息字符串
        """
        return f"<User(account='{self.account}', birth_date={self.birth_date}, gender='{self.gender}')>"

    def to_dict(self):
        """
        将对象转换为字典
        :return: 包含用户信息的字典
        """
        return {
            "id": self.id,
            "account": self.account,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
        }
