# 索克生活 Agent Services

> 由人工智能智能体驱动的现代化健康管理平台 - 微服务架构

[![Python](https://img.shields.io/badge/Python-3.13.3-blue.svg)](https://python.org)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-green.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)](https://github.com/astral-sh/ruff)
[![MyPy](https://img.shields.io/badge/Type%20Checker-MyPy-blue.svg)](http://mypy-lang.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

[![GitHub Stars](https://img.shields.io/github/stars/SUOKE2024/suoke_life?style=social)](https://github.com/SUOKE2024/suoke_life/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/SUOKE2024/suoke_life?style=social)](https://github.com/SUOKE2024/suoke_life/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/SUOKE2024/suoke_life)](https://github.com/SUOKE2024/suoke_life/issues)
[![GitHub License](https://img.shields.io/github/license/SUOKE2024/suoke_life)](https://github.com/SUOKE2024/suoke_life/blob/main/LICENSE)

## 🌟 项目概述

索克生活（Suoke Life）是一个将中医"辨证论治未病"理念与现代预防医学技术相结合的健康管理平台。该平台由四个独立的智能体微服务组成，通过自我学习和进化，为用户提供个性化的全生命周期健康管理服务。

> 🔗 **完整项目**: 本文档介绍的是 [索克生活主项目](https://github.com/SUOKE2024/suoke_life) 中的智能体代理服务部分。查看 [主仓库](https://github.com/SUOKE2024/suoke_life) 了解完整的平台架构和其他服务组件。

### 🤖 四大智能体代理服务

| 服务 | 智能体代理 | 频道职责 | 核心功能 | 端口 | 状态 |
|------|------------|----------|----------|------|------|
| **xiaoai-service** | 小艾 | 首页聊天频道版主 | 五诊合参、语音交互、无障碍服务 | 8001 | ✅ 生产就绪 |
| **xiaoke-service** | 小克 | SUOKE频道版主 | 服务订阅、供应链管理、API集成 | 8002 | ✅ 生产就绪 |
| **laoke-service** | 老克 | 探索频道版主 | 知识传播、社区管理、游戏NPC | 8003 | ✅ 生产就绪 |
| **soer-service** | 索儿 | LIFE频道版主 | 生活管理、健康陪伴、数据整合 | 8004 | ✅ 生产就绪 |

#### 🎯 智能体代理详细功能

##### 🗣️ 智能体代理小艾（xiaoai）- 首页聊天频道版主
> **定位**: 索克生活APP首页智能医疗助手，专注中医五诊合参与无障碍服务

**核心功能**:
- **五诊合参服务**: 
  - 🔍 **望诊**: 面色分析与舌诊图像处理
  - 👂 **闻诊**: 语音特征分析与呼吸音识别  
  - 💬 **问诊**: 智能问诊系统（体质筛查、症状评估、健康咨询）
  - ✋ **切诊**: 脉象数据分析与体征监测
  - 🧮 **算诊**: 综合诊断算法与健康评估
- **智能交互**: 实时自然语音交互与多语种支持（含方言识别）
- **无障碍服务**: 导盲、手语识别、老年友好界面等
- **健康档案**: 医疗记录自动整理与健康档案管理

**技术实现**:
- 多模态大语言模型 (GPT-4o/Gemini 1.5 Pro) 实现跨模态理解
- 轻量级本地模型 (Llama 3-8B) 支持离线基础会话
- 视觉识别组件用于舌象、面色分析
- 与健康档案系统和五诊合参模块深度集成

##### 🛒 智能体代理小克（xiaoke）- SUOKE频道版主  
> **定位**: 索克生活服务生态管理者，专注服务订阅与供应链整合

**核心功能**:
- **服务订阅**: 索克生活服务订阅与个性化推荐
- **医疗资源**: 名医资源智能匹配与预约管理
- **供应链管理**: 优质农产品预（定）制与溯源管理
- **API集成**: 第三方医疗服务API集成（保险、支付、物流）
- **店铺管理**: 在线店铺管理与健康商品推荐

**技术实现**:
- 推荐算法结合用户体质特征和历史偏好
- RCM（收入周期管理）系统集成处理预约与支付
- 区块链技术实现农产品溯源与真实性验证
- 多平台API网关实现第三方服务无缝接入

##### 📚 智能体代理老克（laoke）- 探索频道版主
> **定位**: 中医知识传承者与社区文化建设者，兼任索克游戏NPC

**核心功能**:
- **知识传播**: 中医知识库RAG检索与个性化学习路径
- **社区管理**: 社区内容管理与知识贡献奖励
- **教育培训**: 健康教育课程与认证系统
- **游戏NPC**: 玉米迷宫NPC角色扮演与游戏引导
- **博客管理**: 用户博客管理与内容质量保障

**技术实现**:
- 知识图谱与检索增强生成(RAG)系统
- 用户学习进度追踪与个性化推荐算法
- 基于AR/VR的游戏角色生成与互动系统
- 内容审核与知识安全校验机制

##### 🌱 智能体代理索儿（soer）- LIFE频道版主
> **定位**: 生活健康管理专家，专注个性化健康陪伴与数据整合

**核心功能**:
- **生活管理**: 健康生活习惯培养与行为干预（饮食、运动、睡眠）
- **数据整合**: 多设备传感器数据整合与健康趋势分析
- **智能感知**: 环境与情绪智能感知与动态健康建议
- **养生计划**: 个性化养生计划生成与执行跟踪
- **健康陪伴**: 身心健康陪伴与情感支持（压力管理、情绪疏导）

**技术实现**:
- 多源异构数据融合系统处理各类传感器输入
- 边缘计算实现本地健康数据分析与隐私保护
- 强化学习模型优化个性化健康建议
- 情感计算结合语音、文本、生理信号识别用户情绪状态

> 📊 **详细功能对比**: 查看 [智能体代理功能对比表](AGENT_FEATURES_COMPARISON.md) 了解四大智能体的详细功能矩阵、技术实现对比和开发优先级建议。

## 🏗️ 技术架构

### 核心技术栈

#### 🔧 基础架构
- **语言**: Python 3.13.3
- **包管理**: UV (现代化 Python 包管理器)
- **Web 框架**: FastAPI
- **代码质量**: Ruff (格式化 + 检查) + MyPy (类型检查)
- **测试框架**: pytest
- **容器化**: Docker + Kubernetes

#### 🧠 AI/ML 技术栈
- **大语言模型**: GPT-4o, Gemini 1.5 Pro, Llama 3-8B
- **多模态处理**: 视觉识别、语音处理、自然语言理解
- **机器学习**: scikit-learn, PyTorch, TensorFlow
- **知识图谱**: Neo4j + RAG (检索增强生成)
- **推荐系统**: 协同过滤 + 内容推荐算法

#### 💾 数据存储
- **关系数据库**: PostgreSQL (用户数据、医疗记录)
- **缓存系统**: Redis (会话缓存、实时数据)
- **时序数据库**: InfluxDB (传感器数据、健康指标)
- **文档数据库**: MongoDB (非结构化数据)
- **区块链**: 农产品溯源与数据验证

#### 🔗 集成与通信
- **消息队列**: 内存事件总线
- **API 网关**: Kong + 自定义网关
- **服务发现**: Consul + etcd
- **边缘计算**: 本地AI推理引擎

### 项目特性

#### 🤖 智能体代理特性
- 🧠 **多模态AI交互**: 支持语音、图像、文本的跨模态理解
- 🔍 **中医五诊合参**: 望闻问切算五诊智能化实现
- 🌐 **多语种支持**: 包含方言识别的自然语言处理
- ♿ **无障碍服务**: 导盲、手语识别、老年友好界面
- 🎮 **游戏化体验**: AR/VR游戏NPC与健康教育结合
- 💡 **个性化推荐**: 基于体质特征的智能推荐系统

#### 🏗️ 技术架构特性
- 🚀 **现代化开发工具链**: 使用 UV、Ruff、MyPy 等最新工具
- 🔧 **标准化开发流程**: 统一的 Makefile 和开发命令
- 📦 **微服务架构**: 独立部署、水平扩展
- 🧪 **完整测试覆盖**: 单元测试 + 集成测试
- 🐳 **容器化部署**: Docker + Kubernetes 支持
- 📊 **代码质量保证**: 自动化代码检查和格式化
- 🔒 **类型安全**: 完整的 MyPy 类型检查

#### 🔐 数据安全特性
- 🛡️ **隐私保护**: 边缘计算实现本地数据处理
- 🔗 **区块链溯源**: 农产品真实性验证
- 🔐 **零知识验证**: 健康数据隐私保护
- 📱 **多设备同步**: 安全的跨设备数据同步

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV 包管理器
- Docker (可选)
- Make

### 安装 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 克隆项目

```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/agent-services
```

### 服务开发

选择任一服务进行开发：

```bash
# 进入服务目录
cd xiaoai-service  # 或其他服务

# 查看可用命令
make help

# 环境搭建
make setup

# 启动开发服务器
make dev
```

## 📋 开发指南

### 标准化开发流程

每个服务都支持统一的开发命令：

```bash
# 环境管理
make install      # 安装核心依赖
make install-dev  # 安装开发依赖
make setup        # 完整环境搭建
make clean        # 清理临时文件

# 代码质量
make format       # 格式化代码 (ruff format)
make lint         # 代码检查 (ruff check)
make typecheck    # 类型检查 (mypy)

# 测试
make test         # 运行所有测试
make test-unit    # 运行单元测试
make test-integration  # 运行集成测试

# 开发服务器
make dev          # 启动开发服务器

# 构建和部署
make build        # 构建 Python 包
make docker-build # 构建 Docker 镜像
make docker-run   # 运行 Docker 容器

# 快捷命令组合
make pre-commit   # 预提交检查 (format + lint + typecheck)
make ci           # 持续集成检查 (lint + typecheck + test)
```

### 代码规范

#### 格式化和检查

```bash
# 自动格式化代码
make format

# 检查代码质量
make lint

# 类型检查
make typecheck
```

#### 配置文件

所有服务使用统一的工具配置：

```toml
# pyproject.toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.mypy]
python_version = "3.13"
strict = true
```

### 项目结构

```
services/agent-services/
├── xiaoai-service/          # 小艾智能体服务
│   ├── xiaoai/             # 源代码
│   ├── tests/              # 测试代码
│   ├── pyproject.toml      # 项目配置
│   ├── Makefile           # 开发命令
│   └── Dockerfile         # 容器配置
├── xiaoke-service/         # 小克智能体服务
├── laoke-service/          # 老克智能体服务
├── soer-service/           # 索儿智能体服务
└── README.md              # 本文档
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
make test

# 运行特定类型的测试
make test-unit
make test-integration

# 查看测试覆盖率
make test  # 会生成 htmlcov/ 目录
```

### 测试结构

```
tests/
├── unit/                   # 单元测试
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/            # 集成测试
│   ├── test_api.py
│   └── test_database.py
└── conftest.py            # 测试配置
```

## 🐳 Docker 部署

### 构建镜像

```bash
# 构建单个服务
cd xiaoai-service
make docker-build

# 或使用 docker-compose (在根目录)
docker-compose build xiaoai-service
```

### 运行容器

```bash
# 运行单个服务
make docker-run

# 或使用 docker-compose 运行所有服务
docker-compose up -d
```

### 环境变量

每个智能体代理服务支持以下环境变量：

```bash
# 基础配置
APP_NAME=xiaoai-service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=info
AGENT_NAME=xiaoai  # 智能体代理名称

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/suoke_life
INFLUXDB_URL=http://localhost:8086
NEO4J_URL=bolt://localhost:7687

# API 配置
API_HOST=0.0.0.0
API_PORT=8001
API_PREFIX=/api/v1

# AI/ML 配置
OPENAI_API_KEY=your-openai-key
GOOGLE_AI_API_KEY=your-google-ai-key
LOCAL_MODEL_PATH=/models/llama3-8b
ENABLE_LOCAL_INFERENCE=true

# 智能体特定配置
# 小艾 (xiaoai) - 五诊合参
VISION_MODEL_ENDPOINT=http://vision-service:8080
VOICE_RECOGNITION_ENDPOINT=http://voice-service:8081
TCM_DIAGNOSIS_ENDPOINT=http://tcm-service:8082

# 小克 (xiaoke) - 服务订阅
PAYMENT_GATEWAY_URL=https://payment.example.com
SUPPLY_CHAIN_API_URL=https://supply.example.com
BLOCKCHAIN_NODE_URL=https://blockchain.example.com

# 老克 (laoke) - 知识传播
KNOWLEDGE_GRAPH_URL=http://neo4j:7474
RAG_SERVICE_URL=http://rag-service:8083
GAME_ENGINE_URL=http://game-service:8084

# 索儿 (soer) - 生活管理
IOT_DATA_ENDPOINT=http://iot-gateway:8085
EMOTION_AI_ENDPOINT=http://emotion-service:8086
HEALTH_ANALYTICS_URL=http://analytics:8087

# 安全配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-encryption-key
BLOCKCHAIN_PRIVATE_KEY=your-blockchain-key
```

## 📊 监控和日志

### 健康检查

每个服务都提供健康检查端点：

```bash
# 检查服务状态
curl http://localhost:8001/health

# 检查详细信息
curl http://localhost:8001/health/detailed
```

### 日志配置

```python
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志格式: JSON 或 TEXT
LOG_FORMAT=JSON
```

## 🔧 开发工具

### VS Code 配置

推荐的 VS Code 扩展：

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "ms-python.pytest"
  ]
}
```

### 预提交钩子

```bash
# 安装预提交钩子
pip install pre-commit
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

## 📈 性能优化

### 数据库优化

- 使用连接池
- 实施查询优化
- 添加适当的索引
- 使用 Redis 缓存

### API 优化

- 实施响应缓存
- 使用异步处理
- 添加请求限流
- 优化序列化

## 🔒 安全考虑

### 认证和授权

- JWT Token 认证
- RBAC 权限控制
- API 密钥管理
- HTTPS 强制

### 数据保护

- 敏感数据加密
- 输入验证
- SQL 注入防护
- XSS 防护

## 🤝 贡献指南

### 开发流程

1. Fork [索克生活项目](https://github.com/SUOKE2024/suoke_life)
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 [Pull Request](https://github.com/SUOKE2024/suoke_life/pulls)

### 代码审查

- 确保所有测试通过
- 代码覆盖率 > 80%
- 通过所有代码质量检查
- 更新相关文档

## 📚 API 文档

每个智能体代理服务启动后，可以访问自动生成的 API 文档：

### 🔗 通用文档入口
- **Swagger UI**: `http://localhost:800X/docs`
- **ReDoc**: `http://localhost:800X/redoc`
- **OpenAPI JSON**: `http://localhost:800X/openapi.json`

### 🤖 智能体代理专用端点

#### 小艾 (xiaoai-service:8001) - 五诊合参
```bash
# 五诊合参 API
POST /api/v1/diagnosis/wangzhen    # 望诊 - 面色舌象分析
POST /api/v1/diagnosis/wenzhen     # 闻诊 - 语音呼吸分析
POST /api/v1/diagnosis/wenzhen     # 问诊 - 智能问诊系统
POST /api/v1/diagnosis/qiezhen     # 切诊 - 脉象体征分析
POST /api/v1/diagnosis/suanzhen    # 算诊 - 综合诊断评估

# 无障碍服务 API
POST /api/v1/accessibility/guide   # 导盲导医服务
POST /api/v1/accessibility/sign    # 手语识别
GET  /api/v1/accessibility/ui      # 老年友好界面
```

#### 小克 (xiaoke-service:8002) - 服务订阅
```bash
# 服务订阅 API
GET  /api/v1/services/recommend    # 个性化服务推荐
POST /api/v1/services/subscribe    # 服务订阅管理
GET  /api/v1/doctors/match         # 名医资源匹配

# 供应链管理 API
GET  /api/v1/products/trace        # 农产品溯源
POST /api/v1/products/customize    # 产品定制
GET  /api/v1/supply/status         # 供应链状态
```

#### 老克 (laoke-service:8003) - 知识传播
```bash
# 知识传播 API
GET  /api/v1/knowledge/search      # RAG知识检索
GET  /api/v1/learning/path         # 个性化学习路径
POST /api/v1/community/content     # 社区内容管理

# 游戏NPC API
GET  /api/v1/game/npc/interact     # NPC交互
POST /api/v1/game/maze/guide       # 玉米迷宫引导
GET  /api/v1/game/ar/scene         # AR场景生成
```

#### 索儿 (soer-service:8004) - 生活管理
```bash
# 生活管理 API
POST /api/v1/lifestyle/analyze     # 生活习惯分析
GET  /api/v1/health/plan           # 个性化养生计划
POST /api/v1/sensors/data          # 传感器数据接收

# 健康陪伴 API
POST /api/v1/emotion/detect        # 情绪识别
GET  /api/v1/companion/chat        # 健康陪伴对话
POST /api/v1/intervention/suggest  # 行为干预建议
```

## 🆘 故障排除

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
make clean

# 重新安装
make setup
```

#### 3. 测试失败
```bash
# 检查测试环境
make test-unit

# 查看详细错误
uv run pytest -v --tb=long
```

### 获取帮助

- 📧 技术支持: tech@suoke.life
- 📧 用户支持: support@suoke.life
- 📧 商务合作: business@suoke.life
- 💬 讨论: [GitHub Discussions](https://github.com/SUOKE2024/suoke_life/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/SUOKE2024/suoke_life/issues)
- 🌐 官网: https://suoke.life

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](https://github.com/SUOKE2024/suoke_life/blob/main/LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为索克生活项目做出贡献的开发者和用户！

---

**索克生活团队** ❤️ 用技术传承中医智慧，用创新守护健康生活