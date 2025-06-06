# Docker 部署指南

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 内存: 8GB+
- 磁盘: 50GB+

## 快速启动

### 1. 克隆项目
```bash
git clone https://github.com/suoke-life/suoke_life.git
cd suoke_life
```

### 2. 环境配置
```bash
# 复制环境配置
cp env.example .env

# 编辑配置文件
vim .env
```

### 3. 启动服务
```bash
# 启动所有微服务
docker-compose -f docker-compose.microservices.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 服务端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| API网关 | 8000 | 8000 | 统一入口 |
| 小艾智能体 | 8001 | 8001 | 健康助手 |
| 小克智能体 | 8002 | 8002 | 数据分析 |
| 老克智能体 | 8003 | 8003 | 中医专家 |
| 索儿智能体 | 8004 | 8004 | 生活顾问 |
| 健康数据服务 | 8005 | 8005 | 数据管理 |
| 区块链服务 | 8006 | 8006 | 数据验证 |
| 认证服务 | 8007 | 8007 | 用户认证 |

## 健康检查

```bash
# 检查所有服务
curl http://localhost:8000/health

# 检查单个服务
curl http://localhost:8001/health
```

## 故障排除

### 常见问题

1. **端口冲突**
```bash
# 查看端口占用
netstat -tulpn | grep :8000

# 修改端口映射
vim docker-compose.microservices.yml
```

2. **内存不足**
```bash
# 查看内存使用
docker stats

# 调整内存限制
vim docker-compose.microservices.yml
```

3. **服务启动失败**
```bash
# 查看详细日志
docker-compose logs [service-name]

# 重启服务
docker-compose restart [service-name]
```

## 数据持久化

```yaml
volumes:
  postgres_data:
  redis_data:
  mongodb_data:
  blockchain_data:
```

## 备份与恢复

```bash
# 数据备份
./scripts/backup/backup_all.sh

# 数据恢复
./scripts/backup/restore_all.sh
```
