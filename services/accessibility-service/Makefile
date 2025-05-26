# Suoke Life - Accessibility Service Makefile
# 用于管理开发、测试、构建和部署流程

.PHONY: help install test lint format build docker-build docker-push deploy-aliyun clean

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# 项目配置
PROJECT_NAME := accessibility-service
VERSION := $(shell git describe --tags --always --dirty)
COMMIT_SHA := $(shell git rev-parse --short HEAD)
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')

# Docker配置
DOCKER_REGISTRY := suoke-registry.cn-hangzhou.cr.aliyuncs.com
DOCKER_NAMESPACE := suoke
DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(DOCKER_NAMESPACE)/$(PROJECT_NAME)
DOCKER_PLATFORMS := linux/amd64,linux/arm64

# Python配置
PYTHON := python3.13
PIP := pip
VENV_DIR := venv_py313

help: ## 显示帮助信息
	@echo "$(BLUE)Suoke Life - Accessibility Service$(NC)"
	@echo "$(BLUE)====================================$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

install: ## 安装依赖
	@echo "$(BLUE)安装Python依赖...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)依赖安装完成$(NC)"

install-dev: ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov black isort mypy flake8 bandit safety
	@echo "$(GREEN)开发依赖安装完成$(NC)"

test: ## 运行测试
	@echo "$(BLUE)运行单元测试...$(NC)"
	pytest tests/unit --cov=internal --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)测试完成$(NC)"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(NC)"
	pytest tests/integration -v
	@echo "$(GREEN)集成测试完成$(NC)"

test-all: ## 运行所有测试
	@echo "$(BLUE)运行所有测试...$(NC)"
	pytest tests/ --cov=internal --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)所有测试完成$(NC)"

lint: ## 代码检查
	@echo "$(BLUE)运行代码检查...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)代码检查完成$(NC)"

format: ## 格式化代码
	@echo "$(BLUE)格式化代码...$(NC)"
	black .
	isort .
	@echo "$(GREEN)代码格式化完成$(NC)"

format-check: ## 检查代码格式
	@echo "$(BLUE)检查代码格式...$(NC)"
	black --check --diff .
	isort --check --diff .
	@echo "$(GREEN)代码格式检查完成$(NC)"

type-check: ## 类型检查
	@echo "$(BLUE)运行类型检查...$(NC)"
	mypy --ignore-missing-imports .
	@echo "$(GREEN)类型检查完成$(NC)"

security-check: ## 安全检查
	@echo "$(BLUE)运行安全检查...$(NC)"
	bandit -r internal -f json -o bandit-results.json || true
	safety check -r requirements.txt --json > safety-results.json || true
	@echo "$(GREEN)安全检查完成$(NC)"

build: ## 构建项目
	@echo "$(BLUE)构建项目...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)项目构建完成$(NC)"

docker-build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(NC)"
	docker build -f deploy/docker/Dockerfile -t $(DOCKER_IMAGE):$(VERSION) .
	docker tag $(DOCKER_IMAGE):$(VERSION) $(DOCKER_IMAGE):latest
	@echo "$(GREEN)Docker镜像构建完成$(NC)"

docker-build-multi: ## 构建多架构Docker镜像
	@echo "$(BLUE)构建多架构Docker镜像...$(NC)"
	docker buildx build \
		--platform $(DOCKER_PLATFORMS) \
		--file deploy/docker/Dockerfile \
		--tag $(DOCKER_IMAGE):$(VERSION) \
		--tag $(DOCKER_IMAGE):latest \
		--tag $(DOCKER_IMAGE):$(COMMIT_SHA) \
		--build-arg BUILDTIME=$(BUILD_TIME) \
		--build-arg VERSION=$(VERSION) \
		--build-arg REVISION=$(COMMIT_SHA) \
		.
	@echo "$(GREEN)多架构Docker镜像构建完成$(NC)"

docker-push: ## 推送Docker镜像到阿里云
	@echo "$(BLUE)推送Docker镜像到阿里云容器镜像仓库...$(NC)"
	@if [ -z "$(ALIYUN_REGISTRY_USERNAME)" ] || [ -z "$(ALIYUN_REGISTRY_PASSWORD)" ]; then \
		echo "$(RED)错误: 请设置ALIYUN_REGISTRY_USERNAME和ALIYUN_REGISTRY_PASSWORD环境变量$(NC)"; \
		exit 1; \
	fi
	echo "$(ALIYUN_REGISTRY_PASSWORD)" | docker login $(DOCKER_REGISTRY) --username "$(ALIYUN_REGISTRY_USERNAME)" --password-stdin
	docker buildx build \
		--platform $(DOCKER_PLATFORMS) \
		--file deploy/docker/Dockerfile \
		--tag $(DOCKER_IMAGE):$(VERSION) \
		--tag $(DOCKER_IMAGE):latest \
		--tag $(DOCKER_IMAGE):$(COMMIT_SHA) \
		--build-arg BUILDTIME=$(BUILD_TIME) \
		--build-arg VERSION=$(VERSION) \
		--build-arg REVISION=$(COMMIT_SHA) \
		--push \
		.
	@echo "$(GREEN)Docker镜像推送完成$(NC)"

docker-run: ## 运行Docker容器
	@echo "$(BLUE)运行Docker容器...$(NC)"
	docker run -d \
		--name $(PROJECT_NAME) \
		-p 50051:50051 \
		-e ACCESSIBILITY_CONFIG_PATH=/app/config/config.yaml \
		$(DOCKER_IMAGE):latest
	@echo "$(GREEN)Docker容器启动完成$(NC)"

docker-stop: ## 停止Docker容器
	@echo "$(BLUE)停止Docker容器...$(NC)"
	docker stop $(PROJECT_NAME) || true
	docker rm $(PROJECT_NAME) || true
	@echo "$(GREEN)Docker容器已停止$(NC)"

deploy-aliyun: ## 部署到阿里云
	@echo "$(BLUE)开始部署到阿里云...$(NC)"
	@chmod +x scripts/deploy-production.sh
	@./scripts/deploy-production.sh
	@echo "$(GREEN)部署到阿里云完成$(NC)"

push-github: ## 推送代码到GitHub
	@echo "$(BLUE)推送代码到GitHub...$(NC)"
	git add .
	git commit -m "feat: update accessibility-service - $(BUILD_TIME)" || true
	git push origin main
	@echo "$(GREEN)代码推送完成$(NC)"

clean: ## 清理临时文件
	@echo "$(BLUE)清理临时文件...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/
	rm -f bandit-results.json safety-results.json
	docker system prune -f || true
	@echo "$(GREEN)清理完成$(NC)"

status: ## 显示项目状态
	@echo "$(BLUE)项目状态$(NC)"
	@echo "$(BLUE)========$(NC)"
	@echo "项目名称: $(PROJECT_NAME)"
	@echo "版本: $(VERSION)"
	@echo "提交SHA: $(COMMIT_SHA)"
	@echo "构建时间: $(BUILD_TIME)"
	@echo "Docker镜像: $(DOCKER_IMAGE)"
	@echo "支持平台: $(DOCKER_PLATFORMS)"
	@echo ""

# 组合命令
ci: lint format-check type-check test security-check ## 运行CI检查
	@echo "$(GREEN)CI检查全部通过$(NC)"

pre-commit: format lint type-check test ## 提交前检查
	@echo "$(GREEN)提交前检查完成$(NC)"

release: clean test docker-build-multi docker-push ## 发布版本
	@echo "$(GREEN)版本发布完成$(NC)"

dev-setup: install-dev ## 开发环境设置
	@echo "$(GREEN)开发环境设置完成$(NC)"

# 环境变量检查
check-env:
	@echo "$(BLUE)检查环境变量...$(NC)"
	@if [ -z "$(ALIYUN_REGISTRY_USERNAME)" ]; then \
		echo "$(YELLOW)警告: ALIYUN_REGISTRY_USERNAME未设置$(NC)"; \
	fi
	@if [ -z "$(ALIYUN_REGISTRY_PASSWORD)" ]; then \
		echo "$(YELLOW)警告: ALIYUN_REGISTRY_PASSWORD未设置$(NC)"; \
	fi 