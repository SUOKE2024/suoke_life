import AsyncStorage from "@react-native-async-storage/async-storage";
import { Alert } from "react-native";



// 监控数据类型定义
export interface SystemMetrics {
  timestamp: number;
  performance: {
    memoryUsage: number;
    cpuUsage: number;
    networkLatency: number;
    renderTime: number;
    apiResponseTime: number;
  };
  errors: {
    count: number;
    types: Record<string, number>;
    lastError?: ErrorInfo;
  };
  user: {
    activeTime: number;
    screenViews: Record<string, number>;
    interactions: number;
  };
  business: {
    farmProductViews: number;
    wellnessBookings: number;
    nutritionPlanSelections: number;
    blockchainVerifications: number;
  };
}

export interface ErrorInfo {
  message: string;
  stack?: string;
  timestamp: number;
  screen: string;
  userId?: string;
  severity: "low" | "medium" | "high" | "critical";
  context?: Record<string, any>;
}

export interface AlertRule {
  id: string;
  name: string;
  metric: string;
  threshold: number;
  operator: ">" | "<" | "=" | ">=" | "<=";
  enabled: boolean;
  cooldown: number; // 冷却时间（毫秒）
  lastTriggered?: number;
  actions: AlertAction[];
}

export interface AlertAction {
  type: "notification" | "log" | "api_call" | "user_notification";
  config: Record<string, any>;
}

export interface HealthCheckResult {
  service: string;
  status: "healthy" | "degraded" | "unhealthy";
  responseTime: number;
  lastCheck: number;
  details?: Record<string, any>;
}

// 性能监控类
class PerformanceTracker {
  private static instance: PerformanceTracker;
  private metrics: SystemMetrics[] = [];
  private maxMetricsHistory = 1000;

  static getInstance(): PerformanceTracker {
    if (!PerformanceTracker.instance) {
      PerformanceTracker.instance = new PerformanceTracker();
    }
    return PerformanceTracker.instance;
  }

  recordMetric(metric: Partial<SystemMetrics>): void {
    const timestamp = Date.now();
    const currentMetric: SystemMetrics = {
      timestamp,
      performance: {
        memoryUsage: 0,
        cpuUsage: 0,
        networkLatency: 0,
        renderTime: 0,
        apiResponseTime: 0,
        ...metric.performance,
      },
      errors: {
        count: 0,
        types: {},
        ...metric.errors,
      },
      user: {
        activeTime: 0,
        screenViews: {},
        interactions: 0,
        ...metric.user,
      },
      business: {
        farmProductViews: 0,
        wellnessBookings: 0,
        nutritionPlanSelections: 0,
        blockchainVerifications: 0,
        ...metric.business,
      },
    };

    this.metrics.push(currentMetric);

    // 保持历史记录在限制范围内
    if (this.metrics.length > this.maxMetricsHistory) {
      this.metrics.splice(0, this.metrics.length - this.maxMetricsHistory);
    }

    // 持久化最新指标
    this.persistMetrics();
  }

  getMetrics(timeRange?: { start: number; end: number }): SystemMetrics[] {
    if (!timeRange) {
      return [...this.metrics];
    }

    return this.metrics.filter(
      (metric) =>
        metric.timestamp >= timeRange.start && metric.timestamp <= timeRange.end
    );
  }

  getAverageMetrics(timeRange?: {
    start: number;
    end: number;
  }): Partial<SystemMetrics> {
    const metrics = this.getMetrics(timeRange);
    if (metrics.length === 0) {
      return {};
    }

    const sum = metrics.reduce(
      (acc, metric) => ({
        performance: {
          memoryUsage:
            acc.performance.memoryUsage + metric.performance.memoryUsage,
          cpuUsage: acc.performance.cpuUsage + metric.performance.cpuUsage,
          networkLatency:
            acc.performance.networkLatency + metric.performance.networkLatency,
          renderTime:
            acc.performance.renderTime + metric.performance.renderTime,
          apiResponseTime:
            acc.performance.apiResponseTime +
            metric.performance.apiResponseTime,
        },
        errors: {
          count: acc.errors.count + metric.errors.count,
          types: acc.errors.types,
        },
        user: {
          activeTime: acc.user.activeTime + metric.user.activeTime,
          screenViews: acc.user.screenViews,
          interactions: acc.user.interactions + metric.user.interactions,
        },
        business: {
          farmProductViews:
            acc.business.farmProductViews + metric.business.farmProductViews,
          wellnessBookings:
            acc.business.wellnessBookings + metric.business.wellnessBookings,
          nutritionPlanSelections:
            acc.business.nutritionPlanSelections +
            metric.business.nutritionPlanSelections,
          blockchainVerifications:
            acc.business.blockchainVerifications +
            metric.business.blockchainVerifications,
        },
      }),
      {
        performance: {
          memoryUsage: 0,
          cpuUsage: 0,
          networkLatency: 0,
          renderTime: 0,
          apiResponseTime: 0,
        },
        errors: { count: 0, types: {} },
        user: { activeTime: 0, screenViews: {}, interactions: 0 },
        business: {
          farmProductViews: 0,
          wellnessBookings: 0,
          nutritionPlanSelections: 0,
          blockchainVerifications: 0,
        },
      }
    );

    const count = metrics.length;
    return {
      performance: {
        memoryUsage: sum.performance.memoryUsage / count,
        cpuUsage: sum.performance.cpuUsage / count,
        networkLatency: sum.performance.networkLatency / count,
        renderTime: sum.performance.renderTime / count,
        apiResponseTime: sum.performance.apiResponseTime / count,
      },
      errors: {
        count: sum.errors.count / count,
        types: sum.errors.types,
      },
      user: {
        activeTime: sum.user.activeTime / count,
        screenViews: sum.user.screenViews,
        interactions: sum.user.interactions / count,
      },
      business: {
        farmProductViews: sum.business.farmProductViews / count,
        wellnessBookings: sum.business.wellnessBookings / count,
        nutritionPlanSelections: sum.business.nutritionPlanSelections / count,
        blockchainVerifications: sum.business.blockchainVerifications / count,
      },
    };
  }

  private async persistMetrics(): Promise<void> {
    try {
      const recentMetrics = this.metrics.slice(-100); // 只保存最近100条
      await AsyncStorage.setItem(
        "suoke_metrics",
        JSON.stringify(recentMetrics)
      );
    } catch (error) {
      console.error("持久化指标失败:", error);
    }
  }

  async loadMetrics(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem("suoke_metrics");
      if (stored) {
        this.metrics = JSON.parse(stored);
      }
    } catch (error) {
      console.error("加载指标失败:", error);
    }
  }
}

// 错误监控类
class ErrorTracker {
  private static instance: ErrorTracker;
  private errors: ErrorInfo[] = [];
  private maxErrorHistory = 500;

  static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker();
    }
    return ErrorTracker.instance;
  }

  recordError(error: Omit<ErrorInfo, "timestamp">): void {
    const errorInfo: ErrorInfo = {
      ...error,
      timestamp: Date.now(),
    };

    this.errors.push(errorInfo);

    // 保持历史记录在限制范围内
    if (this.errors.length > this.maxErrorHistory) {
      this.errors.splice(0, this.errors.length - this.maxErrorHistory);
    }

    // 根据严重程度处理
    this.handleErrorSeverity(errorInfo);

    // 持久化错误
    this.persistErrors();
  }

  getErrors(filters?: {
    severity?: ErrorInfo["severity"];
    screen?: string;
    timeRange?: { start: number; end: number };
  }): ErrorInfo[] {
    let filteredErrors = [...this.errors];

    if (filters?.severity) {
      filteredErrors = filteredErrors.filter(
        (error) => error.severity === filters.severity
      );
    }

    if (filters?.screen) {
      filteredErrors = filteredErrors.filter(
        (error) => error.screen === filters.screen
      );
    }

    if (filters?.timeRange) {
      filteredErrors = filteredErrors.filter(
        (error) =>
          error.timestamp >= filters.timeRange!.start &&
          error.timestamp <= filters.timeRange!.end
      );
    }

    return filteredErrors;
  }

  getErrorStats(): {
    total: number;
    bySeverity: Record<ErrorInfo["severity"], number>;
    byScreen: Record<string, number>;
    recentErrors: ErrorInfo[];
  } {
    const bySeverity: Record<ErrorInfo["severity"], number> = {
      low: 0,
      medium: 0,
      high: 0,
      critical: 0,
    };

    const byScreen: Record<string, number> = {};

    this.errors.forEach((error) => {
      bySeverity[error.severity]++;
      byScreen[error.screen] = (byScreen[error.screen] || 0) + 1;
    });

    const recentErrors = this.errors
      .filter((error) => Date.now() - error.timestamp < 24 * 60 * 60 * 1000) // 最近24小时
      .slice(-10); // 最近10个

    return {
      total: this.errors.length,
      bySeverity,
      byScreen,
      recentErrors,
    };
  }

  private handleErrorSeverity(error: ErrorInfo): void {
    switch (error.severity) {
      case "critical":
        // 立即通知用户和开发团队
        Alert.alert("系统错误", "检测到严重错误，请联系技术支持");
        this.sendErrorReport(error);
        break;
      case "high":
        // 记录并在适当时候通知
        this.sendErrorReport(error);
        break;
      case "medium":
      case "low":
        // 仅记录
        break;
    }
  }

  private async sendErrorReport(error: ErrorInfo): Promise<void> {
    try {
      // 这里应该发送到错误报告服务
      console.error("错误报告:", error);

      // 模拟发送到远程服务
      // await fetch('https://api.suokelife.com/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(error)
      // });
    } catch (reportError) {
      console.error("发送错误报告失败:", reportError);
    }
  }

  private async persistErrors(): Promise<void> {
    try {
      const recentErrors = this.errors.slice(-50); // 只保存最近50个错误
      await AsyncStorage.setItem("suoke_errors", JSON.stringify(recentErrors));
    } catch (error) {
      console.error("持久化错误失败:", error);
    }
  }

  async loadErrors(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem("suoke_errors");
      if (stored) {
        this.errors = JSON.parse(stored);
      }
    } catch (error) {
      console.error("加载错误失败:", error);
    }
  }
}

// 告警系统类
class AlertSystem {
  private static instance: AlertSystem;
  private rules: AlertRule[] = [];
  private isEnabled = true;

  static getInstance(): AlertSystem {
    if (!AlertSystem.instance) {
      AlertSystem.instance = new AlertSystem();
      AlertSystem.instance.initializeDefaultRules();
    }
    return AlertSystem.instance;
  }

  private initializeDefaultRules(): void {
    this.rules = [
      {
        id: "high_error_rate",
        name: "错误率过高",
        metric: "errors.count",
        threshold: 10,
        operator: ">",
        enabled: true,
        cooldown: 5 * 60 * 1000, // 5分钟冷却
        actions: [
          {
            type: "user_notification",
            config: { message: "检测到错误率异常，正在自动修复" },
          },
        ],
      },
      {
        id: "slow_api_response",
        name: "API响应缓慢",
        metric: "performance.apiResponseTime",
        threshold: 5000,
        operator: ">",
        enabled: true,
        cooldown: 10 * 60 * 1000, // 10分钟冷却
        actions: [
          {
            type: "log",
            config: { level: "warning", message: "API响应时间超过阈值" },
          },
        ],
      },
      {
        id: "high_memory_usage",
        name: "内存使用率过高",
        metric: "performance.memoryUsage",
        threshold: 80,
        operator: ">",
        enabled: true,
        cooldown: 15 * 60 * 1000, // 15分钟冷却
        actions: [
          {
            type: "log",
            config: { level: "warning", message: "内存使用率过高" },
          },
        ],
      },
    ];
  }

  checkAlerts(metrics: SystemMetrics): void {
    if (!this.isEnabled) {
      return;
    }

    this.rules.forEach((rule) => {
      if (!rule.enabled) {
        return;
      }

      // 检查冷却时间
      if (
        rule.lastTriggered &&
        Date.now() - rule.lastTriggered < rule.cooldown
      ) {
        return;
      }

      const metricValue = this.getMetricValue(metrics, rule.metric);
      if (this.evaluateCondition(metricValue, rule.operator, rule.threshold)) {
        this.triggerAlert(rule, metricValue);
      }
    });
  }

  private getMetricValue(metrics: SystemMetrics, metricPath: string): number {
    const parts = metricPath.split(".");
    let value: any = metrics;

    for (const part of parts) {
      value = value?.[part];
    }

    return typeof value === "number" ? value : 0;
  }

  private evaluateCondition(
    value: number,
    operator: string,
    threshold: number
  ): boolean {
    switch (operator) {
      case ">":
        return value > threshold;
      case "<":
        return value < threshold;
      case "=":
        return value === threshold;
      case ">=":
        return value >= threshold;
      case "<=":
        return value <= threshold;
      default:
        return false;
    }
  }

  private triggerAlert(rule: AlertRule, value: number): void {
    rule.lastTriggered = Date.now();

    console.warn(
      `告警触发: ${rule.name}, 当前值: ${value}, 阈值: ${rule.threshold}`
    );

    rule.actions.forEach((action) => {
      this.executeAction(action, rule, value);
    });
  }

  private executeAction(
    action: AlertAction,
    rule: AlertRule,
    value: number
  ): void {
    switch (action.type) {
      case "notification":
        // 系统通知
        break;
      case "log":
        console.log(
          `[${action.config.level?.toUpperCase()}] ${
            action.config.message
          }: ${value}`
        );
        break;
      case "user_notification":
        Alert.alert("系统提醒", action.config.message);
        break;
      case "api_call":
        // 调用API
        break;
    }
  }

  addRule(rule: Omit<AlertRule, "id">): string {
    const id = `rule_${Date.now()}`;
    this.rules.push({ ...rule, id });
    return id;
  }

  removeRule(id: string): boolean {
    const index = this.rules.findIndex((rule) => rule.id === id);
    if (index !== -1) {
      this.rules.splice(index, 1);
      return true;
    }
    return false;
  }

  updateRule(id: string, updates: Partial<AlertRule>): boolean {
    const rule = this.rules.find((r) => r.id === id);
    if (rule) {
      Object.assign(rule, updates);
      return true;
    }
    return false;
  }

  getRules(): AlertRule[] {
    return [...this.rules];
  }

  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }
}

// 健康检查类
class HealthChecker {
  private static instance: HealthChecker;
  private services: Map<string, HealthCheckResult> = new Map();
  private checkInterval = 30000; // 30秒检查一次
  private intervalId?: ReturnType<typeof setInterval>;

  static getInstance(): HealthChecker {
    if (!HealthChecker.instance) {
      HealthChecker.instance = new HealthChecker();
    }
    return HealthChecker.instance;
  }

  startHealthChecks(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }

    this.intervalId = setInterval(() => {
      this.performHealthChecks();
    }, this.checkInterval);

    // 立即执行一次
    this.performHealthChecks();
  }

  stopHealthChecks(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  private async performHealthChecks(): Promise<void> {
    const services = [
      "xiaoai-service",
      "xiaoke-service",
      "laoke-service",
      "soer-service",
      "eco-services-api",
      "blockchain-service",
    ];

    const checkPromises = services.map((service) => this.checkService(service));
    await Promise.allSettled(checkPromises);
  }

  private async checkService(serviceName: string): Promise<void> {
    const startTime = Date.now();

    try {
      // 模拟健康检查
      const isHealthy = Math.random() > 0.1; // 90%健康率
      const responseTime = Date.now() - startTime + Math.random() * 100;

      const result: HealthCheckResult = {
        service: serviceName,
        status: isHealthy ? "healthy" : "degraded",
        responseTime,
        lastCheck: Date.now(),
        details: {
          endpoint: `https://api.suokelife.com/${serviceName}/health`,
          version: "1.0.0",
        },
      };

      this.services.set(serviceName, result);
    } catch (error) {
      const result: HealthCheckResult = {
        service: serviceName,
        status: "unhealthy",
        responseTime: Date.now() - startTime,
        lastCheck: Date.now(),
        details: {
          error: error instanceof Error ? error.message : "Unknown error",
        },
      };

      this.services.set(serviceName, result);
    }
  }

  getServiceHealth(serviceName: string): HealthCheckResult | null {
    return this.services.get(serviceName) || null;
  }

  getAllServicesHealth(): HealthCheckResult[] {
    return Array.from(this.services.values());
  }

  getSystemHealth(): {
    overall: "healthy" | "degraded" | "unhealthy";
    healthyServices: number;
    totalServices: number;
    averageResponseTime: number;
  } {
    const services = this.getAllServicesHealth();
    const healthyServices = services.filter(
      (s) => s.status === "healthy"
    ).length;
    const totalServices = services.length;
    const averageResponseTime =
      services.length > 0
        ? services.reduce((sum, s) => sum + s.responseTime, 0) / services.length
        : 0;

    let overall: "healthy" | "degraded" | "unhealthy" = "healthy";
    if (healthyServices === 0) {
      overall = "unhealthy";
    } else if (healthyServices < totalServices * 0.8) {
      overall = "degraded";
    }

    return {
      overall,
      healthyServices,
      totalServices,
      averageResponseTime,
    };
  }
}

// 主监控系统类
export class MonitoringSystem {
  private static instance: MonitoringSystem;
  private performanceTracker: PerformanceTracker;
  private errorTracker: ErrorTracker;
  private alertSystem: AlertSystem;
  private healthChecker: HealthChecker;
  private isInitialized = false;

  private constructor() {
    this.performanceTracker = PerformanceTracker.getInstance();
    this.errorTracker = ErrorTracker.getInstance();
    this.alertSystem = AlertSystem.getInstance();
    this.healthChecker = HealthChecker.getInstance();
  }

  static getInstance(): MonitoringSystem {
    if (!MonitoringSystem.instance) {
      MonitoringSystem.instance = new MonitoringSystem();
    }
    return MonitoringSystem.instance;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      await this.performanceTracker.loadMetrics();
      await this.errorTracker.loadErrors();
      this.healthChecker.startHealthChecks();

      this.isInitialized = true;
      console.log("监控系统初始化完成");
    } catch (error) {
      console.error("监控系统初始化失败:", error);
    }
  }

  recordMetric(metric: Partial<SystemMetrics>): void {
    this.performanceTracker.recordMetric(metric);

    // 检查告警
    if (metric.timestamp) {
      this.alertSystem.checkAlerts(metric as SystemMetrics);
    }
  }

  recordError(error: Omit<ErrorInfo, "timestamp">): void {
    this.errorTracker.recordError(error);
  }

  getSystemStatus(): {
    performance: Partial<SystemMetrics>;
    errors: ReturnType<ErrorTracker["getErrorStats"]>;
    health: ReturnType<HealthChecker["getSystemHealth"]>;
    alerts: AlertRule[];
  } {
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;

    return {
      performance: this.performanceTracker.getAverageMetrics({
        start: oneHourAgo,
        end: now,
      }),
      errors: this.errorTracker.getErrorStats(),
      health: this.healthChecker.getSystemHealth(),
      alerts: this.alertSystem.getRules(),
    };
  }

  generateReport(timeRange: { start: number; end: number }): {
    summary: string;
    metrics: SystemMetrics[];
    errors: ErrorInfo[];
    recommendations: string[];
  } {
    const metrics = this.performanceTracker.getMetrics(timeRange);
    const errors = this.errorTracker.getErrors({ timeRange });
    const avgMetrics = this.performanceTracker.getAverageMetrics(timeRange);

    const recommendations: string[] = [];

    // 基于数据生成建议
    if (
      avgMetrics.performance?.apiResponseTime &&
      avgMetrics.performance.apiResponseTime > 3000
    ) {
      recommendations.push("API响应时间较慢，建议优化网络请求或增加缓存");
    }

    if (errors.length > 50) {
      recommendations.push("错误数量较多，建议检查代码质量和异常处理");
    }

    if (
      avgMetrics.performance?.memoryUsage &&
      avgMetrics.performance.memoryUsage > 70
    ) {
      recommendations.push("内存使用率较高，建议优化内存管理");
    }

    const summary = `
时间范围: ${new Date(timeRange.start).toLocaleString()} - ${new Date(
      timeRange.end
    ).toLocaleString()}
指标数量: ${metrics.length}
错误数量: ${errors.length}
平均API响应时间: ${avgMetrics.performance?.apiResponseTime?.toFixed(2) || 0}ms
平均内存使用率: ${avgMetrics.performance?.memoryUsage?.toFixed(2) || 0}%
    `.trim();

    return {
      summary,
      metrics,
      errors,
      recommendations,
    };
  }

  shutdown(): void {
    this.healthChecker.stopHealthChecks();
    this.isInitialized = false;
  }
}

// 导出单例实例
export const monitoringSystem = MonitoringSystem.getInstance();
export { PerformanceTracker, ErrorTracker, AlertSystem, HealthChecker };
