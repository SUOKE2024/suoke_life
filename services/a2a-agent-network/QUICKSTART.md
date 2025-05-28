# 🚀 A2A 智能体网络微服务 - 快速开始指南

本指南将帮助您在 5 分钟内启动并运行 A2A 智能体网络微服务。

## 📋 前置条件

确保您的系统已安装：

- **Python 3.13.3+** 
- **UV 包管理器**
- **Git**

## 🔧 1. 安装 UV 包管理器

如果您还没有安装 UV，请运行：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证安装
uv --version
```

## 📥 2. 获取代码

```bash
# 克隆项目（如果还没有）
git clone https://github.com/suoke-life/suoke-life.git
cd suoke-life/services/a2a-agent-network

# 或者如果您已经在项目目录中
cd services/a2a-agent-network
```

## ⚡ 3. 一键设置开发环境

使用我们的 Makefile 快速设置：

```bash
# 创建虚拟环境、安装依赖、配置 pre-commit
make setup-dev
```

或者手动设置：

```bash
# 创建虚拟环境
uv venv .venv --python 3.13.3

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
uv pip install -e ".[dev,monitoring]"

# 安装 pre-commit hooks
pre-commit install
```

## 🔧 4. 配置服务

```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 编辑配置（可选，默认配置可以直接使用）
vim config/config.yaml
```

## 🚀 5. 启动服务

### 方式一：使用 Makefile（推荐）

```bash
# 开发模式启动
make run-dev
```

### 方式二：使用启动脚本

```bash
# 使用启动脚本
./scripts/start.sh --install-deps
```

### 方式三：直接运行

```bash
# 直接运行 Python
python cmd/server/main.py
```

## ✅ 6. 验证服务

打开新的终端窗口，运行以下命令验证服务：

```bash
# 健康检查
curl http://localhost:5000/health

# 查看指标
curl http://localhost:5000/metrics

# 或使用 Makefile
make health
make metrics
```

预期输出：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "agents": {
    "connected": 0,
    "total": 4
  }
}
```

## 🧪 7. 运行测试

```bash
# 运行所有测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 运行代码质量检查
make check-all
```

## 🐳 8. Docker 部署（可选）

如果您更喜欢使用 Docker：

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run

# 查看日志
make docker-logs
```

## 📊 9. 监控和管理

### 查看日志

```bash
# 查看应用日志
make logs

# 实时查看日志
tail -f logs/app.log
```

### 性能监控

```bash
# 查看系统指标
make metrics

# 查看服务状态
make health
```

## 🔧 10. 开发工具

### 代码格式化

```bash
# 格式化代码
make format
```

### 代码检查

```bash
# 运行 linter
make lint

# 类型检查
make type-check

# 安全检查
make security
```

### 运行演示

```bash
# 运行演示脚本
make demo
```

## 🚨 常见问题

### Q: UV 安装失败
**A:** 确保您有网络连接，并且系统支持 UV。对于企业网络，可能需要配置代理。

### Q: Python 版本不匹配
**A:** 确保安装了 Python 3.13.3+：
```bash
python --version
# 如果版本不对，请安装正确版本的 Python
```

### Q: 依赖安装失败
**A:** 尝试清理缓存并重新安装：
```bash
uv cache clean
uv sync --reinstall
```

### Q: 端口被占用
**A:** 修改配置文件中的端口，或停止占用端口的进程：
```bash
# 查看端口占用
lsof -i :5000

# 修改配置文件
vim config/config.yaml
```

### Q: 服务启动失败
**A:** 检查日志文件：
```bash
# 查看错误日志
cat logs/app.log

# 或使用详细模式启动
python cmd/server/main.py --debug
```

## 📚 下一步

现在您的 A2A 智能体网络微服务已经运行起来了！接下来您可以：

1. **阅读完整文档**: [README.md](README.md)
2. **查看 API 文档**: [docs/API.md](docs/API.md)
3. **了解架构设计**: [docs/architecture.md](docs/architecture.md)
4. **配置智能体**: 连接四个核心智能体服务
5. **部署到生产**: [docs/deployment.md](docs/deployment.md)

## 🆘 获取帮助

如果您遇到问题：

1. 查看 [故障排除文档](docs/troubleshooting.md)
2. 搜索 [GitHub Issues](https://github.com/suoke-life/a2a-agent-network/issues)
3. 创建新的 Issue
4. 联系开发团队

---

**恭喜！** 🎉 您已成功启动 A2A 智能体网络微服务！ 