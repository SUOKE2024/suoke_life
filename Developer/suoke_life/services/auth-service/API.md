# 索克生活认证服务API文档

## 生物识别认证API

### 1. 注册生物识别凭据

用于注册用户的生物识别凭据，如指纹、面部ID等。

**路径:** `/api/auth/biometric/register`  
**方法:** `POST`  
**需要认证:** 是

#### 请求参数

| 参数名        | 类型    | 必需  | 描述                               |
|--------------|---------|------|-----------------------------------|
| userId       | string  | 是   | 用户ID                            |
| deviceId     | string  | 是   | 设备ID                            |
| biometricType| string  | 是   | 生物识别类型 (fingerprint/faceId)  |
| publicKey    | string  | 是   | 公钥                              |
| deviceInfo   | object  | 是   | 设备信息                           |
| attestation  | object  | 否   | 设备证明信息                        |

#### 设备信息对象结构

```json
{
  "os": "iOS/Android",
  "model": "设备型号",
  "osVersion": "系统版本",
  "appVersion": "应用版本"
}
```

#### 响应

**成功响应: `201 Created`**
```json
{
  "success": true,
  "message": "生物识别凭据注册成功",
  "data": {
    "id": "credential-id",
    "userId": "user-id",
    "deviceId": "device-id",
    "biometricType": "fingerprint",
    "createdAt": "2023-01-01T00:00:00Z",
    "expiresAt": "2023-07-01T00:00:00Z",
    "isNewRegistration": true
  }
}
```

**错误响应**
- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 无权注册其他用户的凭据
- `500 Internal Server Error`: 服务器内部错误

### 2. 生成生物识别挑战值

用于生成验证生物识别凭据时需要的挑战值。

**路径:** `/api/auth/biometric/challenge`  
**方法:** `POST`  
**需要认证:** 是

#### 请求参数

| 参数名    | 类型    | 必需  | 描述     |
|----------|---------|------|----------|
| userId   | string  | 是   | 用户ID   |
| deviceId | string  | 是   | 设备ID   |

#### 响应

**成功响应: `200 OK`**
```json
{
  "success": true,
  "message": "生物识别挑战值生成成功",
  "data": {
    "challenge": "random-challenge-string",
    "userId": "user-id",
    "deviceId": "device-id",
    "expiresIn": 300
  }
}
```

**错误响应**
- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 无权为其他用户生成挑战值
- `500 Internal Server Error`: 服务器内部错误

### 3. 验证生物识别凭据

用于验证用户的生物识别凭据。

**路径:** `/api/auth/biometric/verify`  
**方法:** `POST`  
**需要认证:** 是

#### 请求参数

| 参数名        | 类型    | 必需  | 描述                               |
|--------------|---------|------|-----------------------------------|
| userId       | string  | 是   | 用户ID                            |
| deviceId     | string  | 是   | 设备ID                            |
| biometricType| string  | 是   | 生物识别类型 (fingerprint/faceId)  |
| signature    | string  | 是   | 签名                              |
| challenge    | string  | 是   | 挑战值                             |

#### 响应

**成功响应: `200 OK`**
```json
{
  "success": true,
  "message": "生物识别验证成功",
  "data": {
    "isValid": true,
    "userId": "user-id",
    "deviceId": "device-id",
    "biometricType": "fingerprint",
    "verifiedAt": "2023-01-01T00:00:00Z"
  }
}
```

**错误响应**
- `400 Bad Request`: 请求参数无效或验证失败
- `401 Unauthorized`: 未授权访问
- `500 Internal Server Error`: 服务器内部错误

### 4. 获取生物识别凭据列表

获取用户的所有生物识别凭据。

**路径:** `/api/auth/biometric/credentials`  
**方法:** `GET`  
**需要认证:** 是

#### 请求参数

| 参数名  | 类型    | 必需  | 描述     |
|--------|---------|------|----------|
| userId | string  | 是   | 用户ID   |

#### 响应

**成功响应: `200 OK`**
```json
{
  "success": true,
  "message": "获取生物识别凭据列表成功",
  "data": [
    {
      "id": "credential-id-1",
      "userId": "user-id",
      "deviceId": "device-id-1",
      "biometricType": "fingerprint",
      "deviceInfo": {
        "os": "iOS",
        "model": "iPhone 13"
      },
      "createdAt": "2023-01-01T00:00:00Z",
      "lastUsedAt": "2023-01-01T00:00:00Z",
      "expiresAt": "2023-07-01T00:00:00Z"
    },
    {
      "id": "credential-id-2",
      "userId": "user-id",
      "deviceId": "device-id-2",
      "biometricType": "faceId",
      "deviceInfo": {
        "os": "Android",
        "model": "Samsung Galaxy S21"
      },
      "createdAt": "2023-01-02T00:00:00Z",
      "lastUsedAt": "2023-01-02T00:00:00Z",
      "expiresAt": "2023-07-02T00:00:00Z"
    }
  ]
}
```

**错误响应**
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 无权查看其他用户的凭据
- `500 Internal Server Error`: 服务器内部错误

### 5. 删除生物识别凭据

删除用户的生物识别凭据。

**路径:** `/api/auth/biometric/credentials/:id`  
**方法:** `DELETE`  
**需要认证:** 是

#### 路径参数

| 参数名 | 类型    | 必需  | 描述         |
|-------|---------|------|--------------|
| id    | string  | 是   | 凭据ID       |

#### 请求参数

| 参数名  | 类型    | 必需  | 描述     |
|--------|---------|------|----------|
| userId | string  | 是   | 用户ID   |

#### 响应

**成功响应: `200 OK`**
```json
{
  "success": true,
  "message": "生物识别凭据删除成功"
}
```

**错误响应**
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 无权删除其他用户的凭据
- `404 Not Found`: 凭据不存在
- `500 Internal Server Error`: 服务器内部错误

### 6. 更新生物识别凭据

更新用户的生物识别凭据名称。

**路径:** `/api/auth/biometric/credentials/:id`  
**方法:** `PUT`  
**需要认证:** 是

#### 路径参数

| 参数名 | 类型    | 必需  | 描述         |
|-------|---------|------|--------------|
| id    | string  | 是   | 凭据ID       |

#### 请求参数

| 参数名  | 类型    | 必需  | 描述       |
|--------|---------|------|------------|
| userId | string  | 是   | 用户ID     |
| name   | string  | 是   | 凭据名称    |

#### 响应

**成功响应: `200 OK`**
```json
{
  "success": true,
  "message": "生物识别凭据更新成功",
  "data": {
    "id": "credential-id",
    "userId": "user-id",
    "deviceId": "device-id",
    "biometricType": "fingerprint",
    "name": "新的凭据名称",
    "updatedAt": "2023-01-01T00:00:00Z"
  }
}
```

**错误响应**
- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 无权更新其他用户的凭据
- `404 Not Found`: 凭据不存在
- `500 Internal Server Error`: 服务器内部错误

## 安全考虑

1. 所有API端点要求有效的JWT认证
2. 生物识别凭据仅存储公钥，私钥保留在用户设备上
3. 挑战值具有时间限制，通常为5分钟
4. 验证API使用签名验证方式，确保请求有效性
5. 所有敏感操作都会记录安全日志 