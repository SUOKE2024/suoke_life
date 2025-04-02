# 索克生活用户服务 [完成度: 100%]

## 功能概述

用户服务负责处理用户相关的所有功能，包括但不限于：

- 用户注册、登录、注销
- 用户信息管理
- 用户偏好设置
- 健康档案管理
- 知识偏好管理和交互历史
- 社交分享功能
- 用户兴趣图谱匹配

## 技术栈

- Node.js & Express
- MySQL 数据库
- Redis 缓存
- JWT 认证
- 微服务架构

## 新增功能：知识库和知识图谱集成

用户服务现已增强，支持与知识库和知识图谱服务的无缝集成，包括以下功能：

### 1. 知识偏好管理

- 用户可以设置感兴趣的知识领域（中医药、营养健康、精准医疗等）
- 可以选择偏好的内容类型（文章、视频、图解等）
- 可以设置内容难度级别（初级、中级、高级）

### 2. 知识内容交互

- 记录用户浏览知识内容的历史
- 收藏感兴趣的知识内容
- 获取个性化的内容推荐

### 3. 知识图谱交互

- 记录用户与知识图谱的交互历史
- 同步用户偏好到知识图谱服务
- 提供基于用户历史交互的个性化图谱查询

## 最新增强功能

### 1. 基于AI的内容推荐系统

- 通过用户历史数据和偏好分析实现智能推荐
- 支持LLM增强的个性化内容推荐
- 引入反馈机制优化推荐算法

### 2. 性能优化

- 实现多级缓存策略（Redis + 内存缓存）
- 添加性能监控中间件
- 优化大量数据查询

### 3. 测试覆盖率提升

- 添加单元测试和集成测试
- 实现测试覆盖率报告
- 支持持续性集成测试

### 4. 社交分享功能

- 支持分享内容、健康记录和个人成就
- 多平台分享（微信、微博、电子邮件等）
- 分享数据分析和追踪
- 社交分享互动记录

### 5. 用户兴趣图谱匹配

- 基于用户兴趣和知识偏好的匹配推荐
- 兴趣向量计算和相似度匹配
- 用户连接请求和管理
- 匹配分数和匹配理由生成

## 最新升级项目

### 1. 重构路由系统

- 实现模块化路由管理
- 优化控制器与路由分离
- 标准化API响应格式
- RESTful API最佳实践

### 2. 架构优化

- 优化依赖注入模式
- 改进服务层与存储库层交互
- 标准化错误处理机制
- 增强日志记录与监控

### 3. 完整API文档

- 自动生成的API文档
- 详细的接口说明与示例
- 完整的参数和响应说明
- 支持业务场景说明

### 4. 扩展测试覆盖率

- 所有API接口的单元测试
- 主要业务逻辑的集成测试
- 端到端业务流程测试
- 性能与负载测试

## API 接口

### 知识偏好相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/users/:userId/knowledge-preferences | 获取用户知识偏好 |
| PUT | /api/v1/users/:userId/knowledge-preferences | 更新用户知识偏好 |
| GET | /api/v1/users/:userId/interested-domains | 获取用户感兴趣的知识领域 |
| GET | /api/v1/users/:userId/view-history | 获取用户知识内容访问历史 |
| POST | /api/v1/users/view-history | 记录用户知识内容访问 |
| GET | /api/v1/users/:userId/recommended-content | 获取推荐给用户的知识内容 |
| GET | /api/v1/users/:userId/favorites | 获取用户收藏的知识内容 |
| POST | /api/v1/users/favorites | 添加知识内容到用户收藏 |
| DELETE | /api/v1/users/favorites/:contentId | 从用户收藏中移除知识内容 |
| GET | /api/v1/users/:userId/knowledge-graph-interactions | 获取用户知识图谱交互历史 |

### 社交分享相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/social-shares | 创建分享 |
| GET | /api/social-shares/:shareId | 获取分享详情 |
| PUT | /api/social-shares/:shareId | 更新分享 |
| DELETE | /api/social-shares/:shareId | 删除分享 |
| GET | /api/social-shares/user/:userId | 获取用户分享列表 |
| POST | /api/social-shares/:shareId/interactions | 记录分享互动 |
| GET | /api/social-shares/:shareId/interactions | 获取分享互动列表 |
| POST | /api/social-shares/:shareId/link | 生成分享链接 |
| POST | /api/social-shares/view/:shareId | 记录分享查看 |

### 用户兴趣匹配相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/user-matches | 创建用户匹配 |
| GET | /api/user-matches/:matchId | 获取匹配详情 |
| PUT | /api/user-matches/:matchId/status | 更新匹配状态 |
| GET | /api/user-matches | 获取用户匹配列表 |
| DELETE | /api/user-matches/:matchId | 删除匹配记录 |
| POST | /api/user-matches/interest-vector | 计算用户兴趣向量 |
| GET | /api/user-matches/potential | 查找潜在匹配用户 |
| POST | /api/user-matches/connections | 创建用户连接请求 |
| PUT | /api/user-matches/connections/:connectionId/status | 更新连接状态 |
| GET | /api/user-matches/connections | 获取用户连接列表 |

## 数据库结构

已添加以下新表支持相关功能：

### 知识相关表
- `user_knowledge_preferences` - 存储用户知识偏好设置
- `user_content_view_history` - 记录用户内容访问历史
- `user_content_favorites` - 存储用户收藏的内容
- `user_knowledge_graph_interactions` - 记录用户与知识图谱的交互

### 社交分享相关表
- `social_shares` - 存储用户分享记录
- `social_share_interactions` - 记录分享互动情况

### 用户匹配相关表
- `user_matches` - 存储用户匹配记录
- `user_connections` - 存储用户之间的连接关系
- `user_interest_vectors` - 存储用户兴趣向量数据

## 环境变量

需要添加以下环境变量：

```
# 知识服务连接
KNOWLEDGE_BASE_URL=http://knowledge-base-service:3000
KNOWLEDGE_GRAPH_URL=http://knowledge-graph-service:3000

# 社交分享配置
SHARE_BASE_URL=https://suoke.life/share

# 兴趣匹配配置
VECTOR_SIMILARITY_THRESHOLD=0.7
```

## 部署与集成

1. 更新数据库结构：

```bash
npm run migrate
```

2. 与相关服务集成：

确保知识库服务、知识图谱服务等已在同一网络中运行，并且用户服务可以通过环境变量中配置的URL访问它们。

## 安全性

所有API都需要用户认证，并且只有用户自己或管理员可以访问用户的个人数据。

## 访问API文档

服务运行后，可以通过以下地址访问API文档：

```
http://localhost:3002/api/api-docs
```

## 监控与指标

服务提供Prometheus格式的指标，可通过以下地址访问：

```
http://localhost:3002/metrics
```

主要指标包括：
- HTTP请求总数
- HTTP请求持续时间
- 文件上传次数
- 缓存命中率
- 服务错误次数

## 微服务部署优化

用户服务已完成标准化微服务部署优化，包括：

1. **容器化配置优化**
   - 添加 `docker-entrypoint.sh` 实现健康检查和优雅启动/关闭
   - 创建 `docker-compose.yml` 支持本地开发环境

2. **Kubernetes资源优化**
   - 添加 PodDisruptionBudget 确保服务可用性
   - 实现数据备份机制
   - 集成Prometheus监控
   - 使用Kustomize统一管理所有资源
   - 配置专用服务账号

3. **文档完善**
   - 创建完整部署文档
   - 添加故障排查指南
   - 提供详细维护操作指南

### 本地开发启动

```bash
# 确保脚本有执行权限
chmod +x docker-entrypoint.sh

# 启动本地开发环境
docker-compose up -d

# 查看服务日志
docker-compose logs -f user-service

# 关闭环境
docker-compose down
```

### Kubernetes部署

```bash
# 应用所有资源
kubectl apply -k k8s/

# 单独更新部署
kubectl apply -f k8s/deployment.yaml

# 查看服务状态
kubectl get all -l app=user-service -n suoke
```

详细部署文档请参考 [部署文档](docs/deployment.md)

## 未来规划

- 拓展社交网络功能
- 提升用户匹配算法精度
- 增强跨服务数据分析能力
- 构建健康社区生态系统