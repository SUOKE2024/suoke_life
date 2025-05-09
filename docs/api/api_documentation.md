# 索克生活 API 文档

## 概述

本文档详细说明了索克生活APP后端API接口规范，供前端开发团队参考。所有API遵循RESTful设计原则，使用HTTPS协议，并采用JSON格式进行数据交换。

## 基础信息

- **基础URL**：
  - 开发环境：`https://dev-api.suoke.life`
  - 测试环境：`https://staging-api.suoke.life`
  - 生产环境：`https://api.suoke.life`

- **API版本**：v1
- **内容类型**：application/json
- **字符编码**：UTF-8

## 认证与授权

所有API请求（除公开接口外）需要进行身份验证，使用Bearer Token认证方式：

```
Authorization: Bearer {accessToken}
```

### 获取访问令牌

**请求**：
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "phoneOrEmail": "string",
  "password": "string"
}
```

**响应**：
```
Status: 200 OK
Content-Type: application/json

{
  "accessToken": "string",
  "refreshToken": "string",
  "expiresIn": 3600,
  "userId": "string"
}
```

### 刷新令牌

**请求**：
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "string"
}
```

**响应**：
```
Status: 200 OK
Content-Type: application/json

{
  "accessToken": "string",
  "refreshToken": "string",
  "expiresIn": 3600
}
```

## 错误处理

所有API错误响应采用统一格式：

```
{
  "code": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {} // 可选，详细错误信息
}
```

### 常见HTTP状态码

- **200 OK**：请求成功
- **201 Created**：资源创建成功
- **400 Bad Request**：请求参数错误
- **401 Unauthorized**：未授权或token无效
- **403 Forbidden**：权限不足
- **404 Not Found**：资源不存在
- **409 Conflict**：资源冲突
- **422 Unprocessable Entity**：请求格式正确但语义错误
- **500 Internal Server Error**：服务器内部错误

## API端点

### 用户管理

#### 注册用户

**请求**：
```
POST /api/v1/users
Content-Type: application/json

{
  "name": "string",
  "phoneNumber": "string",
  "email": "string",
  "password": "string"
}
```

**响应**：
```
Status: 201 Created
Content-Type: application/json

{
  "id": "string",
  "name": "string",
  "phoneNumber": "string",
  "email": "string",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

#### 获取用户信息

**请求**：
```
GET /api/v1/users/me
Authorization: Bearer {accessToken}
```

**响应**：
```
Status: 200 OK
Content-Type: application/json

{
  "id": "string",
  "name": "string",
  "phoneNumber": "string",
  "email": "string",
  "avatar": "string",
  "createdAt": "2024-01-01T00:00:00Z",
  "healthProfile": {
    "birthDate": "1990-01-01",
    "gender": "male|female|other",
    "height": 170,
    "weight": 65
  }
}
```

### 健康档案

#### 创建健康档案

**请求**：
```
POST /api/v1/health-profiles
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "birthDate": "1990-01-01",
  "gender": "male|female|other",
  "height": 170,
  "weight": 65,
  "bloodType": "A|B|AB|O",
  "allergies": ["string"],
  "chronicConditions": ["string"]
}
```

**响应**：
```
Status: 201 Created
Content-Type: application/json

{
  "id": "string",
  "userId": "string",
  "birthDate": "1990-01-01",
  "gender": "male|female|other",
  "height": 170,
  "weight": 65,
  "bloodType": "A|B|AB|O",
  "allergies": ["string"],
  "chronicConditions": ["string"],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 中医四诊

#### 提交望诊数据

**请求**：
```
POST /api/v1/diagnoses/inspection
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data

{
  "tongueImage": File,
  "faceImage": File,
  "notes": "string"
}
```

**响应**：
```
Status: 201 Created
Content-Type: application/json

{
  "id": "string",
  "userId": "string",
  "tongueImageUrl": "string",
  "faceImageUrl": "string",
  "tongueAnalysis": {
    "color": "string",
    "coating": "string",
    "shape": "string",
    "moisture": "string"
  },
  "faceAnalysis": {
    "complexion": "string",
    "features": ["string"]
  },
  "notes": "string",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

## 数据模型

### User

用户基本信息模型

| 字段         | 类型     | 描述                |
|------------|--------|-------------------|
| id         | string | 用户唯一标识           |
| name       | string | 用户姓名             |
| phoneNumber| string | 手机号码             |
| email      | string | 电子邮箱             |
| avatar     | string | 头像URL            |
| createdAt  | date   | 创建时间             |
| updatedAt  | date   | 更新时间             |

### HealthProfile

健康档案模型

| 字段              | 类型     | 描述                |
|-----------------|--------|-------------------|
| id              | string | 档案唯一标识           |
| userId          | string | 用户ID             |
| birthDate       | date   | 出生日期             |
| gender          | string | 性别               |
| height          | number | 身高(cm)           |
| weight          | number | 体重(kg)           |
| bloodType       | string | 血型               |
| allergies       | array  | 过敏源              |
| chronicConditions| array  | 慢性病史             |
| createdAt       | date   | 创建时间             |
| updatedAt       | date   | 更新时间             |

## 更新日志

### v1.0.0 (2024-07-15)
- 初始API文档发布
- 包含用户认证、用户管理和健康档案基础接口

## 联系与支持

- **技术支持邮箱**：dev-support@suoke.life
- **API文档问题反馈**：api-docs@suoke.life
- **开发者社区**：https://dev.suoke.life

---

> 本文档将随接口变更持续更新，请定期查看最新版本。
> 最后更新：2024年7月15日 