# 小克服务 API 文档

## 接口概述

小克服务API遵循RESTful设计规范，提供了供应链、区块链、物联网和农事活动等功能的接口。

## 基础信息

- **基础URL**: `https://api.suoke.life`（生产环境）或 `http://localhost:3011`（开发环境）
- **API版本**: v1
- **数据格式**: JSON
- **认证方式**: JWT Bearer Token

## 通用响应格式

所有API响应遵循以下统一格式：

```json
{
  "success": true/false,       // 请求是否成功
  "message": "描述信息",        // 操作结果描述
  "data": {},                 // 返回的数据对象(成功时)
  "error": "错误代码"           // 错误代码(失败时)
}
```

## 通用错误代码

| 错误代码 | 描述 |
|---------|------|
| VALIDATION_ERROR | 请求参数验证失败 |
| UNAUTHORIZED | 未经授权的访问 |
| FORBIDDEN | 权限不足 |
| NOT_FOUND | 资源不存在 |
| INTERNAL_SERVER_ERROR | 服务器内部错误 |
| TOO_MANY_REQUESTS | 请求频率超限 |

## 认证与授权

### 1. 获取访问令牌

用户认证通过用户服务完成，小克服务会验证由用户服务颁发的JWT令牌。

### 2. 使用访问令牌

所有需要认证的API都需要在请求头中携带访问令牌：

```
Authorization: Bearer <your_token_here>
```

## 产品管理API

### 获取产品列表

```
GET /api/supply-chain/products
```

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| category | string | 否 | 产品分类 |
| origin | string | 否 | 产地 |
| minPrice | number | 否 | 最低价格 |
| maxPrice | number | 否 | 最高价格 |
| isOrganic | boolean | 否 | 是否有机 |
| sort | string | 否 | 排序方式(price_asc/price_desc/newest/popularity) |
| page | number | 否 | 页码(默认1) |
| limit | number | 否 | 每页数量(默认20) |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取产品列表",
  "data": {
    "products": [
      {
        "_id": "60d21b4667d0d8992e610c85",
        "name": "有机白菜",
        "price": 5.99,
        "category": "蔬菜",
        "origin": "河北省",
        "isOrganic": true,
        "imageUrl": "https://images.suoke.life/products/cabbage.jpg"
      }
    ],
    "pagination": {
      "totalItems": 145,
      "currentPage": 1,
      "pageSize": 20,
      "totalPages": 8
    }
  }
}
```

### 获取产品详情

```
GET /api/supply-chain/products/:id
```

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 产品ID |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取产品详情",
  "data": {
    "_id": "60d21b4667d0d8992e610c85",
    "name": "有机白菜",
    "description": "新鲜采摘的有机白菜，无农药，无化肥。",
    "price": 5.99,
    "category": "蔬菜",
    "origin": "河北省",
    "isOrganic": true,
    "stockQuantity": 100,
    "unit": "斤",
    "imageUrl": "https://images.suoke.life/products/cabbage.jpg",
    "certifications": ["有机认证", "绿色食品"],
    "nutritionFacts": {
      "calories": 25,
      "protein": 1.5,
      "carbohydrates": 5.8,
      "fat": 0.1
    },
    "harvestDate": "2023-06-15T00:00:00.000Z",
    "shelfLife": 7,
    "createdAt": "2023-06-22T10:15:00.000Z",
    "updatedAt": "2023-06-22T10:15:00.000Z"
  }
}
```

### 创建产品

```
POST /api/supply-chain/products
```

**权限要求**: `admin` 或 `supplier`

**请求体示例**:

```json
{
  "name": "有机白菜",
  "description": "新鲜采摘的有机白菜，无农药，无化肥。",
  "price": 5.99,
  "category": "蔬菜",
  "origin": "河北省",
  "isOrganic": true,
  "stockQuantity": 100,
  "unit": "斤",
  "imageUrl": "https://images.suoke.life/products/cabbage.jpg",
  "certifications": ["有机认证", "绿色食品"],
  "nutritionFacts": {
    "calories": 25,
    "protein": 1.5,
    "carbohydrates": 5.8,
    "fat": 0.1
  },
  "harvestDate": "2023-06-15T00:00:00.000Z",
  "shelfLife": 7
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "产品创建成功",
  "data": {
    "_id": "60d21b4667d0d8992e610c85",
    "name": "有机白菜",
    "description": "新鲜采摘的有机白菜，无农药，无化肥。",
    "price": 5.99,
    "category": "蔬菜",
    "origin": "河北省",
    "isOrganic": true,
    "stockQuantity": 100,
    "unit": "斤",
    "imageUrl": "https://images.suoke.life/products/cabbage.jpg",
    "certifications": ["有机认证", "绿色食品"],
    "nutritionFacts": {
      "calories": 25,
      "protein": 1.5,
      "carbohydrates": 5.8,
      "fat": 0.1
    },
    "harvestDate": "2023-06-15T00:00:00.000Z",
    "shelfLife": 7,
    "createdAt": "2023-06-22T10:15:00.000Z",
    "updatedAt": "2023-06-22T10:15:00.000Z"
  }
}
```

### 更新产品

```
PUT /api/supply-chain/products/:id
```

**权限要求**: `admin` 或 `supplier`

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 产品ID |

**请求体示例**:

```json
{
  "price": 6.99,
  "stockQuantity": 80
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "产品更新成功",
  "data": {
    "_id": "60d21b4667d0d8992e610c85",
    "name": "有机白菜",
    "price": 6.99,
    "stockQuantity": 80,
    "updatedAt": "2023-06-23T08:30:00.000Z"
  }
}
```

### 删除产品

```
DELETE /api/supply-chain/products/:id
```

**权限要求**: `admin`

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 产品ID |

**响应示例**:

```json
{
  "success": true,
  "message": "产品删除成功"
}
```

## 区块链溯源API

### 验证产品溯源信息

```
GET /api/blockchain/verify/:productId
```

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| productId | string | 产品ID |

**响应示例**:

```json
{
  "success": true,
  "message": "溯源信息验证成功",
  "data": {
    "productId": "60d21b4667d0d8992e610c85",
    "name": "有机白菜",
    "verified": true,
    "traceabilityChain": [
      {
        "timestamp": "2023-06-15T08:00:00.000Z",
        "stage": "种植",
        "location": "河北省张家口市",
        "operator": "张三农场",
        "details": "种植日期，使用有机肥料",
        "verificationHash": "0x1a2b3c..."
      },
      {
        "timestamp": "2023-06-20T07:30:00.000Z",
        "stage": "收获",
        "location": "河北省张家口市",
        "operator": "张三农场",
        "details": "人工采收",
        "verificationHash": "0x4d5e6f..."
      },
      {
        "timestamp": "2023-06-20T14:00:00.000Z",
        "stage": "包装",
        "location": "河北省张家口市包装厂",
        "operator": "绿鲜包装有限公司",
        "details": "使用可降解材料包装",
        "verificationHash": "0x7g8h9i..."
      },
      {
        "timestamp": "2023-06-21T09:00:00.000Z",
        "stage": "运输",
        "location": "在途（张家口-北京）",
        "operator": "速捷物流",
        "details": "冷链运输，温度3-7℃",
        "verificationHash": "0xj0k1l..."
      },
      {
        "timestamp": "2023-06-22T08:00:00.000Z",
        "stage": "上架",
        "location": "北京市海淀区门店",
        "operator": "绿色生活超市",
        "details": "冷藏展示区",
        "verificationHash": "0xm2n3o..."
      }
    ]
  }
}
```

### 生成产品溯源二维码

```
POST /api/consumer/qrcode
```

**权限要求**: `admin` 或 `supplier`

**请求体示例**:

```json
{
  "productId": "60d21b4667d0d8992e610c85",
  "batchNumber": "B2023062201",
  "expirationDate": "2023-06-29T00:00:00.000Z"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "溯源码生成成功",
  "data": {
    "qrCodeId": "TR-60d21b4667d0d8992e610c85-B2023062201",
    "qrCodeUrl": "https://api.suoke.life/qr/TR-60d21b4667d0d8992e610c85-B2023062201",
    "qrCodeImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEU...",
    "productId": "60d21b4667d0d8992e610c85",
    "productName": "有机白菜",
    "batchNumber": "B2023062201",
    "expirationDate": "2023-06-29T00:00:00.000Z",
    "createdAt": "2023-06-22T10:30:00.000Z"
  }
}
```

## 物联网数据API

### 获取产品环境监控数据

```
GET /api/iot/environment/:productId
```

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| productId | string | 产品ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| from | string | 否 | 开始时间 (ISO格式) |
| to | string | 否 | 结束时间 (ISO格式) |
| metrics | string | 否 | 指标类型，多个用逗号分隔 (temperature, humidity, light, soil) |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取环境数据",
  "data": {
    "productId": "60d21b4667d0d8992e610c85",
    "productName": "有机白菜",
    "timeRange": {
      "from": "2023-06-15T00:00:00.000Z",
      "to": "2023-06-22T00:00:00.000Z"
    },
    "metrics": {
      "temperature": [
        { "timestamp": "2023-06-15T00:00:00.000Z", "value": 22.5 },
        { "timestamp": "2023-06-16T00:00:00.000Z", "value": 23.1 },
        { "timestamp": "2023-06-17T00:00:00.000Z", "value": 21.8 },
        { "timestamp": "2023-06-18T00:00:00.000Z", "value": 22.3 },
        { "timestamp": "2023-06-19T00:00:00.000Z", "value": 24.0 },
        { "timestamp": "2023-06-20T00:00:00.000Z", "value": 23.5 },
        { "timestamp": "2023-06-21T00:00:00.000Z", "value": 22.9 }
      ],
      "humidity": [
        { "timestamp": "2023-06-15T00:00:00.000Z", "value": 65.3 },
        { "timestamp": "2023-06-16T00:00:00.000Z", "value": 68.2 },
        { "timestamp": "2023-06-17T00:00:00.000Z", "value": 70.5 },
        { "timestamp": "2023-06-18T00:00:00.000Z", "value": 67.8 },
        { "timestamp": "2023-06-19T00:00:00.000Z", "value": 63.1 },
        { "timestamp": "2023-06-20T00:00:00.000Z", "value": 64.7 },
        { "timestamp": "2023-06-21T00:00:00.000Z", "value": 66.2 }
      ]
    },
    "summary": {
      "temperature": {
        "min": 21.8,
        "max": 24.0,
        "avg": 22.87
      },
      "humidity": {
        "min": 63.1,
        "max": 70.5,
        "avg": 66.54
      }
    }
  }
}
```

## 农事活动API

### 获取农事活动列表

```
GET /api/supply-chain/activities
```

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| category | string | 否 | 活动分类 |
| location | string | 否 | 活动地点 |
| from | string | 否 | 开始日期 (ISO格式) |
| to | string | 否 | 结束日期 (ISO格式) |
| page | number | 否 | 页码(默认1) |
| limit | number | 否 | 每页数量(默认20) |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取活动列表",
  "data": {
    "activities": [
      {
        "_id": "61e8f67dbc64e5001c3d9a1e",
        "title": "有机蔬菜采摘体验",
        "description": "参与有机蔬菜采摘，体验农耕乐趣",
        "category": "采摘",
        "location": "北京市顺义区张三有机农场",
        "startTime": "2023-07-15T09:00:00.000Z",
        "endTime": "2023-07-15T17:00:00.000Z",
        "price": 88.0,
        "capacity": 50,
        "enrolled": 28,
        "imageUrl": "https://images.suoke.life/activities/harvesting.jpg"
      }
    ],
    "pagination": {
      "totalItems": 15,
      "currentPage": 1,
      "pageSize": 20,
      "totalPages": 1
    }
  }
}
```

### 获取活动详情

```
GET /api/supply-chain/activities/:id
```

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 活动ID |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取活动详情",
  "data": {
    "_id": "61e8f67dbc64e5001c3d9a1e",
    "title": "有机蔬菜采摘体验",
    "description": "参与有机蔬菜采摘，体验农耕乐趣。活动包含蔬菜采摘、农耕体验、农家午餐和农产品礼包等环节。",
    "category": "采摘",
    "location": "北京市顺义区张三有机农场",
    "coordinate": {
      "latitude": 40.1234,
      "longitude": 116.5678
    },
    "organizer": {
      "name": "张三有机农场",
      "contact": "13800138000",
      "description": "专注有机蔬菜种植15年的家庭农场"
    },
    "startTime": "2023-07-15T09:00:00.000Z",
    "endTime": "2023-07-15T17:00:00.000Z",
    "price": 88.0,
    "childPrice": 58.0,
    "capacity": 50,
    "enrolled": 28,
    "imageUrl": "https://images.suoke.life/activities/harvesting.jpg",
    "galleryImages": [
      "https://images.suoke.life/activities/harvesting1.jpg",
      "https://images.suoke.life/activities/harvesting2.jpg",
      "https://images.suoke.life/activities/harvesting3.jpg"
    ],
    "agenda": [
      { "time": "09:00-09:30", "activity": "签到与欢迎" },
      { "time": "09:30-11:30", "activity": "蔬菜采摘体验" },
      { "time": "11:30-13:00", "activity": "农家午餐" },
      { "time": "13:00-15:00", "activity": "农耕体验" },
      { "time": "15:00-16:30", "activity": "农产品加工体验" },
      { "time": "16:30-17:00", "activity": "活动总结与赠送礼品" }
    ],
    "includes": [
      "专业导师指导",
      "采摘工具",
      "1kg自采蔬菜",
      "农家午餐",
      "有机农产品礼包",
      "意外保险"
    ],
    "requirements": [
      "适合3岁以上人群参与",
      "请穿着舒适的衣物和运动鞋",
      "自备防晒用品"
    ],
    "refundPolicy": "活动前48小时取消可获全额退款，24-48小时内取消退款50%，24小时内取消不予退款",
    "reviews": [
      {
        "userId": "5f8b2ecb3f4b8a001c123456",
        "userName": "李四",
        "rating": 4.5,
        "comment": "体验非常棒，孩子很喜欢采摘活动，午餐也很美味。",
        "createdAt": "2023-06-20T14:30:00.000Z"
      }
    ],
    "createdAt": "2023-06-10T08:15:00.000Z",
    "updatedAt": "2023-06-22T10:20:00.000Z"
  }
}
```

### 活动报名

```
POST /api/supply-chain/activities/:id/enroll
```

**权限要求**: 已认证用户

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 活动ID |

**请求体示例**:

```json
{
  "participants": [
    {
      "name": "张三",
      "phone": "13900139000",
      "idCard": "110101199001010010",
      "age": 35,
      "isChild": false
    },
    {
      "name": "小明",
      "age": 8,
      "isChild": true
    }
  ],
  "specialRequests": "需要素食餐点",
  "paymentMethod": "wechat"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "活动报名成功",
  "data": {
    "enrollmentId": "62c52a9e1f45e7001d123456",
    "activityId": "61e8f67dbc64e5001c3d9a1e",
    "activityTitle": "有机蔬菜采摘体验",
    "enrollTime": "2023-06-23T14:20:00.000Z",
    "participantCount": 2,
    "totalPrice": 146.0,
    "paymentStatus": "pending",
    "paymentUrl": "https://pay.suoke.life/wx/62c52a9e1f45e7001d123456"
  }
}
```

## 智能预测API

### 获取产品需求预测

```
GET /api/prediction/demand/:productId
```

**权限要求**: `admin` 或 `supplier`

**路径参数**:

| 参数名 | 类型 | 描述 |
|-------|-----|------|
| productId | string | 产品ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| period | string | 否 | 预测周期(week/month/quarter，默认month) |
| periods | number | 否 | 预测期数(默认3) |

**响应示例**:

```json
{
  "success": true,
  "message": "成功获取需求预测",
  "data": {
    "productId": "60d21b4667d0d8992e610c85",
    "productName": "有机白菜",
    "period": "month",
    "predictions": [
      {
        "period": "2023-07",
        "demandMean": 2350,
        "demandLow": 2100,
        "demandHigh": 2600,
        "confidence": 0.85
      },
      {
        "period": "2023-08",
        "demandMean": 2180,
        "demandLow": 1950,
        "demandHigh": 2400,
        "confidence": 0.82
      },
      {
        "period": "2023-09",
        "demandMean": 2420,
        "demandLow": 2150,
        "demandHigh": 2700,
        "confidence": 0.78
      }
    ],
    "factors": [
      { "name": "季节性", "impact": 0.45 },
      { "name": "价格敏感度", "impact": 0.25 },
      { "name": "市场趋势", "impact": 0.15 },
      { "name": "促销活动", "impact": 0.10 },
      { "name": "其他因素", "impact": 0.05 }
    ],
    "recommendations": [
      "7月需求较高，建议提前2周增加15%的库存",
      "8月预计需求略有下降，可以适当减少采购量",
      "9月开学季需求回升，建议在8月底前补充库存"
    ],
    "lastUpdated": "2023-06-23T08:00:00.000Z"
  }
}
```

## 更多API

完整API文档请访问在线Swagger文档：

```
http://localhost:3011/api-docs  (开发环境)
https://api.suoke.life/api-docs  (生产环境)
```

## API变更记录

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2023-06-23 | 1.0.0 | 初始版本 |
| 2023-06-15 | 0.9.0 | 测试版本 |
