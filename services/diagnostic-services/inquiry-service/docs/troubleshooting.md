# 问诊服务问题排查指南

本文档提供了问诊服务（Inquiry Service）可能遇到的常见问题及详细排查步骤。

## 目录

1. [启动与环境问题](#启动与环境问题)
2. [事件循环与Python兼容性问题](#事件循环与python兼容性问题)
3. [LLM客户端问题](#llm客户端问题)
4. [gRPC相关问题](#grpc相关问题)
5. [依赖问题](#依赖问题)
6. [网络和连接问题](#网络和连接问题)
7. [性能问题](#性能问题)

## 启动与环境问题

### 找不到模块或文件

**症状**:
```
ModuleNotFoundError: No module named 'internal'
```
或
```
No such file or directory: '/path/to/cmd/server.py'
```

**原因**:
- 运行脚本时当前工作目录不正确
- Python路径设置不正确

**解决方案**:
1. 确保在项目根目录下运行:
   ```bash
   cd /absolute/path/to/services/inquiry-service
   python cmd/server.py
   ```

2. 如仍有问题，显式设置Python路径:
   ```bash
   PYTHONPATH=/absolute/path/to/services/inquiry-service python cmd/server.py
   ```
   
3. 使用Python模块导入方式:
   ```bash
   python -c "import sys; sys.path.insert(0, '.'); \
   from cmd.server import serve; serve()"
   ```

### 环境变量问题

**症状**:
配置未生效或使用了默认值，如日志级别没有应用

**原因**:
- `.env`文件未加载
- 环境变量格式有误

**解决方案**:
1. 检查`.env`文件是否存在于项目根目录
2. 验证环境变量格式:
   ```bash
   cat .env
   ```
3. 直接在命令行设置环境变量:
   ```bash
   LOG_LEVEL=DEBUG USE_MOCK_MODE=true python cmd/server.py
   ```

### 目录权限问题

**症状**:
```
PermissionError: [Errno 13] Permission denied: '/path/to/logs/inquiry_service.log'
```

**解决方案**:
1. 检查并创建必要目录:
   ```bash
   mkdir -p logs data/mock_responses
   chmod 755 logs data data/mock_responses
   ```

## 事件循环与Python兼容性问题

### Python 3.13 事件循环错误

**症状**:
```
RuntimeError: Task got Future attached to a different loop
```

**原因**:
Python 3.13对asyncio事件循环有重大变更，导致与旧代码不兼容

**解决方案**:
1. 已修复问题，使用最新版本的`server.py`，主要改动:
   - 使用`asyncio.run()`代替`loop.run_until_complete()`
   - 消除跨线程事件循环传递

2. 如果问题持续，可以降级Python版本:
   ```bash
   # 安装Python 3.11或3.12
   # macOS
   brew install python@3.11
   # 使用特定版本
   python3.11 cmd/server.py
   ```

### asyncio事件循环手动创建问题

**症状**:
```
RuntimeWarning: There is no current event loop in thread 'Thread-1'
```

**解决方案**:
1. 每个线程需要创建自己的事件循环:
   ```python
   def thread_function():
       loop = asyncio.new_event_loop()
       asyncio.set_event_loop(loop)
       # 执行异步代码
       loop.close()
   ```

2. 使用线程安全的方式传递任务:
   ```python
   # 不要将一个循环中创建的Future传递给另一个循环
   # 正确方式是使用回调或队列
   ```

## LLM客户端问题

### LLM依赖导入错误

**症状**:
```
ImportError: No module named 'aiohttp'
```
或
```
ImportError: No module named 'transformers'
```

**解决方案**:
1. 安装缺失的依赖:
   ```bash
   pip install aiohttp httpx transformers torch
   ```

2. 如果只需开发环境测试，启用Mock模式:
   ```
   USE_MOCK_MODE=true
   ```

### 模型加载失败

**症状**:
```
OSError: No file or directory found at ./data/models/tcm_medical_qa
```
或内存耗尽错误
```
CUDA out of memory
```

**解决方案**:
1. 使用Mock模式:
   ```yaml
   # config.yaml
   llm:
     use_mock_mode: true
   ```

2. 如确实需要加载模型:
   - 下载正确的模型文件到指定目录
   - 调整配置降低内存需求:
   ```yaml
   llm:
     load_in_8bit: true
     device_map: "auto"
   ```

### LLM响应格式错误

**症状**:
应用报错，通常是JSON解析错误:
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**解决方案**:
1. 检查llm_client.py中`_parse_response`方法
2. 确保配置或系统提示词指定了正确的输出格式
3. 修复已知的JSON错误处理问题:
   ```python
   try:
       parsed_json = json.loads(raw_response)
   except json.JSONDecodeError:
       # 降级处理为纯文本
       return {
           'response_text': raw_response,
           'response_type': 'TEXT',
           'detected_symptoms': [],
           'follow_up_questions': []
       }
   ```

## gRPC相关问题

### gRPC反射错误

**症状**:
```
ImportError: cannot import name 'reflection'
```
或
```
AttributeError: 'NoneType' object has no attribute 'services_by_name'
```

**解决方案**:
1. 安装gRPC反射库:
   ```bash
   pip install grpcio-reflection
   ```

2. 正确生成gRPC代码:
   ```bash
   python -m grpc_tools.protoc -I./api/grpc --python_out=. --grpc_python_out=. ./api/grpc/inquiry_service.proto
   ```

3. 增强错误处理，允许在缺少反射时继续:
   ```python
   try:
       # 启用反射代码
       # ...
   except Exception as e:
       logger.warning(f"启用反射失败: {str(e)}，继续启动服务")
   ```

### gRPC连接问题

**症状**:
客户端无法连接或调用服务

**解决方案**:
1. 确认服务监听地址和端口:
   ```bash
   # 检查端口是否被占用
   lsof -i :50052
   # 确认服务监听在正确地址
   netstat -an | grep 50052
   ```

2. 检查客户端连接参数

3. 使用gRPC调试工具:
   ```bash
   grpcurl -plaintext localhost:50052 list
   ```

## 依赖问题

### 缺少关键依赖

**症状**:
```
ModuleNotFoundError: No module named 'xxxx'
```

**解决方案**:
1. 安装个别依赖:
   ```bash
   pip install module_name
   ```

2. 安装全部依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 确保依赖版本匹配:
   ```bash
   pip list | grep module_name
   ```

### 版本冲突

**症状**:
```
ImportError: cannot import name 'xxx' from 'yyy'
```

**解决方案**:
1. 创建隔离环境:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. 查找并解决版本冲突:
   ```bash
   pip check
   ```

## 网络和连接问题

### 外部服务连接失败

**症状**:
```
ConnectionRefusedError: [Errno 111] Connection refused
```
或
```
Failed to connect to xxx service
```

**解决方案**:
1. 确认外部服务配置:
   ```yaml
   integration:
     xiaoai_service:
       host: "localhost"  # 确认主机名正确
       port: 50050        # 确认端口正确
   ```

2. 启用Mock模式:
   ```
   MOCK_EXTERNAL_SERVICES=true
   ```

3. 检查网络连接:
   ```bash
   # 测试端口连通性
   nc -zv host port
   # 查看路由
   traceroute host
   ```

### 超时问题

**症状**:
```
TimeoutError: xxxx
```

**解决方案**:
1. 增加超时配置:
   ```yaml
   server:
     timeout_seconds: 300
   integration:
     xiaoai_service:
       timeout_seconds: 30
   ```

2. 启用重试机制:
   ```yaml
   integration:
     xiaoai_service:
       retry_count: 3
       retry_interval_ms: 1000
   ```

## 性能问题

### 服务响应缓慢

**症状**:
API调用延迟高，处理时间长

**解决方案**:
1. 启用性能分析:
   ```python
   import cProfile
   cProfile.run('function_to_profile()')
   ```

2. 增加工作线程:
   ```yaml
   server:
     max_workers: 16
   ```

3. 启用缓存:
   ```yaml
   cache:
     enabled: true
     ttl_seconds: 3600
   ```

4. 启用Mock模式进行性能基准测试:
   ```
   USE_MOCK_MODE=true
   ```

### 内存消耗过高

**症状**:
服务内存占用快速增长或OOM错误

**解决方案**:
1. 使用内存分析工具:
   ```bash
   # 安装memory-profiler
   pip install memory-profiler
   
   # 使用方法
   @profile
   def memory_heavy_function():
       # 代码
   ```

2. 对象生命周期管理:
   ```python
   # 使用弱引用或显式释放大对象
   import weakref
   import gc
   
   # 显式垃圾回收
   gc.collect()
   ```

3. 启用内存监控:
   ```yaml
   metrics:
     memory_tracking_enabled: true
   ```

## 日志与诊断

### 启用详细日志

```bash
LOG_LEVEL=DEBUG python cmd/server.py
```

### 检查错误日志

```bash
tail -f logs/inquiry_service.log | grep ERROR
```

### 服务指标监控

启用Prometheus指标并查看:

```yaml
metrics:
  enabled: true
  port: 9090
```

访问 `http://localhost:9090/metrics` 查看关键指标。

## 故障报告

报告问题时，请提供以下信息:

1. Python版本: `python --version`
2. 依赖列表: `pip freeze`
3. 错误日志和完整堆栈跟踪
4. 复现步骤
5. 操作系统和环境信息

---

如有其他问题，请联系项目维护团队或提交GitHub Issue。 