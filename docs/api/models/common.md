# 通用数据模型

## 概述

本文档描述了索克生活APP API中使用的通用数据模型。这些模型在多个API端点间共享，确保数据结构的一致性。所有时间戳字段均使用ISO 8601格式（YYYY-MM-DDTHH:MM:SSZ）。

## 基础模型

### 分页响应

分页响应模型用于返回分页列表数据：

```json
{
  "items": [],          // 具体数据项数组
  "pagination": {
    "total": 100,       // 总记录数
    "pageSize": 10,     // 每页大小
    "currentPage": 1,   // 当前页码
    "totalPages": 10    // 总页数
  }
}
```

### 分页请求参数

分页请求的通用参数：

| 参数名 | 类型 | 描述 | 默认值 |
|-------|-----|------|-------|
| page | integer | 页码，从1开始 | 1 |
| pageSize | integer | 每页记录数 | 20 |
| sortBy | string | 排序字段 | 因端点而异 |
| sortOrder | string | 排序方式: asc(升序), desc(降序) | desc |

### 基础响应结构

所有API响应遵循以下基础结构：

**成功响应**

```json
{
  "code": "SUCCESS",
  "data": {  },         // 响应数据，因端点而异
  "message": "操作成功"
}
```

**错误响应**

```json
{
  "code": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {  }       // 可选，详细错误信息
}
```

## 用户相关模型

### 用户基本信息 (UserBasic)

用户基本信息模型，用于概要展示：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 用户唯一标识 |
| name | string | 用户姓名 |
| avatarUrl | string | 头像URL |
| role | string | 用户角色 |
| level | integer | 用户等级 |
| createdAt | string | 创建时间 |

```json
{
  "id": "usr_123456789",
  "name": "张三",
  "avatarUrl": "https://api.suoke.life/avatars/default.png",
  "role": "USER",
  "level": 3,
  "createdAt": "2024-07-01T08:00:00Z"
}
```

### 用户详细信息 (UserDetail)

用户详细信息模型，扩展自基本信息：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 用户唯一标识 |
| name | string | 用户姓名 |
| avatarUrl | string | 头像URL |
| phoneNumber | string | 手机号码，脱敏展示 |
| email | string | 电子邮箱，脱敏展示 |
| gender | string | 性别：MALE、FEMALE、OTHER |
| birthDate | string | 出生日期，ISO 8601格式的日期部分 |
| role | string | 用户角色 |
| level | integer | 用户等级 |
| experiencePoints | integer | 经验值 |
| achievements | array | 成就数组 |
| specialties | array | 专长数组 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |
| lastLoginAt | string | 最后登录时间 |

```json
{
  "id": "usr_123456789",
  "name": "张三",
  "avatarUrl": "https://api.suoke.life/avatars/default.png",
  "phoneNumber": "138****5678",
  "email": "z****n@example.com",
  "gender": "MALE",
  "birthDate": "1990-01-01",
  "role": "USER",
  "level": 3,
  "experiencePoints": 2500,
  "achievements": [
    {
      "id": "ach_001",
      "name": "初行者",
      "description": "完成注册并登录应用",
      "iconUrl": "https://api.suoke.life/icons/achievements/first_login.png",
      "unlockedAt": "2024-07-01T08:30:00Z"
    }
  ],
  "specialties": [
    {
      "id": "spc_001",
      "name": "营养师",
      "level": 1,
      "progress": 30
    }
  ],
  "createdAt": "2024-07-01T08:00:00Z",
  "updatedAt": "2024-07-10T15:30:00Z",
  "lastLoginAt": "2024-07-15T09:45:00Z"
}
```

## 健康相关模型

### 体质类型 (ConstitutionType)

中医九种体质类型模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| code | string | 体质代码 |
| name | string | 体质名称 |
| description | string | 体质简短描述 |
| characteristics | array | 体质特征列表 |
| iconUrl | string | 体质图标URL |

```json
{
  "code": "PH",
  "name": "平和质",
  "description": "阴阳气血调和，以天地阴阳之正气所生",
  "characteristics": [
    "面色、肤色润泽",
    "精力充沛",
    "睡眠良好",
    "适应能力强"
  ],
  "iconUrl": "https://api.suoke.life/icons/constitutions/balanced.png"
}
```

### 体质评估结果 (ConstitutionAssessment)

用户体质评估结果模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 评估记录唯一标识 |
| userId | string | 用户ID |
| assessmentDate | string | 评估日期 |
| mainType | object | 主体质类型 |
| secondaryTypes | array | 次要体质类型数组 |
| scores | object | 各体质得分 |
| recommendations | array | 体质调理建议 |
| createdAt | string | 创建时间 |

```json
{
  "id": "ast_123456789",
  "userId": "usr_123456789",
  "assessmentDate": "2024-07-10T14:30:00Z",
  "mainType": {
    "code": "QX",
    "name": "气虚质",
    "description": "气虚质是由先天禀赋不足，或后天失养所导致",
    "iconUrl": "https://api.suoke.life/icons/constitutions/qi_deficiency.png"
  },
  "secondaryTypes": [
    {
      "code": "YX",
      "name": "阳虚质",
      "description": "阳虚质是由先天禀赋不足，或后天失养所导致",
      "iconUrl": "https://api.suoke.life/icons/constitutions/yang_deficiency.png"
    }
  ],
  "scores": {
    "PH": 45,    // 平和质
    "QX": 78,    // 气虚质
    "YX": 65,    // 阳虚质
    "YIX": 32,   // 阴虚质
    "TS": 28,    // 痰湿质
    "SR": 20,    // 湿热质
    "XY": 15,    // 血瘀质
    "QY": 18,    // 气郁质
    "TB": 25     // 特禀质
  },
  "recommendations": [
    {
      "category": "DIET",
      "title": "饮食调理",
      "content": "宜吃具有补气作用的食物：大枣、山药、鸡肉等；忌生冷、油腻食物。"
    },
    {
      "category": "LIFESTYLE",
      "title": "起居调养",
      "content": "保证充足睡眠，避免过度劳累，适当午休。"
    }
  ],
  "createdAt": "2024-07-10T14:30:00Z"
}
```

### 健康数据点 (HealthDataPoint)

健康数据记录模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 数据点唯一标识 |
| userId | string | 用户ID |
| category | string | 数据类别 |
| metricType | string | 指标类型 |
| value | number | 数值 |
| unit | string | 单位 |
| timestamp | string | 记录时间戳 |
| source | string | 数据来源 |
| notes | string | 备注说明 |

```json
{
  "id": "hdp_123456789",
  "userId": "usr_123456789",
  "category": "VITALS",
  "metricType": "HEART_RATE",
  "value": 75,
  "unit": "bpm",
  "timestamp": "2024-07-15T08:30:00Z",
  "source": "MANUAL_INPUT",
  "notes": "清晨测量"
}
```

## 内容相关模型

### 文章 (Article)

知识文章模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 文章唯一标识 |
| title | string | 文章标题 |
| summary | string | 文章摘要 |
| content | string | 文章内容，富文本格式 |
| coverImageUrl | string | 封面图片URL |
| author | object | 作者信息 |
| category | string | 分类 |
| tags | array | 标签数组 |
| readingTime | integer | 预计阅读时间（分钟） |
| viewCount | integer | 浏览次数 |
| likeCount | integer | 点赞次数 |
| publishedAt | string | 发布时间 |
| updatedAt | string | 更新时间 |

```json
{
  "id": "art_123456789",
  "title": "夏季如何调理阳虚体质",
  "summary": "夏季阳气外发，阳虚体质的人常感不适，本文介绍针对性调理方法。",
  "content": "<p>夏季是阳气最为旺盛的季节...</p>",
  "coverImageUrl": "https://api.suoke.life/images/articles/summer_care.jpg",
  "author": {
    "id": "usr_987654321",
    "name": "李医师",
    "avatarUrl": "https://api.suoke.life/avatars/doctors/li.png",
    "title": "主任中医师"
  },
  "category": "SEASONAL_CARE",
  "tags": ["阳虚体质", "夏季养生", "中医调理"],
  "readingTime": 5,
  "viewCount": 1250,
  "likeCount": 78,
  "publishedAt": "2024-06-01T10:00:00Z",
  "updatedAt": "2024-06-05T15:30:00Z"
}
```

### 评论 (Comment)

用户评论模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 评论唯一标识 |
| targetId | string | 评论目标ID |
| targetType | string | 评论目标类型 |
| userId | string | 评论用户ID |
| user | object | 用户基本信息 |
| content | string | 评论内容 |
| likeCount | integer | 点赞次数 |
| replyCount | integer | 回复次数 |
| parentId | string | 父评论ID，顶级评论为null |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

```json
{
  "id": "cmt_123456789",
  "targetId": "art_123456789",
  "targetType": "ARTICLE",
  "userId": "usr_123456789",
  "user": {
    "id": "usr_123456789",
    "name": "张三",
    "avatarUrl": "https://api.suoke.life/avatars/default.png"
  },
  "content": "这篇文章非常实用，我按照建议调理后感觉好多了！",
  "likeCount": 5,
  "replyCount": 2,
  "parentId": null,
  "createdAt": "2024-07-10T09:15:00Z",
  "updatedAt": "2024-07-10T09:15:00Z"
}
```

## 服务相关模型

### 服务项目 (Service)

服务项目模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 服务唯一标识 |
| name | string | 服务名称 |
| description | string | 服务描述 |
| category | string | 服务类别 |
| imageUrl | string | 服务图片URL |
| price | object | 价格信息 |
| duration | integer | 服务时长（分钟） |
| location | object | 服务地点 |
| provider | object | 服务提供者 |
| ratings | object | 评分信息 |
| availabilityStatus | string | 可用状态 |
| tags | array | 标签数组 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

```json
{
  "id": "srv_123456789",
  "name": "中医体质辨识与调理方案",
  "description": "通过四诊合参进行体质辨识，并提供个性化调理方案",
  "category": "MEDICAL_SERVICE",
  "imageUrl": "https://api.suoke.life/images/services/constitution_assessment.jpg",
  "price": {
    "amount": 299,
    "currency": "CNY",
    "unit": "次"
  },
  "duration": 60,
  "location": {
    "type": "ONLINE", 
    "address": null,
    "coordinates": null
  },
  "provider": {
    "id": "prv_987654321",
    "name": "北京中医馆",
    "logoUrl": "https://api.suoke.life/logos/providers/beijing_tcm.png",
    "verified": true
  },
  "ratings": {
    "average": 4.8,
    "count": 156
  },
  "availabilityStatus": "AVAILABLE",
  "tags": ["体质辨识", "个性化方案", "专家一对一"],
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2024-07-01T14:30:00Z"
}
```

### 预约 (Appointment)

预约记录模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 预约唯一标识 |
| userId | string | 用户ID |
| serviceId | string | 服务ID |
| service | object | 服务信息 |
| provider | object | 服务提供者 |
| scheduleTime | string | 预约时间 |
| duration | integer | 预约时长（分钟） |
| status | string | 预约状态 |
| notes | string | 预约备注 |
| paymentStatus | string | 支付状态 |
| amount | object | 支付金额 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

```json
{
  "id": "apt_123456789",
  "userId": "usr_123456789",
  "serviceId": "srv_123456789",
  "service": {
    "id": "srv_123456789",
    "name": "中医体质辨识与调理方案",
    "imageUrl": "https://api.suoke.life/images/services/constitution_assessment.jpg"
  },
  "provider": {
    "id": "prv_987654321",
    "name": "北京中医馆",
    "logoUrl": "https://api.suoke.life/logos/providers/beijing_tcm.png"
  },
  "scheduleTime": "2024-07-20T14:00:00Z",
  "duration": 60,
  "status": "CONFIRMED",
  "notes": "初次体验，希望能详细了解自己的体质特点",
  "paymentStatus": "PAID",
  "amount": {
    "amount": 299,
    "currency": "CNY"
  },
  "createdAt": "2024-07-15T10:30:00Z",
  "updatedAt": "2024-07-15T10:35:00Z"
}
```

## 产品相关模型

### 商品 (Product)

商品模型：

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 商品唯一标识 |
| name | string | 商品名称 |
| description | string | 商品描述 |
| category | string | 商品类别 |
| images | array | 商品图片URL数组 |
| price | object | 价格信息 |
| originalPrice | object | 原价信息 |
| inventory | object | 库存信息 |
| specifications | array | 商品规格 |
| origin | object | 产地信息 |
| producer | object | 生产者信息 |
| certifications | array | 认证信息 |
| ratings | object | 评分信息 |
| constitution | object | 适宜体质信息 |
| seasonality | object | 时令信息 |
| tags | array | 标签数组 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

```json
{
  "id": "prd_123456789",
  "name": "有机黄芪片",
  "description": "内蒙古草原野生黄芪，切片加工，适合气虚体质",
  "category": "HERBS",
  "images": [
    "https://api.suoke.life/images/products/astragalus_1.jpg",
    "https://api.suoke.life/images/products/astragalus_2.jpg"
  ],
  "price": {
    "amount": 98,
    "currency": "CNY",
    "unit": "250g"
  },
  "originalPrice": {
    "amount": 128,
    "currency": "CNY",
    "unit": "250g"
  },
  "inventory": {
    "available": true,
    "quantity": 200,
    "unit": "袋"
  },
  "specifications": [
    {
      "name": "规格",
      "value": "250g/袋"
    },
    {
      "name": "等级",
      "value": "优级"
    }
  ],
  "origin": {
    "province": "内蒙古",
    "city": "赤峰",
    "detail": "克什克腾草原"
  },
  "producer": {
    "id": "pdc_987654321",
    "name": "内蒙古草原珍品有限公司",
    "logoUrl": "https://api.suoke.life/logos/producers/neimeng_herbs.png",
    "verified": true
  },
  "certifications": [
    {
      "name": "有机认证",
      "issuingBody": "中国有机食品认证中心",
      "certNumber": "OFCC98765",
      "validUntil": "2025-12-31"
    }
  ],
  "ratings": {
    "average": 4.9,
    "count": 253
  },
  "constitution": {
    "recommended": ["QX", "YX"],  // 气虚质、阳虚质
    "notRecommended": ["YIX", "SR"]  // 阴虚质、湿热质
  },
  "seasonality": {
    "harvestSeason": "秋季",
    "bestConsumptionPeriod": "全年"
  },
  "tags": ["黄芪", "补气", "有机", "野生"],
  "createdAt": "2024-03-10T10:00:00Z",
  "updatedAt": "2024-07-01T14:30:00Z"
}
```

## 通用枚举值

### 用户角色 (UserRole)

| 值 | 描述 |
|---|------|
| USER | 普通用户 |
| PRACTITIONER | 中医从业者 |
| PRODUCER | 生产商 |
| ADMIN | 管理员 |

### 体质代码 (ConstitutionCode)

| 值 | 描述 |
|---|------|
| PH | 平和质 |
| QX | 气虚质 |
| YX | 阳虚质 |
| YIX | 阴虚质 |
| TS | 痰湿质 |
| SR | 湿热质 |
| XY | 血瘀质 |
| QY | 气郁质 |
| TB | 特禀质 |

### 健康数据类别 (HealthDataCategory)

| 值 | 描述 |
|---|------|
| VITALS | 生命体征 |
| ACTIVITY | 活动数据 |
| SLEEP | 睡眠数据 |
| NUTRITION | 营养数据 |
| TONGUE | 舌象数据 |
| PULSE | 脉象数据 |
| CONSTITUTION | 体质数据 |
| SYMPTOM | 症状数据 |

### 健康指标类型 (HealthMetricType)

| 值 | 描述 |
|---|------|
| HEART_RATE | 心率 |
| BLOOD_PRESSURE | 血压 |
| BLOOD_OXYGEN | 血氧 |
| BODY_TEMPERATURE | 体温 |
| WEIGHT | 体重 |
| STEPS | 步数 |
| SLEEP_DURATION | 睡眠时长 |
| SLEEP_QUALITY | 睡眠质量 |
| TONGUE_COLOR | 舌色 |
| TONGUE_COATING | 舌苔 |
| PULSE_RATE | 脉率 |
| PULSE_PATTERN | 脉象 |

### 预约状态 (AppointmentStatus)

| 值 | 描述 |
|---|------|
| PENDING | 待确认 |
| CONFIRMED | 已确认 |
| CANCELLED | 已取消 |
| COMPLETED | 已完成 |
| NO_SHOW | 未出席 |

### 产品类别 (ProductCategory)

| 值 | 描述 |
|---|------|
| HERBS | 中药材 |
| FOOD | 食品 |
| TEA | 茶饮 |
| AGRICULTURE | 农产品 |
| BEAUTY | 美容护肤 |
| HEALTH_DEVICE | 健康设备 |

---

> 文档最后更新：2024年7月15日 