#!/bin/bash

# 索克生活项目 - 监控系统设置脚本
# 设置完整的监控和日志聚合系统

echo "🔍 索克生活项目 - 监控系统设置"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Docker环境
check_docker() {
    echo -e "${BLUE}检查Docker环境...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker环境检查通过${NC}"
    echo ""
}

# 创建监控目录结构
create_directories() {
    echo -e "${BLUE}创建监控目录结构...${NC}"
    
    # 创建必要的目录
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana/provisioning/dashboards
    mkdir -p monitoring/grafana/provisioning/datasources
    mkdir -p monitoring/logstash/config
    mkdir -p monitoring/logstash/pipeline
    
    echo -e "${GREEN}✅ 监控目录结构创建完成${NC}"
    echo ""
}

# 创建Grafana数据源配置
create_grafana_datasources() {
    echo -e "${BLUE}创建Grafana数据源配置...${NC}"
    
    cat > monitoring/grafana/provisioning/datasources/datasources.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "suoke-logs-*"
    interval: Daily
    timeField: "@timestamp"
    editable: true

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    editable: true
EOF

    echo -e "${GREEN}✅ Grafana数据源配置创建完成${NC}"
    echo ""
}

# 创建Grafana仪表板配置
create_grafana_dashboards() {
    echo -e "${BLUE}创建Grafana仪表板配置...${NC}"
    
    cat > monitoring/grafana/provisioning/dashboards/dashboards.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    # 创建索克生活系统概览仪表板
    cat > monitoring/grafana/provisioning/dashboards/suoke-overview.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "索克生活系统概览",
    "tags": ["suoke", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "系统CPU使用率",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "系统内存使用率",
        "type": "stat",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "服务响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "5s"
  }
}
EOF

    echo -e "${GREEN}✅ Grafana仪表板配置创建完成${NC}"
    echo ""
}

# 验证监控配置
validate_monitoring_config() {
    echo -e "${BLUE}验证监控配置...${NC}"
    
    # 验证Docker Compose配置
    if docker-compose -f monitoring/docker-compose.monitoring.yml config --quiet; then
        echo -e "${GREEN}✅ 监控Docker Compose配置验证通过${NC}"
    else
        echo -e "${RED}❌ 监控Docker Compose配置验证失败${NC}"
        return 1
    fi
    
    # 验证Prometheus配置
    if [ -f "monitoring/prometheus/prometheus.yml" ]; then
        echo -e "${GREEN}✅ Prometheus配置文件存在${NC}"
    else
        echo -e "${RED}❌ Prometheus配置文件缺失${NC}"
        return 1
    fi
    
    echo ""
}

# 启动监控系统
start_monitoring() {
    echo -e "${BLUE}启动监控系统...${NC}"
    
    cd monitoring
    
    # 启动监控服务
    docker-compose -f docker-compose.monitoring.yml up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 监控系统启动成功${NC}"
        echo ""
        echo -e "${YELLOW}监控服务访问地址:${NC}"
        echo "  • Prometheus: http://localhost:9090"
        echo "  • Grafana: http://localhost:3000 (admin/suoke123)"
        echo "  • Kibana: http://localhost:5601"
        echo "  • Jaeger: http://localhost:16686"
        echo ""
    else
        echo -e "${RED}❌ 监控系统启动失败${NC}"
        return 1
    fi
    
    cd ..
}

# 创建监控状态检查脚本
create_monitoring_check() {
    echo -e "${BLUE}创建监控状态检查脚本...${NC}"
    
    cat > scripts/check-monitoring.sh << 'EOF'
#!/bin/bash

echo "🔍 检查监控系统状态..."
echo ""

# 检查监控容器状态
echo "监控容器状态:"
docker ps --filter "name=suoke-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 检查服务健康状态
echo "服务健康检查:"
services=("prometheus:9090" "grafana:3000" "elasticsearch:9200" "kibana:5601" "jaeger:16686")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -s "http://localhost:$port" > /dev/null; then
        echo "  ✅ $name (端口 $port) - 正常"
    else
        echo "  ❌ $name (端口 $port) - 异常"
    fi
done

echo ""
echo "监控系统访问地址:"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000"
echo "  • Kibana: http://localhost:5601"
echo "  • Jaeger: http://localhost:16686"
EOF

    chmod +x scripts/check-monitoring.sh
    echo -e "${GREEN}✅ 监控状态检查脚本创建完成${NC}"
    echo ""
}

# 主执行流程
main() {
    echo -e "${YELLOW}开始设置索克生活监控系统...${NC}"
    echo ""
    
    check_docker
    create_directories
    create_grafana_datasources
    create_grafana_dashboards
    validate_monitoring_config
    start_monitoring
    create_monitoring_check
    
    echo -e "${GREEN}🎉 监控系统设置完成！${NC}"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo "1. 访问 Grafana (http://localhost:3000) 配置仪表板"
    echo "2. 访问 Kibana (http://localhost:5601) 查看日志"
    echo "3. 运行 ./scripts/check-monitoring.sh 检查系统状态"
    echo "4. 配置服务的指标暴露端点"
    echo ""
}

# 执行主函数
main 