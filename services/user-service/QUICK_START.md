# 索克生活用户服务 - 快速启动指南

## 🚀 快速开始

### 前置要求

- Python 3.13.3+
- UV (Python包管理器)
- SQLite3 (开发环境)
- PostgreSQL (生产环境，可选)

### 1. 环境准备

```bash
# 进入用户服务目录
cd services/user-service

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 2. 配置设置

```bash
# 复制配置文件
cp config/config.example.yaml config/config.yaml

# 编辑配置文件（可选）
vim config/config.yaml
```

### 3. 启动服务

#### 方式一：使用简化启动脚本（推荐）
```bash
python run_service.py
```

#### 方式二：使用完整启动脚本
```bash
python cmd/server/main.py --config config/config.yaml
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# API文档
open http://localhost:8000/docs
```

## 🧪 运行测试

### 完整测试套件
```bash
python test_service_completion.py
```

### 单元测试
```bash
pytest tests/ -v
```

### 集成测试
```bash
pytest tests/integration/ -v
```

## 📝 API使用示例

### 1. 创建用户
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "测试用户"
  }'
```

### 2. 获取用户
```bash
curl -X GET "http://localhost:8000/api/v1/users/{user_id}"
```

### 3. 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### 4. 更新用户信息
```bash
curl -X PUT "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "full_name": "更新后的用户名",
    "phone": "13800138000"
  }'
```

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t suoke-user-service .
```

### 运行容器
```bash
docker run -p 8000:8000 -p 50051:50051 suoke-user-service
```

### Docker Compose
```bash
docker-compose up -d
```

## 🔧 开发模式

### 启用调试模式
```bash
export DEBUG=true
python run_service.py
```

### 热重载开发
```bash
uvicorn run_service:app --reload --host 0.0.0.0 --port 8000
```

## 📊 监控和日志

### 查看日志
```bash
# 实时日志
tail -f logs/user_service.log

# 错误日志
tail -f logs/user_service.error.log
```

### Prometheus指标
```bash
curl http://localhost:8000/metrics
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
ls -la data/

# 重新初始化数据库
rm data/user_service.db
python run_service.py
```

#### 3. 依赖安装失败
```bash
# 清理缓存
uv cache clean

# 重新安装
uv sync --reinstall
```

### 日志级别调整
```yaml
# config/config.yaml
logging:
  level: DEBUG  # INFO, WARNING, ERROR
```

## 📈 性能调优

### 数据库优化
```yaml
# config/config.yaml
database:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
```

### 缓存配置
```yaml
# config/config.yaml
cache:
  enabled: true
  ttl: 300  # 5分钟
  max_size: 1000
```

## 🔐 安全配置

### JWT密钥生成
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 密码策略
```yaml
# config/config.yaml
security:
  password_min_length: 8
  password_require_uppercase: true
  password_require_lowercase: true
  password_require_numbers: true
```

## 📚 更多资源

- [完整API文档](http://localhost:8000/docs)
- [架构设计文档](./docs/architecture.md)
- [部署指南](./docs/deployment.md)
- [开发指南](./docs/development.md)

## 🆘 获取帮助

如果遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 运行测试套件
4. 查看API文档
5. 提交Issue

---

**祝您使用愉快！** 🎉 