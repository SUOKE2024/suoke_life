#!/bin/bash

# 索克生活服务CI/CD工作流生成脚本
# 用法: ./create_cicd_workflow.sh <服务路径> [部署名称] [是否添加TCM测试]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 获取参数
SERVICE_PATH="$1"
DEPLOYMENT_NAME="${2:-$1}"
ADD_TCM_TESTS="${3:-false}"

# 显示帮助信息
show_help() {
  echo "索克生活服务CI/CD工作流生成脚本"
  echo "用法: $0 <服务路径> [部署名称] [是否添加TCM测试]"
  echo ""
  echo "参数:"
  echo "  <服务路径>        必填，服务路径，例如: rag-service"
  echo "  [部署名称]        可选，Kubernetes部署名称，默认与服务路径相同"
  echo "  [是否添加TCM测试]  可选，是否添加TCM特征测试步骤，可选值: true/false，默认为false"
  echo ""
  echo "示例:"
  echo "  $0 rag-service"
  echo "  $0 auth-service auth-server"
  echo "  $0 rag-service rag-service true"
  echo ""
}

# 验证参数
if [ -z "$SERVICE_PATH" ]; then
  echo -e "${RED}错误: 服务路径为必填参数${NC}"
  show_help
  exit 1
fi

# 检查服务目录是否存在
if [ ! -d "services/$SERVICE_PATH" ]; then
  echo -e "${RED}错误: 服务目录 services/$SERVICE_PATH 不存在${NC}"
  exit 1
fi

# 生成CI/CD工作流名称
WORKFLOW_NAME="${SERVICE_PATH}-ci-cd"

# 首字母大写服务名称（兼容sh/bash）
FIRST_CHAR=$(echo "$SERVICE_PATH" | cut -c1 | tr '[:lower:]' '[:upper:]')
REST_CHARS=$(echo "$SERVICE_PATH" | cut -c2-)
SERVICE_NAME="$FIRST_CHAR$REST_CHARS"
SERVICE_NAME="${SERVICE_NAME//-/ }"

echo -e "${BLUE}开始为 ${YELLOW}$SERVICE_NAME${BLUE} 生成CI/CD工作流配置...${NC}"

# 创建GitHub Actions工作流目录
mkdir -p .github/workflows/templates

# 如果模板文件不存在，复制模板
if [ ! -f ".github/workflows/templates/service-ci-cd-template.yml" ]; then
  echo -e "${YELLOW}警告: 未找到模板文件，将使用默认模板${NC}"
  cat > .github/workflows/templates/service-ci-cd-template.yml << 'EOL'
name: SERVICE_NAME CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'services/SERVICE_PATH/**'
      - '.github/workflows/SERVICE_WORKFLOW_NAME.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'services/SERVICE_PATH/**'
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod
      version:
        description: '版本标签 (默认为auto)'
        required: false
        default: 'auto'
      skip_tests:
        description: '跳过测试'
        required: false
        default: false
        type: boolean

env:
  REGISTRY: registry.cn-hangzhou.aliyuncs.com
  IMAGE_NAME: suoke/SERVICE_PATH
  SERVICE_DIR: services/SERVICE_PATH

jobs:
  test:
    name: 测试
    runs-on: ubuntu-latest
    if: ${{ !inputs.skip_tests }}
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v3
      
      - name: 设置Go环境
        uses: actions/setup-go@v4
        with:
          go-version: '1.19'

      - name: 安装依赖
        run: |
          cd ${{ env.SERVICE_DIR }}
          go mod download
      
      - name: 静态代码分析
        run: |
          cd ${{ env.SERVICE_DIR }}
          go vet ./...
      
      - name: 运行单元测试
        run: |
          cd ${{ env.SERVICE_DIR }}
          go test -v ./internal/...
      
      - name: 运行集成测试
        run: |
          cd ${{ env.SERVICE_DIR }}
          ./scripts/run_integrated_tests.sh
      
      # 可根据服务特性添加或移除特定测试步骤
      
      - name: 保存测试结果
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: ${{ env.SERVICE_DIR }}/tests/test_results
          retention-days: 5
  
  build:
    name: 构建镜像
    runs-on: ubuntu-latest
    needs: test
    if: ${{ github.event_name == 'push' || github.event_name == 'workflow_dispatch' }}
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v3
      
      - name: 设置版本号
        id: version
        run: |
          if [ "${{ inputs.version }}" = "auto" ] || [ "${{ inputs.version }}" = "" ]; then
            VERSION="$(date +'%Y%m%d%H%M%S')-$(echo ${{ github.sha }} | cut -c1-7)"
          else
            VERSION="${{ inputs.version }}"
          fi
          echo "VERSION=$VERSION" >> $GITHUB_ENV
          echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
      
      - name: 登录到阿里云容器镜像服务
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ALIYUN_REGISTRY_USERNAME }}
          password: ${{ secrets.ALIYUN_REGISTRY_PASSWORD }}
      
      - name: 设置 Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: 构建并推送镜像
        uses: docker/build-push-action@v4
        with:
          context: ./${{ env.SERVICE_DIR }}
          file: ./${{ env.SERVICE_DIR }}/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.VERSION }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          build-args: |
            BUILD_VERSION=${{ env.VERSION }}
            BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
            COMMIT_SHA=${{ github.sha }}
      
      - name: 输出镜像信息
        run: |
          echo "镜像已构建并推送: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.VERSION }}"

  deploy:
    name: 部署
    runs-on: ubuntu-latest
    needs: build
    if: ${{ github.event_name == 'push' || github.event_name == 'workflow_dispatch' }}
    
    environment:
      name: ${{ inputs.environment || 'dev' }}
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v3
      
      - name: 设置 Kubernetes 环境
        uses: azure/k8s-set-context@v1
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      
      - name: 设置环境变量
        run: |
          if [ "${{ inputs.version }}" = "auto" ] || [ "${{ inputs.version }}" = "" ]; then
            VERSION="$(date +'%Y%m%d%H%M%S')-$(echo ${{ github.sha }} | cut -c1-7)"
          else
            VERSION="${{ inputs.version }}"
          fi
          echo "VERSION=$VERSION" >> $GITHUB_ENV
          
          DEPLOY_ENV="${{ inputs.environment }}"
          if [ -z "$DEPLOY_ENV" ]; then
            DEPLOY_ENV="dev"
          fi
          echo "DEPLOY_ENV=$DEPLOY_ENV" >> $GITHUB_ENV
          
          echo "NAMESPACE=suoke-$DEPLOY_ENV" >> $GITHUB_ENV
      
      - name: 检查并创建命名空间
        run: |
          kubectl get namespace ${{ env.NAMESPACE }} || kubectl create namespace ${{ env.NAMESPACE }}
      
      - name: 更新配置中的镜像版本
        run: |
          sed -i "s|image:.*${{ env.IMAGE_NAME }}:.*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.VERSION }}|g" ${{ env.SERVICE_DIR }}/k8s/overlays/${{ env.DEPLOY_ENV }}/deployment.yaml
      
      - name: 部署到 Kubernetes
        run: |
          kubectl apply -k ${{ env.SERVICE_DIR }}/k8s/overlays/${{ env.DEPLOY_ENV }}
      
      - name: 等待部署完成
        run: |
          kubectl rollout status deployment/SERVICE_DEPLOYMENT_NAME -n ${{ env.NAMESPACE }} --timeout=300s
      
      - name: 验证部署
        id: verify
        run: |
          ./scripts/verify_deployment.py SERVICE_PATH ${{ env.NAMESPACE }} 300
      
      - name: 发送部署通知
        if: always()
        run: |
          if [ "${{ steps.verify.outcome }}" == "success" ]; then
            echo "SERVICE_NAME已成功部署到 ${{ env.DEPLOY_ENV }} 环境"
            STATUS="✅ 成功"
          else
            echo "SERVICE_NAME部署失败"
            STATUS="❌ 失败"
          fi
          
          curl -X POST ${{ secrets.WEBHOOK_URL }} \
            -H "Content-Type: application/json" \
            -d '{
              "msgtype": "markdown",
              "markdown": {
                "title": "SERVICE_NAME部署状态",
                "text": "### SERVICE_NAME部署状态\n**环境**: ${{ env.DEPLOY_ENV }}\n**版本**: ${{ env.VERSION }}\n**状态**: '"$STATUS"'\n**时间**: '"$(date '+%Y-%m-%d %H:%M:%S')"'\n**执行人**: ${{ github.actor }}\n[查看详情](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})"
              }
            }'
EOL
fi

# 复制模板并替换变量
echo -e "${GREEN}正在生成工作流文件: .github/workflows/$WORKFLOW_NAME.yml${NC}"
cp .github/workflows/templates/service-ci-cd-template.yml .github/workflows/$WORKFLOW_NAME.yml

# 替换变量（兼容macOS和Linux）
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  sed -i '' "s/SERVICE_NAME/$SERVICE_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i '' "s/SERVICE_PATH/$SERVICE_PATH/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i '' "s/SERVICE_WORKFLOW_NAME/$WORKFLOW_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i '' "s/SERVICE_DEPLOYMENT_NAME/$DEPLOYMENT_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
else
  # Linux
  sed -i "s/SERVICE_NAME/$SERVICE_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i "s/SERVICE_PATH/$SERVICE_PATH/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i "s/SERVICE_WORKFLOW_NAME/$WORKFLOW_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
  sed -i "s/SERVICE_DEPLOYMENT_NAME/$DEPLOYMENT_NAME/g" .github/workflows/$WORKFLOW_NAME.yml
fi

# 如果需要，添加TCM特征测试步骤
if [ "$ADD_TCM_TESTS" = "true" ]; then
  echo -e "${GREEN}添加TCM特征测试步骤...${NC}"
  
  # 准备要添加的TCM测试代码
  TCM_TEST_STEPS='      - name: 准备测试环境
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          mkdir -p test_data/images test_data/audio
          touch test_data/images/tongue_sample.jpg test_data/images/face_sample.jpg
          touch test_data/audio/pulse_sample.mp3 test_data/audio/voice_sample.mp3
          chmod +x run_tests.sh
      
      - name: 运行知识图谱测试
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          ./run_tests.sh --mode kg --mock --clean
      
      - name: 运行多模态测试
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          ./run_tests.sh --mode multimodal --mock --clean
      
      - name: 运行多源检索测试
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          ./run_tests.sh --mode multi_source --mock --clean
      
      - name: 运行自适应学习测试
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          ./run_tests.sh --mode adaptive --mock --clean
          
      - name: 运行TCM特征分析测试
        run: |
          cd ${{ env.SERVICE_DIR }}/tests
          ./run_tests.sh --mode tcm --mock --clean'
  
  # 将TCM测试步骤添加到工作流文件
  sed -i "s/# 可根据服务特性添加或移除特定测试步骤/$TCM_TEST_STEPS/g" .github/workflows/$WORKFLOW_NAME.yml
fi

echo -e "${GREEN}CI/CD工作流配置已生成:${NC} .github/workflows/$WORKFLOW_NAME.yml"
echo ""
echo -e "${BLUE}您可以通过以下命令手动触发工作流:${NC}"
echo -e "gh workflow run $WORKFLOW_NAME --ref develop --field environment=dev"
echo ""
echo -e "${YELLOW}注意:${NC} 请确保服务的Kubernetes配置目录结构符合要求:"
echo -e "services/$SERVICE_PATH/k8s/overlays/{dev,staging,prod}/deployment.yaml"
echo ""

# 检查Kubernetes配置是否存在
K8S_CONFIG_DIR="services/$SERVICE_PATH/k8s"
if [ ! -d "$K8S_CONFIG_DIR" ]; then
  echo -e "${YELLOW}警告:${NC} 未找到 $K8S_CONFIG_DIR 目录，请确保创建必要的Kubernetes配置"
  echo -e "建议的目录结构:"
  echo -e "services/$SERVICE_PATH/k8s/"
  echo -e "├── base/"
  echo -e "│   ├── deployment.yaml"
  echo -e "│   ├── service.yaml"
  echo -e "│   ├── ingress.yaml"
  echo -e "│   └── kustomization.yaml"
  echo -e "└── overlays/"
  echo -e "    ├── dev/"
  echo -e "    │   ├── deployment.yaml"
  echo -e "    │   └── kustomization.yaml"
  echo -e "    ├── staging/"
  echo -e "    │   ├── deployment.yaml"
  echo -e "    │   └── kustomization.yaml"
  echo -e "    └── prod/"
  echo -e "        ├── deployment.yaml"
  echo -e "        └── kustomization.yaml"
fi

# 检查环境配置是否存在
for env in "dev" "staging" "prod"; do
  ENV_CONFIG_DIR="services/$SERVICE_PATH/k8s/overlays/$env"
  if [ ! -d "$ENV_CONFIG_DIR" ]; then
    echo -e "${YELLOW}警告:${NC} 未找到 $ENV_CONFIG_DIR 目录，请创建此环境的Kubernetes配置"
  elif [ ! -f "$ENV_CONFIG_DIR/deployment.yaml" ]; then
    echo -e "${YELLOW}警告:${NC} 未找到 $ENV_CONFIG_DIR/deployment.yaml 文件，部署可能会失败"
  fi
done

echo -e "${GREEN}操作完成!${NC}" 