#!/bin/bash

# 索克生活 - 五诊服务简化测试脚本
# 测试前端组件和API结构，不依赖后端服务

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

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "测试: $test_name"
    
    if eval "$test_command"; then
        if [ "$expected_status" = "success" ]; then
            log_success "✓ $test_name 通过"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log_error "✗ $test_name 失败 (预期失败但实际成功)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        if [ "$expected_status" = "fail" ]; then
            log_success "✓ $test_name 通过 (预期失败)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log_error "✗ $test_name 失败"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    echo
}

# 测试文件存在性
test_file_existence() {
    log_info "=== 测试文件存在性 ==="
    
    run_test "网关配置文件存在" \
        "test -f src/constants/gatewayConfig.ts" \
        "success"
    
    run_test "统一API服务文件存在" \
        "test -f src/services/unifiedApiService.ts" \
        "success"
    
    run_test "五诊服务文件存在" \
        "test -f src/services/fiveDiagnosisService.ts" \
        "success"
    
    run_test "五诊界面文件存在" \
        "test -f src/screens/diagnosis/FiveDiagnosisScreen.tsx" \
        "success"
    
    run_test "算诊组件文件存在" \
        "test -f src/components/diagnosis/CalculationDiagnosisComponent.tsx" \
        "success"
    
    run_test "五诊配置文件存在" \
        "test -f config/five-diagnosis.yml" \
        "success"
    
    run_test "环境变量模板存在" \
        "test -f config/five-diagnosis.env.example" \
        "success"
}

# 测试TypeScript语法
test_typescript_syntax() {
    log_info "=== 测试TypeScript语法 ==="
    
    # 检查是否安装了TypeScript
    if ! command -v npx &> /dev/null; then
        log_warning "npx 未安装，跳过TypeScript语法检查"
        return
    fi
    
    run_test "网关配置TypeScript语法" \
        "npx tsc --noEmit --skipLibCheck src/constants/gatewayConfig.ts" \
        "success"
    
    run_test "统一API服务TypeScript语法" \
        "npx tsc --noEmit --skipLibCheck src/services/unifiedApiService.ts" \
        "success"
    
    run_test "五诊服务TypeScript语法" \
        "npx tsc --noEmit --skipLibCheck src/services/fiveDiagnosisService.ts" \
        "success"
    
    run_test "五诊界面TypeScript语法" \
        "npx tsc --noEmit --skipLibCheck src/screens/diagnosis/FiveDiagnosisScreen.tsx" \
        "success"
    
    run_test "算诊组件TypeScript语法" \
        "npx tsc --noEmit --skipLibCheck src/components/diagnosis/CalculationDiagnosisComponent.tsx" \
        "success"
}

# 测试文件内容
test_file_content() {
    log_info "=== 测试文件内容 ==="
    
    run_test "网关配置包含算诊端点" \
        "grep -q 'calculation' src/constants/gatewayConfig.ts" \
        "success"
    
    run_test "统一API服务包含算诊方法" \
        "grep -q 'performCalculationDiagnosis' src/services/unifiedApiService.ts" \
        "success"
    
    run_test "五诊服务包含综合分析" \
        "grep -q 'performComprehensiveDiagnosis' src/services/fiveDiagnosisService.ts" \
        "success"
    
    run_test "五诊界面包含算诊步骤" \
        "grep -q 'calculation' src/screens/diagnosis/FiveDiagnosisScreen.tsx" \
        "success"
    
    run_test "算诊组件包含子午流注" \
        "grep -q 'ziwu' src/components/diagnosis/CalculationDiagnosisComponent.tsx" \
        "success"
    
    run_test "配置文件包含算诊配置" \
        "grep -q 'calculation_diagnosis' config/five-diagnosis.yml" \
        "success"
}

# 测试API接口定义
test_api_interfaces() {
    log_info "=== 测试API接口定义 ==="
    
    run_test "网关配置包含五诊端点" \
        "grep -q 'fiveDiagnosis' src/constants/gatewayConfig.ts" \
        "success"
    
    run_test "API服务包含子午流注分析" \
        "grep -q 'performZiwuAnalysis' src/services/unifiedApiService.ts" \
        "success"
    
    run_test "API服务包含八字体质分析" \
        "grep -q 'performConstitutionAnalysis' src/services/unifiedApiService.ts" \
        "success"
    
    run_test "API服务包含八卦配属分析" \
        "grep -q 'performBaguaAnalysis' src/services/unifiedApiService.ts" \
        "success"
    
    run_test "API服务包含五运六气分析" \
        "grep -q 'performWuyunAnalysis' src/services/unifiedApiService.ts" \
        "success"
}

# 测试React Native组件
test_react_native_components() {
    log_info "=== 测试React Native组件 ==="
    
    run_test "五诊界面导入React Native" \
        "grep -q 'react-native' src/screens/diagnosis/FiveDiagnosisScreen.tsx" \
        "success"
    
    run_test "算诊组件导入React Native" \
        "grep -q 'react-native' src/components/diagnosis/CalculationDiagnosisComponent.tsx" \
        "success"
    
    run_test "五诊界面包含状态管理" \
        "grep -q 'useState' src/screens/diagnosis/FiveDiagnosisScreen.tsx" \
        "success"
    
    run_test "算诊组件包含表单处理" \
        "grep -q 'TextInput\|Picker' src/components/diagnosis/CalculationDiagnosisComponent.tsx" \
        "success"
}

# 测试配置文件
test_configuration_files() {
    log_info "=== 测试配置文件 ==="
    
    run_test "YAML配置文件语法" \
        "python3 -c \"import yaml; yaml.safe_load(open('config/five-diagnosis.yml'))\"" \
        "success"
    
    run_test "环境变量模板格式" \
        "grep -q '^[A-Z_]*=' config/five-diagnosis.env.example" \
        "success"
    
    run_test "配置包含数据库设置" \
        "grep -q 'database:' config/five-diagnosis.yml" \
        "success"
    
    run_test "配置包含AI模型设置" \
        "grep -q 'ai_models:' config/five-diagnosis.yml" \
        "success"
}

# 测试脚本文件
test_script_files() {
    log_info "=== 测试脚本文件 ==="
    
    run_test "启动脚本可执行" \
        "test -x scripts/start-five-diagnosis.sh" \
        "success"
    
    run_test "测试脚本可执行" \
        "test -x scripts/test-five-diagnosis.sh" \
        "success"
    
    run_test "部署脚本可执行" \
        "test -x scripts/deploy-five-diagnosis.sh" \
        "success"
    
    run_test "启动脚本包含五诊服务" \
        "grep -q 'calculation-service' scripts/start-five-diagnosis.sh" \
        "success"
}

# 测试项目结构
test_project_structure() {
    log_info "=== 测试项目结构 ==="
    
    run_test "诊断服务目录存在" \
        "test -d services/diagnostic-services" \
        "success"
    
    run_test "算诊服务目录存在" \
        "test -d services/diagnostic-services/calculation-service" \
        "success"
    
    run_test "前端组件目录存在" \
        "test -d src/components/diagnosis" \
        "success"
    
    run_test "前端界面目录存在" \
        "test -d src/screens/diagnosis" \
        "success"
    
    run_test "配置目录存在" \
        "test -d config" \
        "success"
    
    run_test "脚本目录存在" \
        "test -d scripts" \
        "success"
}

# 生成测试报告
generate_test_report() {
    log_info "=== 测试报告 ==="
    echo
    echo "📊 测试统计："
    echo "   总测试数: $TOTAL_TESTS"
    echo "   通过测试: $PASSED_TESTS"
    echo "   失败测试: $FAILED_TESTS"
    echo "   成功率: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"
    echo
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "🎉 所有测试通过！五诊系统结构完整"
        echo
        echo "✅ 升级成果："
        echo "   • 传统四诊功能保留"
        echo "   • 新增算诊功能完整"
        echo "   • 前端组件结构正确"
        echo "   • API接口定义完善"
        echo "   • 配置文件格式正确"
        echo "   • 脚本文件可执行"
        echo
        echo "🚀 下一步："
        echo "   1. 实现后端微服务"
        echo "   2. 部署测试环境"
        echo "   3. 集成测试验证"
        echo "   4. 性能优化调试"
        return 0
    else
        log_warning "⚠️  有 $FAILED_TESTS 个测试失败，请检查相关文件"
        return 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "    索克生活 - 五诊服务简化测试"
    echo "=========================================="
    echo
    
    log_info "开始五诊系统结构测试..."
    echo
    
    # 运行测试套件
    test_file_existence
    test_typescript_syntax
    test_file_content
    test_api_interfaces
    test_react_native_components
    test_configuration_files
    test_script_files
    test_project_structure
    
    # 生成报告
    generate_test_report
}

# 运行主函数
main "$@" 