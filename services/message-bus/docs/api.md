# 消息总线服务 API 文档

## 概述

消息总线服务提供基于gRPC的API，用于发布和订阅消息，以及管理消息主题。本文档详细介绍了服务的API接口定义、请求/响应格式和使用示例。

## 目录

- [服务定义](#服务定义)
- [消息发布](#消息发布)
- [主题管理](#主题管理)
- [消息订阅](#消息订阅)
- [健康检查](#健康检查)
- [错误处理](#错误处理)
- [使用示例](#使用示例)

## 服务定义

消息总线服务提供以下主要功能：

- 消息发布：将消息发布到指定主题
- 主题管理：创建、删除、获取和列出主题
- 消息订阅：订阅主题以接收消息更新
- 健康检查：检查服务健康状态

## 消息发布

### PublishMessage

将消息发布到指定主题。

**请求 (PublishRequest)**

```protobuf
message PublishRequest {
  string topic = 1;              // 主题名称
  bytes payload = 2;             // 消息主体内容
  map<string, string> attributes = 3; // 消息属性
}
```

**响应 (PublishResponse)**

```protobuf
message PublishResponse {
  string message_id = 1;         // 已发布消息的ID
  int64 publish_time = 2;        // 服务器处理发布的时间戳
  bool success = 3;              // 是否发布成功
  string error_message = 4;      // 错误信息(如果有)
}
```

**示例**

```python
# 创建客户端
client = MessageBusClient(endpoint="localhost:50051")

# 发布消息
response = client.publish(
    topic="health.data.updated",
    payload={"user_id": "user123", "data_type": "steps", "value": 10000},
    attributes={"priority": "high"}
)

# 检查结果
if response.success:
    print(f"消息已发布，ID: {response.message_id}")
else:
    print(f"发布失败: {response.error_message}")
```

## 主题管理

### CreateTopic

创建新的消息主题。

**请求 (CreateTopicRequest)**

```protobuf
message CreateTopicRequest {
  string name = 1;               // 主题名称
  string description = 2;        // 主题描述
  map<string, string> properties = 3; // 主题属性
  int32 partition_count = 4;     // 分区数量
  int32 retention_hours = 5;     // 消息保留时间(小时)
}
```

**响应 (CreateTopicResponse)**

```protobuf
message CreateTopicResponse {
  bool success = 1;              // 是否创建成功
  string error_message = 2;      // 错误信息(如果有)
  Topic topic = 3;               // 已创建的主题信息
}
```

### GetTopic

获取指定主题的详细信息。

**请求 (GetTopicRequest)**

```protobuf
message GetTopicRequest {
  string name = 1;               // 主题名称
}
```

**响应 (GetTopicResponse)**

```protobuf
message GetTopicResponse {
  Topic topic = 1;               // 主题信息
  bool success = 2;              // 是否成功
  string error_message = 3;      // 错误信息(如果有)
}
```

### ListTopics

获取所有主题的列表，支持分页。

**请求 (ListTopicsRequest)**

```protobuf
message ListTopicsRequest {
  int32 page_size = 1;           // 每页大小
  string page_token = 2;         // 分页标记
}
```

**响应 (ListTopicsResponse)**

```protobuf
message ListTopicsResponse {
  repeated Topic topics = 1;     // 主题列表
  string next_page_token = 2;    // 下一页标记
  int32 total_count = 3;         // 总主题数
}
```

### DeleteTopic

删除指定的主题。

**请求 (DeleteTopicRequest)**

```protobuf
message DeleteTopicRequest {
  string name = 1;               // 主题名称
}
```

**响应 (DeleteTopicResponse)**

```protobuf
message DeleteTopicResponse {
  bool success = 1;              // 是否删除成功
  string error_message = 2;      // 错误信息(如果有)
}
```

**示例**

```python
# 创建主题
create_response = client.create_topic(
    name="user.activity",
    description="用户活动记录",
    properties={"domain": "user", "category": "activity"},
    partition_count=3,
    retention_hours=24
)

# 获取主题
topic = client.get_topic("user.activity")

# 列出所有主题
topics, next_page_token, total = client.list_topics(page_size=10)

# 删除主题
success = client.delete_topic("user.activity")
```

## 消息订阅

### Subscribe

订阅主题以接收消息更新，实现流式传输。

**请求 (SubscribeRequest)**

```protobuf
message SubscribeRequest {
  string topic = 1;              // 主题名称
  string subscription_name = 2;  // 订阅名称
  map<string, string> filter = 3; // 消息过滤条件
  bool acknowledge = 4;          // 是否需要确认
  int32 max_messages = 5;        // 最大批量消息数
  int32 timeout_seconds = 6;     // 超时时间(秒)
}
```

**响应 (SubscribeResponse)**

```protobuf
message SubscribeResponse {
  repeated Message messages = 1; // 消息列表
}
```

**示例**

```python
# 定义消息处理回调
def message_handler(message):
    print(f"收到消息: {message}")
    # 处理消息...

# 订阅主题
subscription = client.subscribe(
    topic="health.data.updated",
    subscription_name="health-monitor",
    callback=message_handler,
    filter_attributes={"priority": "high"}
)

# 运行一段时间后取消订阅
subscription.unsubscribe()
```

## 健康检查

### HealthCheck

检查服务健康状态。

**请求 (HealthCheckRequest)**

```protobuf
message HealthCheckRequest {
  string service = 1;            // 服务名称
}
```

**响应 (HealthCheckResponse)**

```protobuf
message HealthCheckResponse {
  enum ServingStatus {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
    SERVICE_UNKNOWN = 3;
  }
  ServingStatus status = 1;      // 服务状态
}
```

**示例**

```python
# 健康检查
status = client.health_check()

if status == HealthCheckResponse.ServingStatus.SERVING:
    print("服务健康状态正常")
else:
    print("服务异常")
```

## 错误处理

服务使用标准的gRPC错误代码和详细的错误消息来指示各种错误情况：

| 错误代码                  | 描述                        | 常见原因                     |
|-------------------------|----------------------------|----------------------------|
| INVALID_ARGUMENT        | 无效参数                     | 主题名称无效、消息格式错误       |
| NOT_FOUND               | 资源不存在                   | 指定的主题不存在              |
| ALREADY_EXISTS          | 资源已存在                   | 尝试创建已存在的主题           |
| PERMISSION_DENIED       | 权限不足                     | 没有操作权限                 |
| RESOURCE_EXHAUSTED      | 资源耗尽                     | 超出配额或速率限制            |
| UNAVAILABLE             | 服务不可用                   | 服务暂时不可用                |
| INTERNAL                | 内部错误                     | 服务器内部错误                |

所有API接口都可能返回这些错误，客户端应该准备适当处理。

## 使用示例

### Python 客户端完整示例

```python
from message_bus.client import MessageBusClient

# 创建客户端
client = MessageBusClient(endpoint="localhost:50051")

# 创建主题
client.create_topic(
    name="system.events",
    description="系统事件通知",
    partition_count=3,
    retention_hours=48
)

# 发布消息
client.publish(
    topic="system.events",
    payload={"event_type": "server_start", "server_id": "srv-001"},
    attributes={"component": "auth-service", "severity": "info"}
)

# 定义消息处理回调
def process_system_event(message):
    event_data = message.payload_as_json
    print(f"收到系统事件: {event_data}")
    
    # 基于事件类型处理
    if event_data.get("event_type") == "server_start":
        print(f"服务器 {event_data.get('server_id')} 已启动")

# 订阅消息
subscription = client.subscribe(
    topic="system.events",
    subscription_name="system-monitor",
    callback=process_system_event,
    filter_attributes={"component": "auth-service"}
)

# 运行一段时间...

# 取消订阅
subscription.unsubscribe()

# 关闭客户端
client.close()
```

### Go 客户端示例

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    pb "github.com/suoke-life/message-bus/api/grpc"
    "google.golang.org/grpc"
)

func main() {
    // 创建连接
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("连接失败: %v", err)
    }
    defer conn.Close()
    
    // 创建客户端
    client := pb.NewMessageBusServiceClient(conn)
    ctx := context.Background()
    
    // 发布消息
    publishResp, err := client.PublishMessage(ctx, &pb.PublishRequest{
        Topic: "system.events",
        Payload: []byte(`{"event_type":"config_update","component":"api-gateway"}`),
        Attributes: map[string]string{
            "severity": "info",
            "source": "control-plane",
        },
    })
    
    if err != nil {
        log.Fatalf("发布消息失败: %v", err)
    }
    
    fmt.Printf("消息已发布，ID: %s\n", publishResp.MessageId)
    
    // 订阅消息
    stream, err := client.Subscribe(ctx, &pb.SubscribeRequest{
        Topic: "system.events",
        SubscriptionName: "go-client-sub",
        Filter: map[string]string{
            "severity": "info",
        },
    })
    
    if err != nil {
        log.Fatalf("订阅失败: %v", err)
    }
    
    // 接收消息
    for {
        resp, err := stream.Recv()
        if err != nil {
            log.Printf("接收消息错误: %v", err)
            break
        }
        
        for _, msg := range resp.Messages {
            fmt.Printf("收到消息: ID=%s, 主题=%s\n", msg.Id, msg.Topic)
            // 处理消息...
        }
    }
}
```

## 最佳实践

1. **错误处理**: 总是检查API调用的响应状态，并实现适当的重试逻辑。

2. **订阅设计**: 对于每个逻辑组件或功能，创建单独的订阅，而不是使用一个订阅处理所有消息。

3. **消息过滤**: 使用属性过滤来减少客户端接收和处理的消息数量。

4. **主题命名**: 使用层次化命名方案（如`domain.entity.action`）来组织主题。

5. **消息格式**: 尽可能使用结构化数据格式如JSON，并包含足够的元数据。

6. **异步处理**: 消息处理应该是异步的，避免在回调中执行长时间运行的操作。

7. **监控**: 实现对发布/订阅操作的监控，跟踪延迟、错误率等指标。 