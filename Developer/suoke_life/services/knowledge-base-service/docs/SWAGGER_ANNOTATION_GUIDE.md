# Swagger注解编写指南

本指南介绍如何使用Swagger JSDoc注解为索克生活知识库服务的API添加文档。

## 基础概念

Swagger JSDoc使用JSDoc风格的注释为API生成OpenAPI 3.0文档。通过在代码中添加特定格式的注释，可以自动生成完整的API文档。

## 文件注解位置

根据Clean Architecture架构，在以下位置添加Swagger注解：

1. **控制器文件** (`src/controllers/*.ts`) - API端点的主要文档
2. **路由文件** (`src/routes/*.ts`) - 路由标签和分组
3. **模型文件** (`src/models/*.ts`) - 数据模型定义
4. **接口文件** (`src/interfaces/*.ts`) - 通用响应格式和DTO定义

## 控制器方法注解

控制器方法是添加API文档的主要位置，遵循以下格式：

```typescript
/**
 * 方法描述
 * @swagger
 * /api/path/{param}:
 *   get:                        // HTTP方法，可以是get, post, put, delete等
 *     summary: 简短描述          // 端点的简短描述
 *     description: 详细描述      // 端点的详细描述
 *     tags: [标签名称]          // 分组标签
 *     parameters:               // 请求参数定义
 *       - in: path              // 参数位置，可以是path, query, header, cookie
 *         name: param           // 参数名称
 *         schema:               // 参数类型定义
 *           type: string
 *         required: true        // 是否必需
 *         description: 参数描述  // 参数描述
 *     requestBody:              // 请求体（仅适用于POST, PUT等）
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/模型名称'  // 引用预定义模型
 *     responses:                // 响应定义
 *       200:                    // HTTP状态码
 *         description: 成功响应描述
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/响应模型'
 *       400:
 *         description: 错误响应描述
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
```

## 模型定义注解

在模型或接口文件中定义数据结构：

```typescript
/**
 * 模型描述
 * @swagger
 * components:
 *   schemas:
 *     模型名称:
 *       type: object
 *       required:
 *         - 必需字段1
 *         - 必需字段2
 *       properties:
 *         字段1:
 *           type: string
 *           description: 字段描述
 *         字段2:
 *           type: integer
 *           description: 字段描述
 *         嵌套对象:
 *           type: object
 *           properties:
 *             子字段:
 *               type: string
 *         数组字段:
 *           type: array
 *           items:
 *             type: string
 *       example:
 *         字段1: "示例值"
 *         字段2: 123
 */
```

## 路由标签注解

在路由文件中定义API分组标签：

```typescript
/**
 * @swagger
 * tags:
 *   name: 标签名称
 *   description: 标签描述
 */
```

## 安全定义

为需要认证的API添加安全定义：

```typescript
/**
 * @swagger
 * /api/secure-endpoint:
 *   get:
 *     security:
 *       - bearerAuth: []    // JWT认证
 *       - apiKeyAuth: []    // API密钥认证
 */
```

## 响应模型引用

使用预定义的响应模型保持一致性：

```typescript
/**
 * @swagger
 * /api/endpoint:
 *   get:
 *     responses:
 *       200:
 *         content:
 *           application/json:
 *             schema:
 *               allOf:
 *                 - $ref: '#/components/schemas/ApiResponse'  // 基础响应
 *                 - type: object
 *                   properties:
 *                     data:
 *                       $ref: '#/components/schemas/自定义模型'  // 特定数据
 */
```

## 分页响应注解

为分页API添加标准注解：

```typescript
/**
 * @swagger
 * /api/paginated-endpoint:
 *   get:
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 页码（从1开始）
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 每页数量
 *     responses:
 *       200:
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/PaginatedResponse'
 */
```

## 常见数据类型

- `string` - 字符串
- `integer` - 整数
- `number` - 数字（包括浮点数）
- `boolean` - 布尔值
- `object` - 对象
- `array` - 数组

## 特殊格式

- `string` + `format: date` - 日期 (YYYY-MM-DD)
- `string` + `format: date-time` - 日期时间 (ISO 8601)
- `string` + `format: email` - 电子邮件地址
- `string` + `format: uuid` - UUID
- `string` + `format: password` - 密码（在UI中会被遮盖）

## 可重用响应

定义常用响应以便重复使用：

```typescript
/**
 * @swagger
 * components:
 *   responses:
 *     NotFound:
 *       description: 资源未找到
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ErrorResponse'
 */

// 在API文档中引用
/**
 * @swagger
 * /api/endpoint/{id}:
 *   get:
 *     responses:
 *       404:
 *         $ref: '#/components/schemas/responses/NotFound'
 */
```

## 最佳实践

1. **保持一致性** - 使用相同的格式和术语描述类似的API
2. **详细描述参数** - 对每个参数提供清晰的说明和约束
3. **使用引用** - 尽可能引用预定义的组件避免重复
4. **提供示例** - 为请求和响应提供实际的例子
5. **适当分组** - 使用标签将相关API分组在一起
6. **文档化错误** - 记录所有可能的错误响应和状态码

## 测试验证

添加Swagger注解后，务必：

1. 启动服务查看生成的文档
2. 验证所有API是否正确显示
3. 测试示例请求是否工作
4. 检查模型定义是否准确

## 更多资源

- [Swagger JSDoc官方文档](https://github.com/Surnet/swagger-jsdoc/blob/master/docs/GETTING-STARTED.md)
- [OpenAPI 3.0规范](https://swagger.io/specification/)
- [API文档使用指南](./API_DOCS_GUIDE.md)