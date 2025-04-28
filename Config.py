from pathlib import Path
from typing import Any, Dict

from pydantic import ConfigDict


class Config(ConfigDict):
    # 服务器配置
    SERVER_CONFIG: Dict[str, Any] = {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "title": "眼疾识别系统",
    }

    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = ""

    # 数据库配置
    DATABASE_CONFIG: Dict[str, Any] = {
        "url": "sqlite:///./eye.db",
        "connect_args": {"check_same_thread": False},  # 仅SQLite需要此参数
        "autocommit": False,
        "autoflush": False,
    }

    # JWT认证配置
    JWT_CONFIG: Dict[str, Any] = {
        "secret_key": "114514",
        "algorithm": "HS256",
        "access_token_expire_minutes": 120,
    }

    # 文件上传配置
    UPLOAD_CONFIG: Dict[str, Any] = {
        "upload_dir": Path("uploads"),
        "allowed_types": ["image/jpeg", "image/png", "image/jpg"],
    }

    # 识别配置
    IDENTIFICATION_CONFIG: Dict[str, Any] = {"default_threshold": 0.1}

    # 密码哈希配置
    PASSWORD_CONFIG: Dict[str, Any] = {"schemes": ["bcrypt"], "deprecated": "auto"}

    @classmethod
    def get_db_url(cls) -> str:
        return cls.DATABASE_CONFIG["url"]

    @classmethod
    def get_db_connect_args(cls) -> Dict[str, Any]:
        return cls.DATABASE_CONFIG["connect_args"]

    @classmethod
    def get_jwt_secret_key(cls) -> str:
        return cls.JWT_CONFIG["secret_key"]

    @classmethod
    def get_jwt_algorithm(cls) -> str:
        return cls.JWT_CONFIG["algorithm"]

    @classmethod
    def get_jwt_expire_minutes(cls) -> int:
        return cls.JWT_CONFIG["access_token_expire_minutes"]

    @classmethod
    def get_upload_dir(cls) -> Path:
        return cls.UPLOAD_CONFIG["upload_dir"]

    @classmethod
    def get_allowed_types(cls) -> list:
        return cls.UPLOAD_CONFIG["allowed_types"]

    @classmethod
    def get_password_config(cls) -> Dict[str, Any]:
        return cls.PASSWORD_CONFIG
