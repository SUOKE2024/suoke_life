#!/bin/bash

# 索克生活认证服务设置脚本
# 用于初始化开发环境

set -e

echo "🚀 开始设置索克生活认证服务..."

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+\.\d+')
required_version="3.13.3"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 需要Python $required_version 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查UV是否安装
echo "📋 检查UV包管理器..."
if ! command -v uv &> /dev/null; then
    echo "📦 安装UV包管理器..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✅ UV包管理器已安装"

# 创建虚拟环境并安装依赖
echo "📦 安装项目依赖..."
uv sync

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
    echo "⚠️  请编辑 .env 文件配置您的环境变量"
fi

# 创建必要的目录
echo "📁 创建项目目录..."
mkdir -p logs
mkdir -p monitoring/grafana/{dashboards,datasources}
mkdir -p scripts

# 创建数据库初始化脚本
echo "📄 创建数据库初始化脚本..."
cat > scripts/init-db.sql << 'EOF'
-- 索克生活认证服务数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 设置时区
SET timezone = 'UTC';

-- 创建索引函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
EOF

# 创建Prometheus配置
echo "📄 创建Prometheus配置..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:9090']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 5s
EOF

# 创建Grafana数据源配置
echo "📄 创建Grafana配置..."
mkdir -p monitoring/grafana/datasources
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# 创建启动脚本
echo "📄 创建启动脚本..."
cat > scripts/start.sh << 'EOF'
#!/bin/bash

echo "🚀 启动索克生活认证服务..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 文件，请先运行 setup.sh"
    exit 1
fi

# 启动服务
echo "📦 启动Docker容器..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
curl -f http://localhost:8000/health || echo "❌ 认证服务未启动"
curl -f http://localhost:9091 || echo "❌ Prometheus未启动"
curl -f http://localhost:3000 || echo "❌ Grafana未启动"

echo "✅ 服务启动完成！"
echo "🌐 认证服务: http://localhost:8000"
echo "📊 Prometheus: http://localhost:9091"
echo "📈 Grafana: http://localhost:3000 (admin/admin)"
EOF

chmod +x scripts/start.sh

# 创建停止脚本
cat > scripts/stop.sh << 'EOF'
#!/bin/bash

echo "🛑 停止索克生活认证服务..."
docker-compose down

echo "✅ 服务已停止"
EOF

chmod +x scripts/stop.sh

# 创建开发脚本
cat > scripts/dev.sh << 'EOF'
#!/bin/bash

echo "🔧 启动开发模式..."

# 设置开发环境变量
export ENVIRONMENT=development
export DEBUG=true
export SERVER__RELOAD=true

# 启动服务
uv run python -m auth_service.cmd.server.main
EOF

chmod +x scripts/dev.sh

echo "✅ 索克生活认证服务设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env 文件配置环境变量"
echo "2. 运行 ./scripts/start.sh 启动完整环境"
echo "3. 或运行 ./scripts/dev.sh 启动开发模式"
echo ""
echo "🌐 服务地址："
echo "- 认证服务: http://localhost:8000"
echo "- API文档: http://localhost:8000/docs"
echo "- Prometheus: http://localhost:9091"
echo "- Grafana: http://localhost:3000" 