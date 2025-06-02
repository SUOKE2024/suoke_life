# 索克生活API文档

## 🔌 API接口概览

### 健康数据API

#### 获取用户健康数据
```typescript
GET /api/health/data/:userId

Response: ApiResponse<HealthData>
{
  success: boolean;
  data: {
    vitals: VitalSigns;
    symptoms: Symptom[];
    diagnosis: DiagnosisResult;
    recommendations: Recommendation[];
  };
  message?: string;
  error?: ApiError;
}
```

#### 提交健康数据
```typescript
POST /api/health/data

Body: {
  userId: string;
  vitals: VitalSigns;
  symptoms: Symptom[];
  timestamp: number;
}

Response: ApiResponse<{ id: string }>
```

### 智能体API

#### 发送消息给智能体
```typescript
POST /api/agents/:agentId/message

Body: {
  content: string;
  userId: string;
  context?: any;
}

Response: ApiResponse<AgentMessage>
```

#### 获取对话历史
```typescript
GET /api/agents/:agentId/history/:userId

Response: ApiResponse<AgentMessage[]>
```

### 用户管理API

#### 用户注册
```typescript
POST /api/users/register

Body: {
  username: string;
  email: string;
  password: string;
  profile: UserProfile;
}

Response: ApiResponse<User>
```

#### 用户登录
```typescript
POST /api/users/login

Body: {
  email: string;
  password: string;
}

Response: ApiResponse<{
  user: User;
  token: string;
}>
```

## 🔒 认证和授权

所有API请求需要在Header中包含认证token：

```
Authorization: Bearer <token>
```

## 📊 错误处理

API使用统一的错误响应格式：

```typescript
{
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
```

### 常见错误码

- `AUTH_REQUIRED`: 需要认证
- `INVALID_TOKEN`: 无效的认证token
- `PERMISSION_DENIED`: 权限不足
- `VALIDATION_ERROR`: 请求参数验证失败
- `RESOURCE_NOT_FOUND`: 资源不存在
- `INTERNAL_ERROR`: 服务器内部错误

## 🚀 使用示例

### React Native中的API调用

```typescript
import { apiClient } from '../services/apiClient';

// 获取健康数据
const fetchHealthData = async (userId: string) => {
  try {
    const response = await apiClient.get<HealthData>(`/health/data/${userId}`);
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.error?.message);
    }
  } catch (error) {
    Logger.error('获取健康数据失败', error);
    throw error;
  }
};

// 发送智能体消息
const sendAgentMessage = async (agentId: string, content: string) => {
  try {
    const response = await apiClient.post<AgentMessage>(`/agents/${agentId}/message`, {
      content,
      userId: getCurrentUserId(),
    });
    return response.data;
  } catch (error) {
    Logger.error('发送消息失败', error);
    throw error;
  }
};
```
