# Look Service - 索克生活望诊服务

## 概述

Look Service 是索克生活平台的中医望诊服务，基于现代AI技术实现传统中医望诊的数字化。该服务通过分析用户的面部、舌象、体态等图像信息，提供个性化的健康评估和建议。

## 最新优化成果

### 🚀 架构全面升级

经过深度优化，Look Service 已从单体架构升级为具有现代微服务特征的高性能、高可用、易维护的服务：

#### 1. 依赖注入容器 (`internal/container/container.py`)
- ✅ 统一的依赖管理系统
- ✅ 支持异步初始化和生命周期管理
- ✅ 内置健康检查和优雅关闭功能
- ✅ 管理所有服务组件的依赖关系

#### 2. 缓存服务 (`internal/service/cache_service.py`)
- ✅ 抽象缓存接口，支持Redis和内存缓存
- ✅ 缓存统计、LRU淘汰、TTL管理
- ✅ 缓存管理器和装饰器支持
- ✅ 模式匹配删除和缓存键生成

#### 3. 监控指标服务 (`internal/service/metrics_service.py`)
- ✅ 集成Prometheus和OpenTelemetry
- ✅ 全面的指标体系（请求、分析、模型、缓存、数据库、系统资源、错误等）
- ✅ 分布式追踪和系统资源监控
- ✅ 装饰器和中间件支持

#### 4. 通知服务 (`internal/service/notification_service.py`)
- ✅ 多种通知渠道（Webhook、消息队列、邮件、短信、内部）
- ✅ 异步事件处理和订阅机制
- ✅ 通知级别管理和重试机制
- ✅ 事件发布订阅模式

#### 5. 中间件系统 (`internal/middleware/middleware.py`)
- ✅ 完整的中间件链架构
- ✅ 限流、认证、日志、错误处理、指标收集等中间件
- ✅ 中间件组合和配置化管理
- ✅ 统一的请求处理流程

#### 6. 异步任务处理器 (`internal/service/task_processor.py`)
- ✅ 后台任务执行和队列管理
- ✅ 任务调度和优先级管理
- ✅ 任务状态跟踪和结果缓存
- ✅ 批处理和并发控制

#### 7. 数据验证和序列化 (`internal/service/validation_service.py`)
- ✅ 灵活的验证规则系统
- ✅ 多种验证器（类型、长度、范围、正则、选择等）
- ✅ 自定义序列化器和反序列化器
- ✅ 图像数据专用验证器

#### 8. 弹性和重试服务 (`internal/service/resilience_service.py`)
- ✅ 多种重试策略（固定、指数、线性、随机）
- ✅ 断路器模式实现
- ✅ 超时控制和错误处理
- ✅ 装饰器和上下文管理器支持

#### 9. 增强服务实现 (`internal/delivery/enhanced_look_service_impl.py`)
- ✅ 重构的服务实现，使用依赖注入
- ✅ 集成缓存、通知、监控等功能
- ✅ 异步处理和中间件链支持
- ✅ 改进的错误处理和响应构建

#### 10. 服务启动器 (`internal/service/service_launcher.py`)
- ✅ 统一的服务生命周期管理
- ✅ 优雅启动和关闭
- ✅ 健康检查和状态监控
- ✅ 信号处理和后台任务管理

### 🎯 核心特性

#### 异步架构
- 全面支持异步操作，提高并发性能
- 异步任务处理和后台作业
- 非阻塞I/O和资源管理

#### 模块化设计
- 各组件职责清晰，易于测试和维护
- 插件化的中间件和处理器
- 可配置的服务组合

#### 配置驱动
- 灵活的配置管理系统
- 环境特定的配置支持
- 运行时配置更新

#### 可观测性
- 完整的监控、日志和追踪体系
- Prometheus指标集成
- 结构化日志和分布式追踪

#### 容错性
- 健全的错误处理和重试机制
- 断路器模式防止级联故障
- 优雅降级和故障恢复

#### 扩展性
- 水平扩展支持
- 负载均衡和服务发现
- 微服务架构准备

## 技术栈

### 核心技术
- **Python 3.8+**: 主要编程语言
- **gRPC**: 服务间通信协议
- **asyncio**: 异步编程框架
- **structlog**: 结构化日志

### 依赖服务
- **Redis**: 缓存和会话存储
- **PostgreSQL**: 主数据库
- **Prometheus**: 监控指标收集
- **OpenTelemetry**: 分布式追踪

### AI/ML框架
- **TensorFlow/PyTorch**: 深度学习模型
- **OpenCV**: 图像处理
- **scikit-learn**: 机器学习算法

## 快速开始

### 环境要求
- Python 3.8+
- Redis 6.0+
- PostgreSQL 12+

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置服务
```bash
# 复制配置模板
cp config/config.yaml.template config/config.yaml

# 编辑配置文件
vim config/config.yaml
```

### 启动服务
```bash
# 使用服务启动器
python -m internal.service.service_launcher

# 或者使用传统方式
python cmd/server/main.py
```

## 配置说明

### 服务配置
```yaml
server:
  host: "0.0.0.0"
  port: 50053
  max_workers: 10

cache:
  enabled: true
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: null
    max_connections: 20

task_processor:
  max_workers: 10
  queue_size: 1000
  cleanup_interval: 300
  max_result_age: 3600

health_check:
  interval: 30
```

### 监控配置
```yaml
monitoring:
  enabled: true
  prometheus:
    enabled: true
    port: 8080
  tracing:
    enabled: true
    jaeger_endpoint: "http://localhost:14268/api/traces"
```

## API 文档

### gRPC 服务

#### AnalyzeImage
分析用户上传的图像，提供中医望诊结果。

```protobuf
rpc AnalyzeImage(AnalyzeImageRequest) returns (AnalyzeImageResponse);

message AnalyzeImageRequest {
  string user_id = 1;
  bytes image = 2;
  string analysis_type = 3; // "face", "tongue", "body"
  bool save_result = 4;
}

message AnalyzeImageResponse {
  string analysis_id = 1;
  AnalysisResult result = 2;
  string status = 3;
  string message = 4;
}
```

#### GetAnalysisHistory
获取用户的分析历史记录。

```protobuf
rpc GetAnalysisHistory(GetAnalysisHistoryRequest) returns (GetAnalysisHistoryResponse);
```

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8080/health

# 获取详细状态
curl http://localhost:8080/status
```

## 开发指南

### 添加新的分析器
1. 在 `internal/analyzer/` 目录下创建新的分析器类
2. 实现 `BaseAnalyzer` 接口
3. 在容器中注册分析器
4. 更新配置文件

### 添加新的中间件
1. 在 `internal/middleware/` 目录下创建中间件
2. 实现 `Middleware` 接口
3. 在中间件链中注册
4. 配置中间件参数

### 自定义验证规则
```python
from internal.service.validation_service import ValidationRule, validation_service

# 创建自定义验证规则
rule = ValidationRule(
    field_name="custom_field",
    required=True,
    data_type=str,
    pattern=r'^[A-Z]{2,10}$'
)

# 注册规则
validation_service.add_rule("custom_schema", rule)
```

## 部署指南

### Docker 部署
```bash
# 构建镜像
docker build -t look-service:latest .

# 运行容器
docker run -d \
  --name look-service \
  -p 50053:50053 \
  -p 8080:8080 \
  -e REDIS_HOST=redis \
  -e DB_HOST=postgres \
  look-service:latest
```

### Kubernetes 部署
```bash
# 应用配置
kubectl apply -f deploy/kubernetes/

# 检查状态
kubectl get pods -l app=look-service
```

## 监控和运维

### 指标监控
- 服务可用性和响应时间
- 分析请求量和成功率
- 缓存命中率和性能
- 系统资源使用情况

### 日志管理
- 结构化日志输出
- 日志级别配置
- 分布式追踪集成

### 故障排查
1. 检查服务健康状态
2. 查看监控指标和告警
3. 分析日志和追踪信息
4. 检查依赖服务状态

## 性能优化

### 缓存策略
- 分析结果缓存
- 模型预测缓存
- 用户会话缓存

### 并发优化
- 异步处理管道
- 批量请求处理
- 连接池管理

### 资源管理
- 内存使用优化
- GPU资源调度
- 磁盘I/O优化

## 安全考虑

### 数据安全
- 图像数据加密存储
- 用户隐私保护
- 访问权限控制

### 网络安全
- TLS加密通信
- API访问限制
- 防DDoS攻击

## 测试

### 单元测试
```bash
pytest test/unit/
```

### 集成测试
```bash
pytest test/integration/
```

### 性能测试
```bash
python test/performance/load_test.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目维护者：Song Xu <song.xu@icloud.com>
- 邮箱：song.xu@icloud.com
- 文档：https://github.com/SUOKE2024/suoke_life/tree/main/services/diagnostic-services/look-service

---

**注意**: 本服务是索克生活平台的核心组件之一，专注于中医望诊的数字化实现。通过现代化的架构设计和AI技术，为用户提供准确、及时的健康评估服务。 