# 医疗资源服务 API 文档

## 概述

医疗资源服务是索克生活平台的核心服务之一，提供智能医疗资源匹配、预约管理、食农结合、山水养生等功能。

## 服务架构

```
医疗资源服务
├── 核心医疗资源服务 (EnhancedMedicalResourceService)
├── 食农结合服务 (EnhancedFoodAgricultureService)
├── 山水养生服务 (WellnessTourismService)
├── 名医资源管理服务 (FamousDoctorService)
└── 智能预约服务 (IntelligentAppointmentService)
```

## API 端点

### 1. 核心医疗资源 API

#### 1.1 资源匹配
```http
POST /api/v1/medical/resources/match
```

**请求体:**
```json
{
  "patient_id": "string",
  "resource_type": "DOCTOR|HOSPITAL|EQUIPMENT|MEDICINE",
  "specialty": "string",
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "address": "北京市朝阳区"
  },
  "symptoms": ["头痛", "失眠"],
  "budget_range": [100.0, 500.0],
  "priority": "LOW|NORMAL|HIGH|URGENT"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "resource_id": "string",
        "resource_type": "DOCTOR",
        "name": "张三医生",
        "specialty": "中医内科",
        "rating": 4.5,
        "distance_km": 2.3,
        "match_score": 0.95,
        "availability": {
          "next_available": "2024-01-15T09:00:00Z",
          "slots": [...]
        }
      }
    ],
    "total_count": 10,
    "search_criteria": {...}
  }
}
```

#### 1.2 资源调度优化
```http
POST /api/v1/medical/resources/optimize
```

### 2. 食农结合服务 API

#### 2.1 获取食疗推荐
```http
POST /api/v1/food-agriculture/recommendations
```

**请求体:**
```json
{
  "user_id": "string",
  "constitution_type": "QI_DEFICIENCY|YIN_DEFICIENCY|YANG_DEFICIENCY|...",
  "health_goals": ["增强体质", "改善睡眠"],
  "current_symptoms": ["疲劳", "失眠"],
  "dietary_restrictions": ["无麸质", "素食"],
  "preferences": {
    "preferred_categories": ["蔬菜", "水果"],
    "preferred_tastes": ["甘", "酸"]
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "food_id": "string",
        "name": "山药",
        "category": "根茎类",
        "tcm_properties": {
          "nature": "平",
          "taste": "甘",
          "meridians": ["脾", "肺", "肾"]
        },
        "nutritional_info": {
          "calories_per_100g": 56,
          "protein": 1.9,
          "carbohydrates": 12.4
        },
        "health_benefits": ["补脾益肾", "固精止带"],
        "tcm_theory_basis": "山药味甘性平，归脾、肺、肾经，具有补脾益肾的功效",
        "preparation_methods": ["蒸煮", "炖汤", "煮粥"],
        "dosage_recommendation": "每日50-100克",
        "contraindications": ["湿盛中满者慎用"],
        "confidence_score": 0.92,
        "seasonal_suitability": ["秋", "冬"]
      }
    ],
    "total_count": 15,
    "personalization_factors": {
      "constitution_match": 0.95,
      "symptom_relevance": 0.88,
      "seasonal_appropriateness": 0.90
    }
  }
}
```

#### 2.2 创建个性化营养计划
```http
POST /api/v1/food-agriculture/nutrition-plan
```

#### 2.3 智能种植计划
```http
POST /api/v1/food-agriculture/planting-plan
```

### 3. 山水养生服务 API

#### 3.1 查找养生目的地
```http
POST /api/v1/wellness-tourism/destinations
```

**请求体:**
```json
{
  "user_id": "string",
  "constitution_type": "平和质",
  "health_goals": ["放松身心", "改善睡眠"],
  "preferred_wellness_types": ["MOUNTAIN_THERAPY", "WATER_THERAPY", "HOT_SPRING"],
  "budget_range": [1000.0, 3000.0],
  "duration_days": 3,
  "location_preference": {
    "max_distance_km": 500,
    "preferred_regions": ["华北", "华东"]
  },
  "special_requirements": ["适合老年人", "有医疗监护"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "destinations": [
      {
        "destination_id": "string",
        "name": "泰山养生度假村",
        "location": {
          "latitude": 36.2532,
          "longitude": 117.1201,
          "address": "山东省泰安市泰山区"
        },
        "wellness_types": ["MOUNTAIN_THERAPY", "TCM_WELLNESS"],
        "facilities": ["中医理疗中心", "养生餐厅", "冥想花园"],
        "programs": [
          {
            "name": "山地疗养计划",
            "duration_days": 3,
            "price": 1800.0,
            "activities": ["登山健行", "森林浴", "中医调理"]
          }
        ],
        "rating": 4.6,
        "reviews_count": 128,
        "match_score": 0.89,
        "distance_km": 450.2,
        "availability": {
          "next_available": "2024-01-20",
          "booking_status": "AVAILABLE"
        }
      }
    ],
    "total_count": 8,
    "search_metadata": {
      "search_radius_km": 500,
      "filters_applied": ["budget", "wellness_type", "duration"]
    }
  }
}
```

#### 3.2 创建养生计划
```http
POST /api/v1/wellness-tourism/plan
```

### 4. 名医资源管理 API

#### 4.1 搜索名医
```http
POST /api/v1/famous-doctors/search
```

**请求体:**
```json
{
  "keywords": "心血管",
  "specialty": "心血管内科",
  "level": "NATIONAL_MASTER|PROVINCIAL_MASTER|CITY_MASTER",
  "location": "北京",
  "min_rating": 4.5,
  "max_fee": 500.0,
  "available_today": true,
  "min_experience": 10,
  "limit": 10,
  "offset": 0
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "doctors": [
      {
        "doctor_id": "string",
        "name": "王教授",
        "title": "主任医师",
        "level": "NATIONAL_MASTER",
        "hospital": {
          "name": "北京协和医院",
          "level": "三甲"
        },
        "specialties": [
          {
            "name": "心血管内科",
            "experience_years": 25,
            "certifications": ["心血管介入治疗资质"]
          }
        ],
        "achievements": [
          "国家级名老中医",
          "享受国务院特殊津贴专家"
        ],
        "consultation_fee": 300.0,
        "average_rating": 4.8,
        "total_reviews": 256,
        "availability": {
          "next_available_slot": "2024-01-16T14:00:00Z",
          "weekly_schedule": {...}
        },
        "contact_info": {
          "hospital_phone": "010-69156114",
          "department": "心血管内科"
        }
      }
    ],
    "total_count": 25,
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "has_next": true
    }
  }
}
```

#### 4.2 获取医生详细信息
```http
GET /api/v1/famous-doctors/{doctor_id}
```

### 5. 智能预约服务 API

#### 5.1 创建预约请求
```http
POST /api/v1/appointments/request
```

**请求体:**
```json
{
  "patient_id": "string",
  "doctor_id": "string",
  "appointment_type": "CONSULTATION|FOLLOW_UP|EMERGENCY|HEALTH_CHECK",
  "preferred_date": "2024-01-15",
  "time_range_start": "09:00",
  "time_range_end": "17:00",
  "symptoms": ["头痛", "失眠"],
  "urgency_level": "NORMAL|HIGH|URGENT",
  "contact_info": {
    "phone": "13800138000",
    "email": "patient@example.com",
    "emergency_contact": "13900139000"
  },
  "special_requirements": "需要中医调理",
  "insurance_info": {
    "provider": "中国人寿",
    "policy_number": "123456789"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "appointment_id": "string",
    "status": "PENDING|CONFIRMED|CANCELLED",
    "scheduled_time": "2024-01-15T10:00:00Z",
    "doctor_info": {
      "name": "张医生",
      "hospital": "北京中医医院",
      "department": "中医内科"
    },
    "appointment_details": {
      "duration_minutes": 30,
      "consultation_fee": 200.0,
      "location": "门诊楼3楼301室"
    },
    "confirmation_code": "ABC123",
    "instructions": [
      "请提前15分钟到达",
      "携带身份证和病历本"
    ]
  }
}
```

#### 5.2 确认预约
```http
POST /api/v1/appointments/{appointment_id}/confirm
```

#### 5.3 取消预约
```http
POST /api/v1/appointments/{appointment_id}/cancel
```

#### 5.4 获取预约详情
```http
GET /api/v1/appointments/{appointment_id}
```

#### 5.5 获取预约分析
```http
GET /api/v1/appointments/analytics
```

**查询参数:**
- `start_date`: 开始日期
- `end_date`: 结束日期
- `doctor_id`: 医生ID（可选）
- `department`: 科室（可选）

## 错误处理

所有API都遵循统一的错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "constitution_type",
      "reason": "不支持的体质类型"
    }
  },
  "request_id": "req_123456789"
}
```

### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMITED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 内部服务器错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

## 认证和授权

### API密钥认证
```http
Authorization: Bearer <api_key>
```

### JWT令牌认证
```http
Authorization: Bearer <jwt_token>
```

## 限流和配额

- 每个API密钥每分钟最多1000次请求
- 每个用户每天最多10000次请求
- 批量操作每次最多处理100个项目

## 数据格式

### 日期时间格式
- 使用ISO 8601格式：`2024-01-15T10:00:00Z`
- 时区：UTC

### 坐标格式
- 纬度：-90.0 到 90.0
- 经度：-180.0 到 180.0
- 精度：小数点后6位

### 货币格式
- 单位：人民币元
- 精度：小数点后2位

## SDK和示例

### Python SDK
```python
from suoke_medical_client import MedicalResourceClient

client = MedicalResourceClient(api_key="your_api_key")

# 获取食疗推荐
recommendations = client.food_agriculture.get_recommendations(
    user_id="user123",
    constitution_type="QI_DEFICIENCY",
    health_goals=["增强体质"]
)

# 搜索名医
doctors = client.famous_doctors.search(
    specialty="中医内科",
    min_rating=4.5
)

# 创建预约
appointment = client.appointments.create_request(
    patient_id="patient123",
    doctor_id="doctor456",
    appointment_type="CONSULTATION",
    preferred_date="2024-01-15"
)
```

### JavaScript SDK
```javascript
import { MedicalResourceClient } from '@suoke/medical-client';

const client = new MedicalResourceClient({
  apiKey: 'your_api_key'
});

// 获取养生目的地
const destinations = await client.wellnessTourism.findDestinations({
  userId: 'user123',
  constitutionType: '平和质',
  healthGoals: ['放松身心']
});
```

## 版本控制

当前API版本：v1

版本策略：
- 主要版本变更：不兼容的API变更
- 次要版本变更：向后兼容的功能添加
- 补丁版本变更：向后兼容的问题修复

## 支持和联系

- 技术支持：tech-support@suoke.life
- API文档：https://docs.suoke.life/medical-resource-service
- 状态页面：https://status.suoke.life
- GitHub：https://github.com/suoke-life/medical-resource-service 