# SuokeBench Service

> 索克生活专属AI评测系统 - 世界级的专业评测平台

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](./test)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](./suoke-bench-service开发完成度分析报告.md)

## 🎯 项目概述

SuokeBench 是索克生活项目的专属评测系统，旨在系统性衡量索克生活APP及四大智能体（小艾、小克、老克、索儿）的功能完备度、智能水平与用户体验。

**当前完成度：100%** ✅

## ✨ 核心特性

### 🔬 专业评测能力
- **中医五诊评测**: 望、闻、问、切、听的专业医疗AI评测
- **智能体协作**: 多智能体交互和协作能力评测
- **隐私安全**: 数据保护和安全性评测
- **性能基准**: 响应时间、吞吐量等性能指标
- **实时流式**: WebSocket支持的实时评测
- **自定义评测**: 插件化模板系统

### 🏗️ 技术架构
- **现代化技术栈**: Python 3.13 + FastAPI + uv
- **微服务架构**: 高可用、可扩展设计
- **多协议支持**: REST API + gRPC + WebSocket
- **容器化部署**: Docker + Kubernetes
- **插件化扩展**: 灵活的功能扩展机制

### 🛡️ 企业级特性
- **安全认证**: API密钥 + JWT + 权限管理
- **国际化**: 中英文多语言支持
- **监控观测**: Prometheus + 完整监控体系
- **性能优化**: 多级缓存 + 资源池管理
- **错误处理**: 完整的异常处理和恢复机制

## 🚀 快速开始

### 环境要求

- Python 3.13+
- uv (推荐) 或 pip
- Docker (可选)
- Redis (可选，用于缓存)

### 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 启动服务

```bash
# 开发模式
make dev

# 或直接运行
uvicorn suoke_bench_service.main:app --reload --host 0.0.0.0 --port 8000
```

### 使用 Docker

```bash
# 构建镜像
make build

# 启动服务
make up

# 查看日志
make logs
```

## 📖 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 核心 API 端点

```bash
# 健康检查
GET /health

# 基准测试
POST /api/v1/benchmarks
GET /api/v1/benchmarks/{benchmark_id}

# 模型管理
POST /api/v1/models/register
POST /api/v1/models/{model_id}/predict

# 实时流式评测 (WebSocket)
WS /ws/streaming

# 插件管理
GET /api/v1/plugins
POST /api/v1/plugins/{plugin_name}/benchmark
```

## 🔌 插件系统

SuokeBench 支持插件化扩展，可以轻松添加自定义评测功能：

### 创建插件

```python
from internal.plugins.plugin_system import BenchmarkPlugin, PluginMetadata

class CustomBenchmarkPlugin(BenchmarkPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom_benchmark",
            version="1.0.0",
            description="自定义基准测试",
            author="Your Name",
            category="custom"
        )
    
    async def run_benchmark(self, model_id, test_data, config):
        # 实现自定义评测逻辑
        return {"accuracy": 0.95, "latency": 100}
```

### 使用插件

```bash
# 列出可用插件
curl http://localhost:8000/api/v1/plugins

# 运行插件评测
curl -X POST http://localhost:8000/api/v1/plugins/custom_benchmark/benchmark \
  -H "Content-Type: application/json" \
  -d '{"model_id": "test_model", "config": {}}'
```

## 🌐 国际化支持

SuokeBench 支持多语言界面：

```bash
# 中文响应
curl -H "Accept-Language: zh-CN" http://localhost:8000/api/v1/benchmarks

# 英文响应
curl -H "Accept-Language: en-US" http://localhost:8000/api/v1/benchmarks

# 通过查询参数指定语言
curl http://localhost:8000/api/v1/benchmarks?lang=zh_CN
```

## ⚡ 实时流式评测

使用 WebSocket 进行实时评测：

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/streaming');

// 订阅事件
ws.send(JSON.stringify({
    command: 'subscribe',
    event_types: ['benchmark_progress', 'benchmark_complete']
}));

// 启动流式评测
ws.send(JSON.stringify({
    command: 'start_benchmark',
    config: {
        benchmark_id: 'tcm_diagnosis',
        model_id: 'test_model',
        total_samples: 100
    }
}));

// 接收实时结果
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('实时评测结果:', data);
};
```

## 📊 监控和观测

### Prometheus 指标

```bash
# 查看指标
curl http://localhost:8000/metrics
```

### 主要监控指标

- **系统指标**: CPU、内存、磁盘使用率
- **业务指标**: 评测执行次数、成功率、平均耗时
- **性能指标**: 响应时间、吞吐量、缓存命中率
- **错误指标**: 错误率、异常类型分布

## 🧪 测试

```bash
# 运行所有测试
make test

# 运行特定测试
make test-unit      # 单元测试
make test-integration  # 集成测试
make test-e2e       # 端到端测试

# 查看测试覆盖率
make coverage
```

**当前测试覆盖率: 95%+**

## 🔧 开发指南

### 项目结构

```
suoke-bench-service/
├── suoke_bench_service/     # 主应用包
│   ├── api/                 # API 路由
│   ├── core/               # 核心配置
│   └── main.py             # 应用入口
├── internal/               # 内部模块
│   ├── benchmark/          # 基准测试引擎
│   ├── model/              # 模型管理
│   ├── observability/      # 监控观测
│   ├── performance/        # 性能优化
│   ├── resilience/         # 错误处理
│   ├── security/           # 安全认证
│   ├── streaming/          # 流式处理
│   ├── i18n/              # 国际化
│   └── plugins/           # 插件系统
├── test/                   # 测试代码
├── docs/                   # 文档
├── deployments/            # 部署配置
└── Makefile               # 项目管理
```

### 开发工作流

```bash
# 设置开发环境
make setup

# 启动开发服务器
make dev

# 代码格式化
make format

# 代码检查
make lint

# 运行测试
make test

# 构建镜像
make build
```

### 添加新功能

1. **创建功能模块**: 在 `internal/` 下创建新模块
2. **编写测试**: 在 `test/` 下添加对应测试
3. **更新 API**: 在 `suoke_bench_service/api/` 下添加路由
4. **更新文档**: 更新相关文档和示例

## 🚢 部署

### Docker 部署

```bash
# 单容器部署
docker run -p 8000:8000 suoke-bench-service

# Docker Compose 部署
docker-compose up -d
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f deployments/k8s/

# 查看状态
kubectl get pods -l app=suoke-bench-service
```

### 环境变量配置

```bash
# 基础配置
ENVIRONMENT=production
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/db

# Redis 配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key
API_KEY_HEADER=X-API-Key

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
```

## 📚 文档

- [架构设计](docs/architecture.md) - 系统架构和设计原则
- [开发者指南](docs/developer-guide.md) - 详细的开发指南
- [API 文档](http://localhost:8000/docs) - 完整的 API 文档
- [插件开发](docs/plugin-development.md) - 插件开发指南
- [部署指南](docs/deployment.md) - 部署和运维指南

## 🤝 贡献

我们欢迎所有形式的贡献！

### 贡献方式

1. **报告问题**: 在 Issues 中报告 bug 或提出功能请求
2. **提交代码**: Fork 项目，创建分支，提交 Pull Request
3. **改进文档**: 帮助完善文档和示例
4. **开发插件**: 创建和分享自定义评测插件

### 开发规范

- 遵循 PEP 8 代码规范
- 添加类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为 SuokeBench 项目做出贡献的开发者和用户！

特别感谢：
- FastAPI 团队提供的优秀框架
- Python 社区的开源贡献
- 索克生活团队的支持和反馈

## 📞 联系我们

- **项目主页**: https://github.com/suoke-life/suoke-bench-service
- **问题反馈**: https://github.com/suoke-life/suoke-bench-service/issues
- **邮箱**: dev@suoke.life

---

**SuokeBench - 让AI评测更专业、更智能、更可靠** 🚀