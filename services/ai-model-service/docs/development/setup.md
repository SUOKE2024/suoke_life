# 开发环境搭建

本指南将帮助您快速搭建AI Model Service的开发环境。

## 🔧 环境要求

### 系统要求
- **操作系统**: Linux, macOS, Windows (推荐 Linux/macOS)
- **Python**: 3.13+ (推荐使用最新版本)
- **内存**: 最少 8GB RAM (推荐 16GB+)
- **存储**: 最少 10GB 可用空间

### 必需软件

#### 1. Python 3.13+
```bash
# macOS (使用 Homebrew)
brew install python@3.13

# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# CentOS/RHEL
sudo dnf install python3.13 python3.13-venv python3.13-devel
```

#### 2. UV 包管理器
```bash
# 安装 UV (推荐方式)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip 安装
pip install uv

# 验证安装
uv --version
```

#### 3. Git
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo dnf install git
```

#### 4. Docker (可选，用于容器化测试)
```bash
# macOS
brew install docker

# Ubuntu
sudo apt install docker.io docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

#### 5. Kubernetes 工具 (可选，用于 K8s 开发)
```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# minikube (本地 K8s 集群)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

## 📥 获取源代码

### 克隆仓库
```bash
# 克隆主仓库
git clone https://github.com/suoke-life/suoke_life.git
cd suoke_life/services/ai-model-service

# 或者只克隆 ai-model-service 子目录
git clone --filter=blob:none --sparse https://github.com/suoke-life/suoke_life.git
cd suoke_life
git sparse-checkout set services/ai-model-service
cd services/ai-model-service
```

### 检查项目结构
```bash
# 查看项目结构
tree -L 3
# 或
ls -la
```

## 🚀 快速开始

### 1. 自动化设置 (推荐)
```bash
# 使用开发脚本自动设置环境
./scripts/dev.sh setup
```

这个命令会自动完成以下操作：
- 检查并安装 UV 包管理器
- 创建 Python 虚拟环境
- 安装所有开发依赖
- 配置 pre-commit 钩子

### 2. 手动设置

#### 创建虚拟环境
```bash
# 使用 UV 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

#### 安装依赖
```bash
# 安装所有依赖（包括开发依赖）
uv sync --dev

# 或者分别安装
uv sync                    # 生产依赖
uv add --dev pytest black mypy  # 开发依赖
```

#### 验证安装
```bash
# 检查 Python 版本
python --version

# 检查已安装的包
uv pip list

# 运行测试验证环境
./scripts/dev.sh test
```

## ⚙️ 配置开发环境

### 1. 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

### 2. 配置文件设置
```bash
# 复制配置文件模板
cp config/config.example.yaml config/config.yaml

# 编辑配置文件
vim config/config.yaml
```

### 3. IDE 配置

#### VS Code 配置
创建 `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

创建 `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: AI Model Service",
      "type": "python",
      "request": "launch",
      "program": "src/ai_model_service/main.py",
      "args": ["--dev"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  ]
}
```

#### PyCharm 配置
1. 打开项目目录
2. 设置 Python 解释器为 `.venv/bin/python`
3. 配置代码格式化工具：
   - File → Settings → Tools → External Tools
   - 添加 Black、isort、MyPy 工具

### 4. Git 配置

#### Pre-commit 钩子
```bash
# 安装 pre-commit
uv add --dev pre-commit

# 安装钩子
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

#### Git 忽略文件
确保 `.gitignore` 包含以下内容：
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

## 🧪 验证开发环境

### 1. 运行测试
```bash
# 运行所有测试
./scripts/dev.sh test

# 运行特定测试
./scripts/dev.sh test tests/unit/test_models.py

# 运行测试并生成覆盖率报告
./scripts/dev.sh test-cov
```

### 2. 代码质量检查
```bash
# 运行所有检查
./scripts/dev.sh check-all

# 单独运行各项检查
./scripts/dev.sh lint        # 代码检查
./scripts/dev.sh type-check  # 类型检查
./scripts/dev.sh security    # 安全检查
```

### 3. 启动开发服务器
```bash
# 开发模式启动
./scripts/dev.sh dev

# 手动启动
source .venv/bin/activate
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python -m ai_model_service.main --dev
```

### 4. 测试 API
```bash
# 健康检查
curl http://localhost:8080/api/v1/health/

# 查看 API 文档
open http://localhost:8080/docs
```

## 🔧 开发工具

### 1. 代码格式化
```bash
# 自动格式化代码
./scripts/dev.sh format

# 手动运行工具
uv run black src tests
uv run isort src tests
uv run ruff check --fix src tests
```

### 2. 类型检查
```bash
# 运行 MyPy 类型检查
./scripts/dev.sh type-check

# 手动运行
uv run mypy src
```

### 3. 安全检查
```bash
# 运行安全检查
./scripts/dev.sh security

# 手动运行
uv run bandit -r src
```

### 4. 性能分析
```bash
# 安装性能分析工具
uv add --dev py-spy line_profiler memory_profiler

# 使用 py-spy 分析运行中的进程
py-spy record -o profile.svg -- python -m ai_model_service.main

# 使用 line_profiler 分析特定函数
kernprof -l -v script.py
```

## 🐳 Docker 开发环境

### 1. 构建开发镜像
```bash
# 构建镜像
./scripts/dev.sh build

# 手动构建
docker build -t ai-model-service:dev .
```

### 2. 运行开发容器
```bash
# 运行容器
docker run -it --rm \
  -p 8080:8080 \
  -v $(pwd):/app \
  -v ~/.kube:/root/.kube \
  ai-model-service:dev bash

# 在容器内开发
cd /app
./scripts/dev.sh setup
./scripts/dev.sh dev
```

### 3. Docker Compose 开发
创建 `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  ai-model-service:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app
      - ~/.kube:/root/.kube
    environment:
      - PYTHONPATH=/app/src
      - ENVIRONMENT=development
    command: ["./scripts/dev.sh", "dev"]
```

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up
```

## ☸️ Kubernetes 开发环境

### 1. 本地 Kubernetes 集群
```bash
# 启动 minikube
minikube start

# 配置 kubectl
kubectl config use-context minikube

# 验证集群
kubectl cluster-info
```

### 2. 部署到本地集群
```bash
# 构建镜像并加载到 minikube
eval $(minikube docker-env)
docker build -t ai-model-service:dev .

# 部署到集群
kubectl apply -f deploy/kubernetes/

# 查看部署状态
kubectl get pods -l app=ai-model-service
```

### 3. 端口转发
```bash
# 转发服务端口
kubectl port-forward svc/ai-model-service 8080:8080

# 测试服务
curl http://localhost:8080/api/v1/health/
```

## 🚨 常见问题

### 1. Python 版本问题
```bash
# 检查 Python 版本
python --version

# 如果版本不对，使用 pyenv 管理多版本
curl https://pyenv.run | bash
pyenv install 3.13.0
pyenv local 3.13.0
```

### 2. 依赖安装失败
```bash
# 清理缓存
uv cache clean

# 重新安装
rm -rf .venv
uv venv
uv sync --dev
```

### 3. 测试失败
```bash
# 检查环境变量
echo $PYTHONPATH

# 设置正确的 PYTHONPATH
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 重新运行测试
./scripts/dev.sh test
```

### 4. 端口冲突
```bash
# 检查端口占用
lsof -i :8080

# 杀死占用进程
kill -9 <PID>

# 或使用不同端口
export PORT=8081
./scripts/dev.sh dev
```

## 📚 下一步

环境搭建完成后，您可以：

1. 阅读 [代码规范](standards.md)
2. 查看 [测试指南](testing.md)
3. 了解 [贡献流程](contributing.md)
4. 开始开发新功能！

## 🆘 获取帮助

如果遇到问题，可以：

1. 查看 [故障排除指南](../operations/troubleshooting.md)
2. 搜索 [GitHub Issues](https://github.com/suoke-life/suoke_life/issues)
3. 提交新的 [Issue](https://github.com/suoke-life/suoke_life/issues/new)
4. 联系开发团队：dev@suoke.life