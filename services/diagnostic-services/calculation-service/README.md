# 索克生活 - 算诊服务

## 项目概述

算诊服务是"索克生活"健康管理平台中的核心微服务之一，专门提供中医五诊中的"算诊"功能。该服务将传统中医的算诊智慧与现代人工智能技术相结合，为用户提供个性化的健康分析和调养建议。

## 核心特性

### 🔮 算诊功能
- **子午流注分析** - 基于十二经络时间医学的健康分析
- **八字体质分析** - 根据出生时间分析个人体质特征
- **八卦配属分析** - 运用易学理论进行健康状态分析
- **五运六气分析** - 基于运气学说的疾病预测和调养指导
- **综合算诊** - 整合多种算诊方法的全面健康评估

### 🚀 技术特点
- **传统与现代结合** - 将古代算诊智慧数字化
- **个性化分析** - 基于个人信息的精准健康建议
- **时间医学** - 考虑时间因素的治疗和调养指导
- **智能缓存** - 提高响应速度和系统性能
- **限流保护** - 防止API滥用，确保服务稳定
- **完善监控** - 全面的日志记录和错误处理

### 💡 创新价值
- **差异化优势** - 市面上几乎没有类似的算诊功能产品
- **完善诊断体系** - 与望、闻、问、切四诊形成完整的"五诊合参"
- **科学化实现** - 用现代算法实现传统医学理论
- **预防医学** - 从治疗转向预防的健康管理理念

## 项目结构

```
calculation-service/
├── calculation_service/           # 主应用包
│   ├── api/                      # API路由层
│   │   ├── __init__.py
│   │   ├── routes.py            # 路由定义
│   │   └── models.py            # API数据模型
│   ├── core/                    # 核心算法层
│   │   ├── __init__.py
│   │   └── algorithms/          # 算诊算法模块
│   │       ├── __init__.py
│   │       ├── ziwu_liuzhu/     # 子午流注模块
│   │       ├── constitution/    # 八字体质分析模块
│   │       ├── bagua/          # 八卦配属模块
│   │       ├── wuyun_liuqi/    # 五运六气模块
│   │       └── comprehensive_calculator.py  # 综合算诊计算器
│   ├── config/                  # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py         # 应用配置
│   ├── exceptions/              # 异常处理
│   │   ├── __init__.py
│   │   └── calculation_exceptions.py
│   ├── middleware/              # 中间件
│   │   ├── __init__.py
│   │   ├── logging_middleware.py
│   │   ├── error_handler.py
│   │   └── rate_limiter.py
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── validators.py       # 数据验证
│   │   ├── formatters.py       # 数据格式化
│   │   ├── cache.py           # 缓存管理
│   │   └── helpers.py         # 辅助函数
│   └── main.py                 # 应用入口
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── test_calculation.py    # 基础测试
│   └── test_comprehensive.py  # 综合测试
├── requirements.txt           # Python依赖
├── Dockerfile                # Docker构建文件
├── docker-compose.yml        # Docker Compose配置
└── README.md                 # 项目文档
```

## 算法模块详解

### 1. 子午流注分析 (ziwu_liuzhu)
基于中医十二经络的时间医学理论：
- **时辰经络分析** - 分析当前时辰对应的经络状态
- **最佳治疗时间** - 推荐疾病治疗的最佳时机
- **灵龟八法** - 运用灵龟八法进行穴位开合分析
- **调养建议** - 提供基于时间的个性化调养方案

### 2. 八字体质分析 (constitution)
基于出生时间的体质分析：
- **八字计算** - 计算年、月、日、时四柱八字
- **五行强弱** - 分析个人五行属性的强弱分布
- **体质类型** - 确定个人的中医体质类型
- **调理方案** - 提供针对性的体质调理建议

### 3. 八卦配属分析 (bagua)
运用易学八卦理论：
- **本命卦计算** - 根据出生信息计算本命卦象
- **健康分析** - 基于卦象分析健康状态
- **方位指导** - 提供有利的方位和环境建议
- **调理建议** - 基于八卦理论的健康调理方案

### 4. 五运六气分析 (wuyun_liuqi)
基于运气学说的分析：
- **运气推算** - 计算年度的五运六气状态
- **司天在泉** - 分析司天、在泉对健康的影响
- **疾病预测** - 预测可能出现的健康问题
- **调养指导** - 提供顺应运气的调养建议

### 5. 综合算诊 (comprehensive_calculator)
整合所有算诊方法：
- **多维度分析** - 综合多种算诊方法的结果
- **健康风险评估** - 评估整体健康风险等级
- **个性化方案** - 生成个性化的健康管理方案
- **调养重点** - 确定当前阶段的调养重点

## API接口

### 基础接口
- `GET /` - 服务信息
- `GET /ping` - 健康检查
- `GET /docs` - API文档

### 算诊接口
- `POST /api/v1/calculation/ziwu` - 子午流注分析
- `POST /api/v1/calculation/constitution` - 八字体质分析
- `POST /api/v1/calculation/bagua` - 八卦配属分析
- `POST /api/v1/calculation/wuyun` - 五运六气分析
- `POST /api/v1/calculation/comprehensive` - 综合算诊分析

### 管理接口
- `GET /api/v1/calculation/health` - 服务健康状态
- `GET /cache/stats` - 缓存统计信息
- `POST /cache/clear` - 清理缓存
- `POST /cache/cleanup` - 清理过期缓存

## 快速开始

### 环境要求
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行服务
```bash
# 开发模式
uvicorn calculation_service.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn calculation_service.main:app --host 0.0.0.0 --port 8000
```

### Docker部署
```bash
# 构建镜像
docker build -t suoke-calculation-service .

# 运行容器
docker run -p 8003:8000 suoke-calculation-service

# 使用Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量
```bash
# 基础配置
HOST=0.0.0.0                    # 服务主机
PORT=8000                       # 服务端口
DEBUG=false                     # 调试模式

# 缓存配置
ENABLE_CACHE=true               # 启用缓存
CACHE_TTL=3600                  # 缓存生存时间（秒）

# 限流配置
RATE_LIMIT_ENABLED=true         # 启用限流
RATE_LIMIT_MAX_REQUESTS=100     # 最大请求数
RATE_LIMIT_WINDOW_SECONDS=60    # 时间窗口（秒）

# CORS配置
ALLOWED_ORIGINS=["http://localhost:3000"]  # 允许的源
```

## 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_comprehensive.py

# 运行测试并生成覆盖率报告
pytest --cov=calculation_service tests/
```

### 测试覆盖
- 单元测试：测试各个算法模块的功能
- 集成测试：测试API接口的完整流程
- 性能测试：测试服务的响应性能
- 错误处理测试：测试异常情况的处理

## 性能优化

### 缓存策略
- **算诊结果缓存** - 缓存计算结果，避免重复计算
- **时间分析缓存** - 按小时级别缓存时间相关分析
- **自动清理** - 定期清理过期缓存项

### 限流保护
- **IP级别限流** - 防止单个IP的过度请求
- **滑动窗口** - 使用滑动窗口算法进行精确限流
- **优雅降级** - 超限时返回友好的错误信息

### 监控指标
- **响应时间** - 监控API响应时间
- **错误率** - 统计错误请求比例
- **缓存命中率** - 监控缓存使用效果
- **并发数** - 监控同时处理的请求数

## 部署架构

### 微服务架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│ Calculation     │────│   Other         │
│                 │    │ Service         │    │   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Message Bus   │
                    └─────────────────┘
```

### 容器化部署
- **Docker镜像** - 标准化的容器镜像
- **健康检查** - 内置健康检查机制
- **日志收集** - 结构化日志输出
- **配置管理** - 环境变量配置

## 监控和运维

### 日志管理
- **结构化日志** - JSON格式的日志输出
- **日志级别** - 支持不同级别的日志记录
- **请求追踪** - 记录完整的请求处理过程
- **错误追踪** - 详细的错误信息和堆栈跟踪

### 健康检查
- **服务状态** - 检查服务基本运行状态
- **算法状态** - 验证各算法模块的可用性
- **缓存状态** - 检查缓存系统的运行状态
- **依赖检查** - 验证外部依赖的连接状态

### 性能监控
- **响应时间分布** - 统计API响应时间分布
- **吞吐量监控** - 监控每秒处理的请求数
- **资源使用** - 监控CPU、内存使用情况
- **错误统计** - 统计各类错误的发生频率

## 开发指南

### 代码规范
- **PEP 8** - 遵循Python代码规范
- **类型注解** - 使用类型注解提高代码可读性
- **文档字符串** - 为所有函数和类添加文档
- **单元测试** - 为新功能编写对应的测试

### 贡献流程
1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 代码审查和合并

### 算法扩展
如需添加新的算诊算法：
1. 在`core/algorithms/`下创建新模块
2. 实现算法的数据和计算逻辑
3. 在`comprehensive_calculator.py`中集成
4. 添加对应的API接口
5. 编写完整的测试用例

## 技术栈

### 核心技术
- **FastAPI** - 现代化的Python Web框架
- **Pydantic** - 数据验证和序列化
- **Uvicorn** - ASGI服务器
- **Python 3.11** - 编程语言

### 开发工具
- **Pytest** - 测试框架
- **Black** - 代码格式化
- **Flake8** - 代码检查
- **MyPy** - 类型检查

### 部署工具
- **Docker** - 容器化
- **Docker Compose** - 容器编排
- **Traefik** - 反向代理和负载均衡

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目仓库：[GitHub](https://github.com/suoke-life/calculation-service)
- 邮箱：support@suoke.life
- 文档：[在线文档](https://docs.suoke.life/calculation-service)

---

**索克生活 - 让传统中医智慧服务现代健康生活** 🌿 