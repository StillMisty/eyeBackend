# 眼疾识别系统后端

基于FastAPI构建的眼部疾病识别系统后端服务，提供眼部图像上传、疾病识别、用户认证等功能。

## 项目概述

本系统能够通过分析用户上传的眼部图像，识别可能存在的眼部疾病，包括但不限于：

- 白内障 (Cataract)
- 青光眼 (Glaucoma)
- 糖尿病视网膜病变 (Diabetic Retinopathy)
- 黄斑变性 (Macular Degeneration)
- 高血压眼病 (Hypertensive Retinopathy)
- 近视 (Myopia)
- 其他眼部疾病

系统采用深度学习模型进行眼部疾病识别，并结合Grad-CAM技术提供可视化解释，帮助用户理解模型关注的区域。

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite/PostgreSQL
- **认证**: JWT (JSON Web Tokens)
- **机器学习**: TensorFlow
- **可视化**: Grad-CAM

## 项目结构

``` bash
.
├── Config.py                # 配置文件
├── database.py              # 数据库连接
├── main.py                  # 主程序入口
├── pyproject.toml           # 项目依赖
├── auth/                    # 认证相关
│   ├── auth_handler.py      # 认证处理
│   └── auth_router.py       # 认证路由
├── eye_identify/            # 眼疾识别核心
│   ├── GradCam.py           # 模型可视化
│   ├── identify.py          # 识别实现
│   └── model.h5             # 预训练模型
├── models/                  # 数据模型
│   ├── EyeIdentification.py # 识别记录模型
│   ├── IdentifySuggestions.py # 建议模型
│   ├── UserRating.py        # 用户评分模型
│   └── Users.py             # 用户模型
├── routers/                 # API路由
│   ├── identify_router.py   # 识别相关路由
│   ├── introduce_router.py  # 疾病介绍路由
│   └── users_router.py      # 用户相关路由
├── static/                  # 静态资源
│   └── disease_images/      # 疾病图像
├── uploads/                 # 上传目录
└── utils/                   # 工具函数
```

## 主要功能

### 1. 眼部疾病识别

- 上传眼部图像进行疾病识别
- 返回可能的疾病类型及其置信度
- 提供疾病详细描述和建议

### 2. 用户管理

- 用户注册/登录
- JWT token认证
- 用户历史记录管理

### 3. 疾病介绍

- 提供常见眼疾的详细介绍
- 包含症状、原因、治疗方法等信息

## API文档

启动服务后，访问 `http://localhost:8000/docs` 可查看完整的API文档。

## 安装与运行

### 环境要求

- Python 3.12+
- TensorFlow 2.0+
- FastAPI
- SQLAlchemy

### 安装步骤

1. 克隆代码库

```bash
# 需下载git-lfs以同步模型文件
git clone https://github.com/StillMisty/eyeBackend
cd eyeBackend
```

2. 同步虚拟环境并且安装依赖

```bash
# 使用 UV 管理虚拟环境，https://docs.astral.sh/uv/
uv sync
```

3. 修改配置
编辑 `Config.py` 文件，根据实际情况配置数据库连接、JWT密钥等

4. 启动服务

```bash
uv run python main.py
```

## 许可证

本项目遵循 Apache 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
