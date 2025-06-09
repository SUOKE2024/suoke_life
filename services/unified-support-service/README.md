# 索克生活统一支持服务

## 🌟 概述

统一支持服务是索克生活平台的核心支持组件，整合了人工审核服务和无障碍服务，为平台提供全面的支持功能。

## 🏗️ 架构

```
unified-support-service/
├── unified_support_service/          # 主服务包
│   ├── human_review/                # 人工审核服务模块
│   ├── accessibility/               # 无障碍服务模块
│   ├── common/                      # 公共模块
│   ├── api/                         # API接口
│   ├── config/                      # 配置管理
│   └── utils/                       # 工具模块
├── tests/                           # 测试目录
├── config/                          # 配置文件
├── docs/                            # 文档
└── deploy/                          # 部署配置
```

## ✨ 核心功能

### 人工审核服务
- 🔍 智能审核任务分配
- 👥 审核员管理
- 📊 审核质量监控
- 🔒 安全权限管理
- 📈 性能统计分析

### 无障碍服务
- 👁️ 视觉无障碍分析
- 👂 音频无障碍处理
- 🤲 运动无障碍辅助
- 🧠 认知无障碍支持
- 🔧 平台兼容性检查

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python -m unified_support_service
```

### Docker部署

```bash
docker build -t unified-support-service .
docker run -p 8000:8000 unified-support-service
```

## 📊 API文档

服务启动后访问 `http://localhost:8000/docs` 查看完整API文档。

### 主要端点

- `GET /health` - 健康检查
- `POST /human-review/tasks` - 创建审核任务
- `POST /accessibility/analyze` - 无障碍分析
- `GET /human-review/dashboard` - 审核仪表板
- `GET /accessibility/report` - 无障碍报告

## 🔧 配置

### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# 服务配置
HUMAN_REVIEW_ENABLED=true
ACCESSIBILITY_ENABLED=true
LOG_LEVEL=INFO
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/human_review/
pytest tests/accessibility/

# 生成覆盖率报告
pytest --cov=unified_support_service --cov-report=html
```

## 📈 监控

服务提供完整的监控指标：

- 请求响应时间
- 错误率统计
- 服务健康状态
- 资源使用情况

## 🔒 安全

- JWT令牌认证
- 角色权限控制
- 数据加密传输
- 审计日志记录

## 📝 更新日志

### v1.0.0 (2025-06-09)
- ✅ 整合人工审核服务和无障碍服务
- ✅ 统一API接口和配置管理
- ✅ 完整的测试覆盖
- ✅ Docker容器化支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进本服务。

## 📄 许可证

MIT License
