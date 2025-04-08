#!/bin/bash

# 索克生活RAG服务多模态测试一键运行脚本
# 用于自动执行所有测试和生成测试报告

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 显示标题
echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}    索克生活RAG服务多模态搜索测试一键运行脚本    ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建输出目录
mkdir -p output
mkdir -p output/reports

# 显示系统信息
echo -e "${YELLOW}系统信息:${NC}"
echo -e "  ${YELLOW}操作系统:${NC} $(uname -s) $(uname -r)"
echo -e "  ${YELLOW}主机名:${NC} $(hostname)"
echo -e "  ${YELLOW}日期时间:${NC} $(date)"
echo -e "  ${YELLOW}工作目录:${NC} $(pwd)"
echo

# 检查环境和依赖
echo -e "${YELLOW}检查环境和依赖...${NC}"

# 检查Go
if command -v go &> /dev/null; then
    GO_VERSION=$(go version)
    echo -e "  ${GREEN}✓${NC} Go安装正常: $GO_VERSION"
else
    echo -e "  ${RED}✗${NC} Go未安装，无法运行Go版本测试"
    GO_AVAILABLE=false
fi

# 检查curl
if command -v curl &> /dev/null; then
    CURL_VERSION=$(curl --version | head -n 1)
    echo -e "  ${GREEN}✓${NC} curl安装正常: $CURL_VERSION"
else
    echo -e "  ${RED}✗${NC} curl未安装，无法执行测试"
    exit 1
fi

# 检查jq
if command -v jq &> /dev/null; then
    JQ_VERSION=$(jq --version)
    echo -e "  ${GREEN}✓${NC} jq安装正常: $JQ_VERSION"
else
    echo -e "  ${RED}✗${NC} jq未安装，部分测试结果解析可能失败"
fi

# 检查测试资源
echo -e "\n${YELLOW}检查测试资源...${NC}"

if [ -f "assets/tongue_sample.jpg" ]; then
    echo -e "  ${GREEN}✓${NC} 舌诊测试图像正常"
else
    echo -e "  ${RED}✗${NC} 找不到舌诊测试图像"
    MISSING_RESOURCES=true
fi

if [ -f "assets/audio_sample.mp3" ]; then
    echo -e "  ${GREEN}✓${NC} 音频测试文件正常"
else
    echo -e "  ${RED}✗${NC} 找不到音频测试文件"
    MISSING_RESOURCES=true
fi

if [ "$MISSING_RESOURCES" = true ]; then
    echo -e "\n${YELLOW}尝试下载缺失的测试资源...${NC}"
    mkdir -p assets
    
    if [ ! -f "assets/tongue_sample.jpg" ]; then
        echo -e "  ${BLUE}→${NC} 下载舌诊测试图像..."
        curl -s "https://img.freepik.com/free-photo/closeup-tongue-examination-traditional-chinese-medicine_53876-42233.jpg" > assets/tongue_sample.jpg
        if [ -f "assets/tongue_sample.jpg" ]; then
            echo -e "  ${GREEN}✓${NC} 舌诊测试图像下载成功"
        else
            echo -e "  ${RED}✗${NC} 舌诊测试图像下载失败"
        fi
    fi
    
    if [ ! -f "assets/audio_sample.mp3" ]; then
        echo -e "  ${BLUE}→${NC} 下载音频测试文件..."
        curl -s "https://file-examples.com/storage/fe3d669ed563b1e1329ae84/2017/11/file_example_MP3_700KB.mp3" > assets/audio_sample.mp3
        if [ -f "assets/audio_sample.mp3" ]; then
            echo -e "  ${GREEN}✓${NC} 音频测试文件下载成功"
        else
            echo -e "  ${RED}✗${NC} 音频测试文件下载失败"
        fi
    fi
fi

# 测试服务器
echo -e "\n${YELLOW}测试服务器连接...${NC}"
SERVER_URL="http://localhost:8080"

if curl -s "$SERVER_URL/health" > /dev/null; then
    echo -e "  ${GREEN}✓${NC} 服务器连接正常: $SERVER_URL"
    SERVER_AVAILABLE=true
else
    echo -e "  ${RED}✗${NC} 无法连接到服务器: $SERVER_URL"
    echo -e "  ${YELLOW}?${NC} 是否继续测试? [y/N]"
    read -r CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo -e "  ${BLUE}i${NC} 测试取消"
        exit 0
    fi
fi

# 运行Go版本测试
if [ "$GO_AVAILABLE" != false ]; then
    echo -e "\n${YELLOW}运行Go版本测试...${NC}"
    echo -e "  ${BLUE}→${NC} 编译测试程序..."
    
    # 编译Go程序
    if go build; then
        echo -e "  ${GREEN}✓${NC} 编译成功"
        
        # 运行Go测试
        echo -e "  ${BLUE}→${NC} 执行Go测试..."
        ./multimodal -verbose -output-dir "./output" > "./output/reports/go_test_report.txt" 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} Go测试完成"
            echo -e "  ${BLUE}i${NC} 测试报告: output/reports/go_test_report.txt"
        else
            echo -e "  ${RED}✗${NC} Go测试失败"
        fi
    else
        echo -e "  ${RED}✗${NC} 编译失败"
    fi
fi

# 运行Bash脚本测试
echo -e "\n${YELLOW}运行Bash脚本测试...${NC}"
echo -e "  ${BLUE}→${NC} 执行Bash测试..."

if [ -x "./test-multimodal.sh" ]; then
    ./test-multimodal.sh --verbose --output "./output" > "./output/reports/bash_test_report.txt" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Bash测试完成"
        echo -e "  ${BLUE}i${NC} 测试报告: output/reports/bash_test_report.txt"
    else
        echo -e "  ${RED}✗${NC} Bash测试失败"
    fi
else
    echo -e "  ${RED}✗${NC} Bash测试脚本不可执行或不存在"
fi

# 生成测试报告摘要
echo -e "\n${YELLOW}生成测试报告摘要...${NC}"

# 检查输出文件
REPORT_FILE="./output/reports/test_summary.md"

cat > "$REPORT_FILE" << EOF
# 索克生活RAG服务多模态测试报告

**测试时间:** $(date)
**服务器:** $SERVER_URL
**测试环境:** $(uname -s) $(uname -r)

## 测试摘要

EOF

# 检查测试结果
if [ -f "./output/health_check_result.json" ]; then
    echo "- ✅ 健康检查测试通过" >> "$REPORT_FILE"
else
    echo "- ❌ 健康检查测试失败" >> "$REPORT_FILE"
fi

if [ -f "./output/basic_search_result.json" ]; then
    echo "- ✅ 基本搜索测试通过" >> "$REPORT_FILE"
else
    echo "- ❌ 基本搜索测试失败" >> "$REPORT_FILE"
fi

if [ -f "./output/tongue_analysis_result.json" ]; then
    echo "- ✅ 舌诊分析测试通过" >> "$REPORT_FILE"
else
    echo "- ❌ 舌诊分析测试失败" >> "$REPORT_FILE"
fi

if [ -f "./output/audio_analysis_result.json" ]; then
    echo "- ✅ 音频分析测试通过" >> "$REPORT_FILE"
else
    echo "- ❌ 音频分析测试失败" >> "$REPORT_FILE"
fi

if [ -f "./output/multimodal_search_result.json" ]; then
    echo "- ✅ 多模态搜索测试通过" >> "$REPORT_FILE"
else
    echo "- ❌ 多模态搜索测试失败" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

## 详细测试结果

详细测试结果可在以下文件中查看：

- 健康检查: \`output/health_check_result.json\`
- 基本搜索: \`output/basic_search_result.json\`
- 舌诊分析: \`output/tongue_analysis_result.json\`
- 音频分析: \`output/audio_analysis_result.json\`
- 多模态搜索: \`output/multimodal_search_result.json\`

## 测试日志

- Go测试日志: \`output/reports/go_test_report.txt\`
- Bash测试日志: \`output/reports/bash_test_report.txt\`

EOF

echo -e "  ${GREEN}✓${NC} 测试报告摘要已生成: $REPORT_FILE"

# 总结
echo -e "\n${BLUE}=======================================================${NC}"
echo -e "${YELLOW}测试执行完成!${NC}"
echo -e "${YELLOW}测试结果摘要:${NC}"

if [ -f "./output/reports/test_summary.md" ]; then
    # 使用cat加上grep提取摘要内容
    grep -A 10 "## 测试摘要" "./output/reports/test_summary.md" | grep -v "## 详细测试结果" | grep -E "^-"
fi

echo -e "${BLUE}=======================================================${NC}"
echo -e "${YELLOW}测试报告位置:${NC}"
echo -e "  测试报告摘要: $REPORT_FILE"
echo -e "  Go测试报告: output/reports/go_test_report.txt"
echo -e "  Bash测试报告: output/reports/bash_test_report.txt"
echo -e "  JSON结果: output/目录"
echo -e "${BLUE}=======================================================${NC}" 