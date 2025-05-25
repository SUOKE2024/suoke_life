#!/bin/bash

# PostgreSQL安装和配置脚本
# 用于为健康数据服务设置PostgreSQL数据库

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    log_info "检测到操作系统: $OS"
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "检测到以root权限运行"
        SUDO=""
    else
        SUDO="sudo"
    fi
}

# 安装PostgreSQL
install_postgresql() {
    log_step "安装PostgreSQL..."
    
    case $OS in
        "debian")
            $SUDO apt-get update
            $SUDO apt-get install -y postgresql postgresql-contrib postgresql-client
            ;;
        "redhat")
            $SUDO yum install -y postgresql-server postgresql-contrib
            $SUDO postgresql-setup initdb
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install postgresql
            else
                log_error "请先安装Homebrew"
                exit 1
            fi
            ;;
        *)
            log_error "不支持的操作系统"
            exit 1
            ;;
    esac
    
    log_info "PostgreSQL安装完成"
}

# 启动PostgreSQL服务
start_postgresql() {
    log_step "启动PostgreSQL服务..."
    
    case $OS in
        "debian")
            $SUDO systemctl start postgresql
            $SUDO systemctl enable postgresql
            ;;
        "redhat")
            $SUDO systemctl start postgresql
            $SUDO systemctl enable postgresql
            ;;
        "macos")
            brew services start postgresql
            ;;
    esac
    
    log_info "PostgreSQL服务已启动"
}

# 配置PostgreSQL
configure_postgresql() {
    log_step "配置PostgreSQL..."
    
    # 获取PostgreSQL版本和数据目录
    PG_VERSION=$(psql --version | awk '{print $3}' | sed 's/\..*//')
    
    case $OS in
        "debian"|"redhat")
            PG_DATA_DIR="/var/lib/postgresql/$PG_VERSION/main"
            PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"
            ;;
        "macos")
            PG_DATA_DIR="/usr/local/var/postgres"
            PG_CONFIG_DIR="/usr/local/var/postgres"
            ;;
    esac
    
    log_info "PostgreSQL版本: $PG_VERSION"
    log_info "数据目录: $PG_DATA_DIR"
    log_info "配置目录: $PG_CONFIG_DIR"
    
    # 备份原始配置文件
    if [ -f "$PG_CONFIG_DIR/postgresql.conf" ]; then
        $SUDO cp "$PG_CONFIG_DIR/postgresql.conf" "$PG_CONFIG_DIR/postgresql.conf.backup"
        log_info "已备份postgresql.conf"
    fi
    
    if [ -f "$PG_CONFIG_DIR/pg_hba.conf" ]; then
        $SUDO cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup"
        log_info "已备份pg_hba.conf"
    fi
    
    # 优化PostgreSQL配置
    optimize_postgresql_config
    
    # 配置认证
    configure_authentication
    
    # 重启PostgreSQL服务
    restart_postgresql
}

# 优化PostgreSQL配置
optimize_postgresql_config() {
    log_step "优化PostgreSQL配置..."
    
    # 获取系统内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    SHARED_BUFFERS=$((TOTAL_MEM / 4))  # 25% of total memory
    EFFECTIVE_CACHE_SIZE=$((TOTAL_MEM * 3 / 4))  # 75% of total memory
    
    # 创建优化配置
    cat << EOF | $SUDO tee -a "$PG_CONFIG_DIR/postgresql.conf"

# 索克生活健康数据服务优化配置
# 添加时间: $(date)

# 内存配置
shared_buffers = ${SHARED_BUFFERS}MB
effective_cache_size = ${EFFECTIVE_CACHE_SIZE}MB
work_mem = 16MB
maintenance_work_mem = 256MB

# 连接配置
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# WAL配置
wal_buffers = 16MB
checkpoint_completion_target = 0.9
wal_writer_delay = 200ms

# 查询优化
random_page_cost = 1.1
effective_io_concurrency = 200

# 日志配置
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# 统计配置
track_activities = on
track_counts = on
track_io_timing = on
track_functions = all
stats_temp_directory = 'pg_stat_tmp'

# 自动清理配置
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50

EOF

    log_info "PostgreSQL配置优化完成"
}

# 配置认证
configure_authentication() {
    log_step "配置PostgreSQL认证..."
    
    # 备份并修改pg_hba.conf
    cat << EOF | $SUDO tee "$PG_CONFIG_DIR/pg_hba.conf"
# PostgreSQL Client Authentication Configuration File
# 索克生活健康数据服务配置

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# 允许本地网络连接（根据需要调整）
host    all             all             192.168.0.0/16          md5
host    all             all             10.0.0.0/8              md5
host    all             all             172.16.0.0/12           md5

EOF

    log_info "认证配置完成"
}

# 重启PostgreSQL服务
restart_postgresql() {
    log_step "重启PostgreSQL服务..."
    
    case $OS in
        "debian"|"redhat")
            $SUDO systemctl restart postgresql
            ;;
        "macos")
            brew services restart postgresql
            ;;
    esac
    
    log_info "PostgreSQL服务已重启"
}

# 创建数据库和用户
create_database_and_user() {
    log_step "创建数据库和用户..."
    
    # 数据库配置
    DB_NAME=${DB_NAME:-"suoke_health_data"}
    DB_USER=${DB_USER:-"suoke_user"}
    DB_PASSWORD=${DB_PASSWORD:-"suoke_password_$(date +%s)"}
    
    # 切换到postgres用户执行SQL命令
    case $OS in
        "debian"|"redhat")
            $SUDO -u postgres psql << EOF
-- 创建用户
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- 创建数据库
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 创建扩展
\c $DB_NAME
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 授予schema权限
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

\q
EOF
            ;;
        "macos")
            psql postgres << EOF
-- 创建用户
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- 创建数据库
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 创建扩展
\c $DB_NAME
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 授予schema权限
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

\q
EOF
            ;;
    esac
    
    log_info "数据库和用户创建完成"
    log_info "数据库名: $DB_NAME"
    log_info "用户名: $DB_USER"
    log_info "密码: $DB_PASSWORD"
}

# 创建环境配置文件
create_env_file() {
    log_step "创建环境配置文件..."
    
    ENV_FILE="../.env.postgresql"
    
    cat << EOF > "$ENV_FILE"
# PostgreSQL数据库配置
# 生成时间: $(date)

# 数据库连接信息
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# 连接池配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# 其他配置
DB_ECHO=false
DB_POOL_PRE_PING=true

EOF

    log_info "环境配置文件已创建: $ENV_FILE"
}

# 测试数据库连接
test_connection() {
    log_step "测试数据库连接..."
    
    # 使用psql测试连接
    PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_info "✓ 数据库连接测试成功"
    else
        log_error "✗ 数据库连接测试失败"
        exit 1
    fi
}

# 显示安装总结
show_summary() {
    log_step "安装总结"
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}PostgreSQL安装和配置完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}数据库信息:${NC}"
    echo "  主机: localhost"
    echo "  端口: 5432"
    echo "  数据库: $DB_NAME"
    echo "  用户: $DB_USER"
    echo "  密码: $DB_PASSWORD"
    echo ""
    echo -e "${BLUE}配置文件:${NC}"
    echo "  环境配置: $ENV_FILE"
    echo "  PostgreSQL配置: $PG_CONFIG_DIR/postgresql.conf"
    echo "  认证配置: $PG_CONFIG_DIR/pg_hba.conf"
    echo ""
    echo -e "${BLUE}下一步操作:${NC}"
    echo "  1. 将环境配置文件内容添加到您的.env文件中"
    echo "  2. 运行数据迁移脚本（如果从SQLite迁移）:"
    echo "     python scripts/migrate_to_postgresql.py"
    echo "  3. 重启健康数据服务"
    echo "  4. 验证服务正常运行"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo "  - 请妥善保管数据库密码"
    echo "  - 建议定期备份数据库"
    echo "  - 根据实际需求调整PostgreSQL配置"
    echo ""
}

# 主函数
main() {
    echo -e "${GREEN}索克生活健康数据服务 - PostgreSQL安装脚本${NC}"
    echo "=================================================="
    echo ""
    
    # 检查参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --db-name)
                DB_NAME="$2"
                shift 2
                ;;
            --db-user)
                DB_USER="$2"
                shift 2
                ;;
            --db-password)
                DB_PASSWORD="$2"
                shift 2
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --db-name NAME      数据库名称 (默认: suoke_health_data)"
                echo "  --db-user USER      数据库用户 (默认: suoke_user)"
                echo "  --db-password PASS  数据库密码 (默认: 自动生成)"
                echo "  --help              显示此帮助信息"
                echo ""
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                echo "使用 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
    
    # 执行安装步骤
    detect_os
    check_root
    
    # 检查PostgreSQL是否已安装
    if command -v psql &> /dev/null; then
        log_warn "PostgreSQL已安装，跳过安装步骤"
    else
        install_postgresql
    fi
    
    start_postgresql
    configure_postgresql
    create_database_and_user
    create_env_file
    test_connection
    show_summary
    
    log_info "PostgreSQL安装和配置完成！"
}

# 运行主函数
main "$@" 