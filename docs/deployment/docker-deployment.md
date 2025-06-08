# Docker 部署指南

## 概述

本文档介绍如何使用Docker部署索克生活平台。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 可用内存
- 20GB+ 可用磁盘空间

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life
```

### 2. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 服务配置

### 核心服务

| 服务 | 端口 | 说明 |
|------|------|------|
| API网关 | 8080 | 统一入口 |
| 小艾服务 | 8001 | 健康助手 |
| 小克服务 | 8002 | 服务管理 |
| 老克服务 | 8003 | 知识管理 |
| 索儿服务 | 8004 | 生活管理 |

### 数据库服务

| 服务 | 端口 | 说明 |
|------|------|------|
| PostgreSQL | 5432 | 主数据库 |
| Redis | 6379 | 缓存数据库 |
| MongoDB | 27017 | 文档数据库 |

## 监控和日志

### Prometheus监控

访问 http://localhost:9090 查看监控指标

### Grafana仪表板

访问 http://localhost:3000 查看可视化仪表板
- 用户名: admin
- 密码: admin

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs xiaoai-service

# 实时查看日志
docker-compose logs -f
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8080
   
   # 修改docker-compose.yml中的端口映射
   ```

2. **内存不足**
   ```bash
   # 检查内存使用
   docker stats
   
   # 增加Docker内存限制
   ```

3. **服务启动失败**
   ```bash
   # 查看详细错误信息
   docker-compose logs service-name
   
   # 重启服务
   docker-compose restart service-name
   ```

## 生产环境部署

### 安全配置

1. 修改默认密码
2. 配置SSL证书
3. 设置防火墙规则
4. 启用访问日志

### 性能优化

1. 调整容器资源限制
2. 配置数据库连接池
3. 启用缓存策略
4. 设置负载均衡

---

*更新时间: 2024-06-08*
