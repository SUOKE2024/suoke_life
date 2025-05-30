# 索克生活部署指南

## 部署前准备

### 1. 环境要求
- Node.js 18+
- Docker & Docker Compose
- Kubernetes (可选)
- PostgreSQL 14+
- Redis 6+

### 2. 配置文件
- 复制 `.env.production` 并更新配置
- 更新数据库连接信息
- 配置外部服务API密钥

### 3. 构建应用
```bash
npm install
npm run build
```

## Docker部署

### 1. 构建镜像
```bash
docker build -t suokelife:latest .
```

### 2. 运行容器
```bash
docker-compose up -d
```

## Kubernetes部署

### 1. 应用配置
```bash
kubectl apply -f k8s/
```

### 2. 检查状态
```bash
kubectl get pods -l app=suokelife
kubectl get services
```

## 监控和维护

### 1. 健康检查
- 应用健康: `GET /health`
- 就绪检查: `GET /ready`

### 2. 日志查看
```bash
kubectl logs -f deployment/suokelife-app
```

### 3. 备份
```bash
./scripts/backup/backup.sh
```

## 故障排除

### 常见问题
1. 数据库连接失败 - 检查连接字符串
2. 内存不足 - 增加容器内存限制
3. 启动超时 - 检查健康检查配置

### 回滚
```bash
kubectl rollout undo deployment/suokelife-app
```

## 安全注意事项
- 定期更新依赖包
- 监控安全漏洞
- 备份加密
- 访问控制
