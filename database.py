from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Config import Config

# 使用配置类获取数据库URL
SQLALCHEMY_DATABASE_URL = Config.get_db_url()

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=Config.get_db_connect_args(),
)

# 创建SessionLocal类
SessionLocal = sessionmaker(
    autocommit=Config.DATABASE_CONFIG["autocommit"],
    autoflush=Config.DATABASE_CONFIG["autoflush"],
    bind=engine,
)

# 创建Base类，用于创建模型类
Base = declarative_base()


# 数据库初始化函数
def init_db():
    # 导入所有模型，确保它们已注册到Base中
    from models.EyeIdentification import EyeIdentification  # noqa: F401
    from models.IdentifySuggestions import IdentifySuggestions  # noqa: F401
    from models.UserRating import UserRating  # noqa: F401
    from models.Users import Users  # noqa: F401

    # 创建所有表
    Base.metadata.create_all(bind=engine)


# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
