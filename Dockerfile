FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 提取和安装依赖
RUN pip install --no-cache-dir \
    bcrypt>=4.3.0 \
    fastapi>=0.115.12 \
    matplotlib>=3.10.1 \
    numpy>=2.1.3 \
    openai>=1.76.0 \
    opencv-python>=4.11.0.86 \
    passlib>=1.7.4 \
    "psycopg[binary,pool]>=3.2.7" \
    pydantic>=2.11.3 \
    pyjwt>=2.10.1 \
    python-multipart>=0.0.20 \
    sqlalchemy>=2.0.40 \
    tensorflow>=2.19.0 \
    "uvicorn[standard]>=0.34.2"

# 复制项目文件
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建必要的目录
RUN mkdir -p uploads static

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]