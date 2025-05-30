import EnvironmentManager from "../config/EnvironmentManager";
import MonitoringService from "../../services/monitoring/MonitoringService";

/**
 * 索克生活监控系统部署服务
 * 集成Prometheus、Grafana、Jaeger等监控组件
 */

export interface MonitoringStack {
  /** Prometheus配置 */
  prometheus: PrometheusConfig;
  /** Grafana配置 */
  grafana: GrafanaConfig;
  /** Jaeger配置 */
  jaeger: JaegerConfig;
  /** AlertManager配置 */
  alertManager: AlertManagerConfig;
  /** Node Exporter配置 */
  nodeExporter: NodeExporterConfig;
}

export interface PrometheusConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 服务地址 */
  endpoint: string;
  /** 抓取间隔 */
  scrapeInterval: string;
  /** 数据保留时间 */
  retention: string;
  /** 存储配置 */
  storage: {
    path: string;
    size: string;
  };
  /** 抓取目标 */
  scrapeConfigs: ScrapeConfig[];
}

export interface ScrapeConfig {
  /** 任务名称 */
  jobName: string;
  /** 抓取间隔 */
  scrapeInterval: string;
  /** 目标地址 */
  staticConfigs: Array<{
    targets: string[];
    labels?: Record<string, string>;
  }>;
  /** 指标路径 */
  metricsPath: string;
}

export interface GrafanaConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 服务地址 */
  endpoint: string;
  /** 管理员用户 */
  adminUser: string;
  /** 管理员密码 */
  adminPassword: string;
  /** 数据源配置 */
  datasources: GrafanaDatasource[];
  /** 仪表板配置 */
  dashboards: GrafanaDashboard[];
}

export interface GrafanaDatasource {
  /** 数据源名称 */
  name: string;
  /** 数据源类型 */
  type: "prometheus" | "jaeger" | "elasticsearch" | "loki";
  /** 数据源URL */
  url: string;
  /** 是否默认 */
  isDefault: boolean;
  /** 访问模式 */
  access: "proxy" | "direct";
}

export interface GrafanaDashboard {
  /** 仪表板ID */
  id: string;
  /** 仪表板标题 */
  title: string;
  /** 仪表板描述 */
  description: string;
  /** 仪表板JSON配置 */
  json: any;
  /** 文件夹 */
  folder: string;
}

export interface JaegerConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 收集器端点 */
  collectorEndpoint: string;
  /** 查询端点 */
  queryEndpoint: string;
  /** 采样率 */
  samplingRate: number;
  /** 存储配置 */
  storage: {
    type: "memory" | "elasticsearch" | "cassandra";
    config: Record<string, any>;
  };
}

export interface AlertManagerConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 服务端点 */
  endpoint: string;
  /** 告警路由 */
  routes: AlertRoute[];
  /** 接收器 */
  receivers: AlertReceiver[];
}

export interface AlertRoute {
  /** 匹配条件 */
  match: Record<string, string>;
  /** 接收器名称 */
  receiver: string;
  /** 分组等待时间 */
  groupWait: string;
  /** 分组间隔 */
  groupInterval: string;
  /** 重复间隔 */
  repeatInterval: string;
}

export interface AlertReceiver {
  /** 接收器名称 */
  name: string;
  /** Webhook配置 */
  webhookConfigs?: Array<{
    url: string;
    sendResolved: boolean;
  }>;
  /** 邮件配置 */
  emailConfigs?: Array<{
    to: string[];
    subject: string;
    body: string;
  }>;
  /** 钉钉配置 */
  dingdingConfigs?: Array<{
    webhook: string;
    title: string;
    text: string;
  }>;
}

export interface NodeExporterConfig {
  /** 是否启用 */
  enabled: boolean;
  /** 监听端口 */
  port: number;
  /** 收集器 */
  collectors: string[];
}

export interface DeploymentStatus {
  /** 组件名称 */
  component: string;
  /** 部署状态 */
  status: "pending" | "deploying" | "running" | "failed" | "stopped";
  /** 健康状态 */
  health: "healthy" | "unhealthy" | "unknown";
  /** 启动时间 */
  startTime?: number;
  /** 错误信息 */
  error?: string;
  /** 端点URL */
  endpoint?: string;
}

export class MonitoringDeployment {
  private static instance: MonitoringDeployment;
  private envManager: EnvironmentManager;
  private monitoringService: MonitoringService;
  private deploymentStatus: Map<string, DeploymentStatus>;
  private monitoringStack: MonitoringStack;

  private constructor() {
    this.envManager = EnvironmentManager.getInstance();
    this.monitoringService = MonitoringService.getInstance();
    this.deploymentStatus = new Map();
    this.monitoringStack = this.initializeMonitoringStack();
  }

  static getInstance(): MonitoringDeployment {
    if (!MonitoringDeployment.instance) {
      MonitoringDeployment.instance = new MonitoringDeployment();
    }
    return MonitoringDeployment.instance;
  }

  /**
   * 初始化监控栈配置
   */
  private initializeMonitoringStack(): MonitoringStack {
    const config = this.envManager.getConfig();

    return {
      prometheus: {
        enabled: config.monitoring.prometheus.enabled,
        endpoint: `http://${config.monitoring.prometheus.host}:${config.monitoring.prometheus.port}`,
        scrapeInterval: `${config.monitoring.prometheus.scrapeInterval}s`,
        retention: "30d",
        storage: {
          path: "/prometheus/data",
          size: "10GB",
        },
        scrapeConfigs: this.generateScrapeConfigs(),
      },
      grafana: {
        enabled: config.monitoring.grafana.enabled,
        endpoint: `http://${config.monitoring.grafana.host}:${config.monitoring.grafana.port}`,
        adminUser: config.monitoring.grafana.adminUser,
        adminPassword: config.monitoring.grafana.adminPassword,
        datasources: this.generateGrafanaDatasources(),
        dashboards: this.generateGrafanaDashboards(),
      },
      jaeger: {
        enabled: config.monitoring.tracing.enabled,
        collectorEndpoint:
          config.monitoring.tracing.jaegerEndpoint || "http://localhost:14268",
        queryEndpoint: "http://localhost:16686",
        samplingRate: config.monitoring.tracing.samplingRate,
        storage: {
          type: "memory",
          config: {},
        },
      },
      alertManager: {
        enabled: config.monitoring.alerting.enabled,
        endpoint: "http://localhost:9093",
        routes: this.generateAlertRoutes(),
        receivers: this.generateAlertReceivers(),
      },
      nodeExporter: {
        enabled: true,
        port: 9100,
        collectors: ["cpu", "memory", "disk", "network", "filesystem"],
      },
    };
  }

  /**
   * 生成Prometheus抓取配置
   */
  private generateScrapeConfigs(): ScrapeConfig[] {
    const config = this.envManager.getConfig();
    const scrapeConfigs: ScrapeConfig[] = [];

    // API网关监控
    scrapeConfigs.push({
      jobName: "api-gateway",
      scrapeInterval: "15s",
      metricsPath: "/metrics",
      staticConfigs: [
        {
          targets: [
            `${config.services.apiGateway.host}:${config.services.apiGateway.port}`,
          ],
          labels: { service: "api-gateway" },
        },
      ],
    });

    // 智能体服务监控
    Object.entries(config.services.agents).forEach(([name, agent]) => {
      scrapeConfigs.push({
        jobName: `agent-${name}`,
        scrapeInterval: "15s",
        metricsPath: "/metrics",
        staticConfigs: [
          {
            targets: [`${agent.host}:${agent.port}`],
            labels: { service: `agent-${name}`, type: "agent" },
          },
        ],
      });
    });

    // 诊断服务监控
    Object.entries(config.services.diagnosis).forEach(([name, service]) => {
      scrapeConfigs.push({
        jobName: `diagnosis-${name}`,
        scrapeInterval: "15s",
        metricsPath: "/metrics",
        staticConfigs: [
          {
            targets: [`${service.host}:${service.port}`],
            labels: { service: `diagnosis-${name}`, type: "diagnosis" },
          },
        ],
      });
    });

    // 数据服务监控
    Object.entries(config.services.data).forEach(([name, service]) => {
      scrapeConfigs.push({
        jobName: `data-${name}`,
        scrapeInterval: "15s",
        metricsPath: "/metrics",
        staticConfigs: [
          {
            targets: [`${service.host}:${service.port}`],
            labels: { service: `data-${name}`, type: "data" },
          },
        ],
      });
    });

    // Node Exporter监控
    scrapeConfigs.push({
      jobName: "node-exporter",
      scrapeInterval: "15s",
      metricsPath: "/metrics",
      staticConfigs: [
        {
          targets: ["localhost:9100"],
          labels: { service: "node-exporter", type: "infrastructure" },
        },
      ],
    });

    return scrapeConfigs;
  }

  /**
   * 生成Grafana数据源配置
   */
  private generateGrafanaDatasources(): GrafanaDatasource[] {
    return [
      {
        name: "Prometheus",
        type: "prometheus",
        url: this.monitoringStack.prometheus.endpoint,
        isDefault: true,
        access: "proxy",
      },
      {
        name: "Jaeger",
        type: "jaeger",
        url: this.monitoringStack.jaeger.queryEndpoint,
        isDefault: false,
        access: "proxy",
      },
    ];
  }

  /**
   * 生成Grafana仪表板配置
   */
  private generateGrafanaDashboards(): GrafanaDashboard[] {
    return [
      {
        id: "suoke-overview",
        title: "索克生活系统概览",
        description: "系统整体监控仪表板",
        folder: "Suoke Life",
        json: this.generateOverviewDashboard(),
      },
      {
        id: "suoke-agents",
        title: "智能体监控",
        description: "四个智能体的性能监控",
        folder: "Suoke Life",
        json: this.generateAgentsDashboard(),
      },
      {
        id: "suoke-diagnosis",
        title: "诊断服务监控",
        description: "五诊服务的性能监控",
        folder: "Suoke Life",
        json: this.generateDiagnosisDashboard(),
      },
      {
        id: "suoke-infrastructure",
        title: "基础设施监控",
        description: "系统资源和基础设施监控",
        folder: "Suoke Life",
        json: this.generateInfrastructureDashboard(),
      },
    ];
  }

  /**
   * 生成告警路由配置
   */
  private generateAlertRoutes(): AlertRoute[] {
    return [
      {
        match: { severity: "critical" },
        receiver: "critical-alerts",
        groupWait: "10s",
        groupInterval: "5m",
        repeatInterval: "12h",
      },
      {
        match: { severity: "warning" },
        receiver: "warning-alerts",
        groupWait: "30s",
        groupInterval: "10m",
        repeatInterval: "24h",
      },
      {
        match: { service: "agent" },
        receiver: "agent-alerts",
        groupWait: "15s",
        groupInterval: "5m",
        repeatInterval: "6h",
      },
    ];
  }

  /**
   * 生成告警接收器配置
   */
  private generateAlertReceivers(): AlertReceiver[] {
    const config = this.envManager.getConfig();
    const receivers: AlertReceiver[] = [];

    // Webhook接收器
    if (config.monitoring.alerting.webhookUrl) {
      receivers.push({
        name: "critical-alerts",
        webhookConfigs: [
          {
            url: config.monitoring.alerting.webhookUrl,
            sendResolved: true,
          },
        ],
      });
    }

    // 邮件接收器
    if (config.monitoring.alerting.emailConfig) {
      receivers.push({
        name: "warning-alerts",
        emailConfigs: [
          {
            to: ["admin@suoke.life"],
            subject: "索克生活告警: {{ .GroupLabels.alertname }}",
            body: "告警详情: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}",
          },
        ],
      });
    }

    // 智能体专用接收器
    receivers.push({
      name: "agent-alerts",
      webhookConfigs: [
        {
          url:
            config.monitoring.alerting.webhookUrl ||
            "http://localhost:8080/alerts",
          sendResolved: true,
        },
      ],
    });

    return receivers;
  }

  /**
   * 部署监控栈
   */
  async deployMonitoringStack(): Promise<void> {
    console.log("🚀 开始部署监控系统...");

    try {
      // 部署Prometheus
      if (this.monitoringStack.prometheus.enabled) {
        await this.deployPrometheus();
      }

      // 部署Grafana
      if (this.monitoringStack.grafana.enabled) {
        await this.deployGrafana();
      }

      // 部署Jaeger
      if (this.monitoringStack.jaeger.enabled) {
        await this.deployJaeger();
      }

      // 部署AlertManager
      if (this.monitoringStack.alertManager.enabled) {
        await this.deployAlertManager();
      }

      // 部署Node Exporter
      if (this.monitoringStack.nodeExporter.enabled) {
        await this.deployNodeExporter();
      }

      console.log("✅ 监控系统部署完成");
    } catch (error) {
      console.error("❌ 监控系统部署失败:", error);
      throw error;
    }
  }

  /**
   * 部署Prometheus
   */
  private async deployPrometheus(): Promise<void> {
    console.log("📊 部署Prometheus...");

    this.updateDeploymentStatus("prometheus", {
      component: "prometheus",
      status: "deploying",
      health: "unknown",
    });

    try {
      // 生成Prometheus配置文件
      const prometheusConfig = this.generatePrometheusConfig();

      // 模拟部署过程
      await new Promise((resolve) => setTimeout(resolve, 2000));

      this.updateDeploymentStatus("prometheus", {
        component: "prometheus",
        status: "running",
        health: "healthy",
        startTime: Date.now(),
        endpoint: this.monitoringStack.prometheus.endpoint,
      });

      console.log("✅ Prometheus部署成功");
    } catch (error) {
      this.updateDeploymentStatus("prometheus", {
        component: "prometheus",
        status: "failed",
        health: "unhealthy",
        error: error instanceof Error ? error.message : "部署失败",
      });
      throw error;
    }
  }

  /**
   * 部署Grafana
   */
  private async deployGrafana(): Promise<void> {
    console.log("📈 部署Grafana...");

    this.updateDeploymentStatus("grafana", {
      component: "grafana",
      status: "deploying",
      health: "unknown",
    });

    try {
      // 模拟部署过程
      await new Promise((resolve) => setTimeout(resolve, 3000));

      // 配置数据源
      await this.configureGrafanaDatasources();

      // 导入仪表板
      await this.importGrafanaDashboards();

      this.updateDeploymentStatus("grafana", {
        component: "grafana",
        status: "running",
        health: "healthy",
        startTime: Date.now(),
        endpoint: this.monitoringStack.grafana.endpoint,
      });

      console.log("✅ Grafana部署成功");
    } catch (error) {
      this.updateDeploymentStatus("grafana", {
        component: "grafana",
        status: "failed",
        health: "unhealthy",
        error: error instanceof Error ? error.message : "部署失败",
      });
      throw error;
    }
  }

  /**
   * 部署Jaeger
   */
  private async deployJaeger(): Promise<void> {
    console.log("🔍 部署Jaeger...");

    this.updateDeploymentStatus("jaeger", {
      component: "jaeger",
      status: "deploying",
      health: "unknown",
    });

    try {
      // 模拟部署过程
      await new Promise((resolve) => setTimeout(resolve, 2500));

      this.updateDeploymentStatus("jaeger", {
        component: "jaeger",
        status: "running",
        health: "healthy",
        startTime: Date.now(),
        endpoint: this.monitoringStack.jaeger.queryEndpoint,
      });

      console.log("✅ Jaeger部署成功");
    } catch (error) {
      this.updateDeploymentStatus("jaeger", {
        component: "jaeger",
        status: "failed",
        health: "unhealthy",
        error: error instanceof Error ? error.message : "部署失败",
      });
      throw error;
    }
  }

  /**
   * 部署AlertManager
   */
  private async deployAlertManager(): Promise<void> {
    console.log("🚨 部署AlertManager...");

    this.updateDeploymentStatus("alertmanager", {
      component: "alertmanager",
      status: "deploying",
      health: "unknown",
    });

    try {
      // 模拟部署过程
      await new Promise((resolve) => setTimeout(resolve, 1500));

      this.updateDeploymentStatus("alertmanager", {
        component: "alertmanager",
        status: "running",
        health: "healthy",
        startTime: Date.now(),
        endpoint: this.monitoringStack.alertManager.endpoint,
      });

      console.log("✅ AlertManager部署成功");
    } catch (error) {
      this.updateDeploymentStatus("alertmanager", {
        component: "alertmanager",
        status: "failed",
        health: "unhealthy",
        error: error instanceof Error ? error.message : "部署失败",
      });
      throw error;
    }
  }

  /**
   * 部署Node Exporter
   */
  private async deployNodeExporter(): Promise<void> {
    console.log("🖥️ 部署Node Exporter...");

    this.updateDeploymentStatus("node-exporter", {
      component: "node-exporter",
      status: "deploying",
      health: "unknown",
    });

    try {
      // 模拟部署过程
      await new Promise((resolve) => setTimeout(resolve, 1000));

      this.updateDeploymentStatus("node-exporter", {
        component: "node-exporter",
        status: "running",
        health: "healthy",
        startTime: Date.now(),
        endpoint: `http://localhost:${this.monitoringStack.nodeExporter.port}`,
      });

      console.log("✅ Node Exporter部署成功");
    } catch (error) {
      this.updateDeploymentStatus("node-exporter", {
        component: "node-exporter",
        status: "failed",
        health: "unhealthy",
        error: error instanceof Error ? error.message : "部署失败",
      });
      throw error;
    }
  }

  /**
   * 更新部署状态
   */
  private updateDeploymentStatus(
    component: string,
    status: DeploymentStatus
  ): void {
    this.deploymentStatus.set(component, status);
  }

  /**
   * 生成Prometheus配置
   */
  private generatePrometheusConfig(): any {
    return {
      global: {
        scrape_interval: this.monitoringStack.prometheus.scrapeInterval,
        evaluation_interval: "15s",
      },
      scrape_configs: this.monitoringStack.prometheus.scrapeConfigs.map(
        (config) => ({
          job_name: config.jobName,
          scrape_interval: config.scrapeInterval,
          metrics_path: config.metricsPath,
          static_configs: config.staticConfigs,
        })
      ),
    };
  }

  /**
   * 配置Grafana数据源
   */
  private async configureGrafanaDatasources(): Promise<void> {
    // 模拟配置数据源
    await new Promise((resolve) => setTimeout(resolve, 500));
    console.log("📊 Grafana数据源配置完成");
  }

  /**
   * 导入Grafana仪表板
   */
  private async importGrafanaDashboards(): Promise<void> {
    // 模拟导入仪表板
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("📈 Grafana仪表板导入完成");
  }

  /**
   * 生成仪表板配置
   */
  private generateOverviewDashboard(): any {
    return {
      dashboard: {
        title: "索克生活系统概览",
        panels: [
          {
            title: "系统健康状态",
            type: "stat",
            targets: [{ expr: "up" }],
          },
          {
            title: "请求响应时间",
            type: "graph",
            targets: [{ expr: "http_request_duration_seconds" }],
          },
          {
            title: "错误率",
            type: "graph",
            targets: [{ expr: 'rate(http_requests_total{status=~"5.."}[5m])' }],
          },
        ],
      },
    };
  }

  private generateAgentsDashboard(): any {
    return {
      dashboard: {
        title: "智能体监控",
        panels: [
          {
            title: "智能体状态",
            type: "table",
            targets: [{ expr: 'up{type="agent"}' }],
          },
          {
            title: "智能体响应时间",
            type: "graph",
            targets: [{ expr: 'agent_response_time{type="agent"}' }],
          },
        ],
      },
    };
  }

  private generateDiagnosisDashboard(): any {
    return {
      dashboard: {
        title: "诊断服务监控",
        panels: [
          {
            title: "诊断服务状态",
            type: "table",
            targets: [{ expr: 'up{type="diagnosis"}' }],
          },
          {
            title: "诊断准确率",
            type: "graph",
            targets: [{ expr: "diagnosis_accuracy_rate" }],
          },
        ],
      },
    };
  }

  private generateInfrastructureDashboard(): any {
    return {
      dashboard: {
        title: "基础设施监控",
        panels: [
          {
            title: "CPU使用率",
            type: "graph",
            targets: [{ expr: "node_cpu_seconds_total" }],
          },
          {
            title: "内存使用率",
            type: "graph",
            targets: [{ expr: "node_memory_MemAvailable_bytes" }],
          },
        ],
      },
    };
  }

  /**
   * 获取部署状态
   */
  getDeploymentStatus(): Map<string, DeploymentStatus> {
    return this.deploymentStatus;
  }

  /**
   * 获取监控栈配置
   */
  getMonitoringStack(): MonitoringStack {
    return this.monitoringStack;
  }

  /**
   * 检查监控系统健康状态
   */
  async checkHealth(): Promise<{
    overall: "healthy" | "degraded" | "unhealthy";
    components: Record<string, "healthy" | "unhealthy" | "unknown">;
  }> {
    const components: Record<string, "healthy" | "unhealthy" | "unknown"> = {};
    let healthyCount = 0;
    let totalCount = 0;

    for (const [name, status] of this.deploymentStatus.entries()) {
      components[name] = status.health;
      totalCount++;
      if (status.health === "healthy") {
        healthyCount++;
      }
    }

    let overall: "healthy" | "degraded" | "unhealthy";
    if (healthyCount === totalCount) {
      overall = "healthy";
    } else if (healthyCount > totalCount / 2) {
      overall = "degraded";
    } else {
      overall = "unhealthy";
    }

    return { overall, components };
  }

  /**
   * 重启监控组件
   */
  async restartComponent(component: string): Promise<void> {
    const status = this.deploymentStatus.get(component);
    if (!status) {
      throw new Error(`组件不存在: ${component}`);
    }

    console.log(`🔄 重启监控组件: ${component}`);

    this.updateDeploymentStatus(component, {
      ...status,
      status: "deploying",
      health: "unknown",
    });

    // 模拟重启过程
    await new Promise((resolve) => setTimeout(resolve, 2000));

    this.updateDeploymentStatus(component, {
      ...status,
      status: "running",
      health: "healthy",
      startTime: Date.now(),
    });

    console.log(`✅ 组件重启成功: ${component}`);
  }

  /**
   * 停止监控组件
   */
  async stopComponent(component: string): Promise<void> {
    const status = this.deploymentStatus.get(component);
    if (!status) {
      throw new Error(`组件不存在: ${component}`);
    }

    console.log(`⏹️ 停止监控组件: ${component}`);

    this.updateDeploymentStatus(component, {
      ...status,
      status: "stopped",
      health: "unknown",
    });

    console.log(`✅ 组件停止成功: ${component}`);
  }
}

export default MonitoringDeployment;
