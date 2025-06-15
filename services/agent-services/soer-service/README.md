# 索儿智能体服务 (Soer Agent Service)

索儿智能体是索克生活平台的核心AI服务，专注于提供个性化的健康管理、营养分析和生活方式建议。

## 🌟 核心功能

### 🤖 智能对话
- 自然语言交互
- 上下文记忆管理
- 意图识别和情感分析
- 个性化响应生成

### 🏥 健康管理
- 健康数据收集和分析
- 生物指标趋势监测
- 健康风险评估
- 个性化健康建议

### 🍎 营养分析
- 食物营养成分分析
- 膳食计划制定
- 营养目标跟踪
- 食物数据库搜索

### 🏃‍♀️ 生活方式
- 个性化运动计划
- 睡眠质量分析
- 压力水平评估
- 生活习惯建议

### 🔐 用户认证
- JWT令牌认证
- 角色权限管理
- 会话管理
- 安全防护

## 🚀 快速开始

### 环境要求
- Python 3.11+
- MongoDB 7.0+
- Redis 7.0+
- Docker (可选)

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd soer-service
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

4. **启动数据库服务**
```bash
# 启动 MongoDB
mongod --dbpath ./data/db

# 启动 Redis
redis-server
```

5. **运行服务**
```bash
uvicorn soer_service.main:app --reload --host 0.0.0.0 --port 8003
```

### Docker 部署

1. **使用 Docker Compose**
```bash
docker-compose up -d
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **查看日志**
```bash
docker-compose logs -f soer-service
```

## 📚 API 文档

服务启动后，可以通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

### 主要端点

#### 认证端点
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌
- `POST /auth/logout` - 用户登出

#### 智能体端点
- `POST /agent/chat` - 智能对话
- `GET /agent/capabilities` - 获取能力列表
- `GET /agent/history` - 对话历史
- `WebSocket /agent/ws` - 实时对话

#### 健康管理端点
- `POST /health/data` - 提交健康数据
- `GET /health/dashboard` - 健康仪表板
- `POST /health/analyze` - 健康数据分析
- `GET /health/trends` - 健康趋势

#### 营养分析端点
- `POST /nutrition/analyze` - 食物营养分析
- `GET /nutrition/search` - 食物数据库搜索
- `POST /nutrition/diet-plan` - 创建膳食计划
- `POST /nutrition/track-meal` - 记录用餐

#### 生活方式端点
- `POST /lifestyle/exercise-plan` - 创建运动计划
- `POST /lifestyle/sleep/analyze` - 睡眠分析
- `POST /lifestyle/stress/assess` - 压力评估
- `POST /lifestyle/activity/track` - 活动记录

## 🔧 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `MONGODB_URL` | MongoDB连接URL | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | 数据库名称 | `soer_service` |
| `REDIS_URL` | Redis连接URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT密钥 | `your-secret-key-change-in-production` |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API密钥 | - |
| `NUTRITION_API_KEY` | 营养数据库API密钥 | - |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `ENVIRONMENT` | 运行环境 | `development` |

### 数据库配置

服务支持MongoDB作为主数据库，Redis作为缓存和会话存储。

#### MongoDB集合结构
- `users` - 用户基本信息
- `user_profiles` - 用户档案
- `user_sessions` - 用户会话
- `health_data` - 健康数据
- `nutrition_data` - 营养分析数据
- `exercise_plans` - 运动计划
- `conversation_history` - 对话历史

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth_service.py

# 运行性能测试
pytest tests/test_performance.py

# 生成覆盖率报告
pytest --cov=soer_service --cov-report=html
```

### 测试覆盖率
目标测试覆盖率：90%+

## 📊 监控和日志

### 健康检查
- `GET /health` - 服务健康状态
- `GET /metrics` - Prometheus指标

### 日志配置
- 结构化日志输出
- 多级别日志记录
- 日志轮转和归档

### 性能监控
- 响应时间监控
- 吞吐量统计
- 错误率追踪
- 资源使用监控

## 🔒 安全特性

### 认证和授权
- JWT令牌认证
- 角色权限控制
- 会话管理
- 令牌刷新机制

### 安全防护
- 速率限制
- CORS配置
- 安全头部
- 输入验证

### 数据保护
- 密码哈希存储
- 敏感数据加密
- 数据脱敏
- 审计日志

## 🚀 部署指南

### 生产环境部署

1. **环境准备**
```bash
# 创建生产环境配置
cp .env.example .env.production
# 编辑生产环境配置
```

2. **数据库初始化**
```bash
# 运行数据库迁移
python -m alembic upgrade head
```

3. **服务部署**
```bash
# 使用Docker部署
docker-compose -f docker-compose.prod.yml up -d
```

4. **负载均衡配置**
```bash
# 配置Nginx负载均衡
cp nginx.conf.example /etc/nginx/sites-available/soer-service
```

### 扩展部署

- **水平扩展**: 支持多实例部署
- **负载均衡**: Nginx/HAProxy配置
- **数据库集群**: MongoDB副本集
- **缓存集群**: Redis Cluster

## 🤝 开发指南

### 代码规范
- 使用Black进行代码格式化
- 使用isort进行导入排序
- 使用flake8进行代码检查
- 使用mypy进行类型检查

### 提交规范
- 遵循Conventional Commits规范
- 编写清晰的提交信息
- 包含必要的测试用例

### 开发流程
1. 创建功能分支
2. 编写代码和测试
3. 运行代码检查
4. 提交代码审查
5. 合并到主分支

## 📈 性能优化

### 响应时间优化
- 异步处理
- 数据库索引优化
- 缓存策略
- 连接池配置

### 内存优化
- 对象池复用
- 垃圾回收优化
- 内存泄漏检测

### 并发优化
- 异步IO处理
- 连接复用
- 请求队列管理

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MongoDB服务状态
   - 验证连接字符串
   - 检查网络连通性

2. **Redis连接失败**
   - 检查Redis服务状态
   - 验证连接配置
   - 检查内存使用情况

3. **AI服务调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 检查API配额限制

### 日志分析
```bash
# 查看错误日志
grep "ERROR" logs/soer-service.log

# 查看性能日志
grep "PERFORMANCE" logs/soer-service.log

# 实时监控日志
tail -f logs/soer-service.log
```

## 📞 支持和联系

- **项目仓库**: [GitHub Repository]
- **问题反馈**: [Issues]
- **文档站点**: [Documentation]
- **技术支持**: support@suokelife.com

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**索儿智能体服务** - 让健康管理更智能，让生活更美好！ 🌟