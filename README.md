# 索克生活平台 (Suoke Life Platform)

[![生产就绪](https://img.shields.io/badge/状态-生产就绪-green.svg)](./PRODUCTION_READY_OPTIMIZATION_REPORT.md)
[![服务架构](https://img.shields.io/badge/架构-微服务-blue.svg)](./docs/architecture/)
[![API文档](https://img.shields.io/badge/API-v1-orange.svg)](./docs/api/)
[![监控](https://img.shields.io/badge/监控-Grafana-red.svg)](./monitoring/)
[![代码质量](https://img.shields.io/badge/质量-SonarQube-brightgreen.svg)](./docs/QUALITY_SECURITY_PERFORMANCE.md)
[![安全扫描](https://img.shields.io/badge/安全-Snyk-orange.svg)](./docs/QUALITY_SECURITY_PERFORMANCE.md)
[![性能测试](https://img.shields.io/badge/性能-K6-blue.svg)](./docs/QUALITY_SECURITY_PERFORMANCE.md)

## 🌟 项目概述

索克生活是一个基于人工智能的现代化健康管理平台，融合中医"辨证论治未病"理念与现代预防医学技术，提供全方位的健康服务和AI驱动的诊断工具。

### 核心特性
- 🔍 **五诊智能诊断** - 望闻问切算综合诊断
- 🤖 **AI智能体协作** - 小艾、小克、老克、索儿四大智能体
- 📚 **统一知识服务** - 医学知识库和基准测试
- 🛠️ **统一支持服务** - 人工审核和无障碍支持
- 📊 **实时监控** - Prometheus + Grafana监控体系
- 🚀 **自动化部署** - Docker + Kubernetes生产部署
- 🧠 **Claude AI 集成** - 智能代码审查和文档生成
- 🌐 **社区生态增强** - UGC内容创建、专家认证体系
- 🎭 **多模态AI理解** - 文本、图像、语音、生理信号融合分析
- 💭 **情感计算引擎** - 实时情感识别、分析和预测
- 🕸️ **服务网格** - Istio流量管理和安全通信
- 🔍 **搜索引擎** - Elasticsearch全文搜索和日志分析
- 🤖 **AI/ML平台** - MLflow模型管理和实验跟踪

## 🏗️ 架构概览

```
索克生活平台 (现代化微服务架构)
├── 服务网格层 (Istio Service Mesh)
│   ├── 流量管理 (Gateway, VirtualService, DestinationRule)
│   ├── 安全策略 (mTLS, AuthorizationPolicy)
│   └── 可观测性 (Tracing, Metrics, Logging)
├── 智能体服务层 (Agent Services)
│   ├── 小艾服务 (Health Consultation)
│   ├── 小克服务 (Symptom Analysis)
│   ├── 老克服务 (TCM Theory)
│   └── 索儿服务 (Lifestyle)
├── 诊断服务层 (Diagnosis Services)
│   ├── 望诊服务 (Visual Diagnosis)
│   ├── 闻诊服务 (Audio/Smell Diagnosis)
│   ├── 问诊服务 (Inquiry Diagnosis)
│   ├── 切诊服务 (Touch Diagnosis)
│   └── 脉诊服务 (Pulse Diagnosis)
├── 基础服务层 (Foundation Services)
│   ├── 统一知识服务 (Knowledge + Benchmarks)
│   ├── 统一支持服务 (Review + Accessibility)
│   ├── 通信服务 (Messaging + Real-time)
│   ├── 用户管理服务 (Auth + Permissions)
│   ├── 工具服务 (Integration + Resources)
│   └── 区块链服务 (Security + Privacy)
├── 数据处理层 (Data Processing)
│   ├── Elasticsearch (Search Engine)
│   └── MLflow (AI/ML Platform)
├── 基础设施层 (Infrastructure)
│   ├── API网关 (Kong/Istio Gateway)
│   ├── 负载均衡 (Kubernetes Ingress)
│   ├── 服务发现 (Kubernetes DNS)
│   └── 配置管理 (ConfigMap/Secret)
└── 监控运维层 (Observability)
    ├── 监控 (Prometheus + Grafana)
    ├── 日志 (ELK Stack)
    ├── 链路追踪 (Jaeger)
    └── 告警 (AlertManager)
```

## 🚀 快速开始

### 开发环境
```bash
# 1. 克隆项目
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置必要参数

# 4. 启动基础设施
docker-compose -f docker-compose.infrastructure.yml up -d

# 5. 启动开发环境
docker-compose up -d
```

### 生产部署
```bash
# Kubernetes部署（推荐）
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/istio/
kubectl apply -f k8s/elasticsearch/
kubectl apply -f k8s/services/

# Docker Compose部署
docker-compose -f deploy/production/docker-compose.production.yml up -d
```

### 质量保证工具
```bash
# 代码质量检查
./scripts/run-quality-checks.sh

# 安全扫描
snyk test

# 性能测试
./scripts/run-performance-tests.sh
```

## 🛠️ 技术栈

### 后端技术
- **语言**: Python 3.13.3
- **框架**: FastAPI
- **包管理**: UV
- **数据库**: PostgreSQL, Redis, MongoDB, InfluxDB
- **搜索引擎**: Elasticsearch
- **AI/ML**: MLflow, PyTorch, TensorFlow

### 前端技术
- **框架**: React Native
- **语言**: TypeScript
- **状态管理**: Redux Toolkit
- **UI组件**: React Native Elements

### 基础设施
- **容器化**: Docker
- **编排**: Kubernetes
- **服务网格**: Istio
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack
- **CI/CD**: GitHub Actions

### 质量保证
- **代码质量**: SonarQube
- **安全扫描**: Snyk
- **性能测试**: K6
- **测试框架**: pytest, Jest

## 📊 性能指标

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| API响应时间 | <100ms | ✅ 达标 |
| 并发用户 | 1000+ | ✅ 达标 |
| 系统可用性 | 99.9%+ | ✅ 达标 |
| 测试覆盖率 | 95%+ | ✅ 达标 |
| 代码质量评分 | A级 | ✅ 达标 |
| 安全漏洞 | 0个高危 | ✅ 达标 |

## 📚 文档

### 核心文档
- [架构文档](./docs/ARCHITECTURE.md) - 系统架构设计
- [API文档](./docs/api/) - 完整的API接口文档
- [部署指南](./docs/deployment/) - 生产环境部署指南
- [质量保证](./docs/QUALITY_SECURITY_PERFORMANCE.md) - 质量、安全、性能指南

### 开发文档
- [开发指南](./docs/development/) - 开发者指南
- [代码规范](./docs/CODE_QUALITY_STANDARDS.md) - 代码质量标准
- [类型安全](./docs/TYPE_SAFETY_ENHANCEMENT_GUIDE.md) - TypeScript类型安全指南
- [UI改进](./docs/UI_IMPROVEMENT_GUIDE.md) - UI/UX改进指南

### 用户文档
- [用户指南](./docs/user/) - 用户使用手册
- [监控指南](./docs/monitoring/) - 监控系统使用指南
- [故障排除](./docs/troubleshooting/) - 常见问题解决

## 🧪 测试

```bash
# 运行所有测试
uv run pytest

# 前端测试
npm test

# 用户验收测试
cd testing/user_acceptance
python run_tests.py

# 性能测试
k6 run k6/performance-tests/scenarios/load-test.js

# 代码质量检查
sonar-scanner
```

## 🔧 维护

### 健康检查
```bash
# 检查所有服务状态
curl http://localhost/health

# 检查Kubernetes集群状态
kubectl get pods -A

# 检查Istio服务网格状态
istioctl proxy-status
```

### 监控和日志
```bash
# 查看Grafana监控面板
open http://localhost:3000

# 查看Kibana日志分析
open http://localhost:5601

# 查看Jaeger链路追踪
open http://localhost:16686
```

## 🚀 最新更新

### v2.0.0 - 技术栈全面升级
- ✅ 集成Istio服务网格，实现流量管理和安全通信
- ✅ 集成Elasticsearch搜索引擎，提供全文搜索和日志分析
- ✅ 集成MLflow AI/ML平台，实现模型管理和实验跟踪
- ✅ 建立完整的质量保证体系（SonarQube + Snyk + K6）
- ✅ 优化CI/CD流水线，支持自动化质量检查

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码（遵循Conventional Commits规范）
4. 通过质量检查（SonarQube + Snyk + 测试）
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 📞 联系我们

- **技术支持**: tech@suoke.life
- **用户支持**: support@suoke.life
- **商务合作**: business@suoke.life

## 🏆 项目状态

- ✅ 微服务架构优化完成 (15个核心服务)
- ✅ 服务网格集成完成 (Istio)
- ✅ 搜索引擎集成完成 (Elasticsearch)
- ✅ AI/ML平台集成完成 (MLflow)
- ✅ 质量保证体系建立完成
- ✅ 生产部署就绪
- ✅ 监控体系建立
- ✅ 文档完善
- ⏳ 用户验收测试进行中

---

**索克生活 - 智能健康管理的未来** 🌟
