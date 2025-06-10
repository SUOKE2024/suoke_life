# 索克生活平台 (Suoke Life Platform)

[![生产就绪](https://img.shields.io/badge/状态-生产就绪-green.svg)](./PRODUCTION_READY_OPTIMIZATION_REPORT.md)
[![服务架构](https://img.shields.io/badge/架构-微服务-blue.svg)](./docs/architecture/)
[![API文档](https://img.shields.io/badge/API-v1-orange.svg)](./docs/api/)
[![监控](https://img.shields.io/badge/监控-Grafana-red.svg)](./monitoring/)

## 🌟 项目概述

索克生活是一个智能健康管理平台，提供全方位的健康服务和AI驱动的诊断工具。

### 核心特性
- 🔍 **五诊智能诊断** - 望闻问切算综合诊断
- 🤖 **AI智能体协作** - 小艾、小克、老克、索儿四大智能体
- 📚 **统一知识服务** - 医学知识库和基准测试
- 🛠️ **统一支持服务** - 人工审核和无障碍支持
- 📊 **实时监控** - Prometheus + Grafana监控体系
- 🚀 **自动化部署** - Docker + Kubernetes生产部署
- 🧠 **Claude AI 集成** - 智能代码审查和文档生成

## 🏗️ 架构概览

```
索克生活平台
├── 统一知识服务 (Medical Knowledge + Benchmarks)
├── 统一支持服务 (Human Review + Accessibility)
├── 诊断服务 (五诊: 望闻问切算)
├── 智能体服务 (小艾/小克/老克/索儿)
├── 通信服务 (Messaging + Real-time)
├── 用户管理服务 (Auth + Permissions)
├── 工具服务 (Integration + Medical Resources)
├── API网关 (Routing + Load Balancing)
├── 公共服务 (Shared Components)
├── 区块链服务 (Security + Privacy)
└── Claude AI 集成 (Code Review + Documentation)
```

## 🚀 快速开始

### 开发环境
```bash
# 1. 克隆项目
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life

# 2. 安装依赖
npm install

# 3. 配置 Claude AI 集成
./scripts/install-claude.sh

# 4. 启动开发环境
docker-compose up -d
npm start
```

### 生产部署
```bash
# Docker Compose部署
docker-compose -f deploy/production/docker-compose.production.yml up -d

# Kubernetes部署
kubectl apply -f deploy/production/kubernetes.yml
```

### 监控系统
```bash
# 启动监控
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# 访问Grafana
open http://localhost:3000
```

## 📊 性能指标

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| API响应时间 | <100ms | ✅ 达标 |
| 并发用户 | 50+ | ✅ 达标 |
| 系统可用性 | 99.9%+ | ✅ 达标 |
| 测试覆盖率 | 95%+ | ✅ 达标 |

## 📚 文档

- [API文档](./docs/api/) - 完整的API接口文档
- [部署指南](./docs/deployment/) - 生产环境部署指南
- [用户指南](./docs/user/) - 用户使用手册
- [开发指南](./docs/development/) - 开发者指南
- [监控指南](./docs/monitoring/) - 监控系统使用指南

## 🧪 测试

```bash
# 运行所有测试
npm test

# 运行用户验收测试
cd testing/user_acceptance
python run_tests.py

# 性能测试
npm run test:performance
```

## 🔧 维护

### 健康检查
```bash
# 检查所有服务状态
curl http://localhost/health

# 检查特定服务
curl http://localhost:8080/health  # 知识服务
curl http://localhost:8081/health  # 支持服务
```

### 日志查看
```bash
# 查看服务日志
docker-compose logs -f unified-knowledge-service

# 查看监控日志
docker-compose -f monitoring/docker-compose.monitoring.yml logs -f
```

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 📞 联系我们

- **技术支持**: tech@suoke.life
- **用户支持**: support@suoke.life
- **商务合作**: business@suoke.life

## 🏆 项目状态

- ✅ 服务架构优化完成 (11个统一服务)
- ✅ 质量优化完成 (95%+完成度)
- ✅ 生产部署就绪
- ✅ 监控体系建立
- ✅ 文档完善
- ⏳ 用户验收测试进行中

---

**索克生活 - 智能健康管理的未来** 🌟
