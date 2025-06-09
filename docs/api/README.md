# 索克生活平台 API 文档

## 概述
索克生活平台提供统一的健康管理服务API，包括知识服务、支持服务、诊断服务和智能体服务。

## 基础信息
- **基础URL**: `https://api.suoke.life`
- **API版本**: v1
- **认证方式**: Bearer Token
- **数据格式**: JSON

## 服务端点

### 统一知识服务
- **基础路径**: `/api/knowledge/`
- **功能**: 医学知识管理、基准测试

#### 获取医学知识
```
GET /api/knowledge/medical/{topic}
```

### 统一支持服务  
- **基础路径**: `/api/support/`
- **功能**: 人工审核、无障碍支持

#### 提交审核请求
```
POST /api/support/review
```

### 诊断服务
- **基础路径**: `/api/diagnosis/`
- **功能**: 五诊服务（望闻问切算）

#### 开始诊断
```
POST /api/diagnosis/start
```

### 智能体服务
- **基础路径**: `/api/agents/`
- **功能**: AI智能体协作

#### 与智能体对话
```
POST /api/agents/{agent_name}/chat
```

## 错误处理
所有API错误都返回标准格式：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 限流
- 每个API密钥每分钟最多1000次请求
- 超出限制返回429状态码
