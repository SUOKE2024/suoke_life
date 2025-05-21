# 消息总线客户端SDK使用文档

## 概述

消息总线客户端SDK提供了一个简洁易用的接口，用于与消息总线服务进行通信。通过SDK，您可以轻松地发布和订阅消息，以及管理消息主题。

## 安装

您可以通过以下方式安装消息总线客户端SDK：

### 方式一：直接使用项目代码

如果您的项目在同一代码库中，可以直接导入：

```python
from pkg.client import MessageBusClient
```

### 方式二：使用pip安装

```bash
pip install suoke-message-bus-client
```

## 基本用法

### 初始化客户端

```python
from pkg.client import MessageBusClient

# 创建客户端
client = MessageBusClient(
    endpoint="localhost:50051",  # 服务地址
    auth_token=None,             # 认证令牌（可选）
    timeout=10,                  # 请求超时时间（秒）
    max_retries=3,               # 最大重试次数
    secure=False                 # 是否使用TLS加密连接
)

# 使用上下文管理器
with MessageBusClient(endpoint="localhost:50051") as client:
    # 使用客户端
    pass  # 自动关闭连接
```

### 发布消息

```python
# 发布简单消息
result = client.publish(
    topic="my.topic",
    payload="Hello, world!"
)

# 发布JSON消息
result = client.publish(
    topic="user.activity",
    payload={"user_id": "user123", "action": "login", "timestamp": 1617293845}
)

# 发布带属性的消息
result = client.publish(
    topic="health.data.updated",
    payload={"user_id": "user123", "data_type": "steps", "value": 10000},
    attributes={"priority": "high", "source": "mobile-app"}
)

# 获取消息ID和发布时间
message_id = result["message_id"]
publish_time = result["publish_time"]
print(f"消息已发布，ID: {message_id}")
```

### 订阅消息

```python
import asyncio

# 定义异步消息处理函数
async def handle_message(message):
    print(f"收到消息: {message['id']}")
    payload = message["payload"]
    attributes = message["attributes"]
    
    # 处理消息内容
    if isinstance(payload, bytes):
        # 假设是JSON格式
        try:
            payload_json = json.loads(payload.decode('utf-8'))
            print(f"消息内容: {payload_json}")
        except:
            print(f"原始消息内容: {payload}")
    
    # 处理消息属性
    priority = attributes.get("priority", "normal")
    print(f"消息优先级: {priority}")

# 订阅主题
subscription = client.subscribe(
    topic="health.data.updated",
    callback=handle_message,
    filter_attributes={"priority": "high"}  # 只接收高优先级消息
)

# 保持订阅一段时间
await asyncio.sleep(60)

# 取消订阅
subscription.unsubscribe()

# 或使用上下文管理器自动取消订阅
with client.subscribe(topic="my.topic", callback=handle_message) as subscription:
    # 订阅在此处活动
    await asyncio.sleep(60)
    # 离开上下文时自动取消订阅
```

### 主题管理

```python
# 创建主题
topic_info = client.create_topic(
    name="user.activity",
    description="用户活动记录",
    properties={"domain": "user", "category": "activity"},
    partition_count=3,
    retention_hours=24
)

# 获取主题信息
topic = client.get_topic("user.activity")
print(f"主题名称: {topic['name']}")
print(f"描述: {topic['description']}")
print(f"创建时间: {topic['creation_time']}")

# 列出所有主题
topics, next_page_token, total = client.list_topics(page_size=10)
for topic in topics:
    print(f"主题: {topic['name']}")

# 分页获取主题
while next_page_token:
    topics, next_page_token, total = client.list_topics(
        page_size=10, 
        page_token=next_page_token
    )
    for topic in topics:
        print(f"主题: {topic['name']}")

# 删除主题
success = client.delete_topic("user.activity")
if success:
    print("主题已删除")
```

### 健康检查

```python
# 检查服务健康状态
status = client.health_check()
if status == "SERVING":
    print("服务健康正常")
else:
    print(f"服务异常: {status}")
```

## 异常处理

SDK会抛出以下异常：

- `ValueError`: 当业务逻辑出错时（例如，主题不存在）
- `TypeError`: 当参数类型不正确时
- `grpc.RpcError`: 当RPC调用失败时
- `ConnectionError`: 当连接失败时

例如：

```python
try:
    client.publish("nonexistent_topic", "Hello")
except ValueError as e:
    print(f"业务逻辑错误: {e}")
except grpc.RpcError as e:
    print(f"RPC错误: {e.code()}, {e.details()}")
```

## 高级用法

### 异步使用模式

```python
import asyncio

async def main():
    client = MessageBusClient("localhost:50051")
    
    # 创建订阅
    messages_received = []
    
    async def collect_messages(message):
        messages_received.append(message)
    
    # 订阅主题
    with client.subscribe("my.topic", collect_messages) as subscription:
        # 发布一些消息
        for i in range(5):
            client.publish("my.topic", f"Message {i}")
            await asyncio.sleep(0.1)
        
        # 等待接收所有消息
        await asyncio.sleep(1)
    
    # 处理收到的所有消息
    for message in messages_received:
        print(f"收到: {message['payload']}")
    
    client.close()

# 运行主函数
asyncio.run(main())
```

### 使用认证

```python
# 获取认证令牌
auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# 创建带认证的客户端
client = MessageBusClient(
    endpoint="message-bus.suoke-life.com:443",
    auth_token=auth_token,
    secure=True  # 生产环境使用TLS加密
)

# 使用客户端
client.publish("secure.topic", "敏感数据")
```

## 最佳实践

1. **重用客户端**: 创建一个客户端实例并在整个应用程序中重用它，而不是频繁创建和销毁。

2. **错误处理**: 始终使用try-except捕获并处理可能的异常，特别是在发布和订阅消息时。

3. **合理设置超时**: 根据网络环境和操作类型设置合适的超时时间。

4. **优雅清理**: 使用完客户端后调用`close()`方法，或使用上下文管理器自动关闭。

5. **消息结构**: 采用一致的消息结构，推荐使用JSON格式的payload，并通过attributes提供元数据。

6. **订阅管理**: 当不再需要订阅时，务必调用`unsubscribe()`方法取消订阅，以释放资源。

7. **安全性**: 在生产环境中始终使用TLS加密连接（secure=True）和身份验证（auth_token）。 