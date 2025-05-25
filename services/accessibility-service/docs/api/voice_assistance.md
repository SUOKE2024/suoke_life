# 语音助手 API

## 概述

语音助手提供专业的无障碍辅助功能。

## 端点

### POST /voice_assistance/...

详细的API端点文档...

## 示例

### 请求示例

```bash
curl -X POST "https://api.suoke.life/accessibility/v1/voice_assistance/..." \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### 响应示例

```json
{
  "user_id": "user123",
  "timestamp": "2024-01-01T00:00:00Z",
  "result": "..."
}
```

## 错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| E001 | 参数错误 | 检查请求参数 |
| E002 | 文件格式不支持 | 使用支持的文件格式 |

---

[返回主文档](./README.md)
