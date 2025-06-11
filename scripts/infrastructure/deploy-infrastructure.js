#!/usr/bin/env node
/**
 * 索克生活基础设施部署脚本
 * 自动化部署环境配置、监控系统和日志系统
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
class InfrastructureDeployment {
  constructor() {
    this.startTime = Date.now();
    this.deploymentLog = [];
    this.errors = [];
    this.warnings = [];
  }
  /**
   * 记录日志
   */
  log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data;
    };
    this.deploymentLog.push(logEntry);
    const colors =  {;
      info: "\x1b[36m,    // 青色"
success: "\x1b[32m", // 绿色"
warning: \x1b[33m", // 黄色"
error: "\x1b[31m,   // 红色"
debug: "\x1b[37m"    // 白色
    }
    const color = colors[level] || \x1b[0m";
    const icon = {"
      info: "ℹ️,"
      success: "✅","
      warning: ⚠️","
      error: "❌,"
      debug: "🔍
    }[level] || ";
    if (data) {
      }\x1b[0m`);
    }
    if (level === "error) {
      this.errors.push(logEntry);
    } else if (level === "warning") {
      this.warnings.push(logEntry);
    }
  }
  /**
   * 执行命令
   */
  async executeCommand(command, description) {"
    this.log(info", `执行: ${description}`);
    this.log("debug, `命令: ${command}`);
    try {
      const output = execSync(command, { "
        encoding: "utf8","
        stdio: pipe";
      });
      this.log("success, `完成: ${description}`);
      if (output.trim()) {"
        this.log("debug", 输出:", output.trim());
      }
      return { success: true, output };
    } catch (error) {"
      this.log("error, `失败: ${description}`, {
        command,
        error: error.message,
        stdout: error.stdout?.toString(),
        stderr: error.stderr?.toString()
      });
      return { success: false, error };
    }
  }
  /**
   * 检查先决条件
   */
  async checkPrerequisites() {"
    this.log("info", 🔍 检查部署先决条件...");
    const checks = [
      {"
        name: "Node.js,"
        command: "node --version",
        required: true
      },
      {"
        name: npm","
        command: "npm --version,
        required: true
      },
      {"
        name: "Docker","
        command: docker --version",
        required: false
      },
      {"
        name: "Docker Compose,"
        command: "docker-compose --version",
        required: false
      },
      {"
        name: kubectl","
        command: "kubectl version --client,
        required: false
      };
    ];
    let allRequired = true;
    for (const check of checks) {
      const result = await this.executeCommand(check.command, `检查 ${check.name}`);
      if (!result.success) {
        if (check.required) {"
          this.log("error", `必需的依赖 ${check.name} 未安装`);
          allRequired = false;
        } else {"
          this.log(warning", `可选的依赖 ${check.name} 未安装`);
        }
      } else {"
        this.log("success, `${check.name} 已安装: ${result.output.trim()}`);
      }
    }
    if (!allRequired) {"
      throw new Error("缺少必需的依赖，请安装后重试");
    }
    this.log(success", "✅ 先决条件检查完成);
  }
  /**
   * 创建目录结构
   */
  async createDirectoryStructure() {"
    this.log("info", 📁 创建目录结构...");
    const directories = ["
      "logs,"
      "config","
      data/prometheus","
      "data/grafana,"
      "data/elasticsearch","
      data/loki","
      "deploy/monitoring,"
      "deploy/logging","
      deploy/config";
    ];
    for (const dir of directories) {
      const fullPath = path.join(process.cwd(), dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        this.log("success, `创建目录: ${dir}`);
      } else {"
        this.log("info", `目录已存在: ${dir}`);
      }
    }
    this.log(success", "✅ 目录结构创建完成);
  }
  /**
   * 生成环境配置文件
   */
  async generateEnvironmentConfig() {"
    this.log("info", ⚙️ 生成环境配置文件...");
    const environments = ["development, "testing", staging", "production];
    for (const env of environments) {"
      const configPath = path.join(process.cwd(), "config", `${env}.env`);
      if (!fs.existsSync(configPath)) {
        const config = this.generateEnvConfig(env);
        fs.writeFileSync(configPath, config);
        this.log(success", `生成配置文件: config/${env}.env`);
      } else {"
        this.log("info, `配置文件已存在: config/${env}.env`);
      }
    }
    this.log("success", ✅ 环境配置文件生成完成");
  }
  /**
   * 生成环境配置内容
   */
  generateEnvConfig(environment) {
    const baseConfig = {
      development: {,"
  NODE_ENV: "development,"
        DEBUG: "true","
        LOG_LEVEL: debug","
        PROMETHEUS_ENABLED: "false,"
        GRAFANA_ENABLED: "false","
        TRACING_ENABLED: false","
        ALERTING_ENABLED: "false
      },
      testing: {,"
  NODE_ENV: "testing","
        DEBUG: false","
        LOG_LEVEL: "warn,"
        DB_NAME: "suoke_life_test","
        REDIS_DB: 1","
        PROMETHEUS_ENABLED: "false,"
        GRAFANA_ENABLED: "false","
        TRACING_ENABLED: false","
        ALERTING_ENABLED: "false
      },
      staging: {,"
  NODE_ENV: "staging","
        DEBUG: false","
        LOG_LEVEL: "info,"
        PROMETHEUS_ENABLED: "true","
        GRAFANA_ENABLED: true","
        TRACING_ENABLED: "true,"
        ALERTING_ENABLED: "true"
      },
      production: {,"
  NODE_ENV: production","
        DEBUG: "false,"
        LOG_LEVEL: "warn","
        DB_SSL: true","
        DB_POOL_SIZE: "20,"
        REDIS_CLUSTER: "true","
        PROMETHEUS_ENABLED: true","
        GRAFANA_ENABLED: "true,"
        TRACING_ENABLED: "true","
        ALERTING_ENABLED: true","
        STRUCTURED_LOGGING: "true,"
        LOG_ROTATION: "true"
      };
    };
    const commonConfig =  {;
      // 服务配置"
API_GATEWAY_HOST: 0.0.0.0","
      API_GATEWAY_PORT: "8080,"
      API_GATEWAY_TIMEOUT: "30000","
      API_GATEWAY_RATE_LIMIT: 1000",
      // 智能体服务"
XIAOAI_HOST: "localhost,"
      XIAOAI_PORT: "8081","
      XIAOKE_HOST: localhost","
      XIAOKE_PORT: "8082,"
      LAOKE_HOST: "localhost","
      LAOKE_PORT: 8083","
      SOER_HOST: "localhost,"
      SOER_PORT: "8084",
      // 诊断服务"
LOOK_SERVICE_HOST: localhost","
      LOOK_SERVICE_PORT: "8085,"
      LISTEN_SERVICE_HOST: "localhost","
      LISTEN_SERVICE_PORT: 8086","
      INQUIRY_SERVICE_HOST: "localhost,"
      INQUIRY_SERVICE_PORT: "8087","
      PALPATION_SERVICE_HOST: localhost","
      PALPATION_SERVICE_PORT: "8088,"
      CALCULATION_SERVICE_HOST: "localhost","
      CALCULATION_SERVICE_PORT: 8089",
      // 数据服务"
HEALTH_DATA_SERVICE_HOST: "localhost,"
      HEALTH_DATA_SERVICE_PORT: "8090","
      USER_DATA_SERVICE_HOST: localhost","
      USER_DATA_SERVICE_PORT: "8091,"
      BLOCKCHAIN_SERVICE_HOST: "localhost","
      BLOCKCHAIN_SERVICE_PORT: 8092",
      // 数据库配置"
DB_HOST: "localhost,"
      DB_PORT: "5432","
      DB_NAME: suoke_life","
      DB_USER: "postgres,"
      DB_PASSWORD: "your-password","
      DB_SSL: false","
      DB_POOL_SIZE: "10,
      // Redis配置"
REDIS_HOST: "localhost","
      REDIS_PORT: 6379","
      REDIS_PASSWORD: ","
      REDIS_DB: "0","
      REDIS_CLUSTER: false",
      // 监控配置"
PROMETHEUS_HOST: "localhost,"
      PROMETHEUS_PORT: "9090","
      PROMETHEUS_SCRAPE_INTERVAL: 15","
      GRAFANA_HOST: "localhost,"
      GRAFANA_PORT: "3000","
      GRAFANA_ADMIN_USER: admin","
      GRAFANA_ADMIN_PASSWORD: "admin,
      // 日志配置"
LOG_FORMAT: "json","
      LOG_MAX_SIZE: 100MB","
      LOG_MAX_FILES: "10,"
      LOG_MAX_AGE: "30d",
      // 安全配置"
JWT_SECRET: your-jwt-secret-key","
      JWT_EXPIRES_IN: "24h,"
      JWT_ALGORITHM: "HS256","
      CORS_ORIGINS: *","
      CORS_METHODS: "GET,POST,PUT,DELETE,"
      CORS_HEADERS: "Content-Type,Authorization",
      // 性能配置"
MAX_CONNECTIONS: 100","
      MIN_CONNECTIONS: "10,"
      ACQUIRE_TIMEOUT: "30000","
      IDLE_TIMEOUT: 300000","
      CACHE_DEFAULT_TTL: "3600,"
      CACHE_MAX_MEMORY: "1GB","
      MAX_CONCURRENT: 100","
      QUEUE_SIZE: "1000
    };
    const envConfig = { ...commonConfig, ...baseConfig[environment] };
    let configContent = `# 索克生活 ${environment.toUpperCase()} 环境配置\n`;
    configContent += `# 生成时间: ${new Date().toISOString()}\n\n`;
    const sections = {"
      "基础配置": [NODE_ENV", "DEBUG, "LOG_LEVEL"],"
      服务配置": ["API_GATEWAY_HOST, "API_GATEWAY_PORT", API_GATEWAY_TIMEOUT", "API_GATEWAY_RATE_LIMIT],"
      "智能体服务": [XIAOAI_HOST", "XIAOAI_PORT, "XIAOKE_HOST", XIAOKE_PORT", "LAOKE_HOST, "LAOKE_PORT", SOER_HOST", "SOER_PORT],"
      "诊断服务": [LOOK_SERVICE_HOST", "LOOK_SERVICE_PORT, "LISTEN_SERVICE_HOST", LISTEN_SERVICE_PORT", "INQUIRY_SERVICE_HOST, "INQUIRY_SERVICE_PORT", PALPATION_SERVICE_HOST", "PALPATION_SERVICE_PORT, "CALCULATION_SERVICE_HOST", CALCULATION_SERVICE_PORT"],"
      "数据服务: ["HEALTH_DATA_SERVICE_HOST", HEALTH_DATA_SERVICE_PORT", "USER_DATA_SERVICE_HOST, "USER_DATA_SERVICE_PORT", BLOCKCHAIN_SERVICE_HOST", "BLOCKCHAIN_SERVICE_PORT],"
      "数据库配置": [DB_HOST", "DB_PORT, "DB_NAME", DB_USER", "DB_PASSWORD, "DB_SSL", DB_POOL_SIZE"],"
      "Redis配置: ["REDIS_HOST", REDIS_PORT", "REDIS_PASSWORD, "REDIS_DB", REDIS_CLUSTER"],"
      "监控配置: ["PROMETHEUS_ENABLED", PROMETHEUS_HOST", "PROMETHEUS_PORT, "PROMETHEUS_SCRAPE_INTERVAL", GRAFANA_ENABLED", "GRAFANA_HOST, "GRAFANA_PORT", GRAFANA_ADMIN_USER", "GRAFANA_ADMIN_PASSWORD, "TRACING_ENABLED", ALERTING_ENABLED"],"
      "日志配置: ["LOG_FORMAT", LOG_MAX_SIZE", "LOG_MAX_FILES, "LOG_MAX_AGE", STRUCTURED_LOGGING", "LOG_ROTATION],"
      "安全配置": [JWT_SECRET", "JWT_EXPIRES_IN, "JWT_ALGORITHM", CORS_ORIGINS", "CORS_METHODS, "CORS_HEADERS"],"
      性能配置": ["MAX_CONNECTIONS, "MIN_CONNECTIONS", ACQUIRE_TIMEOUT", "IDLE_TIMEOUT, "CACHE_DEFAULT_TTL", CACHE_MAX_MEMORY", "MAX_CONCURRENT, "QUEUE_SIZE"];
    };
    for (const [sectionName, keys] of Object.entries(sections)) {
      configContent += `# ${sectionName}\n`;
      for (const key of keys) {
        if (envConfig[key] !== undefined) {
          configContent += `${key}=${envConfig[key]}\n`;
        }
      }
      configContent += \n";
    }
    return configContent;
  }
  /**
   * 生成Docker配置
   */
  async generateDockerConfig() {"
    this.log("info, "🐳 生成Docker配置文件...");
    // Docker Compose for monitoring stack"
const monitoringCompose = `version: 3.8",
  services: prometheus: ;,
  image: prom/prometheus: latest;,
  container_name: suoke-prometheus;
ports: - "9090:9090",
  volumes:
      - ./deploy/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data: /prometheus;,
  command:"
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - --web.console.libraries=/etc/prometheus/console_libraries"
      - "--web.console.templates=/etc/prometheus/consoles"
      - "--storage.tsdb.retention.time=30d"
      - --web.enable-lifecycle"
    restart: unless-stopped;,
  grafana:
    image: grafana/grafana:latest;,
  container_name: suoke-grafana;
ports: - "3000:3000",
  volumes:
      - grafana_data:/var/lib/grafana
      - ./deploy/monitoring/grafana/provisioning: /etc/grafana/provisioning;,
  environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false;
restart: unless-stopped;,
  jaeger:
    image: jaegertracing/all-in-one:latest;,
  container_name: suoke-jaeger;
ports:"
      - "16686:16686"
      - "14268: 14268",
  environment: - COLLECTOR_ZIPKIN_HTTP_PORT=9411;,
  restart: unless-stopped;
  alertmanager: image: prom/alertmanager:latest;,
  container_name: suoke-alertmanager;
ports: - "9093:9093",
  volumes: - ./deploy/monitoring/alertmanager.yml: /etc/alertmanager/alertmanager.yml;,
  restart: unless-stopped;
node-exporter: image: prom/node-exporter:latest;,
  container_name: suoke-node-exporter;
ports: - "9100:9100",
  volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /: /rootfs: ro;,
  command:"
      - "--path.procfs=/host/proc"
      - "--path.rootfs=/rootfs"
      - --path.sysfs=/host/sys"
      - "--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)
    restart: unless-stopped;,
  volumes:
  prometheus_data:
  grafana_data:
`;
    // Logging stack"
const loggingCompose = `version: "3.8",
  services: elasticsearch: ;,
  image: docker.elastic.co/elasticsearch/elasticsearch: 7.15.0;,
  container_name: suoke-elasticsearch;
environment:
      - discovery.type=single-node"
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports: - "9200:9200",
  volumes: - elasticsearch_data: /usr/share/elasticsearch/data;,
  restart: unless-stopped;
kibana: image: docker.elastic.co/kibana/kibana:7.15.0;,
  container_name: suoke-kibana;
ports: - "5601:5601",
  environment:
      - ELASTICSEARCH_HOSTS=http: // elasticsearch:9200,
  depends_on: - elasticsearch;,
  restart: unless-stopped;
  loki: image: grafana/loki:latest;,
  container_name: suoke-loki;
ports: - "3100:3100",
  volumes: - ./deploy/logging/loki-config.yml: /etc/loki/local-config.yaml;,
  command: -config.file=/etc/loki/local-config.yaml;
restart: unless-stopped;,
  promtail:
    image: grafana/promtail:latest;,
  container_name: suoke-promtail;
volumes:
      - ./logs:/var/log/suoke
      - ./deploy/logging/promtail-config.yml: /etc/promtail/config.yml;,
  command: -config.file=/etc/promtail/config.yml;
restart: unless-stopped;,
  volumes:
  elasticsearch_data:
`;
    // 写入文件"
const monitoringPath = path.join(process.cwd(), deploy", "monitoring, "docker-compose.yml");
    const loggingPath = path.join(process.cwd(), deploy", "logging, "docker-compose.yml");
    fs.writeFileSync(monitoringPath, monitoringCompose);
    fs.writeFileSync(loggingPath, loggingCompose);
    this.log(success", "生成监控Docker配置: deploy/monitoring/docker-compose.yml);
    this.log("success", 生成日志Docker配置: deploy/logging/docker-compose.yml");
    // 生成Prometheus配置
await this.generatePrometheusConfig();
    // 生成Grafana配置
await this.generateGrafanaConfig();
    // 生成日志配置
await this.generateLoggingConfig();
    this.log("success, "✅ Docker配置文件生成完成");
  }
  /**
   * 生成Prometheus配置
   */
  async generatePrometheusConfig() {
    const prometheusConfig = `global: ;,
  scrape_interval: 15s;
evaluation_interval: 15s;,
  rule_files:"
  - "alert_rules.yml"
alerting:
  alertmanagers:
    - static_configs: - targets: - alertmanager:9093;,
  scrape_configs:"
  - job_name: prometheus",
  static_configs:"
      - targets: ["localhost:9090]"
  - job_name: "api-gateway",
  static_configs:"
      - targets: [host.docker.internal:8080"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "agent-xiaoai,
  static_configs:"
      - targets: ["host.docker.internal:8081"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: agent-xiaoke",
  static_configs:"
      - targets: ["host.docker.internal:8082],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "agent-laoke",
  static_configs:"
      - targets: [host.docker.internal:8083"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "agent-soer,
  static_configs:"
      - targets: ["host.docker.internal:8084"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: diagnosis-look",
  static_configs:"
      - targets: ["host.docker.internal:8085],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "diagnosis-listen",
  static_configs:"
      - targets: [host.docker.internal:8086"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "diagnosis-inquiry,
  static_configs:"
      - targets: ["host.docker.internal:8087"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: diagnosis-palpation",
  static_configs:"
      - targets: ["host.docker.internal:8088],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "diagnosis-calculation",
  static_configs:"
      - targets: [host.docker.internal:8089"],
  metrics_path: /metrics;,
  scrape_interval: 15s"
  - job_name: "node-exporter,
  static_configs:"
      - targets: ["node-exporter:9100"]
`;
    const alertRules = `groups:;
  - name: suoke_life_alerts;,
  rules:
      - alert: HighErrorRate;,
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1;
for: 5m;,
  labels:
          severity: warning;,
  annotations:"
          summary: "High error rate detected","
  description: "Error rate is above 10% for 5 minutes"
      - alert: ServiceDown;,
  expr: up == 0;
for: 1m;,
  labels:
          severity: critical;,
  annotations:"
          summary: "Service is down","
  description: "{{ $labels.instance }} has been down for more than 1 minute"
      - alert: HighMemoryUsage;,
  expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9;
for: 5m;,
  labels:
          severity: warning;,
  annotations:"
          summary: "High memory usage","
  description: "Memory usage is above 90% for 5 minutes"
      - alert: HighCPUUsage;,
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80;
for: 5m;,
  labels:
          severity: warning;,
  annotations:"
          summary: "High CPU usage","
  description: "CPU usage is above 80% for 5 minutes"
`;
    const alertManagerConfig = `global: smtp_smarthost: localhost:587","
  smtp_from: "alerts@suoke.life",
  route: group_by: ["alertname"];,
  group_wait: 10s;
group_interval: 10s;,
  repeat_interval: 1h;
receiver: web.hook",
  receivers:"
  - name: "web.hook,
  webhook_configs:"
      - url: "http:// host.docker.internal:8080/alerts",
  send_resolved: true,
  inhibit_rules: - source_match:,"
  severity: critical",
  target_match: severity: "warning,"
  equal: ["alertname", dev", "instance]
`;
    const prometheusPath = path.join(process.cwd(), "deploy", monitoring", "prometheus.yml);
    const alertRulesPath = path.join(process.cwd(), "deploy", monitoring", "alert_rules.yml);
    const alertManagerPath = path.join(process.cwd(), "deploy", monitoring", "alertmanager.yml);
    fs.writeFileSync(prometheusPath, prometheusConfig);
    fs.writeFileSync(alertRulesPath, alertRules);
    fs.writeFileSync(alertManagerPath, alertManagerConfig);
    this.log("success", 生成Prometheus配置文件");
  }
  /**
   * 生成Grafana配置
   */
  async generateGrafanaConfig() {"
    const grafanaDir = path.join(process.cwd(), "deploy, "monitoring", grafana");
    const provisioningDir = path.join(grafanaDir, "provisioning);
    const datasourcesDir = path.join(provisioningDir, "datasources");
    const dashboardsDir = path.join(provisioningDir, dashboards");
    // 创建目录
    [grafanaDir, provisioningDir, datasourcesDir, dashboardsDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
    // 数据源配置
const datasourceConfig = `apiVersion: 1;,
  datasources:
  - name: Prometheus;,
  type: prometheus;
access: proxy;,
  url: http: // prometheus:9090,
  isDefault: true;,
  editable: true
  - name: Jaeger;,
  type: jaeger;
access: proxy;,
  url: http: // jaeger:16686,
  editable: true
`;
    // 仪表板配置
const dashboardConfig = `apiVersion: 1;,
  providers:"
  - name: "default,
  orgId: 1;,
  folder: "Suoke Life",
  type: file;,
  disableDeletion: false;
  updateIntervalSeconds: 10;,
  allowUiUpdates: true;
  options:
      path: /etc/grafana/provisioning/dashboards
`;
    fs.writeFileSync(path.join(datasourcesDir, datasources.yml"), datasourceConfig);
    fs.writeFileSync(path.join(dashboardsDir, "dashboards.yml), dashboardConfig);
    this.log("success", 生成Grafana配置文件");
  }
  /**
   * 生成日志配置
   */
  async generateLoggingConfig() {
    const lokiConfig = `auth_enabled: false;,
  server:
  http_listen_port: 3100;,
  ingester:
  lifecycler: address: 127.0.0.1;,
  ring:
      kvstore: store: inmemory;,
  replication_factor: 1;
final_sleep: 0s;,
  chunk_idle_period: 1h;
max_chunk_age: 1h;,
  chunk_target_size: 1048576;
chunk_retain_period: 30s;,
  max_transfer_retries: 0;
schema_config: configs: - from: 2020-10-24;,
  store: boltdb-shipper;
object_store: filesystem;,
  schema: v11;
index: prefix: index_;,
  period: 24h;
storage_config: boltdb_shipper:,
  active_index_directory: /loki/boltdb-shipper-active;,
  cache_location: /loki/boltdb-shipper-cache;
  cache_ttl: 24h;,
  shared_store: filesystem;
  filesystem: directory: /loki/chunks;,
  limits_config:
  reject_old_samples: true;,
  reject_old_samples_max_age: 168h;
chunk_store_config: max_look_back_period: 0s;,
  table_manager:
  retention_deletes_enabled: false;,
  retention_period: 0s;
ruler: storage:,
  type: local;,
  local: directory: /loki/rules;,
  rule_path: /loki/rules-temp;
alertmanager_url: http:// alertmanager:9093,
  ring: kvstore: store: inmemory;,
  enable_api: true
`;
    const promtailConfig = `server: ;,
  http_listen_port: 9080;
grpc_listen_port: 0;,
  positions:
  filename: /tmp/positions.yaml;,
  clients:
  - url: http:// loki:3100/loki/api/v1/push,
  scrape_configs: - job_name: suoke-logs;,
  static_configs:
      - targets: - localhost;,
  labels:
          job: suoke-life;,
  __path__: /var/log/suoke/*.log
`;
    const lokiPath = path.join(process.cwd(), "deploy, "logging", loki-config.yml");
    const promtailPath = path.join(process.cwd(), "deploy, "logging", promtail-config.yml");
    fs.writeFileSync(lokiPath, lokiConfig);
    fs.writeFileSync(promtailPath, promtailConfig);
    this.log("success, "生成日志系统配置文件");
  }
  /**
   * 部署监控系统
   */
  async deployMonitoring() {"
    this.log(info", "📊 部署监控系统...);
    const monitoringDir = path.join(process.cwd(), "deploy", monitoring");
    // 启动监控服务
const result = await this.executeCommand(
      `cd ${monitoringDir} && docker-compose up -d`,"
      "启动监控服务容器;
    );
    if (!result.success) {"
      throw new Error("监控系统部署失败");
    }
    // 等待服务启动"
this.log(info", "等待监控服务启动...);
    await new Promise(resolve => setTimeout(resolve, 10000));
    // 检查服务状态"
const services = ["prometheus", grafana", "jaeger, "alertmanager", node-exporter"];
    for (const service of services) {
      const checkResult = await this.executeCommand("
        `docker ps --filter "name=suoke-${service}" --format "table {{.Names}}\\t{{.Status}}"`,
        `检查 ${service} 服务状态`;
      );
      if (checkResult.success && checkResult.output.includes("Up)) {"
        this.log("success", `${service} 服务运行正常`);
      } else {"
        this.log(warning", `${service} 服务可能未正常启动`);
      }
    }
    this.log("success, "✅ 监控系统部署完成");
    this.log(info", "监控服务访问地址:);
    this.log("info",   - Prometheus: http:// localhost:9090")"
    this.log("info, "  - Grafana: http:// localhost:3000 (admin/admin)")"
    this.log(info", "  - Jaeger: http:// localhost:16686)"
    this.log("info",   - AlertManager: http:// localhost:9093")
  }
  /**
   * 部署日志系统
   */
  async deployLogging() {"
    this.log("info, "📝 部署日志系统...");
    const loggingDir = path.join(process.cwd(), deploy", "logging);
    // 启动日志服务
const result = await this.executeCommand(
      `cd ${loggingDir} && docker-compose up -d`,"
      "启动日志服务容器";
    );
    if (!result.success) {"
      throw new Error(日志系统部署失败");
    }
    // 等待服务启动"
this.log("info, "等待日志服务启动...");
    await new Promise(resolve => setTimeout(resolve, 15000));
    // 检查服务状态"
const services = [elasticsearch", "kibana, "loki", promtail"];
    for (const service of services) {
      const checkResult = await this.executeCommand("
        `docker ps --filter "name=suoke-${service}" --format "table {{.Names}}\\t{{.Status}}"`,
        `检查 ${service} 服务状态`;
      );
      if (checkResult.success && checkResult.output.includes("Up)) {"
        this.log("success", `${service} 服务运行正常`);
      } else {"
        this.log(warning", `${service} 服务可能未正常启动`);
      }
    }
    this.log("success, "✅ 日志系统部署完成");
    this.log(info", "日志服务访问地址:);
    this.log("info",   - Elasticsearch: http:// localhost:9200")"
    this.log("info, "  - Kibana: http:// localhost:5601")"
    this.log(info", "  - Loki: http:// localhost:3100)
  }
  /**
   * 验证部署
   */
  async validateDeployment() {"
    this.log("info", 🔍 验证部署状态...");
    const checks = [
      {"
        name: "Prometheus,"
        url: "http:// localhost:9090/-/healthy",
        timeout: 5000
      },
      {"
        name: Grafana","
        url: "http://localhost:3000/api/health,
        timeout: 5000
      },
      {"
        name: "Jaeger","
        url: http://localhost:16686",
        timeout: 5000
      },
      {"
        name: "Elasticsearch,"
        url: "http://localhost:9200/_cluster/health",
        timeout: 10000
      },
      {"
        name: Loki","
        url: "http://localhost:3100/ready,
        timeout: 5000
      }
    ];
    let allHealthy = true;
    for (const check of checks) {
      try {
        const result = await this.executeCommand("
          `curl -s -o /dev/null -w "%{http_code}" --max-time 5 ${check.url}`,
          `检查 ${check.name} 健康状态`;
        );
        if (result.success && (result.output.includes("200") || result.output.includes(000"))) {"
          this.log("success, `${check.name} 健康检查通过`);
        } else {"
          this.log("warning", `${check.name} 健康检查失败`);
          allHealthy = false;
        }
      } catch (error) {"
        this.log(warning", `${check.name} 健康检查异常: ${error.message}`);
        allHealthy = false;
      }
    }
    if (allHealthy) {"
      this.log("success, "✅ 所有服务健康检查通过");
    } else {"
      this.log(warning", "⚠️ 部分服务健康检查未通过，请检查服务状态);
    }
    return allHealthy;
  }
  /**
   * 生成部署报告
   */
  generateDeploymentReport() {
    const endTime = Date.now();
    const duration = endTime - this.startTime;
    const report = {
      deploymentInfo: {,
  startTime: new Date(this.startTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        duration: `${Math.round(duration / 1000)}秒`,"
        status: this.errors.length === 0 ? "success" : partial"
      },
      summary: {,
  totalSteps: this.deploymentLog.length,"
        successSteps: this.deploymentLog.filter(log => log.level === "success).length,
        errors: this.errors.length,
        warnings: this.warnings.length
      },
      services: {,
  monitoring: {",
  prometheus: "http:// localhost:9090","
          grafana: http://localhost:3000","
          jaeger: "http://localhost:16686,"
          alertmanager: "http://localhost:9093"
        },
        logging: {,"
  elasticsearch: http://localhost:9200","
          kibana: "http://localhost:5601,"
          loki: "http://localhost:3100"
        }
      },
      nextSteps: ["
        1. 访问Grafana (http://localhost:3000) 配置仪表板","
        "2. 访问Kibana (http://localhost:5601) 配置日志索引,"
        "3. 检查Prometheus (http://localhost:9090) 目标状态","
        4. 配置告警规则和通知渠道","
        "5. 启动应用服务并验证监控数据
      ],
      errors: this.errors,
      warnings: this.warnings,
      fullLog: this.deploymentLog
    };
    // 保存报告"
const reportPath = path.join(process.cwd(), "infrastructure-deployment-report.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    // 生成Markdown报告
const markdownReport = this.generateMarkdownReport(report);
    const markdownPath = path.join(process.cwd(), INFRASTRUCTURE_DEPLOYMENT_REPORT.md");
    fs.writeFileSync(markdownPath, markdownReport);
    this.log("success, `部署报告已生成: ${reportPath}`);
    this.log("success", `Markdown报告已生成: ${markdownPath}`);
    return report;
  }
  /**
   * 生成Markdown报告
   */
  generateMarkdownReport(report) {
    return `# 索克生活基础设施部署报告
## 部署概要
- **开始时间**: ${report.deploymentInfo.startTime}
- **结束时间**: ${report.deploymentInfo.endTime}
- **部署时长**: ${report.deploymentInfo.duration}
- **部署状态**: ${report.deploymentInfo.status === success" ? "✅ 成功 : "⚠️ 部分成功"}
## 统计信息
- **总步骤数**: ${report.summary.totalSteps}
- **成功步骤**: ${report.summary.successSteps}
- **错误数量**: ${report.summary.errors}
- **警告数量**: ${report.summary.warnings}
## 服务访问地址
### 监控服务
- **Prometheus**: [${report.services.monitoring.prometheus}](${report.services.monitoring.prometheus});
- **Grafana**: [${report.services.monitoring.grafana}](${report.services.monitoring.grafana}) (admin/admin)
- **Jaeger**: [${report.services.monitoring.jaeger}](${report.services.monitoring.jaeger});
- **AlertManager**: [${report.services.monitoring.alertmanager}](${report.services.monitoring.alertmanager});
### 日志服务
- **Elasticsearch**: [${report.services.logging.elasticsearch}](${report.services.logging.elasticsearch});
- **Kibana**: [${report.services.logging.kibana}](${report.services.logging.kibana});
- **Loki**: [${report.services.logging.loki}](${report.services.logging.loki});
## 后续步骤"
${report.nextSteps.map(step => `- ${step}`).join(\n")}
## 错误信息"
${report.errors.length === 0 ? "无错误 : report.errors.map(error => `- **${error.timestamp}**: ${error.message}`).join("\n")}
## 警告信息"
${report.warnings.length === 0 ? 无警告" : report.warnings.map(warning => `- **${warning.timestamp}**: ${warning.message}`).join("\n)}
---
*报告生成时间: ${new Date().toISOString()}*
`;
  }
  /**
   * 主部署流程
   */
  async deploy() {
    try {"
      this.log("info", 🚀 开始索克生活基础设施部署...");
      // 1. 检查先决条件
await this.checkPrerequisites();
      // 2. 创建目录结构
await this.createDirectoryStructure();
      // 3. 生成环境配置
await this.generateEnvironmentConfig();
      // 4. 生成Docker配置
await this.generateDockerConfig();
      // 5. 部署监控系统
await this.deployMonitoring();
      // 6. 部署日志系统
await this.deployLogging();
      // 7. 验证部署
await this.validateDeployment();
      // 8. 生成报告
const report = this.generateDeploymentReport();
      this.log("success, "🎉 基础设施部署完成！");
      this.log(info", `部署耗时: ${report.deploymentInfo.duration}`);
      this.log("info, `错误数量: ${report.summary.errors}`);
      this.log("info", `警告数量: ${report.summary.warnings}`);
      return report;
    } catch (error) {"
      this.log(error", `部署失败: ${error.message}`, error);
      // 生成失败报告
const report = this.generateDeploymentReport();
      throw error;
    }
  }
}
// 主执行函数
async function main() {
  const deployment = new InfrastructureDeployment();
  try {
    const report = await deployment.deploy();
    process.exit(0);
  } catch (error) {
    process.exit(1);
  }
}
// 如果直接运行此脚本
if (require.main === module) {
  main();
}
module.exports = InfrastructureDeployment;
