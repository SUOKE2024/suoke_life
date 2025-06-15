# 索克生活API设计规范

## 📋 概述

本文档定义了索克生活平台所有微服务的API设计标准，确保服务间的一致性和可维护性。

## 🎯 设计原则

### 1. RESTful设计
- 使用标准HTTP方法（GET、POST、PUT、DELETE、PATCH）
- 资源导向的URL设计
- 无状态设计

### 2. 版本控制
- 所有API必须包含版本号：`/api/v1/`
- 使用语义化版本控制
- 向后兼容性保证

### 3. 统一响应格式
- 标准化的JSON响应结构
- 一致的错误处理
- 统一的状态码使用

## 🌐 URL规范

### 基础结构
```
https://{service-domain}/api/v{version}/{resource}
```

### 示例
```
# 用户服务
GET /api/v1/users
POST /api/v1/users
GET /api/v1/users/{user_id}
PUT /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}

# 智能体服务
POST /api/v1/agent/chat
GET /api/v1/agent/capabilities
WebSocket /api/v1/agent/ws

# 诊断服务
POST /api/v1/diagnosis/face
POST /api/v1/diagnosis/tongue
GET /api/v1/diagnosis/sessions/{session_id}
```

### 命名规范
- 使用小写字母和连字符
- 资源名使用复数形式
- 避免深层嵌套（最多3层）
- 使用有意义的资源名称

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 实际数据
  },
  "message": "操作成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### 分页响应
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "查询成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

## 🔢 状态码规范

### 成功状态码
- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `202 Accepted` - 请求已接受，异步处理中
- `204 No Content` - 请求成功，无返回内容

### 客户端错误
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 无权限
- `404 Not Found` - 资源不存在
- `409 Conflict` - 资源冲突
- `422 Unprocessable Entity` - 请求格式正确但语义错误
- `429 Too Many Requests` - 请求频率限制

### 服务器错误
- `500 Internal Server Error` - 服务器内部错误
- `502 Bad Gateway` - 网关错误
- `503 Service Unavailable` - 服务不可用
- `504 Gateway Timeout` - 网关超时

## 🔐 认证和授权

### 认证方式
- 使用JWT Bearer Token
- Token在Header中传递：`Authorization: Bearer <token>`

### 权限控制
- 基于角色的访问控制（RBAC）
- 资源级别的权限验证
- API密钥用于服务间通信

## 📝 请求和响应规范

### 请求头
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-Request-ID: <unique-request-id>
X-Client-Version: <client-version>
```

### 响应头
```
Content-Type: application/json
X-Request-ID: <request-id>
X-Response-Time: <response-time-ms>
X-Rate-Limit-Remaining: <remaining-requests>
```

### 请求体规范
- 使用JSON格式
- 字段名使用snake_case
- 必填字段明确标注
- 提供字段验证规则

## 🚀 性能规范

### 响应时间
- API响应时间 < 100ms（P95）
- 数据库查询 < 50ms（P95）
- 外部服务调用 < 200ms（P95）

### 并发处理
- 支持至少1000并发请求
- 实现请求限流和熔断
- 优雅降级机制

## 📋 文档规范

### OpenAPI规范
- 所有API必须提供OpenAPI 3.0文档
- 包含详细的参数说明和示例
- 提供交互式API文档

### 示例文档结构
```yaml
openapi: 3.0.0
info:
  title: 索克生活用户服务API
  version: 2.0.0
  description: 提供用户管理和档案功能
paths:
  /api/v1/users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: 成功返回用户列表
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
```

## 🔍 监控和日志

### 监控指标
- 请求数量和响应时间
- 错误率和成功率
- 资源使用情况

### 日志格式
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "user-service",
  "request_id": "req_123456789",
  "method": "POST",
  "path": "/api/v1/users",
  "status_code": 201,
  "response_time": 45,
  "user_id": "user_123",
  "message": "用户创建成功"
}
```

## 🧪 测试规范

### API测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖所有端点
- 性能测试验证响应时间
- 安全测试验证权限控制

### 测试用例结构
```python
class TestUserAPI:
    async def test_create_user_success(self):
        """测试用户创建成功场景"""
        pass
    
    async def test_create_user_validation_error(self):
        """测试用户创建参数验证错误"""
        pass
    
    async def test_get_user_not_found(self):
        """测试获取不存在的用户"""
        pass
```

## 🔧 实施检查清单

### 开发阶段
- [ ] API设计符合RESTful原则
- [ ] 使用统一的URL结构
- [ ] 实现标准响应格式
- [ ] 添加适当的状态码
- [ ] 实现认证和授权
- [ ] 添加请求验证
- [ ] 实现错误处理

### 测试阶段
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 性能测试通过
- [ ] 安全测试通过
- [ ] API文档完整

### 部署阶段
- [ ] 监控指标配置
- [ ] 日志格式标准化
- [ ] 限流和熔断配置
- [ ] 健康检查端点
- [ ] 文档部署

## 📚 参考资源

- [RESTful API设计指南](https://restfulapi.net/)
- [OpenAPI规范](https://swagger.io/specification/)
- [HTTP状态码参考](https://httpstatuses.com/)
- [JWT认证最佳实践](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

---

**版本**: 2.0.0  
**更新时间**: 2024-01-01  
**维护团队**: 索克生活技术团队