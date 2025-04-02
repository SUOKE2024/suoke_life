# 索克生活知识库服务API文档使用指南

本指南介绍如何访问、使用和理解索克生活知识库服务的API文档系统。

## 访问API文档

API文档采用OpenAPI (Swagger) 规范，提供了交互式的界面来浏览和测试API。

### 本地开发环境

1. 启动服务：
   ```bash
   npm run dev
   ```

2. 打开浏览器访问：
   ```
   http://localhost:3002/api-docs
   ```

### 测试/生产环境

生产环境的API文档默认需要进行基本认证才能访问：

```
测试环境: https://test-api.suoke.life/knowledge-base/api-docs
生产环境: https://api.suoke.life/knowledge-base/api-docs
```

认证信息请向系统管理员获取。

## 文档界面导航

Swagger UI提供直观的导航界面：

1. **顶部导航栏** - 提供搜索、过滤等功能
2. **API分组标签** - 按功能模块组织的API端点
3. **授权按钮** - 用于设置认证信息
4. **模型定义** - 显示API使用的数据模型

## 探索API

### 浏览API端点

1. 点击相应的标签组（如"版本管理"、"审核管理"等）展开相关API
2. 每个API会显示：
   - HTTP方法（GET、POST、PUT、DELETE等）
   - 端点URL
   - 简短描述
   - 详细描述

### 查看请求/响应详情

点击API端点展开详情面板，您可以看到：

1. **参数** - 包括路径参数、查询参数和请求体
2. **响应** - 各种状态码对应的响应结构
3. **请求示例** - 可用于测试的示例数据
4. **响应示例** - 预期的响应格式

## 测试API

Swagger UI允许直接在文档界面中测试API：

1. 展开要测试的API端点
2. 填写必要的参数
3. 对于需要认证的端点，点击"Authorize"按钮并输入认证信息
4. 点击"Execute"按钮发送请求
5. 查看响应数据和状态码

## 认证方式

知识库服务API支持两种认证方式：

1. **JWT认证（Bearer Token）**
   - 适用于用户会话
   - 在Authorize对话框中输入格式为"Bearer {token}"的值

2. **API密钥认证**
   - 适用于服务间调用
   - 在Authorize对话框中输入API密钥
   - 或在请求头中添加`X-API-KEY`字段

## 常见响应格式

所有API遵循统一的响应格式：

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error": "错误类型",
  "statusCode": 400
}
```

## 常见问题

**Q: 如何处理分页数据?**  
A: 分页API接受`page`和`limit`查询参数，返回包含分页信息的响应。

**Q: 认证令牌过期怎么办?**  
A: 需要重新获取有效的认证令牌，JWT令牌有效期为24小时。

**Q: 如何获取Swagger JSON文件?**  
A: 访问`/api-docs.json`端点可以获取完整的OpenAPI规范文件。

## 更多资源

- [项目README](../README.md) - 项目概述和安装说明
- [Swagger注解指南](./SWAGGER_ANNOTATION_GUIDE.md) - 如何编写API文档注解
- [API测试指南](./API_TESTING_GUIDE.md) - 详细的API测试方法