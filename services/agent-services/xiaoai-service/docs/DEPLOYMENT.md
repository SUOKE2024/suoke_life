# xiaoai-service 部署指南

## 环境要求

- Python 3.13.3+
- Docker 20.10+
- Kubernetes 1.25+
- PostgreSQL 15+
- Redis 7+

## 本地开发

```bash
# 克隆代码
git clone <repository>
cd xiaoai-service

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env

# 启动服务
uv run python -m xiaoai_service.cli.main
```

## Docker部署

```bash
# 构建镜像
docker build -t xiaoai-service:latest .

# 运行容器
docker-compose up -d
```

## Kubernetes部署

```bash
# 应用配置
kubectl apply -f deploy/kubernetes/

# 检查状态
kubectl get pods -l app=xiaoai-service
```

## 监控配置

- Prometheus指标：`/metrics`
- 健康检查：`/health`
- 日志级别：INFO

## 性能调优

- 工作进程数：CPU核心数
- 连接池大小：20
- 缓存TTL：3600秒

## 故障排除

常见问题及解决方案详见运维手册。
