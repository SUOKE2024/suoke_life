#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 设置日志文件
LOG_FILE="local-minimal-rag-$(date +%Y%m%d-%H%M%S).log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

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

# 检查依赖
check_dependencies() {
  log "检查依赖..."
  
  # 检查Go是否安装
  if ! command -v go &> /dev/null; then
    log_error "Go未安装，请先安装Go"
    return 1
  fi
  
  # 检查Go版本
  GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
  log "检测到Go版本: $GO_VERSION"
  
  log_success "依赖检查通过"
  return 0
}

# 创建必要的目录
create_directories() {
  log "检查必要的目录..."
  
  for dir in "data" "logs" "config" "models"; do
    if [ ! -d "$dir" ]; then
      log "创建目录: $dir"
      mkdir -p "$dir"
    fi
  done
  
  log_success "目录检查/创建完成"
}

# 创建最小化服务
create_minimal_server() {
  log "创建最小化的服务..."
  
  mkdir -p cmd/server
  
  if [ -f "cmd/server/minimal.go" ]; then
    log "最小化服务文件已存在"
  else
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
    log "最小化服务文件创建完成"
  fi
}

# 编译并运行服务
build_and_run() {
  log "编译服务..."
  
  # 确保go.mod存在
  if [ ! -f "go.mod" ]; then
    log "初始化Go模块..."
    go mod init github.com/suoke-life/rag-service
    go mod tidy
  fi
  
  # 编译服务
  log "编译最小化服务..."
  go build -o bin/rag-minimal-service cmd/server/minimal.go
  
  if [ $? -ne 0 ]; then
    log_error "编译失败"
    return 1
  fi
  
  # 配置环境变量
  export PORT=8080
  export LOG_LEVEL=info
  
  # 后台运行服务
  log "启动服务在端口 $PORT..."
  nohup ./bin/rag-minimal-service > logs/rag-minimal-service.log 2>&1 &
  
  PID=$!
  if [ $? -eq 0 ]; then
    log_success "服务已启动，PID: $PID"
    echo $PID > .rag-minimal.pid
  else
    log_error "服务启动失败"
    return 1
  fi
  
  # 等待服务启动
  log "等待服务启动..."
  sleep 3
  
  # 检查服务健康状态
  curl -s http://localhost:$PORT/health
  if [ $? -eq 0 ]; then
    log_success "服务启动成功！"
    return 0
  else
    log_error "服务健康检查失败"
    return 1
  fi
}

# 停止服务
stop_service() {
  if [ -f ".rag-minimal.pid" ]; then
    PID=$(cat .rag-minimal.pid)
    if ps -p $PID > /dev/null; then
      log "停止运行中的服务 (PID: $PID)..."
      kill $PID
      if [ $? -eq 0 ]; then
        log_success "服务已停止"
      else
        log_error "无法停止服务，请手动终止进程"
      fi
    else
      log "没有找到运行中的服务进程"
    fi
    rm -f .rag-minimal.pid
  else
    log "没有找到之前运行的服务记录"
  fi
}

# 显示帮助
show_help() {
  echo "用法: $0 [选项]"
  echo ""
  echo "选项:"
  echo "  start    编译并启动服务"
  echo "  stop     停止运行中的服务"
  echo "  restart  重启服务"
  echo "  help     显示此帮助信息"
  echo ""
  echo "例如:"
  echo "  $0 start    # 启动服务"
  echo "  $0 stop     # 停止服务"
  echo ""
}

# 主函数
main() {
  local command=${1:-"start"}
  
  echo "=========================================================="
  echo "      索克生活RAG服务本地运行脚本"
  echo "      版本: 1.0.0"
  echo "      日期: $(date)"
  echo "=========================================================="
  
  case "$command" in
    "start")
      check_dependencies || exit 1
      create_directories || exit 1
      create_minimal_server || exit 1
      stop_service
      build_and_run || exit 1
      ;;
      
    "stop")
      stop_service
      ;;
      
    "restart")
      stop_service
      check_dependencies || exit 1
      create_directories || exit 1
      create_minimal_server || exit 1
      build_and_run || exit 1
      ;;
      
    "help")
      show_help
      ;;
      
    *)
      log_error "未知命令: $command"
      show_help
      exit 1
      ;;
  esac
  
  if [ "$command" == "start" ] || [ "$command" == "restart" ]; then
    echo "=========================================================="
    echo "      RAG服务已启动"
    echo "      • 服务地址: http://localhost:8080"
    echo "      • 健康检查: http://localhost:8080/health"
    echo "      • 基本搜索: http://localhost:8080/api/search?q=健康"
    echo "      • 日志文件: logs/rag-minimal-service.log"
    echo "      • 进程ID文件: .rag-minimal.pid"
    echo "      • 停止服务: $0 stop"
    echo "=========================================================="
  fi
}

# 执行主函数
main "$@" 