#!/bin/bash

# 索克生活 - 触诊服务安装配置脚本
# 用于自动化部署和配置触诊服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "操作系统: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "操作系统: macOS"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python版本: $PYTHON_VERSION"
        
        # 检查Python版本是否满足要求 (>= 3.8)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python版本满足要求"
        else
            log_error "Python版本过低，需要3.8或更高版本"
            exit 1
        fi
    else
        log_error "未找到Python3"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3已安装"
    else
        log_error "未找到pip3"
        exit 1
    fi
    
    # 检查Docker（可选）
    if command -v docker &> /dev/null; then
        log_success "Docker已安装"
        DOCKER_AVAILABLE=true
    else
        log_warning "Docker未安装，将跳过容器化部署"
        DOCKER_AVAILABLE=false
    fi
    
    # 检查可用内存
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        MEMORY_GB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    fi
    
    if [ "$MEMORY_GB" -ge 4 ]; then
        log_success "可用内存: ${MEMORY_GB}GB"
    else
        log_warning "可用内存较少: ${MEMORY_GB}GB，建议至少4GB"
    fi
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # 检测Linux发行版
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                python3-dev \
                python3-pip \
                python3-venv \
                libffi-dev \
                libssl-dev \
                libjpeg-dev \
                libpng-dev \
                libfreetype6-dev \
                libblas-dev \
                liblapack-dev \
                libatlas-base-dev \
                gfortran \
                libhdf5-dev \
                libopencv-dev \
                portaudio19-dev \
                libasound2-dev \
                libusb-1.0-0-dev \
                libudev-dev \
                bluetooth \
                libbluetooth-dev \
                i2c-tools \
                curl \
                wget \
                git
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                python3-devel \
                python3-pip \
                libffi-devel \
                openssl-devel \
                libjpeg-devel \
                libpng-devel \
                freetype-devel \
                blas-devel \
                lapack-devel \
                atlas-devel \
                gcc-gfortran \
                hdf5-devel \
                opencv-devel \
                portaudio-devel \
                alsa-lib-devel \
                libusb-devel \
                systemd-devel \
                bluez-libs-devel \
                i2c-tools \
                curl \
                wget \
                git
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install \
                python@3.11 \
                libffi \
                openssl \
                jpeg \
                libpng \
                freetype \
                openblas \
                lapack \
                hdf5 \
                opencv \
                portaudio \
                libusb \
                git
        else
            log_error "请先安装Homebrew: https://brew.sh/"
            exit 1
        fi
    fi
    
    log_success "系统依赖安装完成"
}

# 创建虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_warning "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    log_success "pip已升级到最新版本"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖包..."
    
    # 确保虚拟环境已激活
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # 安装依赖
    pip install -r requirements.txt
    log_success "Python依赖包安装完成"
}

# 创建目录结构
create_directory_structure() {
    log_info "创建目录结构..."
    
    # 创建必要的目录
    mkdir -p data
    mkdir -p logs
    mkdir -p cache
    mkdir -p models
    mkdir -p reports
    mkdir -p backups
    mkdir -p monitoring
    mkdir -p nginx/logs
    mkdir -p nginx/ssl
    
    log_success "目录结构创建完成"
}

# 配置文件初始化
initialize_configuration() {
    log_info "初始化配置文件..."
    
    # 复制示例配置文件
    if [ ! -f "config/palpation.yaml" ]; then
        log_warning "配置文件不存在，请检查config/palpation.yaml"
    else
        log_success "配置文件已存在"
    fi
    
    # 设置环境变量文件
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# 索克生活触诊服务环境变量
PALPATION_SERVICE_HOST=0.0.0.0
PALPATION_SERVICE_PORT=8000
PALPATION_SERVICE_DEBUG=false
PALPATION_DATABASE_PATH=data/palpation.db
PALPATION_CACHE_REDIS_HOST=localhost
PALPATION_CACHE_REDIS_PORT=6379
PALPATION_LOGGING_LEVEL=INFO
EOF
        log_success "环境变量文件创建完成"
    else
        log_warning "环境变量文件已存在"
    fi
}

# 数据库初始化
initialize_database() {
    log_info "初始化数据库..."
    
    # 确保虚拟环境已激活
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # 运行数据库初始化脚本
    python -c "
import sqlite3
import os

# 创建数据库目录
os.makedirs('data', exist_ok=True)

# 连接数据库
conn = sqlite3.connect('data/palpation.db')
cursor = conn.cursor()

# 创建基础表结构
cursor.execute('''
CREATE TABLE IF NOT EXISTS palpation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT UNIQUE NOT NULL,
    device_type TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pulse_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    channel INTEGER NOT NULL,
    value REAL NOT NULL,
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES palpation_sessions(session_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    result_data TEXT NOT NULL,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES palpation_sessions(session_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS device_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    device_type TEXT NOT NULL,
    status TEXT NOT NULL,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 提交更改并关闭连接
conn.commit()
conn.close()

print('数据库初始化完成')
"
    
    log_success "数据库初始化完成"
}

# 设置权限
setup_permissions() {
    log_info "设置文件权限..."
    
    # 设置脚本执行权限
    chmod +x scripts/*.sh
    
    # 设置数据目录权限
    chmod 755 data
    chmod 755 logs
    chmod 755 cache
    chmod 755 reports
    chmod 755 backups
    
    log_success "文件权限设置完成"
}

# 运行测试
run_tests() {
    log_info "运行基础测试..."
    
    # 确保虚拟环境已激活
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # 运行配置测试
    python -c "
try:
    from internal.config.config_manager import ConfigManager
    config = ConfigManager()
    config.load_config('config/palpation.yaml')
    print('配置文件加载测试: 通过')
except Exception as e:
    print(f'配置文件加载测试: 失败 - {e}')
    exit(1)

try:
    import sqlite3
    conn = sqlite3.connect('data/palpation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"')
    table_count = cursor.fetchone()[0]
    conn.close()
    if table_count >= 4:
        print('数据库连接测试: 通过')
    else:
        print('数据库连接测试: 失败 - 表数量不足')
        exit(1)
except Exception as e:
    print(f'数据库连接测试: 失败 - {e}')
    exit(1)

print('所有基础测试通过')
"
    
    log_success "基础测试完成"
}

# Docker部署
deploy_with_docker() {
    if [ "$DOCKER_AVAILABLE" = true ]; then
        log_info "使用Docker部署服务..."
        
        # 构建镜像
        docker build -t palpation-service:latest .
        
        # 启动服务
        docker-compose up -d
        
        log_success "Docker部署完成"
        log_info "服务访问地址:"
        log_info "  - API服务: http://localhost:8000"
        log_info "  - 监控仪表板: http://localhost:8080"
        log_info "  - Grafana: http://localhost:3000 (admin/admin123)"
        log_info "  - Prometheus: http://localhost:9090"
    else
        log_warning "Docker不可用，跳过容器化部署"
    fi
}

# 本地部署
deploy_locally() {
    log_info "本地部署服务..."
    
    # 确保虚拟环境已激活
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # 创建启动脚本
    cat > start_service.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
python main.py
EOF
    
    chmod +x start_service.sh
    
    log_success "本地部署完成"
    log_info "启动服务: ./start_service.sh"
}

# 主函数
main() {
    log_info "开始安装索克生活触诊服务..."
    
    # 检查是否在正确的目录
    if [ ! -f "main.py" ]; then
        log_error "请在触诊服务根目录下运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    check_system_requirements
    install_system_dependencies
    create_virtual_environment
    install_python_dependencies
    create_directory_structure
    initialize_configuration
    initialize_database
    setup_permissions
    run_tests
    
    # 选择部署方式
    echo
    log_info "选择部署方式:"
    echo "1) Docker部署 (推荐)"
    echo "2) 本地部署"
    echo "3) 两种方式都部署"
    read -p "请选择 (1-3): " choice
    
    case $choice in
        1)
            deploy_with_docker
            ;;
        2)
            deploy_locally
            ;;
        3)
            deploy_with_docker
            deploy_locally
            ;;
        *)
            log_warning "无效选择，仅完成基础安装"
            ;;
    esac
    
    echo
    log_success "索克生活触诊服务安装完成！"
    log_info "更多信息请查看README.md文档"
}

# 运行主函数
main "$@" 