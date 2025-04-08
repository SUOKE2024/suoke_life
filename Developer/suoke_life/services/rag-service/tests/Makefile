.PHONY: test coverage clean

# 测试相关变量
TEST_DIRS=./...
COVER_PROFILE=coverage.out
COVER_HTML=coverage.html

# 默认目标
all: test

# 运行所有测试
test:
	@echo "运行所有测试..."
	@cd .. && go test $(TEST_DIRS) -v

# 运行基本测试 (跳过需要外部资源的测试)
test-short:
	@echo "运行基本测试 (跳过需要外部资源的测试)..."
	@cd .. && go test $(TEST_DIRS) -v -short

# 运行并查看代码覆盖率
coverage:
	@echo "生成测试覆盖率报告..."
	@cd .. && go test $(TEST_DIRS) -coverprofile=$(COVER_PROFILE)
	@cd .. && go tool cover -html=$(COVER_PROFILE) -o $(COVER_HTML)
	@echo "测试覆盖率报告已生成: $(COVER_HTML)"

# 运行基准测试
benchmark:
	@echo "运行基准测试..."
	@cd .. && go test $(TEST_DIRS) -bench=. -benchmem

# 清理测试产生的文件
clean:
	@echo "清理测试文件..."
	@cd .. && rm -f $(COVER_PROFILE) $(COVER_HTML)

# 帮助信息
help:
	@echo "可用的命令:"
	@echo "  make test         - 运行所有测试"
	@echo "  make test-short   - 运行基本测试 (跳过需要外部资源的测试)"
	@echo "  make coverage     - 运行测试并生成代码覆盖率报告"
	@echo "  make benchmark    - 运行基准测试"
	@echo "  make clean        - 清理测试产生的文件" 