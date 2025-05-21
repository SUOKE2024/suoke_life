# 索克生活APP服务间通信规范

## 目录

- [通信模式概述](#通信模式概述)
- [服务发现机制](#服务发现机制)
- [同步通信 (gRPC)](#同步通信-grpc)
- [异步通信 (Kafka)](#异步通信-kafka)
- [请求跟踪与监控](#请求跟踪与监控)
- [错误处理与重试策略](#错误处理与重试策略)
- [服务降级与断路器](#服务降级与断路器)
- [服务网格集成](#服务网格集成)
- [安全通信](#安全通信)

## 通信模式概述

索克生活APP微服务架构采用以下通信模式：

1. **同步通信**：通过gRPC实现服务间直接调用，适用于需要立即响应的场景
2. **异步通信**：通过Kafka实现事件驱动架构，适用于异步处理和松耦合场景
3. **混合通信**：根据业务场景需要，结合使用同步和异步通信方式

选择通信模式的指导原则：

| 通信模式 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| **同步 (gRPC)** | 用户请求响应链、需要立即结果的操作 | 低延迟、强类型、双向流 | 服务耦合度高、故障传播风险 |
| **异步 (Kafka)** | 非核心流程、可后台处理的任务、解耦服务 | 服务解耦、削峰填谷、容错性高 | 增加系统复杂性、最终一致性挑战 |

## 服务发现机制

索克生活APP采用Consul作为服务发现和配置中心，实现服务自动注册和发现。

### 服务注册流程

1. 服务启动时自动向Consul注册
2. 注册信息包括：服务名称、版本、IP地址、端口、健康检查URL
3. 定期发送心跳保持注册有效

示例注册配置：

```yaml
consul:
  host: "consul.suokelife.com"
  port: 8500
  service:
    name: "auth-service"
    version: "v1"
    tags: ["prod", "auth", "security"]
    meta:
      api_version: "v1.2.3"
      team: "security-team"
    check:
      http: "http://localhost:8080/health"
      interval: "10s"
      timeout: "1s"
```

### 服务发现使用指南

#### 客户端发现模式

在客户端直接查询Consul获取服务实例：

```python
def get_service_instances(service_name, version=None, tags=None):
    """获取服务实例列表"""
    consul_client = Consul(host=CONSUL_HOST, port=CONSUL_PORT)
    service_instances = consul_client.catalog.service(service_name)
    
    # 过滤版本和标签
    if version or tags:
        filtered_instances = []
        for instance in service_instances:
            if version and instance['ServiceMeta']['version'] != version:
                continue
            if tags and not all(tag in instance['ServiceTags'] for tag in tags):
                continue
            filtered_instances.append(instance)
        return filtered_instances
    
    return service_instances
```

#### 服务网关发现模式

API网关通过Consul发现并路由请求：

```yaml
# Kong服务发现配置
services:
  - name: auth-service
    host: auth-service.service.consul
    port: 80
    protocol: http
    path: /
    plugins:
      - name: consul-discovery
        config:
          service_name: auth-service
          tags: ["prod"]
```

## 同步通信 (gRPC)

### gRPC服务定义规范

所有gRPC服务必须遵循以下Protobuf定义规范：

1. 使用proto3语法
2. 包含版本信息
3. 使用明确的命名约定
4. 提供详细注释

示例：

```protobuf
syntax = "proto3";

package suokelife.auth.v1;

import "google/protobuf/timestamp.proto";

// AuthService 提供用户认证和授权功能
service AuthService {
  // Login 处理用户登录请求并返回访问令牌
  rpc Login(LoginRequest) returns (LoginResponse) {}
  
  // Verify 验证令牌有效性并返回用户信息
  rpc VerifyToken(VerifyTokenRequest) returns (VerifyTokenResponse) {}
}

// LoginRequest 登录请求参数
message LoginRequest {
  // 用户名或电子邮件
  string username = 1;
  // 密码（明文传输，使用TLS加密）
  string password = 2;
}

// LoginResponse 登录响应
message LoginResponse {
  // 访问令牌
  string access_token = 1;
  // 刷新令牌
  string refresh_token = 2;
  // 令牌过期时间
  google.protobuf.Timestamp expires_at = 3;
}

// ... 其他消息定义
```

### gRPC客户端实现指南

#### 连接管理

所有微服务必须实现连接池和优雅的连接管理：

```python
class GrpcClientManager:
    """gRPC客户端管理器，实现连接池和重试机制"""
    
    def __init__(self, service_name, max_connections=10):
        self.service_name = service_name
        self.connection_pool = {}
        self.max_connections = max_connections
        self.lock = threading.Lock()
    
    def get_client(self, service_version="v1"):
        """获取指定版本的服务客户端"""
        key = f"{self.service_name}:{service_version}"
        
        with self.lock:
            if key not in self.connection_pool:
                # 从Consul获取服务实例
                instances = get_service_instances(self.service_name, version=service_version)
                if not instances:
                    raise ServiceDiscoveryError(f"No {self.service_name} instances found")
                
                # 创建gRPC通道和客户端
                instance = random.choice(instances)  # 简单负载均衡
                channel = grpc.insecure_channel(f"{instance['ServiceAddress']}:{instance['ServicePort']}")
                
                # 根据服务名动态创建客户端
                if self.service_name == "auth-service":
                    from suokelife.auth.v1 import auth_pb2_grpc
                    client = auth_pb2_grpc.AuthServiceStub(channel)
                elif self.service_name == "user-service":
                    from suokelife.user.v1 import user_pb2_grpc
                    client = user_pb2_grpc.UserServiceStub(channel)
                # ... 其他服务
                
                self.connection_pool[key] = {
                    "client": client,
                    "channel": channel,
                    "created_at": time.time()
                }
            
            return self.connection_pool[key]["client"]
    
    def refresh_connections(self, max_age=3600):
        """定期刷新超过指定年龄的连接"""
        with self.lock:
            current_time = time.time()
            for key, conn_info in list(self.connection_pool.items()):
                if current_time - conn_info["created_at"] > max_age:
                    conn_info["channel"].close()
                    del self.connection_pool[key]
```

#### 超时和重试策略

gRPC调用应设置合理的超时和重试策略：

```python
def call_with_retry(grpc_method, request, max_retries=3, timeout=5):
    """带重试机制的gRPC调用"""
    retry_count = 0
    last_exception = None
    
    while retry_count < max_retries:
        try:
            metadata = [
                ("x-request-id", generate_request_id()),
                ("x-client-version", CLIENT_VERSION)
            ]
            
            # 设置超时时间
            return grpc_method(request, timeout=timeout, metadata=metadata)
        
        except grpc.RpcError as e:
            last_exception = e
            status_code = e.code()
            
            # 只对特定错误类型进行重试
            if status_code in [grpc.StatusCode.UNAVAILABLE, 
                              grpc.StatusCode.DEADLINE_EXCEEDED]:
                retry_count += 1
                wait_time = min(2 ** retry_count, 10)  # 指数退避
                time.sleep(wait_time)
                continue
            else:
                # 非临时性错误不重试
                raise
    
    # 超过重试次数，抛出最后一个异常
    raise GrpcCallError(f"Failed after {max_retries} retries") from last_exception
```

### 服务间身份验证

服务间调用必须进行身份验证，采用JWT或mTLS：

```python
def get_service_token():
    """获取服务间调用的JWT令牌"""
    payload = {
        "iss": SERVICE_NAME,
        "sub": "service-account",
        "aud": "internal-services",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4())
    }
    
    return jwt.encode(payload, SERVICE_JWT_SECRET, algorithm="HS256")

def create_secure_channel(target, service_name):
    """创建带服务身份验证的gRPC通道"""
    # 添加令牌认证拦截器
    auth_interceptor = TokenAuthInterceptor(get_service_token())
    
    # 创建带拦截器的通道
    return grpc.intercept_channel(
        grpc.insecure_channel(target),
        auth_interceptor
    )

class TokenAuthInterceptor(grpc.UnaryUnaryClientInterceptor,
                          grpc.UnaryStreamClientInterceptor,
                          grpc.StreamUnaryClientInterceptor,
                          grpc.StreamStreamClientInterceptor):
    """gRPC身份验证拦截器"""
    
    def __init__(self, token):
        self.token = token
    
    def _add_token(self, metadata):
        metadata = list(metadata) if metadata else []
        metadata.append(("authorization", f"Bearer {self.token}"))
        return metadata
    
    # ... 实现拦截器方法
```

## 异步通信 (Kafka)

### 事件命名和结构

所有Kafka事件必须遵循以下命名和结构规范：

#### 主题命名规范

Kafka主题命名格式：`{环境}.{服务名}.{事件类型}.{版本}`

例如：
- `prod.auth-service.user-registered.v1`
- `prod.health-service.vital-signs-recorded.v2`

#### 事件内容结构

每个事件消息必须包含以下标准字段：

```json
{
  "meta": {
    "id": "unique-event-id",
    "type": "user-registered",
    "version": "1.0",
    "source": "auth-service",
    "time": "2023-11-10T12:34:56Z",
    "correlation_id": "request-correlation-id"
  },
  "data": {
    // 事件特定数据
  }
}
```

### 事件生产者实现

每个服务的事件生产者应实现以下功能：

1. 事件架构验证
2. 至少一次递送保证
3. 生产者确认机制
4. 死信队列处理

示例实现：

```python
class EventProducer:
    """Kafka事件生产者"""
    
    def __init__(self, bootstrap_servers, service_name, env="prod"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks="all",  # 要求所有副本确认
            retries=5,
            retry_backoff_ms=100,
            max_in_flight_requests_per_connection=1,  # 确保消息顺序
            enable_idempotence=True  # 避免重复消息
        )
        self.service_name = service_name
        self.env = env
    
    def emit_event(self, event_type, data, version="v1", correlation_id=None, partition_key=None):
        """发出事件到Kafka"""
        topic = f"{self.env}.{self.service_name}.{event_type}.{version}"
        
        # 构建事件内容
        event = {
            "meta": {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "version": version,
                "source": self.service_name,
                "time": datetime.utcnow().isoformat() + "Z",
                "correlation_id": correlation_id or "none"
            },
            "data": data
        }
        
        # 发送事件
        future = self.producer.send(topic, value=event, key=partition_key)
        
        try:
            # 同步等待确认
            record_metadata = future.get(timeout=10)
            logger.info(f"Event published: {event_type}, partition: {record_metadata.partition}, offset: {record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {event_type}, error: {str(e)}")
            # 记录到死信队列
            self._log_to_dlq(topic, event, str(e))
            return False
    
    def _log_to_dlq(self, topic, event, error):
        """记录失败事件到死信队列"""
        dlq_topic = f"{topic}.dlq"
        event["meta"]["error"] = error
        event["meta"]["original_topic"] = topic
        event["meta"]["dlq_time"] = datetime.utcnow().isoformat() + "Z"
        
        try:
            self.producer.send(dlq_topic, value=event).get(timeout=10)
        except Exception as e:
            logger.critical(f"Failed to log to DLQ: {dlq_topic}, error: {str(e)}")
    
    def close(self):
        """关闭生产者连接"""
        self.producer.flush()
        self.producer.close()
```

### 事件消费者实现

事件消费者实现应包含以下特性：

1. 自动重试机制
2. 幂等处理
3. 并行处理
4. 优雅关闭

示例实现：

```python
class EventConsumer:
    """Kafka事件消费者"""
    
    def __init__(self, bootstrap_servers, group_id, topics, handlers, max_poll_records=500):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            max_poll_records=max_poll_records
        )
        self.handlers = handlers
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def start(self):
        """启动消费者处理循环"""
        self.running = True
        futures = []
        
        try:
            while self.running:
                messages = self.consumer.poll(timeout_ms=1000, max_records=10)
                
                for partition, msg_batch in messages.items():
                    for msg in msg_batch:
                        event = msg.value
                        event_type = event["meta"]["type"]
                        
                        if event_type in self.handlers:
                            # 提交到线程池处理
                            future = self.executor.submit(
                                self._process_event,
                                event,
                                event_type,
                                msg.partition,
                                msg.offset
                            )
                            futures.append(future)
                
                # 处理完成的任务
                done_futures = [f for f in futures if f.done()]
                for future in done_futures:
                    futures.remove(future)
                    # 检查异常
                    if future.exception():
                        logger.error(f"Event processing error: {future.exception()}")
                
                # 提交偏移量
                self.consumer.commit()
        
        finally:
            # 等待所有任务完成
            for future in futures:
                future.result()
            
            self.consumer.close()
            self.executor.shutdown()
    
    def _process_event(self, event, event_type, partition, offset):
        """处理单个事件"""
        handler = self.handlers[event_type]
        correlation_id = event["meta"].get("correlation_id", "none")
        
        logger.info(f"Processing event: {event_type}, correlation_id: {correlation_id}, partition: {partition}, offset: {offset}")
        
        try:
            # 调用事件处理器
            handler(event)
            return True
        except Exception as e:
            logger.error(f"Failed to process event: {event_type}, error: {str(e)}")
            # 可以实现重试逻辑或记录到死信队列
            return False
    
    def stop(self):
        """优雅停止消费者"""
        self.running = False
```

### 事件架构注册中心

使用Schema Registry管理和验证事件架构：

```python
class EventSchemaRegistry:
    """事件架构注册中心客户端"""
    
    def __init__(self, schema_registry_url):
        self.client = SchemaRegistryClient({'url': schema_registry_url})
        self.cache = {}
    
    def register_schema(self, topic, schema_str):
        """注册事件架构"""
        schema = avro.schema.parse(schema_str)
        schema_id = self.client.register(topic + "-value", schema)
        return schema_id
    
    def get_schema(self, topic, version=None):
        """获取事件架构"""
        cache_key = f"{topic}:{version or 'latest'}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if version:
            schema = self.client.get_by_version(topic + "-value", version)
        else:
            schema = self.client.get_latest_version(topic + "-value")
        
        self.cache[cache_key] = schema
        return schema
    
    def validate_event(self, topic, event_data):
        """验证事件数据符合架构"""
        schema = self.get_schema(topic)
        parsed_schema = avro.schema.parse(schema.schema.schema_str)
        
        try:
            validate(parsed_schema, event_data)
            return True
        except ValidationError as e:
            logger.error(f"Event validation failed for topic {topic}: {str(e)}")
            return False
```

## 请求跟踪与监控

### 分布式追踪实现

所有服务间通信必须实现分布式追踪，以跟踪完整请求路径：

```python
def setup_tracing(service_name):
    """设置分布式追踪"""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    
    jaeger_exporter = JaegerExporter(
        agent_host_name=JAEGER_HOST,
        agent_port=JAEGER_PORT,
        service_name=service_name
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    return trace.get_tracer(service_name)

def trace_grpc_call(tracer, method_name, request, metadata=None):
    """跟踪gRPC调用"""
    with tracer.start_as_current_span(method_name) as span:
        # 添加请求信息到跟踪
        span.set_attribute("rpc.service", "SomeService")
        span.set_attribute("rpc.method", method_name)
        
        if hasattr(request, "username"):
            span.set_attribute("request.username", request.username)
        
        # 获取当前跟踪上下文并传递给下游服务
        if metadata is None:
            metadata = []
        
        from opentelemetry.propagate import inject
        carrier = {}
        inject(carrier)
        
        for key, value in carrier.items():
            metadata.append((key, value))
        
        return metadata
```

### 请求ID传播

所有服务间通信必须传递请求ID，以关联同一请求的所有操作：

```python
def generate_request_id():
    """生成唯一请求ID"""
    return str(uuid.uuid4())

def get_current_request_id():
    """从上下文获取当前请求ID"""
    from contextvars import ContextVar
    request_id_var = ContextVar("request_id", default=None)
    request_id = request_id_var.get()
    
    if request_id is None:
        request_id = generate_request_id()
        request_id_var.set(request_id)
    
    return request_id

class RequestIDMiddleware:
    """FastAPI中间件，处理请求ID"""
    
    async def __call__(self, request, call_next):
        # 尝试从请求头获取请求ID
        request_id = request.headers.get("X-Request-ID")
        
        # 如果没有，生成新的请求ID
        if not request_id:
            request_id = generate_request_id()
        
        # 存储到上下文
        request_id_var = ContextVar("request_id")
        request_id_var.set(request_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 在响应中包含请求ID
        response.headers["X-Request-ID"] = request_id
        
        return response
```

## 错误处理与重试策略

### 全局错误处理策略

所有微服务应实现统一的错误处理策略：

```python
class ServiceError(Exception):
    """服务错误基类"""
    
    def __init__(self, code, message, details=None, retry=False, timeout=0):
        self.code = code
        self.message = message
        self.details = details or {}
        self.retry = retry  # 是否建议重试
        self.timeout = timeout  # 建议的重试等待时间（秒）
        super().__init__(message)

class TemporaryServiceError(ServiceError):
    """临时性服务错误，可以重试"""
    
    def __init__(self, code, message, details=None, timeout=1):
        super().__init__(code, message, details, retry=True, timeout=timeout)

class PermanentServiceError(ServiceError):
    """永久性服务错误，不应重试"""
    
    def __init__(self, code, message, details=None):
        super().__init__(code, message, details, retry=False)

class ServiceUnavailableError(TemporaryServiceError):
    """服务不可用错误"""
    
    def __init__(self, service_name, details=None):
        super().__init__(
            "service_unavailable",
            f"{service_name} service is currently unavailable",
            details,
            timeout=5
        )
```

### 重试策略实现

微服务间调用应实现自适应重试策略：

```python
def with_retry(fn, max_retries=3, retry_conditions=None, backoff_factor=2, max_backoff=30):
    """带重试机制的函数装饰器"""
    retry_conditions = retry_conditions or [
        lambda e: isinstance(e, TemporaryServiceError),
        lambda e: isinstance(e, ConnectionError),
        lambda e: isinstance(e, TimeoutError)
    ]
    
    def should_retry(exception):
        """判断是否应该重试"""
        return any(condition(exception) for condition in retry_conditions)
    
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        retries = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                retries += 1
                
                if retries > max_retries or not should_retry(e):
                    raise
                
                # 计算退避时间
                if hasattr(e, "timeout") and e.timeout > 0:
                    wait_time = e.timeout
                else:
                    wait_time = min(backoff_factor ** retries, max_backoff)
                
                logger.warning(f"Retrying {fn.__name__} after error: {str(e)}, attempt {retries}/{max_retries}, waiting {wait_time}s")
                time.sleep(wait_time)
    
    return wrapper
```

## 服务降级与断路器

每个微服务应实现断路器模式，防止故障级联：

```python
class CircuitBreaker:
    """断路器实现"""
    
    # 断路器状态
    STATE_CLOSED = "closed"  # 正常状态，允许请求通过
    STATE_OPEN = "open"      # 熔断状态，拒绝所有请求
    STATE_HALF_OPEN = "half_open"  # 半开状态，允许部分请求尝试
    
    def __init__(self, failure_threshold=5, recovery_timeout=30, name="default"):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0
        self.half_open_success_threshold = 3
        self.lock = threading.RLock()
    
    def __call__(self, fn):
        """将断路器作为装饰器使用"""
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise ServiceUnavailableError(
                    f"Circuit breaker '{self.name}' is open",
                    details={"recovery_time": self.recovery_time_left()}
                )
            
            try:
                result = fn(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise
        
        return wrapper
    
    def allow_request(self):
        """判断是否允许请求通过"""
        with self.lock:
            if self.state == self.STATE_CLOSED:
                return True
            
            if self.state == self.STATE_OPEN:
                # 检查是否超过恢复时间
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = self.STATE_HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' changed from OPEN to HALF_OPEN")
                    return True
                return False
            
            # 半开状态允许有限请求
            return True
    
    def record_success(self):
        """记录成功请求"""
        with self.lock:
            if self.state == self.STATE_HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_success_threshold:
                    self.state = self.STATE_CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info(f"Circuit breaker '{self.name}' changed from HALF_OPEN to CLOSED")
    
    def record_failure(self):
        """记录失败请求"""
        with self.lock:
            self.last_failure_time = time.time()
            
            if self.state == self.STATE_HALF_OPEN:
                self.state = self.STATE_OPEN
                logger.warning(f"Circuit breaker '{self.name}' changed from HALF_OPEN to OPEN")
                return
            
            if self.state == self.STATE_CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = self.STATE_OPEN
                    logger.warning(f"Circuit breaker '{self.name}' changed from CLOSED to OPEN")
    
    def recovery_time_left(self):
        """返回距离恢复尝试的剩余时间"""
        if self.state != self.STATE_OPEN:
            return 0
        
        elapsed = time.time() - self.last_failure_time
        remaining = max(0, self.recovery_timeout - elapsed)
        return int(remaining)
```

### 降级策略实现

服务应提供降级机制，在依赖服务不可用时提供有限功能：

```python
def with_fallback(fallback_fn, error_types=None):
    """降级处理装饰器"""
    error_types = error_types or (Exception,)
    
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except error_types as e:
                logger.warning(f"Function {fn.__name__} failed, using fallback: {str(e)}")
                return fallback_fn(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@with_fallback(lambda user_id: {"id": user_id, "name": "Unknown", "is_cached": True})
def get_user_profile(user_id):
    # 尝试从用户服务获取完整资料
    response = user_client.get_profile(user_id)
    return response.profile
```

## 服务网格集成

索克生活APP的微服务架构将逐步集成Istio服务网格，提供以下能力：

1. 统一流量管理
2. 安全通信
3. 策略执行
4. 可观测性

### Istio集成指南

每个微服务在Kubernetes部署时应添加以下注解，启用Istio注入：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  template:
    metadata:
      annotations:
        sidecar.istio.io/inject: "true"
        proxy.istio.io/config: |
          tracing:
            zipkin:
              address: zipkin.observability:9411
        sidecar.istio.io/rewriteAppHTTPProbers: "true"
```

### 流量管理策略

使用Istio VirtualService和DestinationRule实现流量控制：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: auth-service
spec:
  hosts:
  - auth-service
  http:
  - name: "v2-routes"
    match:
    - headers:
        x-api-version:
          exact: "v2"
    route:
    - destination:
        host: auth-service
        subset: v2
  - name: "v1-routes"
    route:
    - destination:
        host: auth-service
        subset: v1
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: auth-service
spec:
  host: auth-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### 故障注入测试

使用Istio故障注入测试服务弹性：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: auth-service-fault-injection
spec:
  hosts:
  - auth-service
  http:
  - fault:
      delay:
        percentage:
          value: 10.0
        fixedDelay: 5s
      abort:
        percentage:
          value: 5.0
        httpStatus: 500
    route:
    - destination:
        host: auth-service
```

## 安全通信

### 服务间双向TLS

所有服务间通信应启用mTLS：

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

### 敏感信息传输

敏感信息应加密后传输：

```python
def encrypt_sensitive_data(data, public_key):
    """使用公钥加密敏感数据"""
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    
    encrypted = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()

def decrypt_sensitive_data(encrypted_data, private_key):
    """使用私钥解密敏感数据"""
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    
    decoded = base64.b64decode(encrypted_data)
    decrypted = private_key.decrypt(
        decoded,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()
```

## 结论

索克生活APP的服务间通信规范为微服务提供了一致、高效和可靠的通信机制。所有开发团队必须遵循这些准则，以确保系统的整体性能、可靠性和安全性。

本文档应根据实际经验和新需求定期更新，确保始终反映最佳实践。