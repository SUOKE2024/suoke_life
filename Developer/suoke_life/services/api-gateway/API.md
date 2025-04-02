# 索克生活平台 API 网关 API 文档

## 概述

索克生活平台API网关提供以下功能：

- 统一的API访问入口
- 路由和服务发现
- 身份验证和授权
- 流量管理（限流、熔断）
- 监控和日志
- 缓存
- 灰度发布和A/B测试

## 基础端点

### 健康检查

```
GET /health
```

返回API网关的健康状态。

**响应示例**：

```json
{
  "status": "ok",
  "service": "api-gateway",
  "version": "1.0.0",
  "timestamp": "2023-03-29T12:34:56.789Z"
}
```

### 就绪检查

```
GET /health/ready
```

检查API网关和后端服务是否准备好接受请求。

**响应示例**：

```json
{
  "status": "ready",
  "uptime": 1234,
  "services": {
    "user-service": {
      "available": true,
      "urls": 2
    },
    "auth-service": {
      "available": true,
      "urls": 1
    }
  }
}
```

### 服务指标

```
GET /metrics/prometheus
```

以Prometheus格式返回API网关和服务指标。

## 用户服务 API

### 获取用户信息

```
GET /api/users/profile
```

获取当前登录用户的资料。

**请求头**：

- `Authorization`: Bearer {token}

**响应示例**：

```json
{
  "id": "user123",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2023-01-01T12:00:00Z"
}
```

## 认证服务 API

### 用户登录

```
POST /api/auth/login
```

**请求体**：

```json
{
  "username": "zhangsan",
  "password": "password123"
}
```

**响应示例**：

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2023-03-30T12:34:56.789Z",
  "user": {
    "id": "user123",
    "username": "zhangsan"
  }
}
```

### 用户注册

```
POST /api/auth/register
```

**请求体**：

```json
{
  "username": "lisi",
  "email": "lisi@example.com",
  "password": "securepass123"
}
```

**响应示例**：

```json
{
  "success": true,
  "message": "注册成功",
  "user": {
    "id": "user456",
    "username": "lisi",
    "email": "lisi@example.com"
  }
}
```

## 灰度发布管理 API

### 获取所有灰度发布配置

```
GET /api/canary
```

返回所有服务的灰度发布配置。

**请求头**：

- `Authorization`: Bearer {admin_token}

**响应示例**：

```json
{
  "status": "success",
  "data": {
    "knowledge-graph-service": {
      "enabled": true,
      "versions": [
        {
          "name": "stable",
          "weight": 80
        },
        {
          "name": "beta",
          "weight": 20
        }
      ],
      "metrics": {
        "requests": {
          "stable": 150,
          "beta": 42
        },
        "errors": {
          "stable": 2,
          "beta": 3
        },
        "latency": {
          "stable": {
            "avg": 120,
            "min": 45,
            "max": 350
          },
          "beta": {
            "avg": 95,
            "min": 40,
            "max": 280
          }
        },
        "errorRate": 0.0333
      }
    }
  }
}
```

### 获取特定服务的灰度发布配置

```
GET /api/canary/:serviceName
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称

**响应示例**：

```json
{
  "status": "success",
  "data": {
    "serviceName": "knowledge-graph-service",
    "enabled": true,
    "versions": [
      {
        "name": "stable",
        "url": "http://knowledge-graph-service:3003",
        "weight": 80
      },
      {
        "name": "beta",
        "url": "http://knowledge-graph-service-beta:3003",
        "weight": 20
      }
    ],
    "defaultVersion": "stable",
    "rules": [
      {
        "type": "header",
        "name": "x-beta-tester",
        "values": ["true"],
        "targetVersion": "beta"
      },
      {
        "type": "query",
        "name": "version",
        "values": ["beta"],
        "targetVersion": "beta"
      }
    ],
    "metrics": {
      "requests": {
        "stable": 150,
        "beta": 42
      },
      "errors": {
        "stable": 2,
        "beta": 3
      },
      "latency": {
        "stable": {
          "avg": 120,
          "min": 45,
          "max": 350
        },
        "beta": {
          "avg": 95,
          "min": 40,
          "max": 280
        }
      }
    }
  }
}
```

### 创建或更新灰度发布配置

```
PUT /api/canary/:serviceName
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称

**请求体**：

```json
{
  "enabled": true,
  "versions": [
    {
      "name": "stable",
      "url": "http://knowledge-graph-service:3003",
      "weight": 70
    },
    {
      "name": "beta",
      "url": "http://knowledge-graph-service-beta:3003",
      "weight": 30
    }
  ],
  "defaultVersion": "stable",
  "rules": [
    {
      "type": "header",
      "name": "x-beta-tester",
      "values": ["true"],
      "targetVersion": "beta"
    },
    {
      "type": "query",
      "name": "version",
      "values": ["beta"],
      "targetVersion": "beta"
    }
  ]
}
```

**响应示例**：

```json
{
  "status": "success",
  "message": "成功更新 knowledge-graph-service 灰度发布配置",
  "data": {
    "serviceName": "knowledge-graph-service",
    "enabled": true,
    "versions": [
      {
        "name": "stable",
        "url": "http://knowledge-graph-service:3003",
        "weight": 70
      },
      {
        "name": "beta",
        "url": "http://knowledge-graph-service-beta:3003",
        "weight": 30
      }
    ],
    "defaultVersion": "stable",
    "rules": [
      {
        "type": "header",
        "name": "x-beta-tester",
        "values": ["true"],
        "targetVersion": "beta"
      },
      {
        "type": "query",
        "name": "version",
        "values": ["beta"],
        "targetVersion": "beta"
      }
    ]
  }
}
```

### 启用/禁用灰度发布

```
PATCH /api/canary/:serviceName/toggle
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称

**请求体**：

```json
{
  "enabled": true
}
```

**响应示例**：

```json
{
  "status": "success",
  "message": "已启用 knowledge-graph-service 的灰度发布",
  "data": {
    "enabled": true
  }
}
```

### 重置服务的灰度发布指标

```
POST /api/canary/:serviceName/reset-metrics
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称

**响应示例**：

```json
{
  "status": "success",
  "message": "已重置 knowledge-graph-service 的灰度发布指标"
}
```

### 添加路由规则

```
POST /api/canary/:serviceName/rules
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称

**请求体**：

```json
{
  "type": "device",
  "values": ["mobile"],
  "targetVersion": "mobile-optimized"
}
```

**响应示例**：

```json
{
  "status": "success",
  "message": "成功添加规则",
  "data": {
    "rules": [
      {
        "type": "header",
        "name": "x-beta-tester",
        "values": ["true"],
        "targetVersion": "beta"
      },
      {
        "type": "query",
        "name": "version",
        "values": ["beta"],
        "targetVersion": "beta"
      },
      {
        "type": "device",
        "values": ["mobile"],
        "targetVersion": "mobile-optimized"
      }
    ]
  }
}
```

### 删除路由规则

```
DELETE /api/canary/:serviceName/rules/:ruleIndex
```

**请求头**：

- `Authorization`: Bearer {admin_token}

**路径参数**：

- `serviceName`: 服务名称
- `ruleIndex`: 规则索引

**响应示例**：

```json
{
  "status": "success",
  "message": "成功删除规则",
  "data": {
    "rules": [
      {
        "type": "header",
        "name": "x-beta-tester",
        "values": ["true"],
        "targetVersion": "beta"
      },
      {
        "type": "device",
        "values": ["mobile"],
        "targetVersion": "mobile-optimized"
      }
    ]
  }
}
```

## 灰度发布客户端使用

### 指定版本

客户端可以通过以下方式指定使用特定版本：

1. 添加请求头：
   ```
   X-Canary-Version: beta
   ```

2. 添加查询参数：
   ```
   ?canary_version=beta
   ```

### A/B测试场景

当进行A/B测试时，API网关会根据配置的规则自动将用户分配到不同版本。每个响应都会包含版本信息：

**响应头**：
```
X-Served-By: knowledge-graph-service:beta
```

这样，客户端可以识别请求由哪个版本处理，并收集相应的用户反馈和性能指标。