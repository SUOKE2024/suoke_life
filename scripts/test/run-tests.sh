#!/bin/bash

# 索克生活测试运行脚本
# 运行完整的测试套件，包括单元测试、集成测试和性能测试

set -e

echo "🧪 开始运行索克生活测试套件..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 函数：运行测试并检查结果
run_test() {
    local test_name=$1
    local test_command=$2
    
    print_message $BLUE "📋 运行 ${test_name}..."
    
    if eval $test_command; then
        print_message $GREEN "✅ ${test_name} 通过"
        return 0
    else
        print_message $RED "❌ ${test_name} 失败"
        return 1
    fi
}

# 检查依赖
print_message $YELLOW "🔍 检查测试依赖..."
if ! command -v npm &> /dev/null; then
    print_message $RED "❌ npm 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_message $RED "❌ Node.js 未安装"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    print_message $YELLOW "📦 安装依赖..."
    npm install
fi

# 测试计数器
total_tests=0
passed_tests=0
failed_tests=0

# 1. 代码质量检查
print_message $BLUE "🔍 代码质量检查"
if run_test "ESLint 检查" "npm run lint"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

if run_test "TypeScript 类型检查" "npm run type-check"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# 2. 单元测试
print_message $BLUE "🧪 单元测试"
if run_test "组件单元测试" "npm run test:unit -- --testPathPattern=components"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

if run_test "服务单元测试" "npm run test:unit -- --testPathPattern=services"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

if run_test "工具函数单元测试" "npm run test:unit -- --testPathPattern=utils"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# 3. 集成测试
print_message $BLUE "🔗 集成测试"
if run_test "端到端集成测试" "npm run test:integration"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# 4. 性能测试
print_message $BLUE "⚡ 性能测试"
if run_test "性能基准测试" "npm run test:performance"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# 5. 覆盖率测试
print_message $BLUE "📊 测试覆盖率"
if run_test "覆盖率收集" "npm run test:coverage"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# 6. 后端服务测试（如果存在）
if [ -d "services" ]; then
    print_message $BLUE "🐍 后端服务测试"
    
    # Python 服务测试
    for service_dir in services/*/; do
        if [ -f "${service_dir}requirements.txt" ] && [ -f "${service_dir}pytest.ini" ]; then
            service_name=$(basename "$service_dir")
            if run_test "${service_name} 服务测试" "cd ${service_dir} && python -m pytest"; then
                ((passed_tests++))
            else
                ((failed_tests++))
            fi
            ((total_tests++))
        fi
    done
fi

# 生成测试报告
print_message $BLUE "📋 生成测试报告..."

# 创建报告目录
mkdir -p reports

# 生成 JSON 报告
cat > reports/test-summary.json << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "total_tests": $total_tests,
  "passed_tests": $passed_tests,
  "failed_tests": $failed_tests,
  "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l),
  "status": "$([ $failed_tests -eq 0 ] && echo "PASSED" || echo "FAILED")"
}
EOF

# 生成 Markdown 报告
cat > reports/test-report.md << EOF
# 索克生活测试报告

**生成时间**: $(date)

## 测试概览

- **总测试数**: $total_tests
- **通过测试**: $passed_tests
- **失败测试**: $failed_tests
- **成功率**: $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l)%
- **状态**: $([ $failed_tests -eq 0 ] && echo "✅ 通过" || echo "❌ 失败")

## 测试详情

### 代码质量检查
- ESLint 检查
- TypeScript 类型检查

### 单元测试
- 组件单元测试
- 服务单元测试
- 工具函数单元测试

### 集成测试
- 端到端集成测试

### 性能测试
- 性能基准测试

### 覆盖率测试
- 测试覆盖率收集

## 建议

$([ $failed_tests -eq 0 ] && echo "🎉 所有测试都通过了！代码质量良好。" || echo "⚠️ 有测试失败，请检查并修复相关问题。")

---
*此报告由索克生活自动化测试系统生成*
EOF

# 打印最终结果
echo ""
print_message $BLUE "📊 测试结果汇总"
echo "总测试数: $total_tests"
echo "通过测试: $passed_tests"
echo "失败测试: $failed_tests"
echo "成功率: $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l)%"

if [ $failed_tests -eq 0 ]; then
    print_message $GREEN "🎉 所有测试都通过了！"
    echo ""
    print_message $GREEN "📋 测试报告已生成："
    echo "  - JSON: reports/test-summary.json"
    echo "  - Markdown: reports/test-report.md"
    exit 0
else
    print_message $RED "❌ 有 $failed_tests 个测试失败"
    echo ""
    print_message $YELLOW "📋 测试报告已生成："
    echo "  - JSON: reports/test-summary.json"
    echo "  - Markdown: reports/test-report.md"
    exit 1
fi 