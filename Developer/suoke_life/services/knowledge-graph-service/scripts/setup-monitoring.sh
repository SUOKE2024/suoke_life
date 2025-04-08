#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务监控设置脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义命令行参数
ACTION=$1
NAMESPACE=${2:-"default"}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法:${NC}"
    echo -e "  $0 <action> [namespace]"
    echo -e ""
    echo -e "${BLUE}Actions:${NC}"
    echo -e "  setup     设置监控和日志收集"
    echo -e "  status    检查监控和日志状态"
    echo -e "  logs      查看服务日志"
    echo -e "  metrics   查看服务指标"
    echo -e ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  $0 setup default"
    echo -e "  $0 status suoke-prod"
    echo -e "  $0 logs"
    echo -e "  $0 metrics"
    echo -e ""
}

# 检查参数
if [ -z "$ACTION" ]; then
    show_help
    exit 1
fi

# 检查操作
if [[ ! "$ACTION" =~ ^(setup|status|logs|metrics)$ ]]; then
    echo -e "${RED}❌ 无效的操作: $ACTION${NC}"
    show_help
    exit 1
fi

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl未安装! 请先安装kubectl${NC}"
    exit 1
fi

# 设置监控和日志收集
setup_monitoring() {
    echo -e "\n${BLUE}设置监控和日志收集...${NC}"
    
    # 检查命名空间是否存在
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}命名空间 $NAMESPACE 不存在，正在创建...${NC}"
        kubectl create namespace $NAMESPACE
    fi
    
    # 创建ServiceMonitor
    echo -e "${YELLOW}创建ServiceMonitor...${NC}"
    cat > servicemonitor.yaml << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: knowledge-graph-service-monitor
  namespace: $NAMESPACE
  labels:
    app: knowledge-graph-service
    release: prometheus
spec:
  selector:
    matchLabels:
      app: knowledge-graph-service
  namespaceSelector:
    matchNames:
      - $NAMESPACE
  endpoints:
    - port: metrics
      path: /metrics
      interval: 15s
      scrapeTimeout: 10s
      metricRelabelings:
        # 重命名特定指标
        - sourceLabels: [__name__]
          regex: 'http_requests_total'
          targetLabel: 'http_requests_count'
          action: replace
      relabelings:
        # 添加环境标签
        - targetLabel: environment
          replacement: ${NAMESPACE#suoke-}
        # 添加服务类型标签
        - targetLabel: service_type
          replacement: knowledge-graph
EOF
    
    kubectl apply -f servicemonitor.yaml
    rm servicemonitor.yaml
    
    # 创建日志配置
    echo -e "${YELLOW}创建日志配置...${NC}"
    cat > logging-config.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: knowledge-graph-fluentbit-config
  namespace: $NAMESPACE
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Daemon       Off
        Log_Level    info
        Parsers_File parsers.conf

    [INPUT]
        Name        tail
        Path        /var/log/app/*.log
        Tag         app.*
        Parser      json
        Mem_Buf_Limit 5MB
        Skip_Long_Lines On

    [FILTER]
        Name        kubernetes
        Match       app.*
        Merge_Log   On
        K8s-Logging.Parser On
        K8s-Logging.Exclude On

    [OUTPUT]
        Name        es
        Match       app.*
        Host        elasticsearch-master.logging.svc.cluster.local
        Port        9200
        Index       knowledge-graph-logs
        Type        _doc
        Logstash_Format On
        Logstash_Prefix knowledge-graph
        Retry_Limit 3

  parsers.conf: |
    [PARSER]
        Name        json
        Format      json
        Time_Key    time
        Time_Format %Y-%m-%dT%H:%M:%S.%L
EOF
    
    kubectl apply -f logging-config.yaml
    rm logging-config.yaml
    
    echo -e "${GREEN}✅ 监控和日志收集已设置${NC}"
    
    # 检查Prometheus和Elasticsearch是否可用
    echo -e "\n${BLUE}检查监控组件...${NC}"
    
    if kubectl get svc -n monitoring prometheus-server &> /dev/null; then
        echo -e "${GREEN}✅ Prometheus可用${NC}"
    else
        echo -e "${YELLOW}⚠️ Prometheus未找到，监控可能无法正常工作${NC}"
    fi
    
    if kubectl get svc -n logging elasticsearch-master &> /dev/null; then
        echo -e "${GREEN}✅ Elasticsearch可用${NC}"
    else
        echo -e "${YELLOW}⚠️ Elasticsearch未找到，日志收集可能无法正常工作${NC}"
    fi
}

# 检查监控和日志状态
check_status() {
    echo -e "\n${BLUE}检查监控和日志状态...${NC}"
    
    # 检查ServiceMonitor
    echo -e "${YELLOW}检查ServiceMonitor...${NC}"
    if kubectl get servicemonitor knowledge-graph-service-monitor -n $NAMESPACE &> /dev/null; then
        echo -e "${GREEN}✅ ServiceMonitor已配置${NC}"
        kubectl get servicemonitor knowledge-graph-service-monitor -n $NAMESPACE -o yaml | grep -A 5 "endpoints:"
    else
        echo -e "${RED}❌ ServiceMonitor未配置${NC}"
    fi
    
    # 检查日志配置
    echo -e "\n${YELLOW}检查日志配置...${NC}"
    if kubectl get configmap knowledge-graph-fluentbit-config -n $NAMESPACE &> /dev/null; then
        echo -e "${GREEN}✅ 日志配置已设置${NC}"
    else
        echo -e "${RED}❌ 日志配置未设置${NC}"
    fi
    
    # 检查Pod状态
    echo -e "\n${YELLOW}检查Pod状态...${NC}"
    kubectl get pods -n $NAMESPACE -l app=knowledge-graph-service
    
    # 检查服务状态
    echo -e "\n${YELLOW}检查服务状态...${NC}"
    kubectl get svc -n $NAMESPACE -l app=knowledge-graph-service
    
    # 检查最近的日志
    echo -e "\n${YELLOW}最近的日志片段:${NC}"
    kubectl logs --tail=10 -n $NAMESPACE -l app=knowledge-graph-service
}

# 查看服务日志
view_logs() {
    echo -e "\n${BLUE}查看服务日志...${NC}"
    
    # 获取Pod名称
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=knowledge-graph-service -o jsonpath="{.items[0].metadata.name}" 2>/dev/null)
    
    if [ -z "$POD_NAME" ]; then
        echo -e "${RED}❌ 未找到Pod!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}正在查看Pod $POD_NAME 的日志...${NC}"
    echo -e "${YELLOW}按Ctrl+C退出${NC}"
    
    kubectl logs -f -n $NAMESPACE $POD_NAME
}

# 查看服务指标
view_metrics() {
    echo -e "\n${BLUE}查看服务指标...${NC}"
    
    # 获取服务端口
    SVC_PORT=$(kubectl get svc -n $NAMESPACE knowledge-graph-service -o jsonpath="{.spec.ports[?(@.name=='metrics')].port}" 2>/dev/null)
    
    if [ -z "$SVC_PORT" ]; then
        echo -e "${RED}❌ 未找到服务或指标端口!${NC}"
        exit 1
    fi
    
    # 设置端口转发
    echo -e "${YELLOW}设置端口转发到本地9464端口...${NC}"
    echo -e "${YELLOW}按Ctrl+C退出${NC}"
    
    kubectl port-forward -n $NAMESPACE svc/knowledge-graph-service 9464:$SVC_PORT &
    PF_PID=$!
    
    # 等待端口转发建立
    sleep 3
    
    # 获取指标
    echo -e "${GREEN}获取指标...${NC}"
    curl -s http://localhost:9464/metrics | grep -E "^(knowledge_graph|http_|go_|process_)" | head -20
    
    echo -e "\n${YELLOW}完整指标可在浏览器中查看: http://localhost:9464/metrics${NC}"
    echo -e "${YELLOW}按Enter键退出${NC}"
    read
    
    # 清理端口转发
    kill $PF_PID 2>/dev/null
}

# 执行操作
case $ACTION in
    setup)
        setup_monitoring
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    metrics)
        view_metrics
        ;;
    *)
        show_help
        exit 1
        ;;
esac

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}✅ 操作完成!${NC}"
echo -e "${BLUE}=========================================${NC}"
