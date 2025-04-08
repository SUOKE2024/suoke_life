#!/bin/bash
# 索克生活微服务部署验证脚本
# 用法: ./scripts/validate_deployment.sh <服务名称>
# 例如: ./scripts/validate_deployment.sh rag-service

set -e  # 任何命令失败则立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 打印带颜色的标题
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# 打印成功消息
print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

# 打印错误消息
print_error() {
  echo -e "${RED}❌ $1${NC}"
}

# 打印警告消息
print_warning() {
  echo -e "${YELLOW}⚠️ $1${NC}"
}

# 检查参数
if [ "$#" -lt 1 ]; then
  print_error "用法: $0 <服务名称> [--fix]
  可用服务: rag-service, auth-service, user-service, api-gateway, knowledge-graph-service 等
  例如: $0 rag-service --fix"
  exit 1
fi

SERVICE_NAME=$1
FIX_ISSUES=${2:-""}
SERVICE_PATH="services/$SERVICE_NAME"
ERRORS_FOUND=0
WARNINGS_FOUND=0

# 验证服务是否存在
if [ ! -d "$SERVICE_PATH" ]; then
  print_error "服务不存在: $SERVICE_NAME"
  exit 1
fi

print_header "正在验证 $SERVICE_NAME 服务部署配置"

# 检查Dockerfile是否存在
if [ -f "$SERVICE_PATH/Dockerfile" ]; then
  print_success "Dockerfile存在"
  
  # 检查Dockerfile内容
  if grep -q "HEALTHCHECK" "$SERVICE_PATH/Dockerfile"; then
    print_success "Dockerfile包含健康检查"
  else
    print_warning "Dockerfile不包含健康检查配置，这可能导致K8s无法准确判断服务健康状态"
    WARNINGS_FOUND=$((WARNINGS_FOUND+1))
    
    # 尝试修复
    if [ "$FIX_ISSUES" = "--fix" ]; then
      echo "尝试添加健康检查配置..."
      
      # 推断服务端口
      PORT=$(grep -o "EXPOSE [0-9]*" "$SERVICE_PATH/Dockerfile" | awk '{print $2}')
      if [ -z "$PORT" ]; then
        PORT=3000
        echo "未找到EXPOSE端口，使用默认端口3000"
      fi
      
      # 添加健康检查
      sed -i.bak '/EXPOSE/a\
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 CMD wget --no-verbose --tries=1 --spider http://localhost:'$PORT'/health || exit 1' "$SERVICE_PATH/Dockerfile"
      print_success "已添加健康检查配置"
    fi
  fi
  
  # 检查基础镜像
  BASE_IMAGE=$(grep -o "FROM .*" "$SERVICE_PATH/Dockerfile" | head -1)
  if [[ $BASE_IMAGE == *"latest"* ]]; then
    print_warning "Dockerfile使用latest标签的基础镜像，这可能导致不可预期的构建结果"
    WARNINGS_FOUND=$((WARNINGS_FOUND+1))
    
    # 尝试修复
    if [ "$FIX_ISSUES" = "--fix" ]; then
      echo "尝试替换latest标签..."
      if [[ $BASE_IMAGE == *"node:latest"* ]]; then
        sed -i.bak 's/node:latest/node:18-alpine/' "$SERVICE_PATH/Dockerfile"
        print_success "已将node:latest替换为node:18-alpine"
      fi
    fi
  else
    print_success "Dockerfile使用了固定版本的基础镜像"
  fi
else
  print_error "Dockerfile不存在，这将阻止服务部署"
  ERRORS_FOUND=$((ERRORS_FOUND+1))
  
  # 尝试修复
  if [ "$FIX_ISSUES" = "--fix" ]; then
    echo "尝试创建基本的Dockerfile..."
    
    cat > "$SERVICE_PATH/Dockerfile" <<EOL
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "src/index.js"]
EOL
    print_success "已创建基本的Dockerfile"
  fi
fi

# 检查k8s配置目录
if [ -d "$SERVICE_PATH/k8s" ]; then
  print_success "K8s配置目录存在"
  
  # 检查基础配置文件
  K8S_FILES_COUNT=$(find "$SERVICE_PATH/k8s" -name "*.yaml" -o -name "*.yml" | wc -l)
  if [ "$K8S_FILES_COUNT" -gt 0 ]; then
    print_success "K8s配置文件存在 ($K8S_FILES_COUNT 个文件)"
    
    # 检查deployment.yaml
    if [ -f "$SERVICE_PATH/k8s/deployment.yaml" ] || [ -f "$SERVICE_PATH/k8s/base/deployment.yaml" ]; then
      print_success "Deployment配置文件存在"
      
      # 检查deployment.yaml中的就绪探针和存活探针
      DEPLOYMENT_FILE=""
      if [ -f "$SERVICE_PATH/k8s/deployment.yaml" ]; then
        DEPLOYMENT_FILE="$SERVICE_PATH/k8s/deployment.yaml"
      else
        DEPLOYMENT_FILE="$SERVICE_PATH/k8s/base/deployment.yaml"
      fi
      
      if grep -q "livenessProbe\|readinessProbe" "$DEPLOYMENT_FILE"; then
        print_success "Deployment配置中包含健康检查探针"
      else
        print_warning "Deployment配置中不包含健康检查探针，这可能导致不可靠的服务发现和故障转移"
        WARNINGS_FOUND=$((WARNINGS_FOUND+1))
        
        # 尝试修复
        if [ "$FIX_ISSUES" = "--fix" ]; then
          echo "尝试添加健康检查探针..."
          
          # 推断容器端口
          PORT=$(grep -o "containerPort: [0-9]*" "$DEPLOYMENT_FILE" | awk '{print $2}')
          if [ -z "$PORT" ]; then
            PORT=3000
            echo "未找到containerPort，使用默认端口3000"
          fi
          
          # 搜索容器定义的结束位置并添加探针
          sed -i.bak '/containers:/,/name:/{/name:/!b;/name:/s/.*/& \
          livenessProbe:\
            httpGet:\
              path: \/health\
              port: '$PORT'\
            initialDelaySeconds: 30\
            periodSeconds: 10\
          readinessProbe:\
            httpGet:\
              path: \/health\
              port: '$PORT'\
            initialDelaySeconds: 5\
            periodSeconds: 5\
          &/}' "$DEPLOYMENT_FILE"
          print_success "已添加健康检查探针"
        fi
      fi
      
      # 检查资源限制
      if grep -q "resources:" "$DEPLOYMENT_FILE"; then
        print_success "Deployment配置中包含资源限制"
      else
        print_warning "Deployment配置中不包含资源限制，这可能导致资源调度不合理"
        WARNINGS_FOUND=$((WARNINGS_FOUND+1))
        
        # 尝试修复
        if [ "$FIX_ISSUES" = "--fix" ]; then
          echo "尝试添加资源限制..."
          sed -i.bak '/containers:/,/name:/{/name:/!b;/name:/s/.*/& \
          resources:\
            requests:\
              cpu: 100m\
              memory: 256Mi\
            limits:\
              cpu: 300m\
              memory: 512Mi\
          &/}' "$DEPLOYMENT_FILE"
          print_success "已添加资源限制"
        fi
      fi
    else
      print_warning "Deployment配置文件不存在"
      WARNINGS_FOUND=$((WARNINGS_FOUND+1))
      
      # 尝试修复
      if [ "$FIX_ISSUES" = "--fix" ]; then
        echo "尝试创建基本的deployment.yaml..."
        mkdir -p "$SERVICE_PATH/k8s"
        
        cat > "$SERVICE_PATH/k8s/deployment.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $SERVICE_NAME
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
    spec:
      containers:
      - name: $SERVICE_NAME
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/$SERVICE_NAME:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 300m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
EOL
        print_success "已创建基本的deployment.yaml"
      fi
    fi
    
    # 检查service.yaml
    if [ -f "$SERVICE_PATH/k8s/service.yaml" ] || [ -f "$SERVICE_PATH/k8s/base/service.yaml" ]; then
      print_success "Service配置文件存在"
    else
      print_warning "Service配置文件不存在"
      WARNINGS_FOUND=$((WARNINGS_FOUND+1))
      
      # 尝试修复
      if [ "$FIX_ISSUES" = "--fix" ]; then
        echo "尝试创建基本的service.yaml..."
        mkdir -p "$SERVICE_PATH/k8s"
        
        cat > "$SERVICE_PATH/k8s/service.yaml" <<EOL
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME
spec:
  selector:
    app: $SERVICE_NAME
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
EOL
        print_success "已创建基本的service.yaml"
      fi
    fi
    
    # 检查kustomization.yaml
    if [ -f "$SERVICE_PATH/k8s/kustomization.yaml" ] || [ -f "$SERVICE_PATH/k8s/base/kustomization.yaml" ]; then
      print_success "Kustomization配置文件存在"
    else
      print_warning "Kustomization配置文件不存在，这将使K8s部署更复杂"
      WARNINGS_FOUND=$((WARNINGS_FOUND+1))
      
      # 尝试修复
      if [ "$FIX_ISSUES" = "--fix" ]; then
        echo "尝试创建基本的kustomization.yaml..."
        
        # 检查K8s目录结构
        if [ -d "$SERVICE_PATH/k8s/base" ]; then
          KUSTOMIZE_DIR="$SERVICE_PATH/k8s/base"
        else
          KUSTOMIZE_DIR="$SERVICE_PATH/k8s"
        fi
        
        cat > "$KUSTOMIZE_DIR/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: suoke
resources:
- deployment.yaml
- service.yaml
EOL
        print_success "已创建基本的kustomization.yaml"
        
        # 如果没有overlays目录，创建
        if [ ! -d "$SERVICE_PATH/k8s/overlays" ]; then
          echo "创建环境特定配置目录..."
          mkdir -p "$SERVICE_PATH/k8s/overlays/dev"
          mkdir -p "$SERVICE_PATH/k8s/overlays/staging"
          mkdir -p "$SERVICE_PATH/k8s/overlays/prod"
          
          # 创建dev环境配置
          cat > "$SERVICE_PATH/k8s/overlays/dev/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: suoke-dev
commonLabels:
  environment: development
  app: $SERVICE_NAME
resources:
- ../../base
patchesStrategicMerge:
- resources-patch.yaml
images:
- name: $SERVICE_NAME
  newName: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/$SERVICE_NAME
  newTag: latest
EOL
          
          cat > "$SERVICE_PATH/k8s/overlays/dev/resources-patch.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: $SERVICE_NAME
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 300m
            memory: 512Mi
EOL
          
          # 创建staging环境配置
          cat > "$SERVICE_PATH/k8s/overlays/staging/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: suoke-staging
commonLabels:
  environment: staging
  app: $SERVICE_NAME
resources:
- ../../base
patchesStrategicMerge:
- resources-patch.yaml
images:
- name: $SERVICE_NAME
  newName: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/$SERVICE_NAME
  newTag: latest
EOL
          
          cat > "$SERVICE_PATH/k8s/overlays/staging/resources-patch.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: $SERVICE_NAME
        resources:
          requests:
            cpu: 150m
            memory: 384Mi
          limits:
            cpu: 400m
            memory: 768Mi
EOL
          
          # 创建prod环境配置
          cat > "$SERVICE_PATH/k8s/overlays/prod/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: suoke-prod
commonLabels:
  environment: production
  app: $SERVICE_NAME
resources:
- ../../base
patchesStrategicMerge:
- resources-patch.yaml
images:
- name: $SERVICE_NAME
  newName: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/$SERVICE_NAME
  newTag: latest
EOL
          
          cat > "$SERVICE_PATH/k8s/overlays/prod/resources-patch.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: $SERVICE_NAME
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
EOL
          print_success "已创建环境特定配置"
        fi
      fi
    fi
  else
    print_warning "K8s配置目录为空"
    WARNINGS_FOUND=$((WARNINGS_FOUND+1))
  fi
else
  print_warning "K8s配置目录不存在，这将阻止自动化部署"
  WARNINGS_FOUND=$((WARNINGS_FOUND+1))
  
  # 尝试修复
  if [ "$FIX_ISSUES" = "--fix" ]; then
    echo "尝试创建基本的K8s配置目录结构..."
    mkdir -p "$SERVICE_PATH/k8s/base"
    mkdir -p "$SERVICE_PATH/k8s/overlays/dev"
    mkdir -p "$SERVICE_PATH/k8s/overlays/staging"
    mkdir -p "$SERVICE_PATH/k8s/overlays/prod"
    
    # 创建基本配置文件
    cat > "$SERVICE_PATH/k8s/base/deployment.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $SERVICE_NAME
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
    spec:
      containers:
      - name: $SERVICE_NAME
        image: $SERVICE_NAME:latest
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
EOL
    
    cat > "$SERVICE_PATH/k8s/base/service.yaml" <<EOL
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME
spec:
  selector:
    app: $SERVICE_NAME
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
EOL
    
    cat > "$SERVICE_PATH/k8s/base/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: suoke
resources:
- deployment.yaml
- service.yaml
EOL
    
    # 创建环境特定配置
    for env in dev staging prod; do
      replicas=1
      cpu_req="100m"
      mem_req="256Mi"
      cpu_lim="300m"
      mem_lim="512Mi"
      namespace="suoke-$env"
      
      if [ "$env" = "staging" ]; then
        replicas=2
        cpu_req="150m"
        mem_req="384Mi"
        cpu_lim="400m"
        mem_lim="768Mi"
      elif [ "$env" = "prod" ]; then
        replicas=3
        cpu_req="200m"
        mem_req="512Mi"
        cpu_lim="500m"
        mem_lim="1Gi"
      fi
      
      cat > "$SERVICE_PATH/k8s/overlays/$env/kustomization.yaml" <<EOL
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: $namespace
commonLabels:
  environment: $([ "$env" = "prod" ] && echo "production" || ([ "$env" = "staging" ] && echo "staging" || echo "development"))
  app: $SERVICE_NAME
resources:
- ../../base
patchesStrategicMerge:
- resources-patch.yaml
images:
- name: $SERVICE_NAME
  newName: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/$SERVICE_NAME
  newTag: latest
EOL
      
      cat > "$SERVICE_PATH/k8s/overlays/$env/resources-patch.yaml" <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
spec:
  replicas: $replicas
  template:
    spec:
      containers:
      - name: $SERVICE_NAME
        resources:
          requests:
            cpu: $cpu_req
            memory: $mem_req
          limits:
            cpu: $cpu_lim
            memory: $mem_lim
EOL
    done
    
    print_success "已创建基本的K8s配置目录结构"
  fi
fi

# 检查package.json
if [ -f "$SERVICE_PATH/package.json" ]; then
  print_success "package.json存在"
  
  # 检查健康检查路由
  grep -r "app.get.*health" "$SERVICE_PATH/src" >/dev/null 2>&1 || grep -r "router.get.*health" "$SERVICE_PATH/src" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    print_success "健康检查路由已实现"
  else
    print_warning "未找到健康检查路由实现，这可能导致健康检查失败"
    WARNINGS_FOUND=$((WARNINGS_FOUND+1))
    
    # 尝试修复
    if [ "$FIX_ISSUES" = "--fix" ]; then
      echo "尝试添加健康检查路由..."
      
      # 查找main文件或app.js/index.js
      MAIN_FILE=$(grep -o '"main": *"[^"]*"' "$SERVICE_PATH/package.json" | cut -d'"' -f4)
      if [ -z "$MAIN_FILE" ]; then
        if [ -f "$SERVICE_PATH/src/app.js" ]; then
          MAIN_FILE="src/app.js"
        elif [ -f "$SERVICE_PATH/src/index.js" ]; then
          MAIN_FILE="src/index.js"
        else
          MAIN_FILE="src/server.js"
          mkdir -p "$SERVICE_PATH/src"
          
          # 创建一个基本的服务器文件
          cat > "$SERVICE_PATH/$MAIN_FILE" <<EOL
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: '$SERVICE_NAME' });
});

app.listen(port, () => {
  console.log(\`$SERVICE_NAME service listening at http://localhost:\${port}\`);
});
EOL
          print_success "已创建基本的服务器文件"
          
          # 更新package.json
          sed -i.bak 's/"main": *"[^"]*"/"main": "src\/server.js"/' "$SERVICE_PATH/package.json"
          
          # 如果不存在scripts部分，则添加
          if ! grep -q '"scripts"' "$SERVICE_PATH/package.json"; then
            sed -i.bak '/"name"/a \  "scripts": {\n    "start": "node src\/server.js",\n    "test": "echo \\"Error: no test specified\\" && exit 1"\n  },' "$SERVICE_PATH/package.json"
          fi
          
          print_success "已更新package.json"
        fi
      else
        # 找到main文件，添加健康检查路由
        MAIN_FILE_PATH="$SERVICE_PATH/$MAIN_FILE"
        if [ -f "$MAIN_FILE_PATH" ]; then
          # 检查文件类型是Express应用还是路由
          if grep -q "express()" "$MAIN_FILE_PATH" || grep -q "app\\." "$MAIN_FILE_PATH"; then
            # Express应用，添加路由
            if grep -q "app.listen" "$MAIN_FILE_PATH"; then
              sed -i.bak '/app.listen/i app.get(\x27/health\x27, (req, res) => {\n  res.status(200).json({ status: \x27ok\x27, service: \x27'$SERVICE_NAME'\x27 });\n});' "$MAIN_FILE_PATH"
            else
              echo "未找到app.listen，无法确定添加位置"
            fi
          elif grep -q "router\\." "$MAIN_FILE_PATH"; then
            # Express路由，添加路由
            sed -i.bak '/router\\./i router.get(\x27/health\x27, (req, res) => {\n  res.status(200).json({ status: \x27ok\x27, service: \x27'$SERVICE_NAME'\x27 });\n});' "$MAIN_FILE_PATH"
          else
            echo "无法确定文件类型，跳过添加健康检查路由"
          fi
        else
          echo "main文件不存在，跳过添加健康检查路由"
        fi
      fi
    fi
  fi
  
  # 检查必要的脚本
  for script in "start" "test" "lint"; do
    if grep -q "\"$script\":" "$SERVICE_PATH/package.json"; then
      print_success "package.json包含$script脚本"
    else
      print_warning "package.json不包含$script脚本，这可能影响CI/CD流程"
      WARNINGS_FOUND=$((WARNINGS_FOUND+1))
      
      # 尝试修复
      if [ "$FIX_ISSUES" = "--fix" ]; then
        echo "尝试添加$script脚本..."
        
        # 检查是否已存在scripts部分
        if grep -q '"scripts"' "$SERVICE_PATH/package.json"; then
          # 查找scripts部分结束位置
          if [ "$script" = "start" ]; then
            sed -i.bak '/"scripts"/,/}/s/}/  "start": "node src\/index.js",\n  }/' "$SERVICE_PATH/package.json"
          elif [ "$script" = "test" ]; then
            sed -i.bak '/"scripts"/,/}/s/}/  "test": "echo \\"Error: no test specified\\" && exit 1",\n  }/' "$SERVICE_PATH/package.json"
          elif [ "$script" = "lint" ]; then
            sed -i.bak '/"scripts"/,/}/s/}/  "lint": "eslint .",\n  }/' "$SERVICE_PATH/package.json"
          fi
        else
          # 添加整个scripts部分
          sed -i.bak '/"name"/a \  "scripts": {\n    "start": "node src/index.js",\n    "test": "echo \\"Error: no test specified\\" && exit 1",\n    "lint": "eslint ."\n  },' "$SERVICE_PATH/package.json"
        fi
        print_success "已添加$script脚本"
      fi
    fi
  done
else
  print_error "package.json不存在，这将阻止服务构建"
  ERRORS_FOUND=$((ERRORS_FOUND+1))
  
  # 尝试修复
  if [ "$FIX_ISSUES" = "--fix" ]; then
    echo "尝试创建基本的package.json..."
    
    cat > "$SERVICE_PATH/package.json" <<EOL
{
  "name": "$SERVICE_NAME",
  "version": "1.0.0",
  "description": "$SERVICE_NAME for Suoke Life",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1",
    "lint": "eslint ."
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "eslint": "^8.42.0"
  }
}
EOL
    print_success "已创建基本的package.json"
    
    # 创建基本的源文件
    mkdir -p "$SERVICE_PATH/src"
    cat > "$SERVICE_PATH/src/index.js" <<EOL
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: '$SERVICE_NAME' });
});

app.listen(port, () => {
  console.log(\`$SERVICE_NAME service listening at http://localhost:\${port}\`);
});
EOL
    print_success "已创建基本的源文件"
  fi
fi

# 输出验证结果
print_header "验证结果摘要"
echo "服务: $SERVICE_NAME"
echo "检查总数: $((ERRORS_FOUND + WARNINGS_FOUND + 10))"
echo "错误数: $ERRORS_FOUND"
echo "警告数: $WARNINGS_FOUND"

if [ $ERRORS_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
  print_success "所有检查均已通过，服务可以部署"
  exit 0
elif [ $ERRORS_FOUND -eq 0 ]; then
  print_warning "存在$WARNINGS_FOUND个警告，但服务仍可部署"
  echo "可以使用 $0 $SERVICE_NAME --fix 尝试自动修复警告"
  exit 0
else
  print_error "存在$ERRORS_FOUND个错误，服务无法部署"
  echo "请修复错误后重试，或使用 $0 $SERVICE_NAME --fix 尝试自动修复"
  exit 1
fi 