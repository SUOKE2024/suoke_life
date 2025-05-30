# A2A 智能体网络微服务 API 文档

## 概述

A2A 智能体网络微服务提供 REST API 和 gRPC API 两种接口方式，用于管理智能体网络、执行工作流和监控系统状态。

## 基础信息

- **基础URL**: `http://localhost:5000`
- **API版本**: v1
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证

当前版本暂不需要认证，后续版本将支持 API Key 认证。

## 错误处理

所有 API 响应都遵循统一的格式：

```json
{
  "success": true|false,
  "data": {},
  "error": "错误信息",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP 状态码

- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误

## REST API 接口

### 1. 健康检查

检查服务健康状态。

**请求**
```
GET /health
```

**响应**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "a2a-agent-network"
}
```

### 2. 智能体管理

#### 2.1 获取所有智能体

**请求**
```
GET /api/v1/agents
```

**响应**
```json
{
  "success": true,
  "data": [
    {
      "id": "xiaoai",
      "name": "小艾智能体",
      "description": "健康咨询和诊断智能体",
      "version": "1.0.0",
      "status": "online",
      "url": "http://xiaoai-service:5001",
      "capabilities": [
        {
          "name": "four_diagnoses_coordination",
          "description": "五诊合参功能",
          "enabled": true
        }
      ],
      "last_heartbeat": "2024-01-15T10:29:00Z",
      "metadata": {}
    }
  ],
  "total": 4
}
```

#### 2.2 获取指定智能体信息

**请求**
```
GET /api/v1/agents/{agent_id}
```

**路径参数**
- `agent_id` (string): 智能体ID

**响应**
```json
{
  "success": true,
  "data": {
    "id": "xiaoai",
    "name": "小艾智能体",
    "status": "online",
    "url": "http://xiaoai-service:5001",
    "capabilities": ["diagnosis", "consultation"],
    "last_heartbeat": "2024-01-15T10:29:00Z"
  }
}
```

#### 2.3 获取智能体指标

**请求**
```
GET /api/v1/agents/{agent_id}/metrics
```

**响应**
```json
{
  "success": true,
  "data": {
    "agent_id": "xiaoai",
    "request_count": 150,
    "success_count": 145,
    "error_count": 5,
    "avg_response_time": 1.25,
    "last_request_time": "2024-01-15T10:28:00Z",
    "uptime": 86400.0
  }
}
```

#### 2.4 执行智能体动作

**请求**
```
POST /api/v1/agents/{agent_id}/execute
```

**请求体**
```json
{
  "action": "diagnose",
  "parameters": {
    "symptoms": "头痛、发热",
    "duration": "2天"
  },
  "user_id": "user123",
  "request_id": "req_456",
  "timeout": 30
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "diagnosis": "感冒",
    "confidence": 0.85,
    "recommendations": ["多休息", "多喝水"]
  },
  "execution_time": 1.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. 网络状态

#### 3.1 获取网络状态

**请求**
```
GET /api/v1/network/status
```

**响应**
```json
{
  "success": true,
  "data": {
    "total_agents": 4,
    "online_agents": 3,
    "offline_agents": 1,
    "network_health": 0.75,
    "agents": {
      "xiaoai": "online",
      "xiaoke": "online",
      "laoke": "online",
      "soer": "offline"
    }
  }
}
```

### 4. 工作流管理

#### 4.1 获取工作流列表

**请求**
```
GET /api/v1/workflows
```

**响应**
```json
{
  "success": true,
  "data": [
    {
      "id": "health_consultation",
      "name": "健康咨询工作流",
      "description": "用户健康咨询的完整处理流程",
      "steps": [
        {
          "id": "reception",
          "agent": "xiaoai",
          "action": "接收用户咨询"
        },
        {
          "id": "diagnosis_assessment",
          "agent": "xiaoai",
          "action": "诊断体质评估"
        },
        {
          "id": "knowledge_support",
          "agent": "laoke",
          "action": "提供知识支持"
        },
        {
          "id": "health_profile",
          "agent": "soer",
          "action": "生成健康画像"
        }
      ]
    }
  ],
  "total": 3
}
```

#### 4.2 执行工作流

**请求**
```
POST /api/v1/workflows/execute
```

**请求体**
```json
{
  "workflow_id": "health_consultation",
  "user_id": "user123",
  "parameters": {
    "consultation_type": "症状咨询",
    "symptoms": "头痛、失眠",
    "user_profile": {
      "age": 30,
      "gender": "female"
    }
  },
  "context": {
    "session_id": "session_789"
  },
  "priority": 1,
  "timeout": 300
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_123456",
    "workflow_id": "health_consultation",
    "status": "started",
    "message": "工作流 health_consultation 已开始执行"
  }
}
```

#### 4.3 获取工作流执行状态

**请求**
```
GET /api/v1/workflows/executions/{execution_id}
```

**响应**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_123456",
    "workflow_id": "health_consultation",
    "workflow_name": "健康咨询工作流",
    "status": "completed",
    "user_id": "user123",
    "start_time": "2024-01-15T10:25:00Z",
    "end_time": "2024-01-15T10:28:00Z",
    "execution_time": 180.5,
    "steps_completed": 4,
    "total_steps": 4,
    "result": {
      "diagnosis": "气虚体质",
      "recommendations": ["调理作息", "适量运动"],
      "health_score": 75
    }
  }
}
```

### 5. 监控指标

#### 5.1 获取所有指标

**请求**
```
GET /api/v1/metrics
```

**响应**
```json
{
  "success": true,
  "data": [
    {
      "agent_id": "xiaoai",
      "request_count": 150,
      "success_count": 145,
      "error_count": 5,
      "avg_response_time": 1.25,
      "last_request_time": "2024-01-15T10:28:00Z"
    }
  ],
  "total": 4
}
```

## gRPC API 接口

### 服务定义

```protobuf
service AgentNetworkService {
  rpc RegisterAgent(RegisterAgentRequest) returns (RegisterAgentResponse);
  rpc SendRequest(AgentRequest) returns (AgentResponse);
  rpc ExecuteWorkflow(WorkflowRequest) returns (WorkflowResponse);
  rpc GetNetworkStatus(NetworkStatusRequest) returns (NetworkStatusResponse);
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### 使用示例

#### Python 客户端

```python
import grpc
from api.grpc import agent_service_pb2, agent_service_pb2_grpc

# 创建连接
channel = grpc.insecure_channel('localhost:50051')
stub = agent_service_pb2_grpc.AgentNetworkServiceStub(channel)

# 发送请求
request = agent_service_pb2.AgentRequest(
    agent_id="xiaoai",
    action="diagnose",
    user_id="user123",
    request_id="req_456"
)

response = stub.SendRequest(request)
print(f"Success: {response.success}")
print(f"Data: {response.data}")
```

#### Go 客户端

```go
package main

import (
    "context"
    "log"
    
    "google.golang.org/grpc"
    pb "github.com/suoke-life/a2a-agent-network/api/grpc/v1"
)

func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()
    
    client := pb.NewAgentNetworkServiceClient(conn)
    
    req := &pb.AgentRequest{
        AgentId:   "xiaoai",
        Action:    "diagnose",
        UserId:    "user123",
        RequestId: "req_456",
    }
    
    resp, err := client.SendRequest(context.Background(), req)
    if err != nil {
        log.Fatal(err)
    }
    
    log.Printf("Success: %v", resp.Success)
}
```

## WebSocket API

### 实时监控

连接到 WebSocket 端点以接收实时更新：

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/monitor');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('实时更新:', data);
};

// 订阅智能体状态更新
ws.send(JSON.stringify({
    type: 'subscribe',
    topic: 'agent_status'
}));
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 1001 | 智能体不存在 |
| 1002 | 智能体离线 |
| 1003 | 请求超时 |
| 2001 | 工作流不存在 |
| 2002 | 工作流执行失败 |
| 3001 | 参数验证失败 |
| 5001 | 内部服务错误 |

## 限流说明

- 每个 IP 每分钟最多 100 个请求
- 每个用户每分钟最多 50 个工作流执行请求
- 超出限制将返回 429 状态码

## 版本兼容性

- v1.0.x: 当前稳定版本
- 向后兼容保证：主版本号不变时保持 API 兼容性
- 废弃通知：废弃的 API 将在下一个主版本中移除

## 联系支持

- 技术文档: https://docs.suoke-life.com/a2a-network
- 问题反馈: https://github.com/suoke-life/a2a-agent-network/issues
- 邮箱支持: api-support@suoke-life.com 