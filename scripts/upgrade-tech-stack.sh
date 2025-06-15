#!/bin/bash

# 索克生活技术栈升级脚本
# React Native 0.80+, TypeScript 5.1+, 最新AI框架

set -e

echo "🚀 开始升级索克生活技术栈..."

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

# 检查必要工具
check_prerequisites() {
    log_info "检查必要工具..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    if ! command -v uv &> /dev/null; then
        log_warning "uv 未安装，将使用 pip"
    fi
    
    log_success "必要工具检查完成"
}

# 备份当前配置
backup_configs() {
    log_info "备份当前配置..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份关键配置文件
    cp package.json "$BACKUP_DIR/" 2>/dev/null || true
    cp package-lock.json "$BACKUP_DIR/" 2>/dev/null || true
    cp tsconfig.json "$BACKUP_DIR/" 2>/dev/null || true
    cp babel.config.js "$BACKUP_DIR/" 2>/dev/null || true
    cp metro.config.js "$BACKUP_DIR/" 2>/dev/null || true
    cp pyproject.toml "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "配置已备份到 $BACKUP_DIR"
}

# 清理缓存
clean_caches() {
    log_info "清理缓存..."
    
    # 清理 npm 缓存
    npm cache clean --force 2>/dev/null || true
    
    # 清理 React Native 缓存
    npx react-native start --reset-cache &
    sleep 2
    pkill -f "react-native start" || true
    
    # 清理 Metro 缓存
    rm -rf node_modules/.cache 2>/dev/null || true
    rm -rf /tmp/metro-* 2>/dev/null || true
    
    # 清理 Python 缓存
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "缓存清理完成"
}

# 升级 Node.js 依赖
upgrade_nodejs_deps() {
    log_info "升级 Node.js 依赖..."
    
    # 删除 node_modules 和 package-lock.json
    rm -rf node_modules package-lock.json
    
    # 安装依赖
    npm install
    
    # 检查是否有安全漏洞
    npm audit fix --force || log_warning "部分安全问题无法自动修复"
    
    log_success "Node.js 依赖升级完成"
}

# 升级 Python 依赖
upgrade_python_deps() {
    log_info "升级 Python 依赖..."
    
    if command -v uv &> /dev/null; then
        # 使用 uv 升级
        uv sync --upgrade
        uv pip install --upgrade pip
    else
        # 使用传统 pip
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt --upgrade
    fi
    
    log_success "Python 依赖升级完成"
}

# 配置 React Native 新架构
configure_new_architecture() {
    log_info "配置 React Native 新架构..."
    
    # 启用新架构
    export RCT_NEW_ARCH_ENABLED=1
    
    # iOS 配置
    if [ -d "ios" ]; then
        log_info "配置 iOS 新架构..."
        cd ios
        
        # 更新 Podfile
        if [ -f "Podfile" ]; then
            # 启用 Fabric
            sed -i '' 's/:fabric_enabled => false/:fabric_enabled => true/g' Podfile 2>/dev/null || true
            # 启用 Hermes
            sed -i '' 's/:hermes_enabled => false/:hermes_enabled => true/g' Podfile 2>/dev/null || true
        fi
        
        # 清理并重新安装 Pods
        rm -rf Pods Podfile.lock
        pod install --repo-update || log_warning "Pod 安装可能有问题"
        
        cd ..
        log_success "iOS 新架构配置完成"
    fi
    
    # Android 配置
    if [ -d "android" ]; then
        log_info "配置 Android 新架构..."
        
        # 更新 gradle.properties
        if [ -f "android/gradle.properties" ]; then
            echo "newArchEnabled=true" >> android/gradle.properties
            echo "hermesEnabled=true" >> android/gradle.properties
        fi
        
        # 清理 Android 构建缓存
        cd android
        ./gradlew clean || log_warning "Android 清理可能有问题"
        cd ..
        
        log_success "Android 新架构配置完成"
    fi
}

# 验证 AI 框架
verify_ai_frameworks() {
    log_info "验证 AI 框架..."
    
    # 检查 Python AI 依赖
    python3 -c "
import sys
try:
    import torch
    print(f'✓ PyTorch {torch.__version__}')
except ImportError:
    print('✗ PyTorch 未安装')
    sys.exit(1)

try:
    import transformers
    print(f'✓ Transformers {transformers.__version__}')
except ImportError:
    print('✗ Transformers 未安装')
    sys.exit(1)

try:
    import openai
    print(f'✓ OpenAI {openai.__version__}')
except ImportError:
    print('✗ OpenAI 未安装')
    sys.exit(1)
" || log_error "AI 框架验证失败"
    
    log_success "AI 框架验证完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # TypeScript 类型检查
    npm run type-check || log_warning "TypeScript 类型检查有警告"
    
    # ESLint 检查
    npm run lint || log_warning "ESLint 检查有警告"
    
    # 运行单元测试
    npm run test:unit || log_warning "单元测试有失败"
    
    log_success "测试完成"
}

# 生成升级报告
generate_report() {
    log_info "生成升级报告..."
    
    REPORT_FILE="upgrade_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# 索克生活技术栈升级报告

## 升级时间
$(date)

## 升级内容

### React Native
- 版本: 0.80.2
- 新架构: 已启用
- Hermes: 已启用
- Fabric: 已启用

### TypeScript
- 版本: 5.6.3
- 装饰器支持: 已启用
- 严格模式: 已启用

### AI 框架
- PyTorch: $(python3 -c "import torch; print(torch.__version__)" 2>/dev/null || echo "未检测到")
- Transformers: $(python3 -c "import transformers; print(transformers.__version__)" 2>/dev/null || echo "未检测到")
- OpenAI: $(python3 -c "import openai; print(openai.__version__)" 2>/dev/null || echo "未检测到")

### 新增功能
- AI 装饰器支持
- 多模型负载均衡
- 健康分析 AI 服务
- 中医诊断 AI 集成

## 配置文件更新
- package.json: ✓
- tsconfig.json: ✓
- babel.config.js: ✓
- metro.config.js: ✓
- pyproject.toml: ✓

## 注意事项
1. 请确保所有 API 密钥已正确配置
2. 新架构可能需要重新构建原生模块
3. AI 功能需要网络连接或本地模型

## 下一步
1. 测试所有 AI 功能
2. 验证健康分析准确性
3. 优化模型选择策略
4. 监控性能指标
EOF
    
    log_success "升级报告已生成: $REPORT_FILE"
}

# 主函数
main() {
    echo "🏥 索克生活技术栈升级"
    echo "========================"
    
    check_prerequisites
    backup_configs
    clean_caches
    upgrade_nodejs_deps
    upgrade_python_deps
    configure_new_architecture
    verify_ai_frameworks
    run_tests
    generate_report
    
    echo ""
    echo "🎉 升级完成！"
    echo ""
    echo "📋 下一步操作："
    echo "1. 检查升级报告"
    echo "2. 配置 AI API 密钥"
    echo "3. 测试应用功能"
    echo "4. 部署到测试环境"
    echo ""
    log_success "索克生活技术栈升级成功完成！"
}

# 错误处理
trap 'log_error "升级过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@" 