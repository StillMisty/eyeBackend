# 眼疾识别系统后端

这是一个基于深度学习的眼疾识别系统后端，提供眼部疾病识别、用户管理和疾病建议等功能。

## 功能特点

- **眼疾识别**：上传眼部图像，自动识别可能存在的眼部疾病
- **用户管理**：用户注册、登录、管理个人信息
- **识别记录**：保存并查询历史识别记录
- **疾病建议**：根据识别结果、年龄和性别给出针对性建议
- **RESTful API**：提供标准化的API接口

## 技术栈

- **FastAPI**：高性能的Python Web框架
- **SQLAlchemy**：ORM数据库操作
- **TensorFlow**：深度学习模型支持
- **JWT认证**：用户身份验证
- **异步处理**：利用异步特性提高并发性能

## 快速开始

### 环境要求

- Python 3.10+
- 依赖包：详见 `pyproject.toml`

### 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

### 配置

修改 `Config.py` 文件，配置服务器设置、数据库连接、认证参数等。

### 运行服务

```bash
uv run python main.py
```

服务默认运行在 http://localhost:8000

## API文档

启动服务后，可访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要API接口

### 用户接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me` - 更新当前用户信息

### 眼疾识别接口

- `POST /api/v1/identify/eye` - 上传眼部图像进行识别
- `GET /api/v1/identify/history` - 获取识别历史记录
- `GET /api/v1/identify/history/{identification_id}` - 获取特定识别记录详情
- `GET /api/v1/identify/images/{identification_id}` - 获取识别图像
- `POST /api/v1/identify/suggestion` - 获取疾病建议
- `DELETE /api/v1/identify/history/{identification_id}` - 删除识别记录

## 项目结构

```
eyeBackend/
├── auth/                   # 用户认证相关模块
├── entity/                 # 数据实体定义
├── eye_identify/           # 眼疾识别核心功能
│   └── model.h5            # 深度学习模型文件
├── models/                 # 数据库模型定义
├── routers/                # API路由处理
├── uploads/                # 上传图像存储目录
├── utils/                  # 工具函数
├── Config.py               # 系统配置
├── database.py             # 数据库连接配置
├── main.py                 # 应用主入口
└── pyproject.toml          # 项目依赖配置
```

## 眼疾识别模型

系统使用预训练的深度学习模型，可以识别37种眼部疾病类型，包括：

- 糖尿病视网膜病变 (Diabetic Retinopathy)
- 青光眼 (Glaucoma)
- 白内障 (Cataract)
- 年龄相关性黄斑变性 (Age-related Macular Degeneration)
- 高度近视 (Pathological Myopia)
- 以及其他多种眼部疾病

## 数据存储

- 识别图像按照年/月/日的目录结构存储在 `uploads` 文件夹下
- 用户数据、识别记录等信息存储在SQLite数据库中 (eye.db)

## 授权许可

版权所有 © 2025