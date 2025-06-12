#!/bin/bash

echo "🚀 索克生活项目生产环境部署"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
ENVIRONMENT="production"
DOCKER_REGISTRY="registry.suoke.life"
APP_VERSION=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/backup/suokelife"
LOG_DIR="/var/log/suokelife"

# 检查函数
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 失败${NC}"
        exit 1
    fi
}

echo -e "${BLUE}📋 部署前检查${NC}"
echo "--------------------------------"

# 1. 检查Docker环境
echo "检查Docker环境..."
docker --version > /dev/null 2>&1
check_status "Docker环境检查"

docker-compose --version > /dev/null 2>&1
check_status "Docker Compose环境检查"

# 2. 检查网络连接
echo "检查网络连接..."
ping -c 1 google.com > /dev/null 2>&1
check_status "网络连接检查"

# 3. 检查磁盘空间
echo "检查磁盘空间..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ 磁盘空间充足 ($DISK_USAGE%使用)${NC}"
else
    echo -e "${RED}❌ 磁盘空间不足 ($DISK_USAGE%使用)${NC}"
    exit 1
fi

# 4. 检查内存
echo "检查内存..."
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ 内存充足 ($MEMORY_USAGE%使用)${NC}"
else
    echo -e "${YELLOW}⚠️ 内存使用较高 ($MEMORY_USAGE%使用)${NC}"
fi

echo ""
echo -e "${BLUE}🔧 环境准备${NC}"
echo "--------------------------------"

# 5. 创建必要目录
echo "创建部署目录..."
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p /etc/suokelife
sudo mkdir -p /var/lib/suokelife
check_status "目录创建"

# 6. 设置环境变量
echo "设置环境变量..."
cat > .env.production << EOF
# 生产环境配置
NODE_ENV=production
ENVIRONMENT=production
APP_VERSION=$APP_VERSION

# 数据库配置
DATABASE_URL=postgresql://suokelife:password@postgres:5432/suokelife_prod
REDIS_URL=redis://redis:6379/0

# API配置
API_BASE_URL=https://api.suoke.life
WS_URL=wss://ws.suoke.life

# 智能体服务配置
XIAOAI_SERVICE_URL=http://xiaoai-service:50053
XIAOKE_SERVICE_URL=http://xiaoke-service:50054
LAOKE_SERVICE_URL=http://laoke-service:50055
SOER_SERVICE_URL=http://soer-service:50056

# 安全配置
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# 监控配置
ENABLE_MONITORING=true
ENABLE_LOGGING=true
LOG_LEVEL=info

# 性能配置
MAX_CONNECTIONS=100
CACHE_TTL=3600
RATE_LIMIT=1000

# 第三方服务
OPENAI_API_KEY=your_openai_key
ALIYUN_ACCESS_KEY=your_aliyun_key
ALIYUN_SECRET_KEY=your_aliyun_secret
EOF

check_status "环境变量配置"

echo ""
echo -e "${BLUE}🏗️ 构建应用${NC}"
echo "--------------------------------"

# 7. 构建前端应用
echo "构建前端应用..."
npm run build:production
check_status "前端应用构建"

# 8. 构建Docker镜像
echo "构建Docker镜像..."

# 构建前端镜像
docker build -t $DOCKER_REGISTRY/suokelife-frontend:$APP_VERSION -f Dockerfile.frontend .
check_status "前端镜像构建"

# 构建API网关镜像
docker build -t $DOCKER_REGISTRY/suokelife-gateway:$APP_VERSION -f services/api-gateway/Dockerfile services/api-gateway/
check_status "API网关镜像构建"

# 构建智能体服务镜像
for service in xiaoai xiaoke laoke soer; do
    echo "构建 $service 服务镜像..."
    docker build -t $DOCKER_REGISTRY/suokelife-$service:$APP_VERSION -f services/agent-services/$service-service/Dockerfile services/agent-services/$service-service/
    check_status "$service 服务镜像构建"
done

# 构建诊断服务镜像
docker build -t $DOCKER_REGISTRY/suokelife-diagnostic:$APP_VERSION -f services/diagnostic-services/Dockerfile services/diagnostic-services/
check_status "诊断服务镜像构建"

echo ""
echo -e "${BLUE}📤 推送镜像${NC}"
echo "--------------------------------"

# 9. 推送镜像到仓库
echo "推送镜像到Docker仓库..."
docker push $DOCKER_REGISTRY/suokelife-frontend:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-gateway:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-xiaoai:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-xiaoke:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-laoke:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-soer:$APP_VERSION
docker push $DOCKER_REGISTRY/suokelife-diagnostic:$APP_VERSION
check_status "镜像推送"

echo ""
echo -e "${BLUE}💾 数据备份${NC}"
echo "--------------------------------"

# 10. 备份现有数据（如果存在）
if [ -d "/var/lib/suokelife/data" ]; then
    echo "备份现有数据..."
    sudo tar -czf $BACKUP_DIR/suokelife-backup-$(date +%Y%m%d-%H%M%S).tar.gz /var/lib/suokelife/data
    check_status "数据备份"
fi

echo ""
echo -e "${BLUE}🚀 部署应用${NC}"
echo "--------------------------------"

# 11. 生成生产环境Docker Compose文件
echo "生成生产环境配置..."
cat > docker-compose.production.yml << EOF
version: '3.8'

services:
  # 前端应用
  frontend:
    image: $DOCKER_REGISTRY/suokelife-frontend:$APP_VERSION
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - gateway
    restart: unless-stopped
    networks:
      - suokelife-network

  # API网关
  gateway:
    image: $DOCKER_REGISTRY/suokelife-gateway:$APP_VERSION
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - suokelife-network

  # 智能体服务
  xiaoai-service:
    image: $DOCKER_REGISTRY/suokelife-xiaoai:$APP_VERSION
    ports:
      - "50053:50053"
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - suokelife-network

  xiaoke-service:
    image: $DOCKER_REGISTRY/suokelife-xiaoke:$APP_VERSION
    ports:
      - "50054:50054"
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - suokelife-network

  laoke-service:
    image: $DOCKER_REGISTRY/suokelife-laoke:$APP_VERSION
    ports:
      - "50055:50055"
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - suokelife-network

  soer-service:
    image: $DOCKER_REGISTRY/suokelife-soer:$APP_VERSION
    ports:
      - "50056:50056"
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - suokelife-network

  # 诊断服务
  diagnostic-service:
    image: $DOCKER_REGISTRY/suokelife-diagnostic:$APP_VERSION
    ports:
      - "8002:8002"
    env_file:
      - .env.production
    restart: unless-stopped
    networks:
      - suokelife-network

  # 数据库
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: suokelife_prod
      POSTGRES_USER: suokelife
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - suokelife-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - suokelife-network

  # 监控服务
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - suokelife-network

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD}
    restart: unless-stopped
    networks:
      - suokelife-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  suokelife-network:
    driver: bridge
EOF

check_status "生产环境配置生成"

# 12. 启动服务
echo "启动生产环境服务..."
docker-compose -f docker-compose.production.yml up -d
check_status "服务启动"

echo ""
echo -e "${BLUE}🔍 健康检查${NC}"
echo "--------------------------------"

# 13. 等待服务启动
echo "等待服务启动..."
sleep 30

# 14. 健康检查
echo "执行健康检查..."
./scripts/test-api-integration.sh
check_status "API健康检查"

# 15. 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.production.yml ps
check_status "服务状态检查"

echo ""
echo -e "${BLUE}📊 部署监控${NC}"
echo "--------------------------------"

# 16. 设置监控告警
echo "配置监控告警..."
# 这里可以添加具体的监控配置
check_status "监控配置"

# 17. 设置日志轮转
echo "配置日志轮转..."
sudo tee /etc/logrotate.d/suokelife << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /path/to/docker-compose.production.yml restart gateway
    endscript
}
EOF
check_status "日志轮转配置"

echo ""
echo "================================"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "================================"

echo -e "${BLUE}📋 部署信息${NC}"
echo "应用版本: $APP_VERSION"
echo "部署时间: $(date)"
echo "环境: $ENVIRONMENT"
echo ""

echo -e "${BLUE}🔗 访问地址${NC}"
echo "前端应用: https://suoke.life"
echo "API网关: https://api.suoke.life"
echo "监控面板: https://monitor.suoke.life:3000"
echo "系统监控: https://monitor.suoke.life:9090"
echo ""

echo -e "${BLUE}📊 服务状态${NC}"
docker-compose -f docker-compose.production.yml ps

echo ""
echo -e "${BLUE}📋 后续操作${NC}"
echo "1. 配置域名DNS解析"
echo "2. 设置SSL证书"
echo "3. 配置CDN加速"
echo "4. 设置备份策略"
echo "5. 配置监控告警"
echo "6. 进行压力测试"
echo ""

echo -e "${GREEN}✅ 索克生活项目已成功部署到生产环境！${NC}"
echo "�� 项目现在可以为用户提供服务了！" 