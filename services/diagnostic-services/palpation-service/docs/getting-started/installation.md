# 安装指南

本指南将帮助您在本地环境中安装和配置触诊服务。

## 系统要求

### 硬件要求

- **CPU**: 2核心以上（推荐4核心）
- **内存**: 4GB以上（推荐8GB）
- **存储**: 10GB可用空间
- **网络**: 稳定的互联网连接

### 软件要求

- **操作系统**: 
  - Linux (Ubuntu 20.04+, CentOS 8+)
  - macOS 12.0+
  - Windows 10+ (WSL2推荐)
- **Python**: 3.13.3+
- **UV**: 最新版本
- **Git**: 2.0+

### 外部依赖

- **Redis**: 6.0+ (用于缓存)
- **PostgreSQL**: 13.0+ (用于数据存储)

## 安装步骤

### 1. 安装Python 3.13.3

#### Ubuntu/Debian

```bash
# 添加deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 安装Python 3.13
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### macOS

```bash
# 使用Homebrew
brew install python@3.13

# 或使用pyenv
pyenv install 3.13.3
pyenv global 3.13.3
```

#### Windows

从[Python官网](https://www.python.org/downloads/)下载并安装Python 3.13.3。

### 2. 安装UV包管理器

```bash
# 使用pip安装
pip install uv

# 或使用curl安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 3. 安装Redis

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS

```bash
brew install redis
brew services start redis
```

#### Docker方式

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 4. 安装PostgreSQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE palpation_service;
CREATE USER palpation_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE palpation_service TO palpation_user;
\q
```

#### macOS

```bash
brew install postgresql
brew services start postgresql

# 创建数据库
createdb palpation_service
```

#### Docker方式

```bash
docker run -d --name postgres \
  -e POSTGRES_DB=palpation_service \
  -e POSTGRES_USER=palpation_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15-alpine
```

### 5. 克隆项目

```bash
git clone https://github.com/suokelife/suoke_life.git
cd suoke_life/services/diagnostic-services/palpation-service
```

### 6. 安装项目依赖

```bash
# 安装开发依赖
make install-dev

# 或直接使用uv
uv sync
```

### 7. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 服务配置
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
SERVICE_DEBUG=true

# 数据库配置
DATABASE_URL=postgresql://palpation_user:your_password@localhost:5432/palpation_service

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/palpation_service.log

# AI模型配置
MODEL_PATH=models/
ENABLE_GPU=false

# 监控配置
METRICS_PORT=9090
ENABLE_METRICS=true
```

### 8. 初始化数据库

```bash
# 运行数据库迁移
make migrate

# 或手动运行
uv run alembic upgrade head
```

### 9. 验证安装

```bash
# 运行测试
make test

# 启动服务
make run-dev
```

访问以下URL验证服务：

- 服务状态: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## Docker安装

如果您偏好使用Docker，可以使用以下方式快速启动：

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f palpation-service

# 停止服务
docker-compose down
```

### 单独构建Docker镜像

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run
```

## 故障排除

### 常见问题

#### 1. Python版本问题

```bash
# 检查Python版本
python3.13 --version

# 如果命令不存在，创建软链接
sudo ln -s /usr/bin/python3.13 /usr/local/bin/python3.13
```

#### 2. UV安装失败

```bash
# 清理缓存
uv cache clean

# 重新安装
pip install --upgrade uv
```

#### 3. Redis连接失败

```bash
# 检查Redis状态
redis-cli ping

# 如果返回PONG，说明Redis正常运行
```

#### 4. PostgreSQL连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U palpation_user -d palpation_service
```

#### 5. 端口冲突

如果8000端口被占用，可以修改配置：

```bash
# 修改.env文件中的端口
SERVICE_PORT=8001

# 或使用环境变量
export SERVICE_PORT=8001
make run-dev
```

### 获取帮助

如果遇到其他问题，请：

1. 查看[故障排除文档](../troubleshooting.md)
2. 检查[GitHub Issues](https://github.com/suokelife/suoke_life/issues)
3. 联系开发团队：dev@suokelife.com

## 下一步

安装完成后，您可以：

- 阅读[配置指南](configuration.md)了解详细配置
- 查看[运行指南](running.md)学习如何运行服务
- 浏览[API文档](../api/overview.md)了解接口使用 