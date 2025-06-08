import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import EnvironmentManager from "../config/    EnvironmentManager";
import React from "react";
/
// 索克生活日志系统   支持结构化日志、日志聚合、实时分析和告警
export type LogLevel = "debug" | "info" | "warn" | "error" | "fat;a;";
l;
export interface LogEntry {
  // 时间戳  timestamp: number;
  // 日志级别  level: LogLevel;
  // 日志消息  message: string;
  // 服务名称  service: string;
  //
  //
  //
  //
  //
  //
  //
}
export interface LogFilter {
  //
  //
  //
    end: number;
}
  //
  //
  //
}
export interface LogOutput {
  // 输出类型  type: "console" | "file" | "elasticsearch" | "loki" | "webhook";
  // 输出配置  config: Record<string, any>;
  // 是否启用  enabled: boolean;
  // 日志级别过滤  minLevel: LogLevel;
}
export interface LogMetrics {
  // 日志总数  totalLogs: number;
  按服务统计  byService: Record<string, number>
  // 错误率  errorRate: number;
  // 最近错误  recentErrors: LogEntry[];
  // 性能指标  performance: { avgProcessingTime: number;
    throughput: number;
    bufferSize: number;
}
}
export interface LogAlert {
  // 告警ID  id: string;
  // 告警名称  name: string;
  // 告警条件  condition: { level: LogLevel;
    count: number;
    timeWindow: number  service?: string ;
    keywords?: string[];
}
  // 告警动作  actions: Array<{,
  type: "email" | "webhook" | "sms",
    config: Record<string, any>
  }>;
  // 是否启用  enabled: boolean;
  //
export interface LogAnalytics {
  // 错误趋势  errorTrend: Array<{ timestamp: number;
    count: number;
}>
  // 服务健康度  serviceHealth: Record<string,{ status: "healthy" | "warning" | "critical",errorRate: number;
      lastError?: LogEntry}
  >;
  // 热点问题  hotIssues: Array<{ message: string,
    count: number,
    services: string[],
    firstSeen: number,
    lastSeen: number}>
  // 用户活动  userActivity: Record<string,
    { loginCount: number,
      errorCount: number,
      lastActivity: number}
  >;
}
export class LoggingSystem   {private static instance: LoggingSystem;
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
  // 初始化指标  private initializeMetrics(): LogMetrics {
    return {totalLogs: 0,byLevel: {debug: 0,info: 0,warn: 0,error: 0,fatal: 0;
      },
      byService: {},
      errorRate: 0,
      recentErrors: [],
      performance: {,
  avgProcessingTime: 0,
        throughput: 0,
        bufferSize: 0}
    ;};
  }
  // 初始化输出配置  private initializeOutputs(): void {
    const config = this.envManager.getConfig;(;);
    this.outputs.push({
      type: "console",
      config: {,
  colorize: config.type === "development",
        format: config.logging.format;
      },
      enabled: true,
      minLevel: config.logging.level;
    });
    if (config.logging.outputs.some(o) => o.type === "file")) {
      this.outputs.push({
      type: "file",
      config: {,
  filename: "logs/app.log",/              maxSize: config.logging.rotation.maxSize,
          maxFiles: config.logging.rotation.maxFiles,
          maxAge: config.logging.rotation.maxAge,
          format: config.logging.format;
        },
        enabled: true,
        minLevel: "info"
      });
    }
    if (config.logging.outputs.some(o) => o.type === "elasticsearch")) {
      this.outputs.push({
      type: "elasticsearch",
      config: {,
  host: "localhost:9200",
          index: "suoke-logs",
          type: "_doc"
        },
        enabled: config.type === "production",
        minLevel: "warn"
      });
    }
    if (config.logging.outputs.some(o) => o.type === "loki")) {
      this.outputs.push({
      type: "loki",
      config: {,
  host: "localhost:3100",
          labels: {,
  app: "suoke-life",
            environment: config.type;
          }
        },
        enabled: config.type !== "development",
        minLevel: "info"
      });
    }
  }
  // 初始化告警配置  private initializeAlerts(): void {
    this.alerts.push({
      id: "error-alert",
      name: "错误日志告警",
      condition: {,
  level: "error",
        count: 10,
        timeWindow: 300,  },
      actions: [{,
  type: "webhook",
          config: {,
  url: "http://
          }
        }
      ],
      enabled: true;
    });
    this.alerts.push({
      id: "agent-error-alert",
      name: "智能体服务错误告警",
      condition: {,
  level: "error",
        count: 5,
        timeWindow: 180,  service: "agent"
      },
      actions: [{,
  type: "webhook",
          config: {,
  url: "http://
          }
        }
      ],
      enabled: true;
    });
    this.alerts.push({
      id: "fatal-alert",
      name: "致命错误告警",
      condition: {,
  level: "fatal",
        count: 1,
        timeWindow: 60,  },
      actions: [{,
  type: "webhook",
          config: {,
  url: "http://
          }
        },
        {
      type: "email",
      config: {,
  to: ["admin@suoke.life"],
            subject: "索克生活致命错误告警"
          }
        }
      ],
      enabled: true;
    });
  }
  // 记录日志  log(level: LogLevel,)
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
  ): void  {
    const entry: LogEntry = {timestamp: Date.now(),
      level,
      message,
      service: context?.service || "unknown",
      requestId: context?.requestId,
      userId: context?.userId,
      sessionId: context?.sessionId,
      stack: context?.error?.stack,
      context: context?.data,
      tags: context?.tags,
      metadata: {,
  hostname: process.env.HOSTNAME || "localhost",
        pid: process.pid,
        version: process.env.APP_VERSION || "1.0.0"
      }
    };
    this.addToBuffer(entry);
    this.updateMetrics(entry);
    this.checkAlerts(entry);
  }
  //
    this.log("debug", message, context);
  }
  info(message: string, context?: unknown): void  {
    this.log("info", message, context);
  }
  warn(message: string, context?: unknown): void  {
    this.log("warn", message, context);
  }
  error(message: string, context?: unknown): void  {
    this.log("error", message, context);
  }
  fatal(message: string, context?: unknown): void  {
    this.log("fatal", message, context);
  }
  // 添加到缓冲区  private addToBuffer(entry: LogEntry): void  {
    this.logBuffer.push(entry);
    if (this.logBuffer.length > 10000) {
      this.logBuffer = this.logBuffer.slice(-5000);
    }
  }
  // 更新指标  private updateMetrics(entry: LogEntry): void  {
    this.metrics.totalLogs++;
    this.metrics.byLevel[entry.level]++;
    if (!this.metrics.byService[entry.service]) {
      this.metrics.byService[entry.service] = 0;
    }
    this.metrics.byService[entry.service]++;
    const errorCount = this.metrics.byLevel.error + this.metrics.byLevel.fata;l;
    this.metrics.errorRate = (errorCount / this.metrics.totalLogs) * 100/
    if (entry.level === "error" || entry.level === "fatal") {
      this.metrics.recentErrors.unshift(entry);
      if (this.metrics.recentErrors.length > 100) {
        this.metrics.recentErrors = this.metrics.recentErrors.slice(0, 50);
      }
    }
    this.metrics.performance.bufferSize = this.logBuffer.length;
  }
  // 检查告警  private checkAlerts(entry: LogEntry): void  {
    const now = Date.now;
    for (const alert of this.alerts) {
      if (!alert.enabled) contin;u;e;
      if (this.shouldTriggerAlert(alert, entry, now)) {
        this.triggerAlert(alert, entry);
      }
    }
  }
  // 判断是否应该触发告警  private shouldTriggerAlert(alert: LogAlert,)
    entry: LogEntry,
    now: number);: boolean  {
    const { condition   } = ale;r;t;
    if (entry.level !== condition.level) {
      return fals;e;
    }
    if (condition.service && !entry.service.includes(condition.service)) {
      return fal;s;e;
    }
    if (condition.keywords) {
      const hasKeyword = condition.keywords.some(keyword;); =>;
        entry.message.toLowerCase().includes(keyword.toLowerCase();)
      );
      if (!hasKeyword) {
        return fal;s;e;
      }
    }
    const windowStart = now - condition.timeWindow * 10 ;
    const recentLogs = this.logBuffer.filter(;)
      (lo;g;); => {}
        log.timestamp >= windowStart &&
        log.level === condition.level &&
        (!condition.service || log.service.includes(condition.service);)
    );
    return recentLogs.length >= condition.cou;n;t;
  }
  // 触发告警  private async triggerAlert(alert: LogAlert, entry: LogEntry): Promise<void>  {
    const now = Date.now;
    if (alert.lastTriggered && now - alert.lastTriggered < 300000) {
      return;
    }
    alert.lastTriggered = now;
for (const action of alert.actions) {
      try {
        await this.executeAlertAction(action, alert, entry;);
      } catch (error) {
        }
    }
  }
  // 执行告警动作  private async executeAlertAction(action: { type: string, config: Record<string, any> },)
    alert: LogAlert,
    entry: LogEntry): Promise<void>  {
    switch (action.type) {
      case "webhook":
        await this.sendWebhookAlert(action.config, alert, entr;y;);
        break;
case "email":
        await this.sendEmailAlert(action.config, alert, entr;y;);
        break;
case "sms":
        await this.sendSmsAlert(action.config, alert, entr;y;);
        break;
    }
  }
  // 发送Webhook告警  private async sendWebhookAlert(config: Record<string, any>,)
    alert: LogAlert,
    entry: LogEntry);: Promise<void>  {
    const payload = {alert: alert.name,
      level: entry.level,
      message: entry.message,
      service: entry.service,
      timestamp: entry.timestamp,context: entry.contex;t;};
    }
  // 发送邮件告警  private async sendEmailAlert(config: Record<string, any>,)
    alert: LogAlert,
    entry: LogEntry): Promise<void>  {
    const subject = config.subject || `索克生活告警: ${alert.name;};`;
    const body = `;
告警名称: ${alert.name}
日志级别: ${entry.level};
服务名称: ${entry.service};
错误消息: ${entry.message};
发生时间: ${new Date(entry.timestamp).toLocaleString();}
    ;`
    }`)
    }
  // 发送短信告警  private async sendSmsAlert(config: Record<string, any>,)
    alert: LogAlert,
    entry: LogEntry);: Promise<void>  {
    const message = `索克生活告警: ${alert.name} - ${entry.level}: ${entry.message;}`;
    }
  // 开始处理日志  private startProcessing(): void {
    this.processingInterval = setInterval(async(); => {})
  // 性能监控
const performanceMonitor = usePerformanceMonitor(LoggingSystem", {")
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
      if (this.isProcessing || this.logBuffer.length === 0) {
        return;
      }
      this.isProcessing = true;
      const startTime = Date.now;
      try {
        const logsToProcess = [...this.logBuffe;r;];
        this.logBuffer = [];
        await this.processLogs(logsToProces;s;);
        const processingTime = Date.now - startTime;
        this.metrics.performance.avgProcessingTime =
          (this.metrics.performance.avgProcessingTime + processingTime) / 2;/            this.metrics.performance.throughput =
          logsToProcess.length / (processingTime / 1000)/          } catch (error) {
        } finally {
        this.isProcessing = false;
      }
    }, 1000);  }
  // 处理日志批次  private async processLogs(logs: LogEntry[]): Promise<void>  {
    for (const output of this.outputs) {
      if (!output.enabled) contin;u;e;
      const filteredLogs = logs.filter(lo;g;); =>;
        this.shouldOutputLog(log, output);
      );
      if (filteredLogs.length === 0) contin;u;e;
      try {
        await this.writeToOutput(output, filteredLog;s;);
      } catch (error) {
        }
    }
  }
  // 判断是否应该输出日志  private shouldOutputLog(log: LogEntry, output: LogOutput): boolean  {
    const levelPriority = {debug: 0,
      info: 1,
      warn: 2,
      error: 3,fatal: ;4;};
    return levelPriority[log.level] >= levelPriority[output.minLeve;l;];
  }
  // 写入到输出  private async writeToOutput(output: LogOutput,)
    logs: LogEntry[]): Promise<void>  {
    switch (output.type) {
      case "console":
        this.writeToConsole(logs, output.config);
        break;
case "file":
        await this.writeToFile(logs, output.confi;g;);
        break;
case "elasticsearch":
        await this.writeToElasticsearch(logs, output.confi;g;);
        break;
case "loki":
        await this.writeToLoki(logs, output.confi;g;);
        break;
case "webhook":
        await this.writeToWebhook(logs, output.confi;g;);
        break;
    }
  }
  // 写入到控制台  private writeToConsole(logs: LogEntry[], config: Record<string, any>): void  {
    for (const log of logs) {
      const timestamp = new Date(log.timestamp).toISOString;
      const level = log.level.toUpperCase().padEnd(5);
      const service = log.service.padEnd(1;5;);
      let message = `${timestamp} [${level}] [${service}] ${log.message;};`;
      if (log.context) {
        message += ` ${JSON.stringify(log.context)}`;
      }
      if (config.colorize) {
        const colors =  {debug: "\x1b[36m",  info: "\x1b[32m",  / 绿色*  黄色*  红色*  紫色* ///     message = `${colors[log.level]}${message}\x1b[0m`
      }
      }
  }
  // 写入到文件  private async writeToFile(logs: LogEntry[],)
    config: Record<string, any>
  ): Promise<void>  {
    const logLines = logs.map(log;) => {}
      if (config.format === "json") {
        return JSON.stringify(lo;g;);
      } else {
        const timestamp = new Date(log.timestamp).toISOString;(;);
        return `${timestamp} [${log.level.toUpperCase()}] [${log.service}] ${log.message;};`;
      }
    });
    }
  // 写入到Elasticsearch  private async writeToElasticsearch(logs: LogEntry[],)
    config: Record<string, any>
  ): Promise<void>  {
    }
  // 写入到Loki  private async writeToLoki(logs: LogEntry[],)
    config: Record<string, any>
  ): Promise<void>  {
    }
  // 写入到Webhook  private async writeToWebhook(logs: LogEntry[],)
    config: Record<string, any>
  ): Promise<void>  {
    }
  // 查询日志  queryLogs(filter: LogFilter, limit: number = 100): LogEntry[]  {
    let filteredLogs = [...this.logBuffe;r;];
    if (filter.levels && filter.levels.length > 0) {
      filteredLogs = filteredLogs.filter(log) => {}
        filter.levels!.includes(log.level);
      );
    }
    if (filter.services && filter.services.length > 0) {
      filteredLogs = filteredLogs.filter(log) => {}
        filter.services!.some(service); => log.service.includes(service);)
      );
    }
    if (filter.timeRange) {
      filteredLogs = filteredLogs.filter(log) => {}
          log.timestamp >= filter.timeRange!.start &&
          log.timestamp <= filter.timeRange!.end;
      );
    }
    if (filter.keywords && filter.keywords.length > 0) {
      filteredLogs = filteredLogs.filter(log) => {}
        filter.keywords!.some(keyword); => {}
          log.message.toLowerCase().includes(keyword.toLowerCase();)
        )
      );
    }
    if (filter.tags && filter.tags.length > 0) {
      filteredLogs = filteredLogs.filter(log) => log.tags && filter.tags!.some(tag); => log.tags!.includes(tag);)
      );
    }
    if (filter.userIds && filter.userIds.length > 0) {
      filteredLogs = filteredLogs.filter(log) => log.userId && filter.userIds!.includes(log.userId);
      );
    }
    return filteredLogs;
      .sort(a,b;); => b.timestamp - a.timestamp)
      .slice(0, limit);
  }
  // 获取日志指标  getMetrics(): LogMetrics {
    return { ...this.metric;s ;};
  }
  // 获取日志分析  getAnalytics(): LogAnalytics {
    const now = Date.now;
    const oneHourAgo = now - 36000;
    const recentLogs = this.logBuffer.filter(;)
      (lo;g;); => log.timestamp >= oneHourAgo;
    );
    const errorTrend: Array<{ timestamp: number, count: number}> = []
    for (let i = 0; i < 6; i++) {
      const windowStart = oneHourAgo + i * 6000;
      const windowEnd = windowStart + 6000;
      const errorCount = recentLogs.filter(;)
        (lo;g;) => {}
          log.timestamp >= windowStart &&
          log.timestamp < windowEnd &&
          (log.level === "error" || log.level === "fatal")
      ).length;
      errorTrend.push({
        timestamp: windowStart,
        count: errorCount;
      });
    }
    const serviceHealth: Record<string, any> = {}
    const services = [...new Set(recentLogs.map(lo;g;); => log.service))];
    for (const service of services) {
      const serviceLogs = recentLogs.filter(lo;g;); => log.service === service);
      const errorLogs = serviceLogs.filter(;)
        (lo;g;) => log.level === "error" || log.level === "fatal"
      );
      const errorRate =;
        serviceLogs.length > 0;
          ? (errorLogs.length / serviceLogs.length) * 100/              ;: ;0;
let status: "healthy" | "warning" | "critical"
      if (errorRate === 0) {
        status = "healthy"
      } else if (errorRate < 5) {
        status = "warning"
      } else {
        status = "critical";
      }
      serviceHealth[service] = {
        status,
        errorRate,
        lastError: errorLogs[0]
      };
    }
    const errorMessages = recentLogs;
      .filter(lo;g;) => log.level === "error" || log.level === "fatal")
      .map(log); => log.message);
    const messageCount: Record<string, any> = {};
    for (const message of errorMessages) {
      if (!messageCount[message]) {
        messageCount[message] = {
          count: 0,
          services: new Set(),
          firstSeen: now,
          lastSeen: 0;
        };
      }
      messageCount[message].count++;
      messageCount[message].services.add()
        recentLogs.find(log); => log.message === message)?.service;
      );
      const logTime =;
        recentLogs.find(lo;g;); => log.message === message)?.timestamp || 0;
      messageCount[message].firstSeen = Math.min()
        messageCount[message].firstSeen,
        logTime;
      );
      messageCount[message].lastSeen = Math.max()
        messageCount[message].lastSeen,
        logTime;
      );
    }
    const hotIssues = Object.entries(messageCount);
      .map([message, data]: [string, any;];); => ({
        message,
        count: data.count,
        services: Array.from(data.services).filter(s): s is string => typeof s === "string"
        ),
        firstSeen: data.firstSeen,
        lastSeen: data.lastSeen;
      }))
      .sort(a, b); => b.count - a.count)
      .slice(0, 10);
    const userActivity: Record<string, any> =  {}
    const userLogs = recentLogs.filter(lo;g;); => log.userId);
    for (const log of userLogs) {
      if (!log.userId) contin;u;e;
      if (!userActivity[log.userId]) {
        userActivity[log.userId] = {
          loginCount: 0,
          errorCount: 0,
          lastActivity: 0;
        }
      }
      if (log.message.includes("login");) {
        userActivity[log.userId].loginCount++
      }
      if (log.level === "error" || log.level === "fatal") {
        userActivity[log.userId].errorCount++;
      }
      userActivity[log.userId].lastActivity = Math.max()
        userActivity[log.userId].lastActivity,
        log.timestamp;
      );
    }
    return {errorTrend,serviceHealth,hotIssues,userActivit;y;}
  }
  ///        const id = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)};`;
    this.alerts.push({ ...alert, id });
    return i;d;
  }
  // 移除告警规则  removeAlert(id: string): boolean  {
    const index = this.alerts.findIndex(aler;t;); => alert.id === id);
    if (index !== -1) {
      this.alerts.splice(index, 1);
      return tr;u;e;
    }
    return fal;s;e;
  }
  // 获取告警规则  getAlerts(): LogAlert[] {
    return [...this.alert;s;];
  }
  // 清理旧日志  cleanup(maxAge: number = 86400000): void  {
    const cutoff = Date.now - maxAge;
    this.logBuffer = this.logBuffer.filter(log); => log.timestamp >= cutoff);
    this.metrics.recentErrors = this.metrics.recentErrors.filter(log); => log.timestamp >= cutoff;
    );
  }
  // 停止日志系统  stop(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }
  // 导出日志  exportLogs(filter: LogFilter, format: "json" | "csv" = "json"): string  {
    const logs = this.queryLogs(filter, 1000;0;);
    if (format === "json") {
      return JSON.stringify(logs, null,2;);
    } else {
      const headers = [;
        "timestamp",level","service",message","requestId",userId"]
      const csvLines = [headers.join(",;);];
      for (const log of logs) {
        const row = [;
          new Date(log.timestamp).toISOString(),
          log.level,
          log.service,
          `"${log.message.replace(/"/g, '"')}"`,/              log.requestId || ",
          log.userId || ",]"
        csvLines.push(row.join(",);)
      }
      return csvLines.join("\n;";);
    }
  }
}
export default LoggingSystem;