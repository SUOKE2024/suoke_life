# 索克生活 API 文档

## 📚 API文档概览

本目录包含索克生活平台所有微服务的完整API文档。

## 🏗️ 服务架构

### 核心服务
- [API网关](./core-services/api-gateway.md) - 统一入口和路由管理
- [认证服务](./core-services/auth-service.md) - 用户认证和授权
- [用户服务](./core-services/user-service.md) - 用户信息管理

### 智能体服务
- [小艾服务](./agent-services/xiaoai-service.md) - 健康助手和多模态诊断
- [小克服务](./agent-services/xiaoke-service.md) - 商业服务和产品推荐
- [老克服务](./agent-services/laoke-service.md) - 知识传播和社区管理
- [索儿服务](./agent-services/soer-service.md) - 生活管理和营养指导

### 诊断服务
- [望诊服务](./diagnostic-services/look-service.md) - 视觉诊断和舌象分析
- [闻诊服务](./diagnostic-services/listen-service.md) - 音频诊断和声纹分析
- [问诊服务](./diagnostic-services/inquiry-service.md) - 智能问诊和症状收集
- [切诊服务](./diagnostic-services/palpation-service.md) - 脉象分析和触诊辅助
- [算诊服务](./diagnostic-services/calculation-service.md) - 综合诊断和治疗建议

### 业务服务
- [健康数据服务](./business-services/health-data-service.md) - 健康数据存储和分析
- [区块链服务](./business-services/blockchain-service.md) - 数据确权和溯源
- [RAG服务](./business-services/rag-service.md) - 知识检索和增强
- [消息总线](./business-services/message-bus.md) - 异步消息处理
- [医疗资源服务](./business-services/medical-resource-service.md) - 医疗资源管理

## 🔧 API使用指南

### 认证方式
所有API请求都需要在Header中包含JWT令牌：
```
Authorization: Bearer <your-jwt-token>
```

### 基础URL
- **开发环境**: `http://localhost:8080/api/v1`
- **测试环境**: `https://test-api.suoke.life/api/v1`
- **生产环境**: `https://api.suoke.life/api/v1`

### 响应格式
所有API响应都遵循统一格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### 错误处理
错误响应格式：
```json
{
  "code": 400,
  "message": "参数错误",
  "error": "详细错误信息",
  "timestamp": "2025-01-27T10:00:00Z"
}
```

## 📖 快速开始

1. [获取API密钥](./guides/authentication.md)
2. [SDK使用指南](./guides/sdk-usage.md)
3. [示例代码](./examples/)
4. [Postman集合](./postman/)

## 🔗 相关链接

- [部署文档](../deployment/)
- [用户文档](../user/)
- [故障排除](../troubleshooting/)
- [更新日志](./CHANGELOG.md)

