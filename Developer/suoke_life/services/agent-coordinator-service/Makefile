# 代理协调器服务Makefile

# 变量定义
APP_NAME := agent-coordinator
MODULE := github.com/suoke-life/agent-coordinator-service
VERSION := $(shell git describe --tags --always --dirty --match='v*' 2>/dev/null || echo 'dev')
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
LDFLAGS := -ldflags "-s -w -X ${MODULE}/internal/version.Version=${VERSION} -X ${MODULE}/internal/version.BuildDate=${BUILD_DATE} -X ${MODULE}/internal/version.GitCommit=${GIT_COMMIT}"
GO_FILES := $(shell find . -name "*.go" -type f -not -path "./vendor/*")

# 默认目标
.PHONY: all
all: build

# 清理构建产物
.PHONY: clean
clean:
	@echo "正在清理构建产物..."
	@rm -rf ./bin/
	@rm -rf ./dist/
	@rm -f ./coverage.out
	@rm -f ./${APP_NAME}
	@echo "清理完成"

# 格式化代码
.PHONY: fmt
fmt:
	@echo "正在格式化代码..."
	@gofmt -w ${GO_FILES}
	@echo "格式化完成"

# 代码检查
.PHONY: lint
lint:
	@echo "正在进行代码检查..."
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run ./...; \
	else \
		echo "错误: golangci-lint未安装，执行: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
		exit 1; \
	fi

# 依赖管理
.PHONY: deps
deps:
	@echo "正在下载依赖..."
	@go mod download
	@go mod tidy
	@echo "依赖下载完成"

# 生成Swagger文档
.PHONY: swagger
swagger:
	@echo "正在生成Swagger文档..."
	@if command -v swag >/dev/null 2>&1; then \
		swag init -g cmd/main.go -o ./docs/swagger; \
	else \
		echo "错误: swag未安装，执行: go install github.com/swaggo/swag/cmd/swag@latest"; \
		exit 1; \
	fi
	@echo "Swagger文档生成完成"

# 本地开发构建
.PHONY: build
build: clean deps fmt
	@echo "正在构建${APP_NAME}..."
	@CGO_ENABLED=0 go build ${LDFLAGS} -o ${APP_NAME} ./cmd/main.go
	@echo "构建完成: ./${APP_NAME}"

# 生产环境构建
.PHONY: build-prod
build-prod: clean deps
	@echo "正在构建生产版本${APP_NAME}..."
	@CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo ${LDFLAGS} -o ${APP_NAME} ./cmd/main.go
	@echo "生产版本构建完成: ./${APP_NAME}"

# 构建多平台版本
.PHONY: build-all
build-all: clean deps
	@echo "正在构建多平台版本..."
	@mkdir -p dist
	@for os in linux darwin windows; do \
		for arch in amd64 arm64; do \
			if [ "$$os" = "windows" ]; then \
				GOOS=$$os GOARCH=$$arch CGO_ENABLED=0 go build ${LDFLAGS} -o dist/${APP_NAME}_$${os}_$${arch}.exe ./cmd/main.go; \
			else \
				GOOS=$$os GOARCH=$$arch CGO_ENABLED=0 go build ${LDFLAGS} -o dist/${APP_NAME}_$${os}_$${arch} ./cmd/main.go; \
			fi; \
		done; \
	done
	@echo "多平台版本构建完成: ./dist/"

# 运行应用
.PHONY: run
run: build
	@echo "正在运行${APP_NAME}..."
	@./${APP_NAME}

# 执行单元测试
.PHONY: test
test:
	@echo "正在执行单元测试..."
	@go test -v ./...

# 执行测试并输出覆盖率
.PHONY: test-coverage
test-coverage:
	@echo "正在执行测试并生成覆盖率报告..."
	@go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "测试覆盖率报告已生成: coverage.html"

# 执行基准测试
.PHONY: benchmark
benchmark:
	@echo "正在执行基准测试..."
	@go test -bench=. -benchmem ./...

# Docker相关目标
.PHONY: docker-build
docker-build:
	@echo "正在构建Docker镜像..."
	@docker build -f Dockerfile.go -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:${VERSION} \
		--build-arg VERSION=${VERSION} \
		--build-arg BUILD_DATE=${BUILD_DATE} \
		--build-arg GIT_COMMIT=${GIT_COMMIT} .
	@echo "Docker镜像构建完成: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:${VERSION}"

.PHONY: docker-push
docker-push: docker-build
	@echo "正在推送Docker镜像..."
	@docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:${VERSION}
	@docker tag suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:${VERSION} suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:latest
	@docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:latest
	@echo "Docker镜像推送完成"

.PHONY: docker-run
docker-run: docker-build
	@echo "正在运行Docker容器..."
	@docker run -p 3007:3007 --name ${APP_NAME} --rm \
		-e PORT=3007 \
		-e CONFIG_PATH=/app/config/config.json \
		suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${APP_NAME}:${VERSION}

# 帮助信息
.PHONY: help
help:
	@echo "代理协调器服务构建工具"
	@echo ""
	@echo "可用命令:"
	@echo "  all             默认命令，执行构建"
	@echo "  clean           清理构建产物"
	@echo "  fmt             格式化代码"
	@echo "  lint            代码检查"
	@echo "  deps            下载和更新依赖"
	@echo "  swagger         生成Swagger文档"
	@echo "  build           开发环境构建"
	@echo "  build-prod      生产环境构建"
	@echo "  build-all       构建多平台版本"
	@echo "  run             构建并运行"
	@echo "  test            执行单元测试"
	@echo "  test-coverage   执行测试并生成覆盖率报告"
	@echo "  benchmark       执行基准测试"
	@echo "  docker-build    构建Docker镜像"
	@echo "  docker-push     构建并推送Docker镜像"
	@echo "  docker-run      构建并运行Docker容器"
	@echo "  help            显示帮助信息" 