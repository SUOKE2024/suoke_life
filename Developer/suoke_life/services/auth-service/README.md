# 索克生活认证服务

## 项目概述
索克生活认证服务是索克生活APP后端微服务架构的组成部分，负责用户认证、授权和会话管理等核心安全功能。

## 功能特性
- 用户认证与授权
- 会话管理
- 双因素认证
- 监控与指标收集
- 安全审计日志
- 知识库权限管理
- 生物识别认证
- 跨浏览器CSRF保护

## 技术栈
- Node.js
- Express.js
- Winston (日志)
- Mocha & Chai (测试)
- Redis (缓存和会话)
- MySQL (数据存储)

## 项目结构
```
services/auth-service/
├── src/                    # 源代码
│   ├── controllers/        # 控制器
│   ├── middlewares/        # 中间件
│   ├── services/           # 服务层
│   └── utils/              # 工具函数
├── test/                   # 测试
│   ├── unit/               # 单元测试
│   └── integration/        # 集成测试
├── app.js                  # 应用配置
├── server.js               # 服务入口
└── package.json            # 项目配置
```

## 指标服务
指标服务提供应用性能和健康状况的监控功能：

### 主要功能
- 计数器(Counter): 记录事件发生次数
- 仪表盘(Gauge): 记录当前值，如连接数
- 计时器(Timer): 记录耗时情况
- 直方图(Histogram): 记录值的分布情况

### API端点
- GET /api/metrics: 获取所有指标
- DELETE /api/metrics: 重置所有指标

## 安装与运行
```bash
# 安装依赖
npm install

# 开发模式运行
npm run dev

# 生产模式运行
npm start

# 运行测试
npm test
```

## 监控与日志
- 应用指标: http://localhost:3000/api/metrics
- 日志文件: ./logs/combined.log

认证服务版本：v2.0.0（已完全支持JWT刷新机制和知识库权限管理，跨浏览器CSRF保护，多层缓存）
数据库：MySQL（根据架构规范要求）

## 功能亮点

- 标准JWT认证
- OAuth2.0第三方登录
- 短信验证码认证
- 手机号快速登录
- 生物识别认证
- 跨浏览器CSRF保护
- 密码策略实施
- 知识库和知识图谱权限管理
- 多级缓存与权限优化
- 多角色权限合并逻辑

## 知识库权限管理

完整的知识库和知识图谱权限管理功能，支持：

- 细粒度权限控制：`knowledge:read`、`knowledge:write`、`graph:read`、`graph:write`、`sensitive:read`等
- 领域特定权限：`tcm:read`、`nutrition:read`、`mental_health:read`等
- 基于角色的权限管理
- 权限验证API（包括高性能批量验证）
- 资源访问日志
- 多角色权限合并逻辑
- 内存+Redis多级缓存

### 权限类型

| 权限名称 | 描述 |
|---------|------|
| knowledge:read | 基础知识库读取权限 |
| knowledge:write | 基础知识库编辑权限 |
| graph:read | 知识图谱查询权限 |
| graph:write | 知识图谱编辑权限 |
| sensitive:read | 敏感知识访问权限 |
| tcm:read | 中医知识访问权限 |
| nutrition:read | 营养知识访问权限 |
| mental_health:read | 心理健康知识访问权限 |
| environmental_health:read | 环境健康知识访问权限 |
| precision_medicine:read | 精准医疗知识访问权限 |

### API端点

| 路径 | 方法 | 描述 |
|-----|------|------|
| /api/v1/knowledge/permissions | GET | 获取当前用户的知识库权限 |
| /api/v1/knowledge/check-access | POST | 检查对特定资源的访问权限 |
| /api/v1/knowledge/batch-check-access | POST | 批量检查多个资源的访问权限 |
| /api/v1/knowledge/user/:userId/permissions | GET | 获取指定用户的知识库权限 |
| /api/v1/knowledge/user/:userId/permissions | POST | 分配知识库权限给用户 |
| /api/v1/knowledge/user/:userId/permissions | DELETE | 撤销用户的知识库权限 |
| /api/v1/knowledge/access-log | POST | 记录知识资源访问日志 |
| /api/v1/knowledge/access-logs | GET | 获取知识资源访问日志 |

## 性能优化

本服务已实现多级缓存策略，大幅提升性能：

- 内存缓存：用于高频访问的权限检查和用户权限
- Redis缓存：作为二级缓存，提供更长期的数据存储
- 分级缓存策略：
  - L1缓存：高频访问的只读资源（10分钟TTL）
  - L2缓存：标准权限（30分钟TTL）
  - L3缓存：低频访问权限（2小时TTL）
- 批量处理能力：支持单次请求批量检查多个资源权限

性能测试显示：
- 平均响应时间：<100ms
- 高负载下（70%+）响应时间：<150ms
- 每秒处理权限检查请求：5000+

## 安全增强

- 跨浏览器CSRF保护：对不同浏览器（尤其是Safari）提供专门处理
- 改进的SameSite Cookie策略
- 生物识别认证支持：指纹、面部ID等
- 设备注册和验证

## 数据库迁移

执行以下命令应用数据库迁移：

```bash
NODE_ENV=production node ./node_modules/.bin/knex migrate:latest --knexfile ./src/config/knexfile.js
```

## 环境变量

配置文件位于 `.env`，主要环境变量包括：

```
# 服务器配置
PORT=3001
NODE_ENV=production

# 数据库配置
DB_HOST=mysql-service
DB_PORT=3306
DB_USER=suoke_auth
DB_PASSWORD=xxxxx
DB_NAME=suoke_auth

# JWT配置
JWT_SECRET=xxxxxxxxxxxx
JWT_EXPIRES_IN=1h
JWT_REFRESH_EXPIRES_IN=7d

# Redis配置
REDIS_HOST=redis-service
REDIS_PORT=6379
REDIS_PASSWORD=xxxxx

# 服务间认证
INTERNAL_SERVICE_KEY=xxxxxxxxxxxx
```

## 集成指南

其他服务可通过以下步骤与认证服务集成：

1. 在请求时添加JWT令牌到Authorization头：`Bearer {token}`
2. 对需要知识库权限的资源，使用`/api/v1/knowledge/check-access`验证权限
3. 对于需要批量检查的场景，使用`/api/v1/knowledge/batch-check-access`提高性能
4. 记录资源访问日志到`/api/v1/knowledge/access-log`