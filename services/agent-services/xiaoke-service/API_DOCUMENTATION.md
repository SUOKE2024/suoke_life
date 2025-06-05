# XiaoKe Service API 文档

## 概述
XiaoKe智能体服务提供商业化健康服务，包括名医匹配、农产品溯源、健康商品推荐等功能。

## API端点

### 1. 智能体管理
- `GET /api/v1/agent/status` - 获取智能体状态
- `POST /api/v1/agent/chat` - 与智能体对话

### 2. 名医匹配
- `GET /api/v1/doctors/search` - 搜索医生
- `POST /api/v1/appointments/create` - 创建预约
- `GET /api/v1/appointments/{id}` - 获取预约详情

### 3. 农产品溯源
- `GET /api/v1/products/{id}/trace` - 产品溯源信息
- `POST /api/v1/products/verify` - 产品验证

### 4. 健康商品推荐
- `GET /api/v1/recommendations` - 获取推荐商品
- `POST /api/v1/products/rate` - 商品评价

## 响应格式
所有API响应都遵循统一格式：
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```
