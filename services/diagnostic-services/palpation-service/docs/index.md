# 触诊服务文档

欢迎使用索克生活触诊服务！这是一个基于AI的中医触诊智能分析微服务，提供多模态数据融合、智能分析和预测功能。

## 🎯 项目概述

触诊服务是索克生活健康管理平台的核心组件之一，专注于将传统中医触诊技术与现代AI技术相结合，为用户提供精准的健康状态评估和个性化建议。

### 核心特性

- **多模态数据融合**: 支持压力、温度、纹理等多种传感器数据的智能融合
- **AI智能分析**: 基于深度学习的触诊数据分析和模式识别
- **实时预测**: 提供健康状态的实时预测和趋势分析
- **智能报告**: 自动生成详细的触诊分析报告
- **高性能缓存**: 智能缓存管理，提升响应速度
- **实时监控**: 完整的服务监控和指标收集

### 技术栈

- **Python 3.13.3**: 最新的Python版本，提供更好的性能和特性
- **FastAPI**: 现代、快速的Web框架
- **UV**: 快速的Python包管理器
- **Pydantic**: 数据验证和序列化
- **Redis**: 高性能缓存
- **PostgreSQL**: 可靠的数据存储
- **Prometheus**: 监控和指标收集

## 🚀 快速开始

### 环境要求

- Python 3.13.3+
- UV 包管理器
- Redis 服务器
- PostgreSQL 数据库

### 安装

```bash
# 克隆项目
git clone https://github.com/suokelife/suoke_life.git
cd suoke_life/services/diagnostic-services/palpation-service

# 安装依赖
make install-dev

# 运行服务
make run-dev
```

### 验证安装

访问 [http://localhost:8000](http://localhost:8000) 查看服务状态。

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看API文档。

## 📚 文档导航

- [快速开始](getting-started/installation.md) - 详细的安装和配置指南
- [API文档](api/overview.md) - 完整的API参考
- [架构设计](architecture/overview.md) - 系统架构和设计理念
- [开发指南](development/setup.md) - 开发环境搭建和贡献指南

## 🔧 开发

### 开发环境搭建

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 代码格式化
make format

# 类型检查
make type-check

# 安全检查
make security-check
```

### 项目结构

```
palpation-service/
├── palpation_service/          # 主包
│   ├── __init__.py
│   ├── main.py                 # 主程序
│   └── internal/               # 内部模块
├── tests/                      # 测试
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
├── docs/                       # 文档
├── config/                     # 配置文件
├── pyproject.toml              # 项目配置
├── Makefile                    # 构建脚本
└── README.md                   # 项目说明
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看[开发指南](development/setup.md)了解如何参与项目开发。

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](https://github.com/suokelife/suoke_life/blob/main/LICENSE) 文件。

## 📞 支持

如果您遇到问题或有任何疑问，请：

- 查看[故障排除](troubleshooting.md)文档
- 提交[Issue](https://github.com/suokelife/suoke_life/issues)
- 联系开发团队：dev@suokelife.com 