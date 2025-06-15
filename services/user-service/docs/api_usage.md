# 索克生活用户服务 API 使用指南

本文档提供了用户服务API的详细使用说明，包括REST API和gRPC API的调用方法和示例。

## REST API

### 基础信息

- 基础URL: `https://api.suoke.life/v1`
- 认证方式: Bearer Token (JWT)
- 内容类型: `application/json`

### 认证

所有API请求都需要在HTTP头部包含有效的认证令牌:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 创建用户

**请求**:

```http
POST /api/v1/users
Content-Type: application/json

{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "phone": "+8613800138000",
  "fullName": "张三",
  "password": "Password123!",
  "metadata": {
    "country": "China",
    "region": "Beijing"
  }
}
```

**响应**:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "userId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "phone": "+8613800138000",
  "fullName": "张三",
  "createdAt": "2023-09-15T08:00:00Z",
  "updatedAt": "2023-09-15T08:00:00Z",
  "status": "active",
  "metadata": {
    "country": "China",
    "region": "Beijing"
  },
  "roles": ["user"],
  "preferences": {}
}
```

### 获取用户信息

**请求**:

```http
GET /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "phone": "+8613800138000",
  "fullName": "张三",
  "createdAt": "2023-09-15T08:00:00Z",
  "updatedAt": "2023-09-15T08:00:00Z",
  "status": "active",
  "metadata": {
    "country": "China",
    "region": "Beijing"
  },
  "roles": ["user"],
  "preferences": {
    "theme": "light",
    "language": "zh-CN"
  }
}
```

### 更新用户信息

**请求**:

```http
PUT /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "phone": "+8613900139000",
  "fullName": "张三丰",
  "metadata": {
    "country": "China",
    "region": "Shanghai"
  }
}
```

**响应**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "phone": "+8613900139000",
  "fullName": "张三丰",
  "createdAt": "2023-09-15T08:00:00Z",
  "updatedAt": "2023-09-15T09:00:00Z",
  "status": "active",
  "metadata": {
    "country": "China",
    "region": "Shanghai"
  },
  "roles": ["user"],
  "preferences": {
    "theme": "light",
    "language": "zh-CN"
  }
}
```

### 获取用户健康摘要

**请求**:

```http
GET /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479/health-summary
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "dominantConstitution": "balanced",
  "recentMetrics": [
    {
      "metricName": "height",
      "value": 175.0,
      "unit": "cm",
      "timestamp": "2023-09-14T10:00:00Z"
    },
    {
      "metricName": "weight",
      "value": 68.5,
      "unit": "kg",
      "timestamp": "2023-09-14T10:00:00Z"
    },
    {
      "metricName": "bmi",
      "value": 22.4,
      "unit": "",
      "timestamp": "2023-09-14T10:00:00Z"
    }
  ],
  "lastAssessmentDate": "2023-09-14T10:00:00Z",
  "healthScore": 85,
  "constitutionScores": {
    "balanced": 0.8,
    "qi_deficiency": 0.2,
    "yang_deficiency": 0.1,
    "yin_deficiency": 0.1,
    "phlegm_dampness": 0.3,
    "damp_heat": 0.2,
    "blood_stasis": 0.1,
    "qi_depression": 0.1,
    "special": 0.0
  }
}
```

### 绑定设备

**请求**:

```http
POST /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479/devices
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "deviceId": "device-123456",
  "deviceType": "smartphone",
  "deviceName": "我的华为手机",
  "deviceMetadata": {
    "os": "Android",
    "model": "Huawei P40",
    "osVersion": "12"
  }
}
```

**响应**:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "success": true,
  "bindingId": "b47ac10b-58cc-4372-a567-0e02b2c3d999",
  "bindingTime": "2023-09-15T10:00:00Z"
}
```

### 获取设备列表

**请求**:

```http
GET /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479/devices
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "devices": [
    {
      "deviceId": "device-123456",
      "deviceType": "smartphone",
      "deviceName": "我的华为手机",
      "bindingTime": "2023-09-15T10:00:00Z",
      "bindingId": "b47ac10b-58cc-4372-a567-0e02b2c3d999",
      "isActive": true,
      "lastActiveTime": "2023-09-15T15:30:00Z",
      "deviceMetadata": {
        "os": "Android",
        "model": "Huawei P40",
        "osVersion": "12"
      }
    }
  ]
}
```

### 解绑设备

**请求**:

```http
DELETE /api/v1/users/f47ac10b-58cc-4372-a567-0e02b2c3d479/devices/device-123456
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```http
HTTP/1.1 204 No Content
```

## gRPC API

### 环境设置

1. 引入 protobuf 定义文件: `api/grpc/user.proto`
2. 使用语言特定工具生成客户端代码
3. 设置连接和认证

### 示例 (Python)

```python
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from protobuf.suoke.user.v1 import user_pb2, user_pb2_grpc

# 连接设置
channel = grpc.insecure_channel('api.suoke.life:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

# 认证设置
metadata = [('authorization', f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')]

# 创建用户
def create_user():
    request = user_pb2.CreateUserRequest(
        username="zhangsan",
        email="zhangsan@example.com",
        phone="+8613800138000",
        full_name="张三",
        password_hash="已加密的密码哈希",  # 注意：客户端应该在发送前进行哈希处理
    )
    
    # 添加元数据
    request.metadata["country"] = "China"
    request.metadata["region"] = "Beijing"
    
    # 发送请求
    response = stub.CreateUser(request, metadata=metadata)
    print(f"User created with ID: {response.user_id}")
    return response

# 获取用户信息
def get_user(user_id):
    request = user_pb2.GetUserRequest(
        user_id=user_id
    )
    
    # 发送请求
    response = stub.GetUser(request, metadata=metadata)
    print(f"User details: {response.username}, {response.email}")
    return response

# 更新用户信息
def update_user(user_id):
    request = user_pb2.UpdateUserRequest(
        user_id=user_id,
        phone="+8613900139000",
        full_name="张三丰"
    )
    
    # 添加元数据
    request.metadata["country"] = "China"
    request.metadata["region"] = "Shanghai"
    
    # 发送请求
    response = stub.UpdateUser(request, metadata=metadata)
    print(f"User updated: {response.username}, {response.phone}")
    return response

# 绑定设备
def bind_device(user_id):
    request = user_pb2.BindDeviceRequest(
        user_id=user_id,
        device_id="device-123456",
        device_type="smartphone",
        device_name="我的华为手机"
    )
    
    # 添加设备元数据
    request.device_info["os"] = "Android"
    request.device_info["model"] = "Huawei P40"
    request.device_info["osVersion"] = "12"
    
    # 发送请求
    response = stub.BindUserDevice(request, metadata=metadata)
    print(f"Device bound: {response.binding_id}")
    return response

# 获取用户健康摘要
def get_health_summary(user_id):
    request = user_pb2.GetUserRequest(
        user_id=user_id
    )
    
    # 发送请求
    response = stub.GetUserHealthSummary(request, metadata=metadata)
    print(f"Health score: {response.health_score}")
    return response
```

### 示例 (Go)

```go
package main

import (
    "context"
    "log"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/metadata"
    
    pb "github.com/suoke_life/user-service/protobuf/suoke/user/v1"
)

func main() {
    // 连接设置
    conn, err := grpc.Dial("api.suoke.life:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("Failed to connect: %v", err)
    }
    defer conn.Close()
    
    client := pb.NewUserServiceClient(conn)
    
    // 认证设置
    ctx := metadata.AppendToOutgoingContext(
        context.Background(),
        "authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    
    // 创建用户
    createUser(ctx, client)
}

func createUser(ctx context.Context, client pb.UserServiceClient) {
    req := &pb.CreateUserRequest{
        Username:     "zhangsan",
        Email:        "zhangsan@example.com",
        PhoneNumber:  "+8613800138000",
        FullName:     "张三",
        PasswordHash: "已加密的密码哈希",
        Metadata:     map[string]string{
            "country": "China",
            "region":  "Beijing",
        },
    }
    
    resp, err := client.CreateUser(ctx, req)
    if err != nil {
        log.Fatalf("Could not create user: %v", err)
    }
    
    log.Printf("User created with ID: %s", resp.UserId)
}

func getUserHealthSummary(ctx context.Context, client pb.UserServiceClient, userID string) {
    req := &pb.GetUserRequest{
        UserId: userID,
    }
    
    resp, err := client.GetUserHealthSummary(ctx, req)
    if err != nil {
        log.Fatalf("Could not get health summary: %v", err)
    }
    
    log.Printf("Health score: %d", resp.HealthScore)
    log.Printf("Dominant constitution: %s", resp.DominantConstitution.String())
}
```

## 错误处理

### REST API 错误响应

所有错误响应都遵循以下格式:

```json
{
  "code": "ERROR_CODE",
  "message": "错误描述",
  "details": {
    "field": "错误字段",
    "reason": "具体原因"
  },
  "requestId": "追踪ID"
}
```

常见错误代码:

| HTTP状态码 | 错误代码 | 描述 |
|----------|----------|-----|
| 400 | INVALID_PARAMETER | 请求参数无效 |
| 401 | UNAUTHORIZED | 未授权访问 |
| 403 | FORBIDDEN | 没有操作权限 |
| 404 | USER_NOT_FOUND | 用户不存在 |
| 404 | DEVICE_NOT_FOUND | 设备不存在 |
| 409 | USER_ALREADY_EXISTS | 用户名或邮箱已存在 |
| 409 | DEVICE_ALREADY_BOUND | 设备已绑定 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

### gRPC API 错误处理

gRPC API 使用标准 gRPC 状态码和错误详情：

| gRPC状态码 | 描述 |
|-----------|-----|
| INVALID_ARGUMENT | 请求参数无效 |
| UNAUTHENTICATED | 未授权访问 |
| PERMISSION_DENIED | 没有操作权限 |
| NOT_FOUND | 资源不存在 |
| ALREADY_EXISTS | 资源已存在 |
| INTERNAL | 服务器内部错误 |

## 最佳实践

1. **总是使用TLS连接**：确保所有API调用都通过HTTPS/TLS进行
2. **使用适当的认证**：正确设置和更新认证令牌
3. **实现错误重试**：对于网络故障或服务端错误，实现指数退避重试
4. **处理时区问题**：所有时间戳都是UTC格式，在客户端处理时区转换
5. **缓存用户数据**：减少对服务器的频繁请求，但确保设置合理的缓存过期时间

## 使用示例

### 注册并完善用户资料流程

1. 通过 `POST /api/v1/users` 创建基本用户
2. 通过 `PUT /api/v1/users/{userId}` 补充详细资料
3. 通过 `PUT /api/v1/users/{userId}/preferences` 设置用户偏好
4. 通过 `POST /api/v1/users/{userId}/devices` 绑定设备

### 健康数据访问流程

1. 通过 `GET /api/v1/users/{userId}/health-summary` 获取健康摘要
2. 根据健康摘要数据，使用其他服务API获取详细健康报告 