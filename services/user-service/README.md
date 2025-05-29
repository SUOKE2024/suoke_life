# 索克生活用户服务 (User Service)

索克生活平台的用户认证、授权和用户数据管理微服务。

## 功能特性

- 用户注册和登录
- JWT 令牌认证
- 用户权限管理
- 用户资料管理
- 密码加密和验证
- 会话管理

## 技术栈

- **Python**: 3.13.3
- **Web框架**: FastAPI
- **数据库**: SQLAlchemy + SQLite/PostgreSQL
- **缓存**: Redis
- **认证**: JWT + Passlib
- **包管理**: UV (Python 包管理器)

## 开发环境设置

### 前置要求

- Python 3.13.3+
- UV (Python 包管理器)
- Redis (用于缓存)

### 安装依赖

```bash
# 使用 UV 安装依赖项
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 环境配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：
```env
# 数据库配置
DATABASE_URL=sqlite:///./user_service.db
# DATABASE_URL=postgresql://user:password@localhost/user_service

# Redis 配置
REDIS_URL=redis://localhost:6379

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务配置
HOST=0.0.0.0
PORT=8001
DEBUG=true
```

### 数据库迁移

```bash
# 初始化数据库
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## 运行服务

### 开发模式

```bash
# 使用 UV 运行
uv run python -m user_service

# 或者激活虚拟环境后运行
source .venv/bin/activate
python -m user_service
```

### 生产模式

```bash
# 使用 Uvicorn
uvicorn user_service.main:app --host 0.0.0.0 --port 8001

# 或者使用 Gunicorn (推荐生产环境)
gunicorn user_service.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API 文档

服务启动后，可以访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=user_service --cov-report=html

# 运行特定测试文件
uv run pytest test/test_auth.py
```

## 代码质量

```bash
# 代码格式化
uv run black user_service/
uv run isort user_service/

# 代码检查
uv run flake8 user_service/
uv run mypy user_service/

# 使用 Ruff (推荐)
uv run ruff check user_service/
uv run ruff format user_service/
```

## Docker 部署

```bash
# 构建镜像
docker build -t user-service .

# 运行容器
docker run -p 8001:8001 user-service
```

## 项目结构

```
user-service/
├── user_service/           # 主要源代码
│   ├── __init__.py
│   ├── main.py            # 应用入口
│   ├── api/               # API 路由
│   ├── core/              # 核心配置和工具
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── test/                  # 测试文件
├── migrations/            # 数据库迁移文件
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 锁定的依赖版本
├── .python-version       # Python 版本
└── README.md             # 项目文档
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: https://github.com/suokelife/suoke_life
- 邮箱: dev@suokelife.com 