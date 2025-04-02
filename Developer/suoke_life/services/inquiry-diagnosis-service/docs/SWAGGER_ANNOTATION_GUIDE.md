# Swagger注解指南 - 索克生活问诊诊断服务

## 概述

本文档提供了在索克生活问诊诊断服务中正确使用Swagger JSDoc注解的详细指南。正确的文档注解不仅方便API使用者，也提高了开发效率。

## 控制器注解

### 控制器类注解

为控制器类添加标签注解：

```typescript
/**
 * 控制器描述
 * @swagger
 * tags:
 *   name: 标签名称
 *   description: 标签描述
 */
export class SomeController {
  // ...
}
```

### API端点注解

为控制器方法添加完整的API端点注解：

```typescript
/**
 * 方法描述
 * @swagger
 * /api/path:
 *   method:                           // get, post, put, delete 等
 *     summary: 简短描述
 *     description: 详细描述
 *     tags: [标签名称]                 // 与控制器标签一致
 *     security:                       // 可选，指定安全要求
 *       - bearerAuth: []
 *       - apiKeyAuth: []
 *     parameters:                     // 路径参数、查询参数等
 *       - in: path
 *         name: paramName
 *         schema:
 *           type: string
 *         required: true
 *         description: 参数描述
 *     requestBody:                    // POST/PUT 请求体
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/RequestModel'
 *     responses:                      // 响应定义
 *       200:
 *         description: 成功响应
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ResponseModel'
 *       400:
 *         description: 请求错误
 *       401:
 *         description: 未授权
 *       404:
 *         description: 资源不存在
 *       500:
 *         description: 服务器错误
 */
```

## 数据模型注解

为接口和模型添加完整的组件Schema注解：

```typescript
/**
 * @swagger
 * components:
 *   schemas:
 *     ModelName:
 *       type: object
 *       required:
 *         - requiredField1
 *         - requiredField2
 *       properties:
 *         field1:
 *           type: string
 *           description: 字段描述
 *         field2:
 *           type: number
 *           description: 字段描述
 *         field3:
 *           type: array
 *           items:
 *             type: string
 *           description: 字段描述
 *         field4:
 *           type: object
 *           properties:
 *             nestedField:
 *               type: string
 *           description: 字段描述
 *         field5:
 *           $ref: '#/components/schemas/AnotherModel'
 *       example:
 *         field1: "示例值"
 *         field2: 123
 *         field3: ["示例1", "示例2"]
 *         field4:
 *           nestedField: "嵌套示例"
 */
```

## 通用数据类型参考

以下是常用数据类型的注解示例：

### 基本类型

```
type: string
type: number
type: integer
type: boolean
type: array
type: object
```

### 字符串格式

```
type: string
format: date        // ISO8601 日期格式 (yyyy-MM-dd)
format: date-time   // ISO8601 日期时间格式 (yyyy-MM-ddTHH:mm:ssZ)
format: password    // 密码类型，UI会遮盖
format: email       // 电子邮件格式
format: uuid        // UUID 格式
format: uri         // URI 格式
```

### 数组定义

```
type: array
items:
  type: string      // 简单数组
  
type: array
items:
  $ref: '#/components/schemas/Model'  // 对象数组
```

### 枚举值

```
type: string
enum: [value1, value2, value3]
```

## 安全定义

服务已配置了两种安全验证方式，可以在需要的API注解中引用：

### JWT认证

```
security:
  - bearerAuth: []
```

### API密钥认证

```
security:
  - apiKeyAuth: []
```

### 两种认证都需要

```
security:
  - bearerAuth: []
  - apiKeyAuth: []
```

## 特殊注解用法

### 分页响应

```
responses:
  200:
    description: 成功返回分页数据
    content:
      application/json:
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                total:
                  type: integer
                limit:
                  type: integer
                offset:
                  type: integer
                results:
                  type: array
                  items:
                    $ref: '#/components/schemas/Model'
```

### 文件上传

```
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary
```

## 最佳实践

1. **命名一致性** - 确保模型名称和引用一致
2. **完整描述** - 为每个API和参数提供清晰描述
3. **分组合理** - 使用标签将相关API分组
4. **示例值** - 为复杂模型提供示例值
5. **错误响应** - 详细定义可能的错误响应
6. **必填标记** - 明确标记必填字段
7. **验证规则** - 添加最小值、最大值、正则表达式等验证规则

## 常见错误及解决方法

1. **模型引用错误** - 确保引用 `'#/components/schemas/ModelName'` 与模型定义完全一致
2. **路径定义冲突** - 确保不同的API路径定义不冲突
3. **缺少响应定义** - 确保每个API至少定义200响应
4. **类型定义错误** - 确保使用正确的数据类型（如 string, number, boolean 等）
5. **标签拼写错误** - 确保tags中使用的标签名与标签定义完全一致

---

遵循这些指南可以确保API文档的一致性和可用性。如有问题，请联系技术团队 <tech@suoke.life>。