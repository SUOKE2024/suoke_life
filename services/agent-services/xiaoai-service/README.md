# 小艾智能体服务 (XiaoAI Agent Service)

[![Python Version](https://img.shields.io/badge/python-3.13.3%2B-blue.svg)](https://python.org)
[![Development Status](https://img.shields.io/badge/status-100%25%20complete-brightgreen.svg)](PROJECT_STATUS_FINAL.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checker](https://img.shields.io/badge/type%20checker-mypy-blue.svg)](http://mypy-lang.org/)

小艾智能体服务是索克生活APP的核心AI健康管理服务，基于中医五诊协调理论，提供智能化的健康诊断、体质分析和个性化建议。

## 🌟 核心特性

- **五诊协调**: 集成望、闻、问、切、算诊五诊，提供全面的中医诊断
- **辨证分析**: 基于八纲辨证理论的智能证型分析
- **体质识别**: 九种体质类型的精准识别和分析
- **多模态处理**: 支持文本、图像、音频等多种数据类型
- **个性化建议**: 基于诊断结果生成个性化的健康建议
- **无障碍服务**: 完整的无障碍功能支持
- **高性能**: 异步架构，支持高并发处理
- **可扩展**: 模块化设计，易于扩展和维护

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                         │
├─────────────────────────────────────────────────────────────┤
│                    小艾智能体服务                            │
├─────────────────┬─────────────────┬─────────────────────────┤
│   五诊协调器     │   辨证分析器     │   体质分析器             │
├─────────────────┼─────────────────┼─────────────────────────┤
│  多模态处理器    │   建议引擎      │   AI模型管理器           │
├─────────────────┴─────────────────┴─────────────────────────┤
│                    外部服务集成                             │
├─────────────────┬─────────────────┬─────────────────────────┤
│   望诊服务   │   闻诊服务   │   问诊服务  │  切诊服务  │   算诊服务  ｜
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV 包管理器
- PostgreSQL 15+
- Redis 7+
- Docker (可选)

### 安装

1. **克隆项目**
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life/services/agent-services/xiaoai-service
```

2. **安装依赖**
```bash
# 安装UV包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
make install-all
```

3. **配置环境**
```bash
# 复制配置文件
cp config/config.yaml.example config/config.yaml
cp .env.example .env

# 编辑配置文件
vim config/config.yaml
vim .env
```

4. **初始化数据库**
```bash
# 创建数据库
createdb xiaoai_db

# 运行数据库迁移
make db-init
```

5. **启动服务**
```bash
# 开发模式
make dev

# 生产模式
make serve
```

### Docker 部署

```bash
# 构建并启动所有服务
make docker-compose-up

# 查看日志
make docker-compose-logs

# 停止服务
make docker-compose-down
```

## 📖 使用指南

### API 调用示例

#### 创建诊断会话

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "metadata": {
      "source": "mobile_app",
      "version": "1.0.0"
    }
  }'
```

#### 开始诊断流程

```bash
curl -X POST "http://localhost:8000/sessions/{session_id}/diagnosis" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis_data": {
      "looking": {
        "tongue_image": "base64_encoded_image",
        "face_image": "base64_encoded_image"
      },
      "inquiry": {
        "chief_complaint": "最近感觉疲劳",
        "symptoms": ["疲劳", "食欲不振"]
      }
    }
  }'
```

### Python SDK 使用

```python
from xiaoai_client import XiaoAIClient

# 初始化客户端
client = XiaoAIClient(
    base_url="http://localhost:8000",
    access_token="your_access_token"
)

# 创建诊断会话
session = await client.create_session(
    user_id="user_123456",
    metadata={"source": "python_sdk"}
)

# 开始诊断
diagnosis_data = {
    "looking": {"tongue_image": "base64_image_data"},
    "inquiry": {"chief_complaint": "疲劳乏力"}
}

diagnosis = await client.start_diagnosis(
    session_id=session.session_id,
    diagnosis_data=diagnosis_data
)

# 获取结果
result = await client.get_diagnosis_result(
    session_id=session.session_id,
    diagnosis_id=diagnosis.diagnosis_id
)

print(f"诊断结果: {result.syndrome_analysis}")
```

## 🧪 开发指南

### 开发环境搭建

```bash
# 完整开发环境搭建
make dev-setup

# 启动开发服务器
make dev
```

### 代码质量检查

```bash
# 运行所有检查
make ci

# 单独运行检查
make lint          # 代码检查
make typecheck     # 类型检查
make test          # 运行测试
make security      # 安全检查
```

### 测试

```bash
# 运行所有测试
make test

# 运行特定类型的测试
make test-unit         # 单元测试
make test-integration  # 集成测试
make test-e2e         # 端到端测试

# 运行性能测试
make benchmark
```

### 代码格式化

```bash
# 自动格式化代码
make format

# 检查代码格式
make lint
```

## 📊 监控和运维

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 使用Make命令检查
make health
```

### 性能监控

服务集成了 Prometheus 指标和 Grafana 仪表板：

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 日志查看

```bash
# 查看应用日志
tail -f logs/xiaoai-service.log

# 查看Docker日志
docker logs xiaoai-service

# 查看Kubernetes日志
kubectl logs -f deployment/xiaoai-service
```

## 🚀 部署

### 环境部署

```bash
# 部署到测试环境
./scripts/deploy.sh staging

# 部署到生产环境
./scripts/deploy.sh production

# 模拟部署（不执行实际操作）
./scripts/deploy.sh staging --dry-run
```

### Kubernetes 部署

```bash
# 使用Helm部署
helm install xiaoai-service k8s/helm-chart \
  --namespace suokelife \
  --values k8s/values-production.yaml

# 升级部署
helm upgrade xiaoai-service k8s/helm-chart \
  --namespace suokelife \
  --values k8s/values-production.yaml
```

## 📚 文档

- [API 文档](docs/api.md) - 完整的API接口文档
- [开发文档](docs/development.md) - 开发指南和最佳实践
- [部署文档](docs/deployment.md) - 部署和运维指南
- [架构文档](docs/architecture.md) - 系统架构设计

## 🔧 配置

### 主要配置项

```yaml
# config/config.yaml
app:
  name: "xiaoai-service"
  version: "1.0.0"
  debug: false
  log_level: "INFO"

database:
  host: "localhost"
  port: 5432
  name: "xiaoai_db"
  user: "xiaoai_user"
  password: "your_password"

redis:
  host: "localhost"
  port: 6379
  db: 0

ai_models:
  base_path: "./models"
  cache_size: 1000
  auto_unload_timeout: 3600
```

### 环境变量

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=xiaoai_db
DB_USER=xiaoai_user
DB_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AI模型配置
AI_MODELS_PATH=./models
HUGGINGFACE_TOKEN=your_token
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [mypy](http://mypy-lang.org/) 进行类型检查
- 编写完整的测试用例
- 更新相关文档

## 📈 性能指标

### 基准测试结果

| 操作 | 平均响应时间 | 95%分位数 | QPS |
|------|-------------|-----------|-----|
| 创建会话 | 15ms | 25ms | 1000 |
| 五诊协调 | 2.5s | 4s | 100 |
| 辨证分析 | 800ms | 1.2s | 200 |
| 体质分析 | 600ms | 1s | 250 |
| 生成建议 | 1.2s | 2s | 150 |

### 系统要求

| 环境 | CPU | 内存 | 存储 | 网络 |
|------|-----|------|------|------|
| 开发 | 2核 | 4GB | 20GB | 100Mbps |
| 测试 | 4核 | 8GB | 50GB | 1Gbps |
| 生产 | 8核 | 16GB | 200GB | 10Gbps |

## 🔒 安全

### 安全特性

- JWT 令牌认证
- API 请求限流
- 数据加密传输
- 敏感信息脱敏
- 安全审计日志

### 安全检查

```bash
# 运行安全扫描
make security

# 检查依赖漏洞
make check-security-deps
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🆘 支持

### 获取帮助

- **技术支持**: tech-support@suoke.life
- **API问题**: api-support@suoke.life
- **文档反馈**: docs@suoke.life
- **GitHub Issues**: [提交问题](https://github.com/SUOKE2024/suoke_life/issues)

### 常见问题

#### Q: 如何配置AI模型？
A: 在 `config/config.yaml` 中配置模型路径和参数，确保模型文件存在于指定路径。

#### Q: 服务启动失败怎么办？
A: 检查数据库连接、Redis连接和配置文件，查看日志获取详细错误信息。

#### Q: 如何扩展新的诊断类型？
A: 实现新的诊断处理器，继承 `BaseDiagnosisProcessor` 类，并在协调器中注册。

## 🎯 路线图

### v1.1.0 (计划中)
- [ ] 支持更多中医诊断方法
- [ ] 增强AI模型准确性
- [ ] 优化性能和内存使用
- [ ] 添加更多无障碍功能

### v1.2.0 (计划中)
- [ ] 支持多语言
- [ ] 集成更多外部服务
- [ ] 增加实时诊断功能
- [ ] 完善监控和告警

### v2.0.0 (长期规划)
- [ ] 重构为微服务架构
- [ ] 支持联邦学习
- [ ] 增加边缘计算支持
- [ ] 完整的AI解释性

## 📊 统计信息

- **代码行数**: ~15,000 行
- **测试覆盖率**: 95%+
- **文档覆盖率**: 100%
- **API端点**: 20+
- **支持的诊断类型**: 4种
- **支持的体质类型**: 9种

---

<div align="center">

**[索克生活](https://suoke.life) | [文档](https://docs.suoke.life) | [API](https://api.suoke.life) | [支持](mailto:support@suoke.life)**

Made with ❤️ by the SuokeLife Team

</div>