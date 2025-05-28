#!/bin/bash

# 老克智能体服务开发环境快速启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动老克智能体服务开发环境${NC}"

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 设置开发环境变量
export ENVIRONMENT=development
export DEBUG=true
export RELOAD=true
export LOG_LEVEL=debug

# 检查是否存在配置文件
if [ ! -f ".env" ] && [ ! -f "config/config.yaml" ]; then
    echo -e "${GREEN}📝 创建开发配置文件...${NC}"
    
    # 创建基本的 .env 文件
    cat > .env << EOF
# 开发环境配置
ENVIRONMENT=development
DEBUG=true

# 数据库配置（使用默认值）
DATABASE__POSTGRES_PASSWORD=laoke_dev_password
DATABASE__REDIS_PASSWORD=

# AI 配置（需要手动设置）
AI__OPENAI_API_KEY=your_openai_api_key
AI__ANTHROPIC_API_KEY=your_anthropic_api_key

# 安全配置
SECURITY__JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production
EOF
    
    echo -e "${GREEN}✅ 已创建 .env 文件，请根据需要修改 API 密钥${NC}"
fi

# 启动服务
echo -e "${GREEN}🔧 启动开发服务器...${NC}"
./scripts/start.sh --reload --log-level debug 