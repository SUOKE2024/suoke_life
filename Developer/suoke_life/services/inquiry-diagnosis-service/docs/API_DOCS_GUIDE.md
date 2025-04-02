# 索克生活问诊诊断服务API文档使用指南

## 概述

本文档介绍如何使用和维护索克生活问诊诊断服务的API文档。我们使用Swagger/OpenAPI规范来提供交互式API文档，方便开发者了解、测试和集成我们的API。

## 访问API文档

### 开发环境

在开发环境中，可以通过以下URL访问API文档：

```
http://localhost:3007/api-docs
```

### 生产环境

在生产环境中，API文档默认关闭。如需访问，需要在环境变量中设置：

```
ENABLE_API_DOCS=true
API_DOCS_BASIC_AUTH=true
API_DOCS_USERNAME=your_username
API_DOCS_PASSWORD=your_password
```

然后可以通过以下URL访问：

```
https://api.suoke.life/inquiry-diagnosis/api-docs
```

## 文档功能

Swagger UI提供了以下主要功能：

1. **API端点浏览**：按标签分组显示所有API端点
2. **请求/响应模型**：详细展示每个API的请求和响应格式
3. **交互式测试**：直接在页面上测试API调用
4. **授权管理**：配置JWT认证令牌或API密钥
5. **模型展示**：显示应用中使用的所有数据模型

## 授权设置

在测试需要授权的API时，可以按以下步骤设置授权：

1. 点击界面右上角的"Authorize"按钮
2. 根据API的要求选择认证方式：
   - Bearer Token: 输入`Bearer your_jwt_token`
   - API Key: 输入API密钥

## 为新API添加文档

使用JSDoc风格的注释为控制器方法添加文档：

```typescript
/**
 * 方法描述
 * @swagger
 * /api/resource/{id}:
 *   get:
 *     summary: 简短描述
 *     tags: [资源分类]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 资源ID
 *     responses:
 *       200:
 *         description: 成功响应描述
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ResourceModel'
 *       404:
 *         description: 资源不存在
 */
public getResource = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  // 实现代码
}
```

## 数据模型文档

使用JSDoc风格的注释为数据模型添加文档：

```typescript
/**
 * @swagger
 * components:
 *   schemas:
 *     ResourceModel:
 *       type: object
 *       required:
 *         - id
 *         - name
 *       properties:
 *         id:
 *           type: string
 *           description: 资源ID
 *         name:
 *           type: string
 *           description: 资源名称
 *         description:
 *           type: string
 *           description: 资源描述
 */
export interface ResourceModel {
  id: string;
  name: string;
  description?: string;
}
```

## 最佳实践

1. **保持文档更新**：每当修改API时，同时更新文档注释
2. **使用标签**：使用一致的标签对API进行分组
3. **详细描述**：提供足够的描述信息，包括参数用途、可能的值等
4. **包含示例**：添加请求和响应的示例，帮助开发者更好地理解
5. **标记必填字段**：在schema的required数组中列出必填参数
6. **安全性考虑**：在生产环境中启用基本认证，保护API文档

## 故障排除

如果遇到文档问题：

1. **文档未显示**：检查环境变量`ENABLE_API_DOCS`是否设置为true
2. **基本认证失败**：确认环境变量中的用户名和密码配置
3. **API未显示**：检查控制器方法是否有正确的JSDoc注释
4. **模型引用错误**：确保模型名称在引用时完全匹配

## 维护和更新

Swagger配置文件位于`src/config/swagger.ts`。如需更改全局配置，请编辑此文件。

更新API文档步骤：

1. 修改控制器或模型中的JSDoc注释
2. 重新构建和启动服务
3. 刷新API文档页面查看更新

---

更多信息请参阅[OpenAPI规范](https://swagger.io/specification/)和[Swagger JSDoc文档](https://github.com/Surnet/swagger-jsdoc/blob/master/docs/GETTING-STARTED.md)。