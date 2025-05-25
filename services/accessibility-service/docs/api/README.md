# Accessibility Service API文档

## 概述

索克生活无障碍服务API

**版本**: 1.0.0  
**基础URL**: `https://api.suoke.life/accessibility/v1`

## 快速开始

### 认证

本API支持两种认证方式：

1. **Bearer Token (JWT)**
   ```
   Authorization: Bearer <your-jwt-token>
   ```

2. **API Key**
   ```
   X-API-Key: <your-api-key>
   ```

### 基本请求示例

```bash
curl -X POST "https://api.suoke.life/accessibility/v1/blind-assistance/analyze-scene" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "user_id=user123" \
  -F "image=@scene.jpg"
```

## 服务模块

### 🦮 [导盲服务](./blind_assistance.md)
- 场景分析
- 障碍物检测  
- 导航指导

### 🎤 [语音助手](./voice_assistance.md)
- 语音转文字
- 文字转语音
- 语音命令处理

### 🤟 [手语识别](./sign_language.md)
- 手语动作识别
- 手语翻译
- 实时手语交流

### 📖 [屏幕阅读](./screen_reading.md)
- 内容解析
- 语音播报
- 可访问性优化

### 🔄 [内容转换](./content_conversion.md)
- 格式转换
- 可访问性增强
- 多媒体处理

## 错误处理

API使用标准HTTP状态码：

- `200` - 成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `429` - 请求频率限制
- `500` - 服务器内部错误

错误响应格式：
```json
{
  "code": "INVALID_PARAMETER",
  "message": "参数user_id不能为空",
  "details": {
    "field": "user_id",
    "value": null
  }
}
```

## 速率限制

- 全局限制：1000次/分钟
- 用户限制：100次/分钟
- IP限制：200次/分钟

## SDK和工具

- [Python SDK](./sdk/python.md)
- [JavaScript SDK](./sdk/javascript.md)
- [Postman集合](./postman_collection.json)

## 支持

- 📧 邮箱：tech@suoke.life
- 📖 文档：https://docs.suoke.life
- 🐛 问题反馈：https://github.com/suoke-life/issues

---

*最后更新：2025-05-24*
