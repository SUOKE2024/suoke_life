# Corn Maze Service 快速启动指南

## 前置要求

- Python 3.13.3+
- UV 包管理器
- Git

## 快速开始

### 1. 安装 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd suoke_life/services/corn-maze-service
```

### 3. 安装依赖

```bash
# 使用开发脚本
python scripts/dev.py install

# 或直接使用 UV
uv sync --dev
```

### 4. 配置环境

```bash
# 复制环境配置文件
cp env.example .env

# 编辑配置（可选）
vim .env
```

### 5. 运行测试

```bash
# 运行所有检查
python scripts/dev.py check

# 或单独运行测试
python scripts/dev.py test
```

### 6. 启动服务

```bash
# 使用开发脚本
python scripts/dev.py server

# 或直接运行
uv run python -m corn_maze_service.cmd.server.main
```

## 开发命令

### 常用命令

```bash
# 安装依赖
python scripts/dev.py install

# 运行服务器
python scripts/dev.py server

# 运行测试
python scripts/dev.py test

# 代码检查
python scripts/dev.py lint

# 格式化代码
python scripts/dev.py format

# 类型检查
python scripts/dev.py type-check

# 运行所有检查
python scripts/dev.py check
```

### Makefile 命令

```bash
# 安装依赖
make install

# 开发模式启动
make dev

# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format

# 类型检查
make type-check

# 构建 Docker 镜像
make build

# 运行 Docker 容器
make run
```

## API 端点

### 健康检查

```bash
curl http://localhost:8080/health
```

### 迷宫管理

```bash
# 创建迷宫
curl -X POST http://localhost:8080/api/v1/mazes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试迷宫",
    "description": "这是一个测试迷宫",
    "size": 10,
    "theme": "health",
    "difficulty": "easy",
    "is_public": true
  }'

# 获取迷宫列表
curl http://localhost:8080/api/v1/mazes

# 获取迷宫详情
curl http://localhost:8080/api/v1/mazes/{maze_id}

# 删除迷宫
curl -X DELETE http://localhost:8080/api/v1/mazes/{maze_id}
```

## 配置说明

### 环境变量

```bash
# 应用配置
APP_NAME=corn-maze-service
APP_VERSION=0.2.0
ENVIRONMENT=development

# 服务端口
HTTP_PORT=8080
GRPC_PORT=50051
PROMETHEUS_PORT=8000

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./corn_maze.db
REDIS_URL=redis://localhost:6379

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 迷宫配置
MAZE_MAX_SIZE=100
MAZE_MIN_SIZE=5
MAZE_DEFAULT_DIFFICULTY=medium
```

### 配置文件

项目使用 Pydantic Settings 进行配置管理，支持：

- 环境变量
- `.env` 文件
- 默认值
- 类型验证

## 项目结构

```
corn_maze_service/
├── __init__.py                 # 包初始化
├── config/                     # 配置管理
│   ├── __init__.py
│   └── settings.py            # 设置类
├── pkg/                       # 共享包
│   ├── __init__.py
│   └── logging.py            # 日志配置
├── cmd/                       # 命令行入口
│   └── server/
│       ├── __init__.py
│       └── main.py           # 服务器主程序
└── internal/                  # 内部模块
    ├── __init__.py
    ├── delivery/              # 交付层
    │   ├── __init__.py
    │   ├── http.py           # HTTP API
    │   └── grpc.py           # gRPC 服务
    └── model/                 # 数据模型
        ├── __init__.py
        └── maze.py           # 迷宫模型
```

## 开发工作流

### 1. 功能开发

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发代码
# 编辑相关文件...

# 3. 运行测试
python scripts/dev.py test

# 4. 代码检查
python scripts/dev.py check

# 5. 提交代码
git add .
git commit -m "feat: add new feature"

# 6. 推送分支
git push origin feature/new-feature
```

### 2. 测试驱动开发

```bash
# 1. 编写测试
vim tests/test_new_feature.py

# 2. 运行测试（应该失败）
python scripts/dev.py test

# 3. 实现功能
vim corn_maze_service/...

# 4. 运行测试（应该通过）
python scripts/dev.py test

# 5. 重构代码
# 优化实现...

# 6. 再次测试
python scripts/dev.py test
```

### 3. 代码质量检查

```bash
# 运行所有检查
python scripts/dev.py check

# 单独运行各项检查
python scripts/dev.py lint      # 代码风格检查
python scripts/dev.py type-check # 类型检查
python scripts/dev.py test      # 单元测试
```

## 故障排除

### 常见问题

#### 1. UV 安装失败

```bash
# 检查 Python 版本
python --version

# 重新安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 依赖安装失败

```bash
# 清理缓存
uv cache clean

# 重新安装
uv sync --dev
```

#### 3. 测试失败

```bash
# 查看详细错误信息
python scripts/dev.py test -v

# 运行特定测试
uv run pytest tests/test_config.py -v
```

#### 4. 服务启动失败

```bash
# 检查端口占用
lsof -i :8080

# 查看日志
python scripts/dev.py server
```

### 调试技巧

#### 1. 启用调试日志

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG

# 启动服务
python scripts/dev.py server
```

#### 2. 使用 Python 调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

#### 3. 查看测试覆盖率

```bash
# 生成覆盖率报告
uv run pytest --cov=corn_maze_service --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t corn-maze-service .

# 运行容器
docker run -p 8080:8080 -p 50051:50051 corn-maze-service
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/

# 查看状态
kubectl get pods -l app=corn-maze-service
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写单元测试
- 更新文档

### 提交信息格式

```
type(scope): description

[optional body]

[optional footer]
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建

## 获取帮助

- 查看文档：`docs/`
- 提交 Issue：GitHub Issues
- 联系团队：dev@suokelife.com

## 许可证

本项目采用专有许可证，仅供"索克生活"项目内部使用。 