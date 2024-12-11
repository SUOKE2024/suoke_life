# API设计文档

## 1. API概述

### 1.1 基础信息
- 基础URL: https://api.suoke.life
- 版本: v1
- 格式: JSON
- 认证: Bearer Token

### 1.2 通用规范
- 时间格式: ISO 8601
- 编码: UTF-8
- 分页: 基于cursor
- 限流: 基于令牌桶

## 2. 认证接口

### 2.1 用户认证
```
POST /api/v1/auth/login
Request:
{
    "username": string,
    "password": string
}
Response:
{
    "token": string,
    "expires_in": number
}
```

### 2.2 令牌刷新
```
POST /api/v1/auth/refresh
Header:
    Authorization: Bearer {token}
Response:
{
    "token": string,
    "expires_in": number
}
```

## 3. 数据分析接口

### 3.1 用户图谱分析
```
POST /api/v1/analysis/user-graph
Request:
{
    "user_id": string,
    "data_type": ["behavior", "health", "preference"],
    "time_range": {
        "start": datetime,
        "end": datetime
    }
}
Response:
{
    "graph_data": {
        "nodes": [...],
        "edges": [...],
        "metrics": {...}
    }
}
```

### 3.2 行为模式分析
```
POST /api/v1/analysis/behavior
Request:
{
    "user_id": string,
    "behavior_data": [...],
    "analysis_type": string
}
Response:
{
    "patterns": [...],
    "recommendations": [...]
}
```

## 4. AI服务接口

### 4.1 对话服务
```
POST /api/v1/ai/chat
Request:
{
    "user_id": string,
    "message": string,
    "context": [...],
    "preferences": {...}
}
Response:
{
    "reply": string,
    "suggestions": [...],
    "context_id": string
}
```

### 4.2 个性化建议
```
POST /api/v1/ai/recommend
Request:
{
    "user_id": string,
    "scenario": string,
    "user_data": {...}
}
Response:
{
    "recommendations": [...],
    "explanation": string
}
```

## 5. 数据集管理接口

### 5.1 数据上传
```
POST /api/v1/dataset/upload
Request:
{
    "type": string,
    "data": [...],
    "metadata": {
        "source": string,
        "timestamp": datetime,
        "quality_score": number
    }
}
Response:
{
    "dataset_id": string,
    "status": string,
    "validation_results": {...}
}
```

### 5.2 数据验证
```
POST /api/v1/dataset/validate
Request:
{
    "dataset_id": string,
    "validation_rules": [...]
}
Response:
{
    "is_valid": boolean,
    "errors": [...],
    "quality_metrics": {...}
}
```

## 6. 系统管理接口

### 6.1 健康检查
```
GET /api/v1/system/health
Response:
{
    "status": string,
    "components": {
        "database": string,
        "cache": string,
        "ai_service": string
    }
}
```

### 6.2 性能指标
```
GET /api/v1/system/metrics
Response:
{
    "cpu_usage": number,
    "memory_usage": number,
    "api_latency": number,
    "active_users": number
}
```

## 7. 错误处理

### 7.1 错误码
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 429: 请求过于频繁
- 500: 服务器错误

### 7.2 错误响应格式
```
{
    "error": {
        "code": number,
        "message": string,
        "details": {...}
    }
} 