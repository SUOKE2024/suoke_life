# 老克智能体服务 (Laoke Service)

> 索克生活平台的知识传播和社区管理智能体

[![Python](https://img.shields.io/badge/Python-3.13.3+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5+-green.svg)](https://fastapi.tiangolo.com)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-orange.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目简介

老克智能体是索克生活平台的核心智能体之一，专注于中医知识传播、学习路径规划和社区内容管理。它基于现代化的 Python 技术栈构建，采用 FastAPI 框架，支持异步处理和高并发访问。

### 🎯 核心功能

- **知识内容管理**: 管理中医知识内容，包括内容创建、编辑、分类和质量控制
- **学习路径规划**: 为用户规划个性化的中医学习路径，包括课程安排和进度跟踪
- **社区内容管理**: 管理社区内容，包括内容审核、用户互动和社区活动组织
- **中医知识问答**: 回答用户的中医相关问题，提供专业的知识解答和建议
- **内容推荐**: 基于用户兴趣和学习历史推荐个性化的学习内容

### 🏗️ 技术架构

- **Web框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + Redis
- **AI集成**: OpenAI GPT-4, Anthropic Claude
- **向量数据库**: ChromaDB
- **监控**: Prometheus + Grafana
- **日志**: Loguru + Structlog
- **包管理**: UV (Python 3.13.3+)

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV 包管理器
- PostgreSQL 12+
- Redis 6+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/agent-services/laoke-service
```

2. **安装 UV 包管理器**（如果未安装）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

3. **创建虚拟环境并安装依赖**
```bash
uv venv --python 3.13
uv sync --extra dev --extra performance --extra monitoring
```

4. **配置环境**
```bash
# 复制配置文件
cp config/config.example.yaml config/config.yaml

# 或者使用环境变量（推荐开发环境）
cp .env.example .env
```

5. **启动服务**
```bash
# 开发环境快速启动
./scripts/dev.sh

# 或者使用完整启动脚本
./scripts/start.sh --reload
```

### 🔧 开发环境设置

使用开发脚本可以快速启动开发环境：

```bash
./scripts/dev.sh
```

这个脚本会：
- 自动检查 Python 和 UV 环境
- 安装所有开发依赖
- 创建基础配置文件
- 启动开发服务器（支持热重载）

## 📚 使用指南

### CLI 工具

项目提供了强大的命令行工具：

```bash
# 查看帮助
uv run laoke-cli --help

# 配置管理
uv run laoke-cli config show          # 显示当前配置
uv run laoke-cli config validate      # 验证配置
uv run laoke-cli config export        # 导出配置模板

# 智能体管理
uv run laoke-cli agent status         # 检查智能体状态
uv run laoke-cli agent test -m "你好"  # 测试智能体响应

# 数据库管理
uv run laoke-cli db init              # 初始化数据库
uv run laoke-cli db migrate           # 执行数据库迁移
uv run laoke-cli db status            # 检查数据库状态

# 启动服务
uv run laoke-cli serve --reload       # 启动开发服务器
```

### API 接口

服务启动后，可以访问以下接口：

- **API 文档**: http://localhost:8080/docs
- **健康检查**: http://localhost:8080/health
- **监控指标**: http://localhost:8080/metrics

#### 主要 API 端点

```bash
# 聊天接口
POST /api/v1/chat
{
  "message": "什么是阴阳学说？",
  "message_type": "knowledge_query"
}

# 知识搜索
POST /api/v1/knowledge/search
{
  "query": "中医基础理论",
  "category": "中医基础理论",
  "limit": 10
}

# 学习计划
POST /api/v1/learning/plan
{
  "goal": "中医入门",
  "current_level": "初级",
  "available_time": "30分钟/天"
}

# 社区帖子
GET /api/v1/community/posts?category=学习交流&limit=10
```

### 配置说明

#### 环境变量配置

```bash
# 基础配置
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DATABASE__POSTGRES_HOST=localhost
DATABASE__POSTGRES_PASSWORD=your_password
DATABASE__REDIS_HOST=localhost

# AI 配置
AI__OPENAI_API_KEY=your_openai_key
AI__ANTHROPIC_API_KEY=your_anthropic_key

# 安全配置
SECURITY__JWT_SECRET_KEY=your_jwt_secret
```

#### YAML 配置文件

详细配置请参考 `config/config.example.yaml`。

## 🧪 测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest test/unit/

# 运行集成测试
uv run pytest test/integration/

# 生成覆盖率报告
uv run pytest --cov=laoke_service --cov-report=html
```

## 📊 监控和日志

### 日志

服务使用结构化日志，支持多种输出格式：

```bash
# 查看实时日志
tail -f logs/laoke-service.log

# 使用 CLI 工具查看日志
uv run laoke-cli logs --follow
```

### 监控指标

- **Prometheus 指标**: http://localhost:8080/metrics
- **健康检查**: http://localhost:8080/health/ready
- **存活检查**: http://localhost:8080/health/live

## 🔧 开发工具

### 代码质量

```bash
# 代码格式化
uv run black .
uv run isort .

# 代码检查
uv run ruff check .
uv run mypy .

# 安全检查
uv run bandit -r laoke_service/
uv run safety check
```

### 性能分析

```bash
# 内存分析
uv run memory-profiler laoke_service/cmd/server/main.py

# 性能分析
uv run py-spy record -o profile.svg -- python -m laoke_service.cmd.server.main
```

## 📦 部署

### Docker 部署

```bash
# 构建镜像
docker build -t laoke-service:latest .

# 运行容器
docker run -p 8080:8080 -e ENVIRONMENT=production laoke-service:latest
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 添加类型注解
- 编写单元测试
- 更新文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- **文档**: https://docs.suoke.life/laoke-service
- **问题反馈**: https://github.com/SUOKE2024/suoke_life/issues
- **讨论**: https://github.com/SUOKE2024/suoke_life/discussions

## 🙏 致谢

感谢所有为索克生活项目做出贡献的开发者和用户！

---

**索克生活团队** ❤️ **开源** 