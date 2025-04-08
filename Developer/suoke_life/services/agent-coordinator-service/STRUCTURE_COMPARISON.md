# Node.js和Go实现结构对比文档

本文档对比了代理协调器服务在Node.js和Go实现中的代码结构差异，以便于理解两个版本之间的映射关系。

## 目录结构对比

| Node.js结构 | Go结构 | 说明 |
|------------|--------|------|
| `src/index.ts` | `cmd/main.go` | 应用程序入口点 |
| `src/controllers/` | `internal/handlers/` | 控制器/处理器 |
| `src/routes/` | `internal/router/` | 路由定义 |
| `src/middlewares/` | `internal/middleware/` | 中间件 |
| `src/services/` | `internal/services/` | 服务层 |
| `src/models/` | `internal/models/` | 数据模型 |
| `src/utils/config-loader.ts` | `internal/config/` | 配置加载 |
| `src/utils/` | `internal/utils/`或`pkg/` | 实用工具 |
| `src/errors/` | `internal/api/errors/` | 错误定义 |

## API路由对比

| Node.js路由 | Go路由 | 说明 |
|------------|--------|------|
| `/api/sessions` | `/api/sessions` | 会话管理API |
| `/api/agents` | `/api/agents` | 代理服务API |
| `/api/coordination` | `/api/coordination` | 协调操作API |
| `/api/knowledge` | `/api/knowledge` | 知识服务API |

## 主要功能模块对比

### 1. 会话管理

| Node.js实现 | Go实现 | 说明 |
|------------|--------|------|
| `session-routes.ts` | `internal/router/session_routes.go` | 路由定义 |
| `session-controller.ts` | `internal/handlers/session_handler.go` | 控制器逻辑 |
| `session-service.ts` | `internal/services/session_service.go` | 服务层业务逻辑 |
| `session-model.ts` | `internal/models/session.go` | 数据模型 |

### 2. 代理服务

| Node.js实现 | Go实现 | 说明 |
|------------|--------|------|
| `agent-routes.ts` | `internal/router/agent_routes.go` | 路由定义 |
| `agent-controller.ts` | `internal/handlers/agent_handler.go` | 控制器逻辑 |
| `agent-service.ts` | `internal/services/agent_service.go` | 服务层业务逻辑 |
| `agent-model.ts` | `internal/models/agent.go` | 数据模型 |

### 3. 协调操作

| Node.js实现 | Go实现 | 说明 |
|------------|--------|------|
| `coordination-routes.ts` | `internal/router/coordination_routes.go` | 路由定义 |
| `coordination-controller.ts` | `internal/handlers/coordination_handler.go` | 控制器逻辑 |
| `coordination-service.ts` | `internal/services/coordination_service.go` | 服务层业务逻辑 |
| `coordination-model.ts` | `internal/models/coordination.go` | 数据模型 |

### 4. 知识服务

| Node.js实现 | Go实现 | 说明 |
|------------|--------|------|
| `knowledge-routes.ts` | `internal/router/knowledge_routes.go` | 路由定义 |
| `knowledge-controller.ts` | `internal/handlers/knowledge_handler.go` | 控制器逻辑 |
| `knowledge-service.ts` | `internal/services/knowledge_service.go` | 服务层业务逻辑 |
| `knowledge-model.ts` | `internal/models/knowledge.go` | 数据模型 |

## 中间件对比

| Node.js中间件 | Go中间件 | 说明 |
|--------------|----------|------|
| `auth-middleware.ts` | `internal/middleware/auth.go` | API认证中间件 |
| `error-handler.ts` | `internal/middleware/error.go` | 错误处理中间件 |
| `morgan + logger` | `internal/middleware/logger.go` | 日志中间件 |
| `express-rate-limit` | `internal/middleware/rate_limiter.go` | 速率限制中间件 |

## 配置结构对比

| Node.js配置 | Go配置 | 说明 |
|------------|--------|------|
| `.env` | `.env` | 环境变量 |
| `config.json` | `config.json` | 配置文件 |
| `loadConfig()` | `config.LoadConfig()` | 配置加载函数 |

## 持久化实现对比

| Node.js实现 | Go实现 | 说明 |
|------------|--------|------|
| `redis-service.ts` | `internal/services/redis_service.go` | Redis服务 |
| 内存存储 | `internal/services/memory_service.go` | 内存存储 |
| 文件系统存储 | `internal/services/file_service.go` | 文件系统存储 |

## 核心差异

1. **错误处理**：
   - Node.js: 使用回调和Promise的错误处理
   - Go: 显式错误返回和错误检查

2. **并发模型**：
   - Node.js: 事件循环和回调
   - Go: Goroutines和通道

3. **类型系统**：
   - Node.js: TypeScript的静态类型
   - Go: 原生静态类型

4. **性能特性**：
   - Node.js: 非阻塞I/O，单线程
   - Go: 高并发，多线程，适合CPU密集型任务

5. **内存管理**：
   - Node.js: 垃圾回收
   - Go: 垃圾回收 + 值语义

## 功能测试矩阵

| 功能 | Node.js测试 | Go测试 | 功能等价性 |
|------|------------|--------|-----------|
| 创建会话 | ✅ | ✅ | 完全等价 |
| 获取会话 | ✅ | ✅ | 完全等价 |
| 更新会话 | ✅ | ✅ | 完全等价 |
| 删除会话 | ✅ | ✅ | 完全等价 |
| 代理方法调用 | ✅ | ✅ | 完全等价 |
| 知识图谱查询 | ✅ | ✅ | 完全等价 |
| 速率限制 | ✅ | ✅ | 完全等价 |
| API认证 | ✅ | ✅ | 完全等价 |
| 健康检查 | ✅ | ✅ | 完全等价 |
| 指标收集 | ✅ | ⚠️ | 部分实现 |
| Redis持久化 | ✅ | ⚠️ | 部分实现 |
| 文件系统持久化 | ✅ | ⚠️ | 部分实现 |
| 分布式追踪 | ✅ | ❌ | 尚未实现 | 