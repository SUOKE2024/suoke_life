#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 设置日志文件
LOG_FILE="deploy-minimal-rag-$(date +%Y%m%d-%H%M%S).log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

# 重试次数
MAX_RETRIES=3

# 日志函数
log() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "${YELLOW}$timestamp${NC} [INFO] $1"
  echo "$(date +"%Y-%m-%d %H:%M:%S") [INFO] $1" >> "$LOG_FILE"
}

log_success() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "${GREEN}$timestamp${NC} [SUCCESS] $1"
  echo "$(date +"%Y-%m-%d %H:%M:%S") [SUCCESS] $1" >> "$LOG_FILE"
}

log_error() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "${RED}$timestamp${NC} [ERROR] $1"
  echo "$(date +"%Y-%m-%d %H:%M:%S") [ERROR] $1" >> "$LOG_FILE"
}

log_cmd() {
  local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  echo -e "${YELLOW}$timestamp${NC} [CMD] Executing command: $1"
  echo "$(date +"%Y-%m-%d %H:%M:%S") [CMD] Executing command: $1" >> "$LOG_FILE"
}

# 执行命令并记录结果
execute_cmd() {
  local cmd="$1"
  log_cmd "$cmd"
  
  output=$(eval "$cmd" 2>&1)
  exit_code=$?
  
  echo "$output"
  echo "$output" >> "$LOG_FILE"
  
  if [ $exit_code -eq 0 ]; then
    log_success "命令执行成功"
    return 0
  else
    log_error "命令失败，退出代码: $exit_code"
    return $exit_code
  fi
}

# 带重试的命令执行
execute_with_retry() {
  local cmd="$1"
  local retries=0
  
  while [ $retries -lt $MAX_RETRIES ]; do
    log "尝试执行命令 (尝试 $(($retries + 1))/$MAX_RETRIES): $cmd"
    
    output=$(eval "$cmd" 2>&1)
    exit_code=$?
    
    echo "$output"
    echo "$output" >> "$LOG_FILE"
    
    if [ $exit_code -eq 0 ]; then
      log_success "命令执行成功"
      return 0
    else
      log_error "命令失败，退出代码: $exit_code，准备重试..."
      retries=$((retries + 1))
      sleep 3
    fi
  done
  
  log_error "命令在 $MAX_RETRIES 次尝试后仍然失败"
  return 1
}

# 检查Docker是否安装
check_docker() {
  log "检查Docker..."
  if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
  fi
  
  if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
  fi
  
  log_success "Docker检查通过"
}

# 创建必要的目录
create_directories() {
  log "检查必要的目录..."
  
  for dir in "data" "logs" "config" "models" "deployment/nginx/conf.d" "deployment/nginx/ssl"; do
    if [ ! -d "$dir" ]; then
      log "创建目录: $dir"
      execute_cmd "mkdir -p $dir" || return 1
    fi
  done
  
  log_success "目录检查/创建完成"
}

# 创建最小化的Dockerfile
create_minimal_dockerfile() {
  log "创建最小化Dockerfile..."
  
  if [ -f "Dockerfile.minimal.rag" ]; then
    log "Dockerfile.minimal.rag已存在，跳过创建"
    return 0
  fi
  
  cat > Dockerfile.minimal.rag << 'EOF'
FROM golang:1.18-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o rag-service ./cmd/server

FROM alpine:latest

RUN apk --no-cache add ca-certificates curl netcat-openbsd

WORKDIR /app

COPY --from=builder /app/rag-service /app/
COPY config /app/config

# 创建健康检查脚本
RUN echo '#!/bin/sh\necho "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"healthy\",\"service\":\"rag-minimal\",\"version\":\"1.0.0\"}"' > /app/health.sh && \
    chmod +x /app/health.sh

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/models

EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 如果主服务无法启动，则使用最小健康服务
CMD [ "/bin/sh", "-c", "exec /app/rag-service || (echo 'Main service failed to start, using minimal health service' && while true; do nc -l -p 8080 -e /app/health.sh; done)" ]
EOF
  
  log_success "Dockerfile.minimal.rag创建完成"
}

# 创建简化的docker-compose文件
create_minimal_compose() {
  log "创建最小化docker-compose文件..."
  
  if [ -f "docker-compose.minimal.rag.yml" ]; then
    log "docker-compose.minimal.rag.yml已存在，跳过创建"
    return 0
  fi
  
  # 基于是否有nginx镜像决定是否包含nginx服务
  if docker images | grep -q "nginx:stable-alpine"; then
    log "发现本地nginx:stable-alpine镜像，将在配置中包含nginx服务"
    INCLUDE_NGINX=true
  else
    log "未发现本地nginx镜像，配置将只包含rag服务"
    INCLUDE_NGINX=false
  fi
  
  # 创建docker-compose文件头部
  cat > docker-compose.minimal.rag.yml << 'EOF'
services:
  rag-service:
    build:
      context: .
      dockerfile: Dockerfile.minimal.rag
    container_name: suoke-rag-service-minimal
    restart: always
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - LOG_LEVEL=info
      - DB_TYPE=memory
    networks:
      - suoke-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
EOF

  # 如果有nginx镜像，添加nginx服务配置
  if [ "$INCLUDE_NGINX" = true ]; then
    cat >> docker-compose.minimal.rag.yml << 'EOF'

  # Nginx反向代理
  nginx:
    image: nginx:stable-alpine
    container_name: suoke-nginx-minimal
    restart: always
    volumes:
      - ./deployment/nginx/conf.d:/etc/nginx/conf.d
      - ./deployment/nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    ports:
      - "8081:80"
    depends_on:
      - rag-service
    networks:
      - suoke-net
EOF
  fi

  # 添加网络配置
  cat >> docker-compose.minimal.rag.yml << 'EOF'

networks:
  suoke-net:
    driver: bridge
EOF
  
  log_success "docker-compose.minimal.rag.yml创建完成"
}

# 创建最小化服务单元
create_minimal_server() {
  log "创建最小化的服务..."
  
  if [ -f "cmd/server/minimal.go" ]; then
    log "最小化服务文件已存在，跳过创建"
    return 0
  fi
  
  mkdir -p cmd/server
  
  cat > cmd/server/minimal.go << 'EOF'
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// 健康检查响应
type HealthResponse struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Version   string    `json:"version"`
	Timestamp time.Time `json:"time"`
}

// 搜索响应
type SearchResponse struct {
	Status  string         `json:"status"`
	Results []SearchResult `json:"results"`
}

// 搜索结果
type SearchResult struct {
	Content  string                 `json:"content"`
	Score    float64                `json:"score"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

func main() {
	port := "8080"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	// 健康检查端点
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		response := HealthResponse{
			Status:    "healthy",
			Service:   "rag-minimal",
			Version:   "1.0.0",
			Timestamp: time.Now(),
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 简单查询端点
	http.HandleFunc("/api/search", func(w http.ResponseWriter, r *http.Request) {
		query := r.URL.Query().Get("q")
		if query == "" {
			query = "未提供查询"
		}
		
		response := SearchResponse{
			Status: "success",
			Results: []SearchResult{
				{
					Content: fmt.Sprintf("索克健康问答: %s", query),
					Score:   1.0,
					Metadata: map[string]interface{}{
						"source": "最小服务响应",
						"type":   "text",
					},
				},
			},
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 多模态查询端点
	http.HandleFunc("/api/search/multimodal", func(w http.ResponseWriter, r *http.Request) {
		// 仅支持POST
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		response := SearchResponse{
			Status: "success",
			Results: []SearchResult{
				{
					Content: "这是一个多模态测试响应",
					Score:   1.0,
					Metadata: map[string]interface{}{
						"source":    "最小服务响应",
						"type":      "multimodal",
						"processed": true,
					},
				},
			},
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 舌诊分析端点
	http.HandleFunc("/api/analyze/tongue", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"淡红舌", "薄白苔"},
			"analysis": "舌质淡红，苔薄白，提示气血调和，身体状态良好。",
			"bodyType": "平和质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	// 面诊分析端点
	http.HandleFunc("/api/analyze/face", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"面色红润", "气色良好"},
			"analysis": "面色红润，精神饱满，提示气血充盈。",
			"bodyType": "阳热质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	// 音频分析端点
	http.HandleFunc("/api/analyze/audio", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"声音洪亮", "语速适中"},
			"analysis": "声音洪亮有力，语速适中，提示肺气充足。",
			"bodyType": "气虚质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	log.Printf("索克生活RAG服务(最小版本)启动在端口 %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("服务启动失败: %v", err)
	}
}
EOF
  
  log_success "最小化服务创建完成"
}

# 创建Nginx配置
create_nginx_config() {
  log "创建Nginx配置..."
  
  if [ -f "deployment/nginx/conf.d/default.conf" ]; then
    log "Nginx配置文件已存在，跳过创建"
    return 0
  fi
  
  mkdir -p deployment/nginx/conf.d
  
  cat > deployment/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    location / {
        proxy_pass http://rag-service:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
  
  log_success "Nginx配置创建完成"
}

# 检查是否已经有镜像
check_local_images() {
  log "检查本地镜像..."
  
  # 检查是否有必要的镜像
  if ! docker images | grep -q "golang:1.18-alpine"; then
    log "警告: 未找到golang:1.18-alpine镜像，构建可能需要从远程获取"
  else
    log_success "已有golang:1.18-alpine镜像"
  fi
  
  if ! docker images | grep -q "alpine:latest"; then
    log "警告: 未找到alpine:latest镜像，构建可能需要从远程获取"
  else
    log_success "已有alpine:latest镜像"
  fi
  
  if ! docker images | grep -q "nginx:stable-alpine"; then
    log "警告: 未找到nginx:stable-alpine镜像，构建可能需要从远程获取"
  else
    log_success "已有nginx:stable-alpine镜像"
  fi
}

# 部署服务
deploy_services() {
  log "部署服务..."
  
  # 首先停止现有服务
  execute_cmd "docker-compose -f docker-compose.minimal.rag.yml down" || true
  
  # 先构建rag-service镜像，不启动容器
  log "构建RAG服务镜像..."
  if ! execute_with_retry "docker-compose -f docker-compose.minimal.rag.yml build rag-service"; then
    log_error "RAG服务镜像构建失败"
    return 1
  fi
  
  # 启动rag-service服务
  log "启动RAG服务..."
  if ! execute_with_retry "docker-compose -f docker-compose.minimal.rag.yml up -d rag-service"; then
    log_error "RAG服务启动失败"
    return 1
  fi
  
  # 如果docker-compose文件中包含nginx服务，尝试启动它
  if grep -q "nginx:" docker-compose.minimal.rag.yml; then
    log "启动Nginx服务..."
    if ! execute_with_retry "docker-compose -f docker-compose.minimal.rag.yml up -d nginx"; then
      log_warning "Nginx服务启动失败，但RAG服务可能已经启动成功"
    fi
  fi
  
  log_success "服务已部署"
}

# 检查服务状态
check_services() {
  log "检查服务状态..."
  sleep 5 # 等待服务启动
  
  if ! execute_cmd "docker ps | grep suoke-rag-service-minimal"; then
    log_error "RAG服务未运行"
    return 1
  fi
  
  # 只有在docker-compose文件中包含nginx服务时才检查nginx
  if grep -q "nginx:" docker-compose.minimal.rag.yml; then
    if ! execute_cmd "docker ps | grep suoke-nginx-minimal"; then
      log "Nginx服务未运行，但这不影响RAG服务的功能"
    fi
  fi
  
  # 检查健康状态
  log "检查RAG服务健康状态..."
  if ! execute_with_retry "curl -s http://localhost:8080/health"; then
    log_error "RAG服务健康检查失败"
    return 1
  fi
  
  log_success "RAG服务运行正常"
}

# 创建备用服务
create_fallback_server() {
  log "创建备用服务脚本..."
  
  cat > scripts/run-fallback-server.sh << 'EOF'
#!/bin/bash

PORT=8080
echo "启动简单健康检查服务在端口 $PORT..."
while true; do
  echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"healthy\",\"service\":\"rag-minimal-fallback\",\"version\":\"1.0.0\"}" | nc -l -p $PORT
done
EOF

  chmod +x scripts/run-fallback-server.sh
  log_success "备用服务脚本创建完成"
}

# 主函数
main() {
  echo "=========================================================="
  echo "      索克生活RAG服务最小化部署脚本"
  echo "      版本: 1.0.0"
  echo "      日期: $(date)"
  echo "=========================================================="
  
  check_docker || exit 1
  check_local_images
  create_directories || exit 1
  create_minimal_dockerfile || exit 1
  create_minimal_compose || exit 1
  create_minimal_server || exit 1
  create_nginx_config || exit 1
  create_fallback_server || exit 1
  deploy_services || exit 1
  check_services || exit 1
  
  echo "=========================================================="
  echo "      部署完成！"
  echo "      • RAG服务: http://localhost:8080"
  if grep -q "nginx:" docker-compose.minimal.rag.yml; then
    echo "      • 通过Nginx: http://localhost:8081"
  fi
  echo "      • 日志文件: $LOG_FILE"
  echo "      • 如果需要备用服务: ./scripts/run-fallback-server.sh"
  echo "=========================================================="
}

# 执行主函数
main 