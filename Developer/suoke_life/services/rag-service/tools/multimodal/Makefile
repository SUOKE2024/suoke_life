# 索克生活RAG服务多模态测试工具 Makefile

# 基本配置
GO=go
SERVER=http://localhost:8080
OUTPUT_DIR=./output
ASSETS_DIR=./assets
REPORTS_DIR=$(OUTPUT_DIR)/reports

# 默认目标
.PHONY: all
all: test

# 清理输出
.PHONY: clean
clean:
	@echo "正在清理输出目录..."
	@rm -rf $(OUTPUT_DIR)
	@echo "清理完成"

# 构建Go测试工具
.PHONY: build
build:
	@echo "构建Go测试工具..."
	@$(GO) build -o multimodal
	@echo "构建完成"

# 运行测试
.PHONY: test
test:
	@echo "运行一键测试脚本..."
	@./run-tests.sh

# 仅运行Go测试
.PHONY: test-go
test-go: build
	@echo "运行Go版本测试..."
	@mkdir -p $(OUTPUT_DIR) $(REPORTS_DIR)
	@./multimodal -verbose -server $(SERVER) -output-dir $(OUTPUT_DIR)

# 仅运行Bash测试
.PHONY: test-bash
test-bash:
	@echo "运行Bash版本测试..."
	@mkdir -p $(OUTPUT_DIR) $(REPORTS_DIR)
	@./test-multimodal.sh --verbose --server $(SERVER) --output $(OUTPUT_DIR)

# 下载测试资源
.PHONY: download-assets
download-assets:
	@echo "下载测试资源..."
	@mkdir -p $(ASSETS_DIR)
	@curl -s "https://img.freepik.com/free-photo/closeup-tongue-examination-traditional-chinese-medicine_53876-42233.jpg" > $(ASSETS_DIR)/tongue_sample.jpg
	@curl -s "https://file-examples.com/storage/fe3d669ed563b1e1329ae84/2017/11/file_example_MP3_700KB.mp3" > $(ASSETS_DIR)/audio_sample.mp3
	@echo "下载完成"

# 帮助信息
.PHONY: help
help:
	@echo "索克生活RAG服务多模态测试工具"
	@echo ""
	@echo "可用目标:"
	@echo "  all           默认目标，运行完整测试"
	@echo "  build         仅构建Go测试工具"
	@echo "  test          运行完整测试套件（Go和Bash）"
	@echo "  test-go       仅运行Go版本测试"
	@echo "  test-bash     仅运行Bash版本测试"
	@echo "  clean         清理输出目录"
	@echo "  download-assets 下载测试资源文件"
	@echo "  help          显示此帮助信息"
	@echo ""
	@echo "环境变量:"
	@echo "  SERVER        设置服务器URL (默认: $(SERVER))"
	@echo "  OUTPUT_DIR    设置输出目录 (默认: $(OUTPUT_DIR))"
	@echo ""
	@echo "示例:"
	@echo "  make test SERVER=http://dev.suoke.life:8080"
	@echo "  make test-go SERVER=https://api.suoke.life OUTPUT_DIR=./results" 