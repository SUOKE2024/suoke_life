import EnvironmentManager from "../config/EnvironmentManager";

/**
 * 索克生活日志系统
 * 支持结构化日志、日志聚合、实时分析和告警
 */

export type LogLevel = "debug" | "info" | "warn" | "error" | "fatal";

export interface LogEntry {
  /** 时间戳 */
  timestamp: number;
  /** 日志级别 */
  level: LogLevel;
  /** 日志消息 */
  message: string;
  /** 服务名称 */
  service: string;
  /** 请求ID */
  requestId?: string;
  /** 用户ID */
  userId?: string;
  /** 会话ID */
  sessionId?: string;
  /** 错误堆栈 */
  stack?: string;
  /** 上下文数据 */
  context?: Record<string, any>;
  /** 标签 */
  tags?: string[];
  /** 元数据 */
  metadata?: Record<string, any>;
}

export interface LogFilter {
  /** 日志级别过滤 */
  levels?: LogLevel[];
  /** 服务过滤 */
  services?: string[];
  /** 时间范围过滤 */
  timeRange?: {
    start: number;
    end: number;
  };
  /** 关键词过滤 */
  keywords?: string[];
  /** 标签过滤 */
  tags?: string[];
  /** 用户过滤 */
  userIds?: string[];
}

export interface LogOutput {
  /** 输出类型 */
  type: "console" | "file" | "elasticsearch" | "loki" | "webhook";
  /** 输出配置 */
  config: Record<string, any>;
  /** 是否启用 */
  enabled: boolean;
  /** 日志级别过滤 */
  minLevel: LogLevel;
}

export interface LogMetrics {
  /** 日志总数 */
  totalLogs: number;
  /** 按级别统计 */
  byLevel: Record<LogLevel, number>;
  /** 按服务统计 */
  byService: Record<string, number>;
  /** 错误率 */
  errorRate: number;
  /** 最近错误 */
  recentErrors: LogEntry[];
  /** 性能指标 */
  performance: {
    avgProcessingTime: number;
    throughput: number;
    bufferSize: number;
  };
}

export interface LogAlert {
  /** 告警ID */
  id: string;
  /** 告警名称 */
  name: string;
  /** 告警条件 */
  condition: {
    level: LogLevel;
    count: number;
    timeWindow: number; // 秒
    service?: string;
    keywords?: string[];
  };
  /** 告警动作 */
  actions: Array<{
    type: "email" | "webhook" | "sms";
    config: Record<string, any>;
  }>;
  /** 是否启用 */
  enabled: boolean;
  /** 最后触发时间 */
  lastTriggered?: number;
}

export interface LogAnalytics {
  /** 错误趋势 */
  errorTrend: Array<{
    timestamp: number;
    count: number;
  }>;
  /** 服务健康度 */
  serviceHealth: Record<
    string,
    {
      status: "healthy" | "warning" | "critical";
      errorRate: number;
      lastError?: LogEntry;
    }
  >;
  /** 热点问题 */
  hotIssues: Array<{
    message: string;
    count: number;
    services: string[];
    firstSeen: number;
    lastSeen: number;
  }>;
  /** 用户活动 */
  userActivity: Record<
    string,
    {
      loginCount: number;
      errorCount: number;
      lastActivity: number;
    }
  >;
}

export class LoggingSystem {
  private static instance: LoggingSystem;
  private envManager: EnvironmentManager;
  private logBuffer: LogEntry[];
  private outputs: LogOutput[];
  private alerts: LogAlert[];
  private metrics: LogMetrics;
  private isProcessing: boolean;
  private processingInterval: NodeJS.Timeout | null;

  private constructor() {
    this.envManager = EnvironmentManager.getInstance();
    this.logBuffer = [];
    this.outputs = [];
    this.alerts = [];
    this.metrics = this.initializeMetrics();
    this.isProcessing = false;
    this.processingInterval = null;

    this.initializeOutputs();
    this.initializeAlerts();
    this.startProcessing();
  }

  static getInstance(): LoggingSystem {
    if (!LoggingSystem.instance) {
      LoggingSystem.instance = new LoggingSystem();
    }
    return LoggingSystem.instance;
  }

  /**
   * 初始化指标
   */
  private initializeMetrics(): LogMetrics {
    return {
      totalLogs: 0,
      byLevel: {
        debug: 0,
        info: 0,
        warn: 0,
        error: 0,
        fatal: 0,
      },
      byService: {},
      errorRate: 0,
      recentErrors: [],
      performance: {
        avgProcessingTime: 0,
        throughput: 0,
        bufferSize: 0,
      },
    };
  }

  /**
   * 初始化输出配置
   */
  private initializeOutputs(): void {
    const config = this.envManager.getConfig();

    // 控制台输出
    this.outputs.push({
      type: "console",
      config: {
        colorize: config.type === "development",
        format: config.logging.format,
      },
      enabled: true,
      minLevel: config.logging.level,
    });

    // 文件输出
    if (config.logging.outputs.some((o) => o.type === "file")) {
      this.outputs.push({
        type: "file",
        config: {
          filename: "logs/app.log",
          maxSize: config.logging.rotation.maxSize,
          maxFiles: config.logging.rotation.maxFiles,
          maxAge: config.logging.rotation.maxAge,
          format: config.logging.format,
        },
        enabled: true,
        minLevel: "info",
      });
    }

    // Elasticsearch输出
    if (config.logging.outputs.some((o) => o.type === "elasticsearch")) {
      this.outputs.push({
        type: "elasticsearch",
        config: {
          host: "localhost:9200",
          index: "suoke-logs",
          type: "_doc",
        },
        enabled: config.type === "production",
        minLevel: "warn",
      });
    }

    // Loki输出
    if (config.logging.outputs.some((o) => o.type === "loki")) {
      this.outputs.push({
        type: "loki",
        config: {
          host: "localhost:3100",
          labels: {
            app: "suoke-life",
            environment: config.type,
          },
        },
        enabled: config.type !== "development",
        minLevel: "info",
      });
    }
  }

  /**
   * 初始化告警配置
   */
  private initializeAlerts(): void {
    // 错误告警
    this.alerts.push({
      id: "error-alert",
      name: "错误日志告警",
      condition: {
        level: "error",
        count: 10,
        timeWindow: 300, // 5分钟
      },
      actions: [
        {
          type: "webhook",
          config: {
            url: "http://localhost:8080/alerts/error",
            method: "POST",
          },
        },
      ],
      enabled: true,
    });

    // 智能体服务告警
    this.alerts.push({
      id: "agent-error-alert",
      name: "智能体服务错误告警",
      condition: {
        level: "error",
        count: 5,
        timeWindow: 180, // 3分钟
        service: "agent",
      },
      actions: [
        {
          type: "webhook",
          config: {
            url: "http://localhost:8080/alerts/agent",
            method: "POST",
          },
        },
      ],
      enabled: true,
    });

    // 致命错误告警
    this.alerts.push({
      id: "fatal-alert",
      name: "致命错误告警",
      condition: {
        level: "fatal",
        count: 1,
        timeWindow: 60, // 1分钟
      },
      actions: [
        {
          type: "webhook",
          config: {
            url: "http://localhost:8080/alerts/fatal",
            method: "POST",
          },
        },
        {
          type: "email",
          config: {
            to: ["admin@suoke.life"],
            subject: "索克生活致命错误告警",
          },
        },
      ],
      enabled: true,
    });
  }

  /**
   * 记录日志
   */
  log(
    level: LogLevel,
    message: string,
    context?: {
      service?: string;
      requestId?: string;
      userId?: string;
      sessionId?: string;
      error?: Error;
      data?: Record<string, any>;
      tags?: string[];
    }
  ): void {
    const entry: LogEntry = {
      timestamp: Date.now(),
      level,
      message,
      service: context?.service || "unknown",
      requestId: context?.requestId,
      userId: context?.userId,
      sessionId: context?.sessionId,
      stack: context?.error?.stack,
      context: context?.data,
      tags: context?.tags,
      metadata: {
        hostname: process.env.HOSTNAME || "localhost",
        pid: process.pid,
        version: process.env.APP_VERSION || "1.0.0",
      },
    };

    this.addToBuffer(entry);
    this.updateMetrics(entry);
    this.checkAlerts(entry);
  }

  /**
   * 便捷日志方法
   */
  debug(message: string, context?: any): void {
    this.log("debug", message, context);
  }

  info(message: string, context?: any): void {
    this.log("info", message, context);
  }

  warn(message: string, context?: any): void {
    this.log("warn", message, context);
  }

  error(message: string, context?: any): void {
    this.log("error", message, context);
  }

  fatal(message: string, context?: any): void {
    this.log("fatal", message, context);
  }

  /**
   * 添加到缓冲区
   */
  private addToBuffer(entry: LogEntry): void {
    this.logBuffer.push(entry);

    // 限制缓冲区大小
    if (this.logBuffer.length > 10000) {
      this.logBuffer = this.logBuffer.slice(-5000);
    }
  }

  /**
   * 更新指标
   */
  private updateMetrics(entry: LogEntry): void {
    this.metrics.totalLogs++;
    this.metrics.byLevel[entry.level]++;

    if (!this.metrics.byService[entry.service]) {
      this.metrics.byService[entry.service] = 0;
    }
    this.metrics.byService[entry.service]++;

    // 更新错误率
    const errorCount = this.metrics.byLevel.error + this.metrics.byLevel.fatal;
    this.metrics.errorRate = (errorCount / this.metrics.totalLogs) * 100;

    // 记录最近错误
    if (entry.level === "error" || entry.level === "fatal") {
      this.metrics.recentErrors.unshift(entry);
      if (this.metrics.recentErrors.length > 100) {
        this.metrics.recentErrors = this.metrics.recentErrors.slice(0, 50);
      }
    }

    // 更新性能指标
    this.metrics.performance.bufferSize = this.logBuffer.length;
  }

  /**
   * 检查告警
   */
  private checkAlerts(entry: LogEntry): void {
    const now = Date.now();

    for (const alert of this.alerts) {
      if (!alert.enabled) continue;

      // 检查告警条件
      if (this.shouldTriggerAlert(alert, entry, now)) {
        this.triggerAlert(alert, entry);
      }
    }
  }

  /**
   * 判断是否应该触发告警
   */
  private shouldTriggerAlert(
    alert: LogAlert,
    entry: LogEntry,
    now: number
  ): boolean {
    const { condition } = alert;

    // 检查日志级别
    if (entry.level !== condition.level) {
      return false;
    }

    // 检查服务过滤
    if (condition.service && !entry.service.includes(condition.service)) {
      return false;
    }

    // 检查关键词过滤
    if (condition.keywords) {
      const hasKeyword = condition.keywords.some((keyword) =>
        entry.message.toLowerCase().includes(keyword.toLowerCase())
      );
      if (!hasKeyword) {
        return false;
      }
    }

    // 检查时间窗口内的日志数量
    const windowStart = now - condition.timeWindow * 1000;
    const recentLogs = this.logBuffer.filter(
      (log) =>
        log.timestamp >= windowStart &&
        log.level === condition.level &&
        (!condition.service || log.service.includes(condition.service))
    );

    return recentLogs.length >= condition.count;
  }

  /**
   * 触发告警
   */
  private async triggerAlert(alert: LogAlert, entry: LogEntry): Promise<void> {
    const now = Date.now();

    // 防止重复告警（5分钟内不重复）
    if (alert.lastTriggered && now - alert.lastTriggered < 300000) {
      return;
    }

    alert.lastTriggered = now;

    console.warn(`🚨 触发告警: ${alert.name}`);

    // 执行告警动作
    for (const action of alert.actions) {
      try {
        await this.executeAlertAction(action, alert, entry);
      } catch (error) {
        console.error("告警动作执行失败:", error);
      }
    }
  }

  /**
   * 执行告警动作
   */
  private async executeAlertAction(
    action: { type: string; config: Record<string, any> },
    alert: LogAlert,
    entry: LogEntry
  ): Promise<void> {
    switch (action.type) {
      case "webhook":
        await this.sendWebhookAlert(action.config, alert, entry);
        break;
      case "email":
        await this.sendEmailAlert(action.config, alert, entry);
        break;
      case "sms":
        await this.sendSmsAlert(action.config, alert, entry);
        break;
    }
  }

  /**
   * 发送Webhook告警
   */
  private async sendWebhookAlert(
    config: Record<string, any>,
    alert: LogAlert,
    entry: LogEntry
  ): Promise<void> {
    const payload = {
      alert: alert.name,
      level: entry.level,
      message: entry.message,
      service: entry.service,
      timestamp: entry.timestamp,
      context: entry.context,
    };

    // 模拟发送Webhook
    console.log(`📤 发送Webhook告警到: ${config.url}`, payload);
  }

  /**
   * 发送邮件告警
   */
  private async sendEmailAlert(
    config: Record<string, any>,
    alert: LogAlert,
    entry: LogEntry
  ): Promise<void> {
    const subject = config.subject || `索克生活告警: ${alert.name}`;
    const body = `
告警名称: ${alert.name}
日志级别: ${entry.level}
服务名称: ${entry.service}
错误消息: ${entry.message}
发生时间: ${new Date(entry.timestamp).toLocaleString()}
    `;

    // 模拟发送邮件
    console.log(`📧 发送邮件告警到: ${config.to.join(", ")}`);
    console.log(`主题: ${subject}`);
    console.log(`内容: ${body}`);
  }

  /**
   * 发送短信告警
   */
  private async sendSmsAlert(
    config: Record<string, any>,
    alert: LogAlert,
    entry: LogEntry
  ): Promise<void> {
    const message = `索克生活告警: ${alert.name} - ${entry.level}: ${entry.message}`;

    // 模拟发送短信
    console.log(`📱 发送短信告警到: ${config.phone}`);
    console.log(`内容: ${message}`);
  }

  /**
   * 开始处理日志
   */
  private startProcessing(): void {
    this.processingInterval = setInterval(async () => {
      if (this.isProcessing || this.logBuffer.length === 0) {
        return;
      }

      this.isProcessing = true;
      const startTime = Date.now();

      try {
        const logsToProcess = [...this.logBuffer];
        this.logBuffer = [];

        await this.processLogs(logsToProcess);

        // 更新性能指标
        const processingTime = Date.now() - startTime;
        this.metrics.performance.avgProcessingTime =
          (this.metrics.performance.avgProcessingTime + processingTime) / 2;
        this.metrics.performance.throughput =
          logsToProcess.length / (processingTime / 1000);
      } catch (error) {
        console.error("日志处理失败:", error);
      } finally {
        this.isProcessing = false;
      }
    }, 1000); // 每秒处理一次
  }

  /**
   * 处理日志批次
   */
  private async processLogs(logs: LogEntry[]): Promise<void> {
    for (const output of this.outputs) {
      if (!output.enabled) continue;

      const filteredLogs = logs.filter((log) =>
        this.shouldOutputLog(log, output)
      );

      if (filteredLogs.length === 0) continue;

      try {
        await this.writeToOutput(output, filteredLogs);
      } catch (error) {
        console.error(`输出到 ${output.type} 失败:`, error);
      }
    }
  }

  /**
   * 判断是否应该输出日志
   */
  private shouldOutputLog(log: LogEntry, output: LogOutput): boolean {
    const levelPriority = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
      fatal: 4,
    };

    return levelPriority[log.level] >= levelPriority[output.minLevel];
  }

  /**
   * 写入到输出
   */
  private async writeToOutput(
    output: LogOutput,
    logs: LogEntry[]
  ): Promise<void> {
    switch (output.type) {
      case "console":
        this.writeToConsole(logs, output.config);
        break;
      case "file":
        await this.writeToFile(logs, output.config);
        break;
      case "elasticsearch":
        await this.writeToElasticsearch(logs, output.config);
        break;
      case "loki":
        await this.writeToLoki(logs, output.config);
        break;
      case "webhook":
        await this.writeToWebhook(logs, output.config);
        break;
    }
  }

  /**
   * 写入到控制台
   */
  private writeToConsole(logs: LogEntry[], config: Record<string, any>): void {
    for (const log of logs) {
      const timestamp = new Date(log.timestamp).toISOString();
      const level = log.level.toUpperCase().padEnd(5);
      const service = log.service.padEnd(15);

      let message = `${timestamp} [${level}] [${service}] ${log.message}`;

      if (log.context) {
        message += ` ${JSON.stringify(log.context)}`;
      }

      // 颜色输出（开发环境）
      if (config.colorize) {
        const colors = {
          debug: "\x1b[36m", // 青色
          info: "\x1b[32m", // 绿色
          warn: "\x1b[33m", // 黄色
          error: "\x1b[31m", // 红色
          fatal: "\x1b[35m", // 紫色
        };
        message = `${colors[log.level]}${message}\x1b[0m`;
      }

      console.log(message);
    }
  }

  /**
   * 写入到文件
   */
  private async writeToFile(
    logs: LogEntry[],
    config: Record<string, any>
  ): Promise<void> {
    // 模拟文件写入
    const logLines = logs.map((log) => {
      if (config.format === "json") {
        return JSON.stringify(log);
      } else {
        const timestamp = new Date(log.timestamp).toISOString();
        return `${timestamp} [${log.level.toUpperCase()}] [${log.service}] ${
          log.message
        }`;
      }
    });

    console.log(`📁 写入 ${logs.length} 条日志到文件: ${config.filename}`);
  }

  /**
   * 写入到Elasticsearch
   */
  private async writeToElasticsearch(
    logs: LogEntry[],
    config: Record<string, any>
  ): Promise<void> {
    // 模拟Elasticsearch写入
    console.log(
      `🔍 写入 ${logs.length} 条日志到Elasticsearch: ${config.host}/${config.index}`
    );
  }

  /**
   * 写入到Loki
   */
  private async writeToLoki(
    logs: LogEntry[],
    config: Record<string, any>
  ): Promise<void> {
    // 模拟Loki写入
    console.log(`📊 写入 ${logs.length} 条日志到Loki: ${config.host}`);
  }

  /**
   * 写入到Webhook
   */
  private async writeToWebhook(
    logs: LogEntry[],
    config: Record<string, any>
  ): Promise<void> {
    // 模拟Webhook写入
    console.log(`🔗 发送 ${logs.length} 条日志到Webhook: ${config.url}`);
  }

  /**
   * 查询日志
   */
  queryLogs(filter: LogFilter, limit: number = 100): LogEntry[] {
    let filteredLogs = [...this.logBuffer];

    // 按级别过滤
    if (filter.levels && filter.levels.length > 0) {
      filteredLogs = filteredLogs.filter((log) =>
        filter.levels!.includes(log.level)
      );
    }

    // 按服务过滤
    if (filter.services && filter.services.length > 0) {
      filteredLogs = filteredLogs.filter((log) =>
        filter.services!.some((service) => log.service.includes(service))
      );
    }

    // 按时间范围过滤
    if (filter.timeRange) {
      filteredLogs = filteredLogs.filter(
        (log) =>
          log.timestamp >= filter.timeRange!.start &&
          log.timestamp <= filter.timeRange!.end
      );
    }

    // 按关键词过滤
    if (filter.keywords && filter.keywords.length > 0) {
      filteredLogs = filteredLogs.filter((log) =>
        filter.keywords!.some((keyword) =>
          log.message.toLowerCase().includes(keyword.toLowerCase())
        )
      );
    }

    // 按标签过滤
    if (filter.tags && filter.tags.length > 0) {
      filteredLogs = filteredLogs.filter(
        (log) => log.tags && filter.tags!.some((tag) => log.tags!.includes(tag))
      );
    }

    // 按用户过滤
    if (filter.userIds && filter.userIds.length > 0) {
      filteredLogs = filteredLogs.filter(
        (log) => log.userId && filter.userIds!.includes(log.userId)
      );
    }

    // 按时间倒序排列并限制数量
    return filteredLogs
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  /**
   * 获取日志指标
   */
  getMetrics(): LogMetrics {
    return { ...this.metrics };
  }

  /**
   * 获取日志分析
   */
  getAnalytics(): LogAnalytics {
    const now = Date.now();
    const oneHourAgo = now - 3600000;
    const recentLogs = this.logBuffer.filter(
      (log) => log.timestamp >= oneHourAgo
    );

    // 错误趋势（按10分钟分组）
    const errorTrend: Array<{ timestamp: number; count: number }> = [];
    for (let i = 0; i < 6; i++) {
      const windowStart = oneHourAgo + i * 600000;
      const windowEnd = windowStart + 600000;
      const errorCount = recentLogs.filter(
        (log) =>
          log.timestamp >= windowStart &&
          log.timestamp < windowEnd &&
          (log.level === "error" || log.level === "fatal")
      ).length;

      errorTrend.push({
        timestamp: windowStart,
        count: errorCount,
      });
    }

    // 服务健康度
    const serviceHealth: Record<string, any> = {};
    const services = [...new Set(recentLogs.map((log) => log.service))];

    for (const service of services) {
      const serviceLogs = recentLogs.filter((log) => log.service === service);
      const errorLogs = serviceLogs.filter(
        (log) => log.level === "error" || log.level === "fatal"
      );
      const errorRate =
        serviceLogs.length > 0
          ? (errorLogs.length / serviceLogs.length) * 100
          : 0;

      let status: "healthy" | "warning" | "critical";
      if (errorRate === 0) {
        status = "healthy";
      } else if (errorRate < 5) {
        status = "warning";
      } else {
        status = "critical";
      }

      serviceHealth[service] = {
        status,
        errorRate,
        lastError: errorLogs[0],
      };
    }

    // 热点问题
    const errorMessages = recentLogs
      .filter((log) => log.level === "error" || log.level === "fatal")
      .map((log) => log.message);

    const messageCount: Record<string, any> = {};
    for (const message of errorMessages) {
      if (!messageCount[message]) {
        messageCount[message] = {
          count: 0,
          services: new Set(),
          firstSeen: now,
          lastSeen: 0,
        };
      }
      messageCount[message].count++;
      messageCount[message].services.add(
        recentLogs.find((log) => log.message === message)?.service
      );
      const logTime =
        recentLogs.find((log) => log.message === message)?.timestamp || 0;
      messageCount[message].firstSeen = Math.min(
        messageCount[message].firstSeen,
        logTime
      );
      messageCount[message].lastSeen = Math.max(
        messageCount[message].lastSeen,
        logTime
      );
    }

    const hotIssues = Object.entries(messageCount)
      .map(([message, data]: [string, any]) => ({
        message,
        count: data.count,
        services: Array.from(data.services).filter(
          (s): s is string => typeof s === "string"
        ),
        firstSeen: data.firstSeen,
        lastSeen: data.lastSeen,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // 用户活动
    const userActivity: Record<string, any> = {};
    const userLogs = recentLogs.filter((log) => log.userId);

    for (const log of userLogs) {
      if (!log.userId) continue;

      if (!userActivity[log.userId]) {
        userActivity[log.userId] = {
          loginCount: 0,
          errorCount: 0,
          lastActivity: 0,
        };
      }

      if (log.message.includes("login")) {
        userActivity[log.userId].loginCount++;
      }

      if (log.level === "error" || log.level === "fatal") {
        userActivity[log.userId].errorCount++;
      }

      userActivity[log.userId].lastActivity = Math.max(
        userActivity[log.userId].lastActivity,
        log.timestamp
      );
    }

    return {
      errorTrend,
      serviceHealth,
      hotIssues,
      userActivity,
    };
  }

  /**
   * 添加告警规则
   */
  addAlert(alert: Omit<LogAlert, "id">): string {
    const id = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.alerts.push({ ...alert, id });
    return id;
  }

  /**
   * 移除告警规则
   */
  removeAlert(id: string): boolean {
    const index = this.alerts.findIndex((alert) => alert.id === id);
    if (index !== -1) {
      this.alerts.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * 获取告警规则
   */
  getAlerts(): LogAlert[] {
    return [...this.alerts];
  }

  /**
   * 清理旧日志
   */
  cleanup(maxAge: number = 86400000): void {
    // 默认24小时
    const cutoff = Date.now() - maxAge;
    this.logBuffer = this.logBuffer.filter((log) => log.timestamp >= cutoff);
    this.metrics.recentErrors = this.metrics.recentErrors.filter(
      (log) => log.timestamp >= cutoff
    );
  }

  /**
   * 停止日志系统
   */
  stop(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  /**
   * 导出日志
   */
  exportLogs(filter: LogFilter, format: "json" | "csv" = "json"): string {
    const logs = this.queryLogs(filter, 10000);

    if (format === "json") {
      return JSON.stringify(logs, null, 2);
    } else {
      // CSV格式
      const headers = [
        "timestamp",
        "level",
        "service",
        "message",
        "requestId",
        "userId",
      ];
      const csvLines = [headers.join(",")];

      for (const log of logs) {
        const row = [
          new Date(log.timestamp).toISOString(),
          log.level,
          log.service,
          `"${log.message.replace(/"/g, '""')}"`,
          log.requestId || "",
          log.userId || "",
        ];
        csvLines.push(row.join(","));
      }

      return csvLines.join("\n");
    }
  }
}

export default LoggingSystem;
