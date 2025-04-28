from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.auth_router import router as auth_router
from Config import Config
from database import init_db
from routers.identify_router import router as identify_router
from routers.users_router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    init_db()
    yield


app = FastAPI(title=Config.SERVER_CONFIG["title"], lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(identify_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.SERVER_CONFIG["host"],
        port=Config.SERVER_CONFIG["port"],
        reload=Config.SERVER_CONFIG["reload"],
    )
