from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from Config import Config
from database import get_db
from models.Users import Users

# 密码哈希配置
pwd_context = CryptContext(**Config.get_password_config())
# JWT配置
SECRET_KEY = Config.get_jwt_secret_key()
ALGORITHM = Config.get_jwt_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = Config.get_jwt_expire_minutes()

# 创建安全方案，用于Swagger UI显示锁图标
security = HTTPBearer()


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, account: str, password: str):
    """验证用户"""
    user = db.query(Users).filter(Users.account == account).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user_from_token(token: str, db: Session):
    """从JWT令牌获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account: str = payload.get("sub")
        if account is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(Users).filter(Users.account == account).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_from_request(request: Request, db: Session):
    """从请求头获取当前用户（直接调用函数使用）"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.replace("Bearer ", "")
    return get_current_user_from_token(token, db)


# 创建可以用作依赖项的函数
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """从请求头获取当前用户（作为依赖项使用）"""
    token = credentials.credentials
    return get_current_user_from_token(token, db)
