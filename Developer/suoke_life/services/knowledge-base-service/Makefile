# 索克生活知识库服务Makefile

# 变量定义
SERVICE_NAME = knowledge-base-service
BUILD_DIR = ./build
DOCKER_IMAGE = suoke.life/$(SERVICE_NAME)
VERSION ?= $(shell git describe --tags --always --dirty || echo "dev")
COMMIT_HASH ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
LDFLAGS = -ldflags "-w -s -X main.Version=$(VERSION) -X main.CommitHash=$(COMMIT_HASH) -X main.BuildDate=$(BUILD_DATE)"
GO_FILES = $(shell find . -name "*.go" -not -path "./vendor/*")
GOPATH ?= $(shell go env GOPATH)
MOCKERY = $(GOPATH)/bin/mockery

.PHONY: all build clean test lint docker generate help mock bench coverage e2e test-all test-short test-containers ci-local

# 默认目标
all: help

# 构建可执行文件
build:
	@echo "构建 $(SERVICE_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@CGO_ENABLED=0 go build $(LDFLAGS) -o $(BUILD_DIR)/$(SERVICE_NAME) ./cmd/$(SERVICE_NAME)
	@echo "构建完成: $(BUILD_DIR)/$(SERVICE_NAME)"

# 清理构建产物
clean:
	@echo "清理构建目录..."
	@rm -rf $(BUILD_DIR)
	@rm -rf ./test-output
	@echo "清理完成"

# 运行所有单元测试
test:
	@echo "运行单元测试..."
	@go test -race ./internal/domain/... ./internal/interfaces/... ./pkg/...

# 运行集成测试
integration:
	@echo "运行集成测试..."
	@go test -race ./internal/test/integration/...

# 运行端到端测试
e2e:
	@echo "运行端到端测试..."
	@bash ./scripts/run_tests.sh -e

# 运行基准测试
bench:
	@echo "运行基准测试..."
	@mkdir -p ./test-output
	@go test -benchmem -run=^$$ -bench=. ./internal/test/benchmark/... | tee ./test-output/benchmark.txt

# 运行全部测试
test-all: 
	@bash ./scripts/run_tests.sh -u -i -e -c -r

# 运行代码检查
lint:
	@echo "运行代码检查..."
	@golangci-lint run ./...

# 生成覆盖率报告
coverage:
	@echo "生成测试覆盖率报告..."
	@mkdir -p ./test-output
	@go test -coverprofile=./test-output/coverage.out ./internal/... ./pkg/...
	@go tool cover -html=./test-output/coverage.out -o ./test-output/coverage.html
	@go tool cover -func=./test-output/coverage.out
	@echo "覆盖率报告已生成: ./test-output/coverage.html"

# 构建Docker镜像
docker:
	@echo "构建Docker镜像 $(DOCKER_IMAGE):$(VERSION)..."
	@docker build -t $(DOCKER_IMAGE):$(VERSION) \
		--build-arg VERSION=$(VERSION) \
		--build-arg COMMIT_HASH=$(COMMIT_HASH) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		.
	@docker tag $(DOCKER_IMAGE):$(VERSION) $(DOCKER_IMAGE):latest
	@echo "Docker镜像构建完成"

# 构建测试用Docker镜像
docker-test:
	@echo "构建测试用Docker镜像..."
	@docker build -t $(DOCKER_IMAGE):test -f Dockerfile.test .
	@echo "测试Docker镜像构建完成"

# 生成Mock对象
mock:
	@echo "生成Mock对象..."
	@if [ ! -f $(MOCKERY) ]; then \
		echo "安装mockery..."; \
		go install github.com/vektra/mockery/v2@latest; \
	fi
	@$(MOCKERY) --all --keeptree --dir=./internal --output=./internal/test/mocks
	@echo "Mock对象生成完成"

# 生成代码
generate:
	@echo "运行Go生成命令..."
	@go generate ./...
	@echo "代码生成完成"

# 运行本地开发服务
dev:
	@echo "运行本地开发服务..."
	@go run ./cmd/$(SERVICE_NAME)/main.go

# 运行Docker测试环境
test-env-up:
	@echo "启动测试环境..."
	@docker-compose -f docker-compose.test.yml up -d
	@echo "测试环境已启动"

test-env-down:
	@echo "关闭测试环境..."
	@docker-compose -f docker-compose.test.yml down -v
	@echo "测试环境已关闭"

# 添加一个新的测试命令，用于运行短测试模式
test-short:
	@echo "运行短测试模式 (跳过外部依赖) 📝"
	@go test -short ./internal/domain/service/... ./internal/interfaces/rest/... ./internal/test/benchmark/... ./internal/test/integration/...

# 添加一个新的测试命令，用于运行TestContainers集成测试
test-containers:
	@echo "运行TestContainers集成测试 🐳"
	@go test ./internal/test/integration/document_repository_testcontainers_test.go -v

# 添加本地CI流水线命令
ci-local:
	@echo "运行本地CI流水线 🚀"
	@./scripts/run_ci_local.sh

# 帮助信息
help:
	@echo "索克生活知识库服务 - 可用命令:"
	@echo ""
	@echo "管理命令:"
	@echo "  make build          - 构建服务可执行文件"
	@echo "  make clean          - 清理构建目录"
	@echo "  make docker         - 构建Docker镜像"
	@echo "  make docker-test    - 构建测试用Docker镜像"
	@echo ""
	@echo "测试命令:"
	@echo "  make test           - 运行单元测试"
	@echo "  make integration    - 运行集成测试"
	@echo "  make e2e            - 运行端到端测试"
	@echo "  make bench          - 运行基准测试"
	@echo "  make test-all       - 运行全部测试并生成报告"
	@echo "  make coverage       - 生成测试覆盖率报告"
	@echo "  make test-short     - 运行短测试模式(跳过外部依赖)"
	@echo "  make test-containers- 运行TestContainers集成测试"
	@echo ""
	@echo "CI/CD命令:"
	@echo "  make ci-local       - 在本地运行CI流水线"
	@echo ""
	@echo "开发辅助命令:"
	@echo "  make lint           - 运行代码检查"
	@echo "  make mock           - 生成Mock对象"
	@echo "  make generate       - 运行Go生成命令"
	@echo "  make dev            - 运行本地开发服务"
	@echo "  make test-env-up    - 启动测试环境"
	@echo "  make test-env-down  - 关闭测试环境"
	@echo ""