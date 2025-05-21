# 问诊服务启动指南

本文档提供了问诊服务（Inquiry Service）的详细启动指南、环境配置说明和常见问题排查方法。

## 环境要求

- **操作系统**：Linux, macOS, Windows
- **Python版本**：Python 3.9+（已支持Python 3.13）
- **内存**：最小2GB，推荐4GB以上
- **存储**：至少500MB可用空间

## 依赖安装

### 核心依赖

```bash
# 安装基础依赖
pip install python-dotenv grpcio grpcio-tools grpcio-reflection PyYAML httpx aiohttp

# 安装所有依赖（生产环境）
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-asyncio black isort mypy flake8
```

### 特殊依赖说明

- **LLM模型相关依赖**：如果使用本地推理模式，需安装额外的深度学习库
  ```bash
  pip install torch transformers
  ```

- **监控相关依赖**
  ```bash
  pip install prometheus-client opentelemetry-api opentelemetry-sdk
  ```

## 环境配置

### 1. 创建环境变量文件

从示例文件创建`.env`：

```bash
cp .env-example .env
```

### 2. 常用的环境变量配置

```
# 服务基础配置
SERVICE_NAME=inquiry-service
SERVICE_ENV=development  # development, testing, production
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# LLM模型配置
USE_MOCK_MODE=true  # 开发环境使用mock模式
MOCK_EXTERNAL_SERVICES=true  # 模拟外部服务调用

# 服务端口配置
GRPC_PORT=50052
METRICS_PORT=9090
METRICS_ENABLED=false  # 开发环境关闭指标收集
```

### 3. 目录准备

确保创建必要的目录：

```bash
mkdir -p logs data/mock_responses
```

## 启动步骤

### 1. 启动开发环境服务

```bash
# 确保在项目根目录下运行
cd /path/to/services/inquiry-service

# 启动服务
python cmd/server.py
```

### 2. 使用Docker启动

```bash
# 构建镜像
docker build -t inquiry-service:latest .

# 运行容器
docker run -p 50052:50052 -p 9090:9090 --env-file .env inquiry-service:latest
```

### 3. 使用Docker Compose启动完整开发环境

```bash
docker-compose up -d
```

## 验证服务是否正常启动

服务正常启动后，日志输出应包含：

```
INFO - 问诊服务已启动，监听地址: 0.0.0.0:50052
```

可以使用grpcurl工具测试：

```bash
# 安装grpcurl（macOS）
brew install grpcurl

# 查看服务定义
grpcurl -plaintext localhost:50052 list

# 测试健康检查接口
grpcurl -plaintext localhost:50052 grpc.health.v1.Health/Check
```

## 运行模式说明

### 1. Mock模式

开发环境推荐使用Mock模式，避免依赖外部服务和LLM模型。Mock模式配置：

```yaml
# config/config.yaml
llm:
  use_mock_mode: true

mock:
  enabled: true
  response_delay_ms: 200
```

或通过环境变量：

```
USE_MOCK_MODE=true
MOCK_EXTERNAL_SERVICES=true
```

### 2. 本地模型推理模式

配置本地模型：

```yaml
# config/config.yaml
llm:
  model_type: "llama3"
  use_mock_mode: false
  local_inference: true
  local_model_path: "./data/models/tcm_medical_qa"
```

### 3. 远程API模式

使用远程LLM API：

```yaml
# config/config.yaml
llm:
  model_type: "gpt4"
  use_mock_mode: false
  local_inference: false
  remote_endpoint: "http://ai-inference-service:8080/v1"
```

## 常见问题与解决方案

### 路径相关问题

**问题**: 找不到模块或文件

```
ModuleNotFoundError: No module named 'internal'
```

**解决方案**:
1. 确保在正确的目录下运行：
   ```bash
   cd /path/to/services/inquiry-service
   python cmd/server.py
   ```

2. 如果仍有问题，显式设置PYTHONPATH：
   ```bash
   PYTHONPATH=/path/to/services/inquiry-service python cmd/server.py
   ```

### Python 3.13 兼容性问题

**问题**: 在Python 3.13中运行时出现事件循环错误：

```
RuntimeError: Task got Future attached to a different loop
```

**解决方案**:
- 已在最新版本修复，使用`asyncio.run()`代替`loop.run_until_complete()`
- 如果问题持续，可以尝试降级到Python 3.11或3.12

### gRPC反射导入错误

**问题**: 启动时出现反射模块导入错误：

```
ImportError: cannot import name 'service_identity'
```

**解决方案**:
1. 安装缺失的依赖：
   ```bash
   pip install service-identity
   ```

2. 关闭服务器反射（不推荐，但可临时使用）：
   在config.yaml中设置：
   ```yaml
   server:
     enable_reflection: false
   ```

### 外部服务连接问题

**问题**: 无法连接到其他微服务

**解决方案**:
1. 确认服务配置正确：
   ```yaml
   integration:
     xiaoai_service:
       host: "localhost"  # 开发环境使用localhost
       port: 50050
   ```

2. 启用Mock模式：
   ```
   MOCK_EXTERNAL_SERVICES=true
   ```

### 内存不足问题

**问题**: 启动LLM模型时出现OOM错误

**解决方案**:
1. 使用Mock模式进行开发
2. 减小模型量化精度：
   ```yaml
   llm:
     quantization: "int8"  # 或 "int4"
   ```
3. 调整模型加载参数：
   ```yaml
   llm:
     load_in_8bit: true
     device_map: "auto"
   ```

## 高级配置

### 性能调优

对于高流量场景：

```yaml
# 增加工作线程数
server:
  max_workers: 16
  max_concurrent_sessions: 1000

# 启用缓存
cache:
  enabled: true
  ttl_seconds: 3600
```

### 日志配置

调整日志级别和格式：

```yaml
logging:
  level: "info"  # 生产环境推荐info级别
  format: "json"  # json格式便于日志分析
  output: "both"  # 同时输出到控制台和文件
```

### 与Kubernetes集成

Kubernetes部署时的健康检查配置：

```yaml
health_check:
  enabled: true
  interval_seconds: 30
  timeout_seconds: 5
  unhealthy_threshold: 3
```

## 调试技巧

### 启用详细日志

```bash
LOG_LEVEL=DEBUG python cmd/server.py
```

### 使用交互式调试

```python
# 在代码中添加断点
import pdb; pdb.set_trace()
```

### 查看指标数据

服务开启指标收集后，访问：

```
http://localhost:9090/metrics
```

## 参考资源

- [gRPC Python文档](https://grpc.io/docs/languages/python/)
- [asyncio文档](https://docs.python.org/3/library/asyncio.html)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Prometheus文档](https://prometheus.io/docs/introduction/overview/) 