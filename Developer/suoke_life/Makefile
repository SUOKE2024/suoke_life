.PHONY: build push deploy logs clean help test test-unit test-integration run create-cicd run-ci-cd run-tests deploy-rag rag-status

# 构建所有微服务的 Docker 镜像
build:
	@echo "构建所有微服务 Docker 镜像..."
	docker-compose build

# 推送所有微服务的 Docker 镜像到仓库
push:
	@echo "将所有微服务 Docker 镜像推送到仓库..."
	docker-compose push

# 使用 Helm 部署微服务
deploy:
	@echo "使用 Helm 部署微服务..."
	helm upgrade --install suoke-microservices microservices/helm --namespace default

# 查看 docker-compose 日志
logs:
	@echo "显示 docker-compose 日志..."
	docker-compose logs -f

# 清理所有容器、镜像和数据卷
clean:
	@echo "清理无用的 Docker 容器、镜像和数据卷..."
	docker-compose down --rmi all --volumes

# 显示可用命令帮助
help:
	@echo "可用命令:"
	@echo "  make build            - 构建所有 Docker 镜像"
	@echo "  make push             - 推送所有镜像到仓库"
	@echo "  make deploy           - 使用 Helm 部署微服务"
	@echo "  make logs             - 查看日志"
	@echo "  make clean            - 清理所有容器和镜像"
	@echo "  make test             - 执行所有测试"
	@echo "  make test-unit        - 执行单元测试"
	@echo "  make test-integration - 执行集成测试"
	@echo "  make run              - 运行服务"
	@echo "  make create-cicd      - 创建CI/CD工作流配置"
	@echo "  make run-ci-cd        - 运行CI/CD流程"
	@echo "  make run-tests        - 运行所有测试套件"
	@echo "  make deploy-rag       - 部署RAG服务到生产环境"
	@echo "  make rag-status       - 查看RAG服务状态"

# 构建目标平台二进制
build-go:
	go build -o bin/agent-coordinator-service ./cmd/server

# 执行所有测试
test: test-unit test-integration

# 执行单元测试
test-unit:
	go test -v ./internal/...

# 执行集成测试
test-integration:
	go test -v ./internal/tests/integration/...

# 运行服务
run:
	go run ./cmd/server/main.go

# 清理构建文件
clean-go:
	rm -rf bin/

# 创建CI/CD工作流配置
create-cicd:
	@echo "为哪个服务创建CI/CD工作流？"
	@read -p "服务路径（例如：rag-service）: " SERVICE_PATH; \
	read -p "部署名称 [default: $$SERVICE_PATH]: " DEPLOYMENT_NAME; \
	DEPLOYMENT_NAME=$${DEPLOYMENT_NAME:-$$SERVICE_PATH}; \
	read -p "是否添加TCM特征测试？(y/n) [default: n]: " ADD_TCM; \
	ADD_TCM=$${ADD_TCM:-n}; \
	if [ "$$ADD_TCM" = "y" ] || [ "$$ADD_TCM" = "Y" ]; then \
		ADD_TCM_FLAG="true"; \
	else \
		ADD_TCM_FLAG="false"; \
	fi; \
	./scripts/create_cicd_workflow.sh $$SERVICE_PATH $$DEPLOYMENT_NAME $$ADD_TCM_FLAG

# 运行CI/CD流程
run-ci-cd:
	@echo "运行哪个服务的CI/CD流程？"
	@read -p "服务工作流名称（例如：rag-service-ci-cd）: " WORKFLOW_NAME; \
	read -p "分支名称 [default: develop]: " BRANCH; \
	BRANCH=$${BRANCH:-develop}; \
	read -p "环境 [default: dev]: " ENVIRONMENT; \
	ENVIRONMENT=$${ENVIRONMENT:-dev}; \
	read -p "版本标签 [default: auto]: " VERSION; \
	VERSION=$${VERSION:-auto}; \
	read -p "是否跳过测试？(y/n) [default: n]: " SKIP_TESTS; \
	SKIP_TESTS=$${SKIP_TESTS:-n}; \
	if [ "$$SKIP_TESTS" = "y" ] || [ "$$SKIP_TESTS" = "Y" ]; then \
		SKIP_TESTS_FLAG="true"; \
	else \
		SKIP_TESTS_FLAG="false"; \
	fi; \
	gh workflow run $$WORKFLOW_NAME --ref $$BRANCH --field environment=$$ENVIRONMENT --field version=$$VERSION --field skip_tests=$$SKIP_TESTS_FLAG

# 运行全部测试套件
run-tests:
	@mkdir -p test-results
	@echo "运行哪个服务的测试？"
	@read -p "服务路径（例如：rag-service）: " SERVICE_PATH; \
	read -p "测试模式 (kg|multimodal|multi_source|adaptive|tcm|all) [default: all]: " TEST_MODE; \
	TEST_MODE=$${TEST_MODE:-all}; \
	read -p "是否使用模拟模式？(y/n) [default: y]: " MOCK; \
	MOCK=$${MOCK:-y}; \
	if [ "$$MOCK" = "y" ] || [ "$$MOCK" = "Y" ]; then \
		MOCK_FLAG="--mock"; \
	else \
		MOCK_FLAG=""; \
	fi; \
	read -p "是否启用详细输出？(y/n) [default: y]: " VERBOSE; \
	VERBOSE=$${VERBOSE:-y}; \
	if [ "$$VERBOSE" = "y" ] || [ "$$VERBOSE" = "Y" ]; then \
		VERBOSE_FLAG="--verbose"; \
	else \
		VERBOSE_FLAG=""; \
	fi; \
	echo "运行 $$SERVICE_PATH 服务的 $$TEST_MODE 测试..."; \
	cd services/$$SERVICE_PATH/tests && ./run_tests.sh --mode $$TEST_MODE $$MOCK_FLAG $$VERBOSE_FLAG --clean 

# 部署RAG服务到生产环境
deploy-rag:
	@echo "部署RAG服务到生产环境..."
	./scripts/deploy_rag_service.sh --env prod 

# 查看RAG服务状态
rag-status:
	@echo "查看RAG服务状态..."
	./scripts/check_rag_status.sh --env prod 