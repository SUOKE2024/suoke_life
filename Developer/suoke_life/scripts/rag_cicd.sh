#!/bin/bash

# 索克生活RAG服务CI/CD工作流设置脚本
# 支持macOS和Linux

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

SERVICE_PATH="rag-service"
WORKFLOW_NAME="${SERVICE_PATH}-ci-cd"
SERVICE_NAME="RAG Service"

echo -e "${BLUE}开始为 ${YELLOW}$SERVICE_NAME${BLUE} 设置CI/CD工作流...${NC}"

# 创建目录结构
mkdir -p /Users/songxu/Developer/suoke_life/.github/workflows
mkdir -p /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/tests
mkdir -p /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/scripts

# 创建CI/CD工作流文件
cat > /Users/songxu/Developer/suoke_life/.github/workflows/$WORKFLOW_NAME.yml << 'EOL'
name: RAG Service CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'services/rag-service/**'
      - '.github/workflows/rag-service-ci-cd.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'services/rag-service/**'
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
  IMAGE_NAME: suoke/rag-service
  SERVICE_DIR: services/rag-service

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
      
      - name: 运行TCM特征测试
        run: |
          cd ${{ env.SERVICE_DIR }}
          go run ./tests/test_multimodal.go -i ./tests/samples/tongue.jpg -q "舌红苔白" -v
      
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
          kubectl rollout status deployment/rag-service -n ${{ env.NAMESPACE }} --timeout=300s
      
      - name: 部署后测试验证
        run: |
          # 等待服务可用
          echo "等待服务完全启动..."
          sleep 30
          
          # 获取服务URL
          SERVICE_URL=$(kubectl get svc rag-service -n ${{ env.NAMESPACE }} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
          
          # 执行健康检查
          curl -s -f "http://$SERVICE_URL:8080/health" || exit 1
          
          echo "部署验证成功！服务已可用于: http://$SERVICE_URL:8080"
EOL

# 创建运行集成测试的脚本
cat > /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/scripts/run_integrated_tests.sh << 'EOL'
#!/bin/bash

# RAG服务集成测试运行脚本
set -e

echo "开始运行RAG服务集成测试..."

# 创建测试结果目录
mkdir -p ../tests/test_results

# 运行基本功能测试
echo "运行基本功能测试..."
go test -v ../internal/handlers/search_test.go

# 运行性能测试
echo "运行性能测试..."
go test -v ../internal/rag/performance_test.go -bench=.

# 运行多模态功能测试
echo "运行多模态功能测试..."
go run ../tests/test_multimodal.go -i ../tests/samples/tongue.jpg -q "舌红苔白" -v

echo "集成测试完成！"
EOL

# 设置脚本权限
chmod +x /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/scripts/run_integrated_tests.sh

# 创建测试样本目录
mkdir -p /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/tests/samples
mkdir -p /Users/songxu/Developer/suoke_life/services/$SERVICE_PATH/tests/test_results

echo -e "${GREEN}CI/CD工作流设置完成！${NC}"
echo -e "已创建以下文件:"
echo -e "- ${YELLOW}.github/workflows/$WORKFLOW_NAME.yml${NC}"
echo -e "- ${YELLOW}services/$SERVICE_PATH/scripts/run_integrated_tests.sh${NC}"
echo -e "\n使用以下命令将测试样本添加到项目中:"
echo -e "${BLUE}cp /path/to/tongue.jpg services/$SERVICE_PATH/tests/samples/${NC}"
echo -e "\n要触发GitHub Actions工作流，请提交并推送更改。" 