#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

// 1. 修复ErrorBoundary的React.memo问题
function fixErrorBoundary() {
  const errorBoundaryPath = src/components/common/ErrorBoundary.tsx";
  if (fs.existsSync(errorBoundaryPath)) {
    let content = fs.readFileSync(errorBoundaryPath, "utf8);

    // 移除React.memo包装
content = content.replace(
      "export default React.memo(ErrorBoundary);",
      export default ErrorBoundary;"
    );

    fs.writeFileSync(errorBoundaryPath, content);
    }
}

// 2. 创建Logger服务替换console输出
function createLoggerService() {
  const loggerContent = `/**
 * 统一日志服务
 * 在开发环境输出到控制台，生产环境可发送到监控服务
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3}

interface LogEntry {;
  level: LogLevel;
  message: string;
  timestamp: Date;
  context?: any;
  stack?: string;
}

class Logger {
  private static instance: Logger;
  private logLevel: LogLevel = __DEV__ ? LogLevel.DEBUG : LogLevel.WARN;
  private logs: LogEntry[] = [];
  private maxLogs = 1000;

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private log(level: LogLevel, message: string, context?: any): void {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date(),
      context,
      stack: level >= LogLevel.ERROR ? new Error().stack : undefined};

    // 添加到内存日志
this.logs.push(entry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    // 开发环境输出到控制台
if (__DEV__ && level >= this.logLevel) {
      const timestamp = entry.timestamp.toISOString();
      const levelName = LogLevel[level];

      switch (level) {
        case LogLevel.DEBUG:
          break;
        case LogLevel.INFO:
          break;
        case LogLevel.WARN:
          break;
        case LogLevel.ERROR:
          if (entry.stack) {
            }
          break;
      }
    }

    // 生产环境发送到监控服务
if (!__DEV__ && level >= LogLevel.ERROR) {
      this.sendToMonitoring(entry);
    }
  }

  private async sendToMonitoring(entry: LogEntry): Promise<void> {
    try {
      // 这里可以集成Sentry、Bugsnag等监控服务
      // await monitoringService.reportError(entry)
    } catch (error) {
      // 静默失败，避免日志服务本身出错
    }
  }

  debug(message: string, context?: any): void {
    this.log(LogLevel.DEBUG, message, context)
  }

  info(message: string, context?: any): void {
    this.log(LogLevel.INFO, message, context);
  }

  warn(message: string, context?: any): void {
    this.log(LogLevel.WARN, message, context);
  }

  error(message: string, context?: any): void {
    this.log(LogLevel.ERROR, message, context);
  }

  // 获取最近的日志
getRecentLogs(count: number = 100): LogEntry[] {
    return this.logs.slice(-count);
  }

  // 清除日志
clearLogs(): void {
    this.logs = [];
  }

  // 设置日志级别
setLogLevel(level: LogLevel): void {
    this.logLevel = level;
  }
}

// 导出单例实例
export const logger = Logger.getInstance();

// 便捷的全局函数
export const log = {
  debug: (message: string, context?: any) => logger.debug(message, context),
  info: (message: string, context?: any) => logger.info(message, context),
  warn: (message: string, context?: any) => logger.warn(message, context),;
  error: (message: string, context?: any) => logger.error(message, context)};
`;

  const loggerPath = "src/services/Logger.ts";
  fs.writeFileSync(loggerPath, loggerContent);
  }

// 3. 修复useHealthData hook的依赖项问题
function fixUseHealthDataHook() {
  const hookPath = "src/hooks/useHealthData.ts";
  if (fs.existsSync(hookPath)) {
    let content = fs.readFileSync(hookPath, utf8");

    // 修复addHealthData的依赖项
content = content.replace(
      /const addHealthData = useCallback\(\(data: HealthData\) => \{[\s\S]*?\}, \[\]\); \/\/ TODO:.*$/m,
      `const addHealthData = useCallback((data: HealthData) => {;
    setHealthData((prev) => [...prev, data]);
  }, []);`
    );

    // 修复removeHealthData的依赖项
content = content.replace(
      /const removeHealthData = useCallback\(\(id: string\) => \{[\s\S]*?\}, \[\]\); \/\/ TODO:.*$/m,
      `const removeHealthData = useCallback((id: string) => {;
    setHealthData((prev) => prev.filter((item) => item.id !== id));
  }, []);`
    );

    fs.writeFileSync(hookPath, content);
    }
}

// 4. 更新App.tsx使用Logger
function updateAppWithLogger() {
  const appPath = src/App.tsx";
  if (fs.existsSync(appPath)) {
    let content = fs.readFileSync(appPath, "utf8);

    // 添加Logger导入
if (!content.includes("import { log }")) {
      content = content.replace(
        import React from "react";",
        `import React from "react";
import { log } from "./services/Logger";`
      );
    }

    // 替换console.log
content = content.replace(
      ",
      "log.debug("App 正在渲染...");"
    );

    fs.writeFileSync(appPath, content);
    }
}

// 5. 创建类型安全的API接口
function createTypeSafeApiInterfaces() {
  const typesContent = `/**
 * API相关的类型定义
 * 替换any类型，提供类型安全
 */
;
// 基础API响应类型
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  timestamp: string;
}

// API错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  stack?: string;
}

// API请求配置
export interface ApiRequest {
  url: string;
  method: "GET" | POST" | "PUT | "DELETE" | PATCH";
  data?: Record<string, unknown>;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
  timeout?: number;
}

// 离线数据类型
export interface OfflineData {
  id: string;
  timestamp: number;
  operation: "CREATE | "UPDATE" | DELETE";
  entity: string;
  payload: Record<string, unknown>;
  synced: boolean;
}

// 数据冲突类型
export interface DataConflict {
  id: string;
  entity: string;
  clientData: Record<string, unknown>;
  serverData: Record<string, unknown>;
  timestamp: number;
  resolved: boolean;
}

// 健康数据类型
export interface HealthMetric {
  id: string;
  type: "heart_rate | "blood_pressure" | weight" | "blood_sugar | "sleep" | steps";
  value: number | string;
  unit: string;
  timestamp: string;
  source: "manual | "device" | api";
  metadata?: Record<string, unknown>;
}

// 智能体消息类型
export interface AgentMessage {
  id: string;
  agentId: string;
  content: string;
  type: "text | "image" | audio" | "file;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// 诊断数据类型
export interface DiagnosisData {
  id: string;
  userId: string;
  type: "five_diagnosis" | symptom_analysis" | "health_assessment;
  data: Record<string, unknown>;
  result?: DiagnosisResult;
  timestamp: string;
  status: "pending" | processing" | "completed | "failed";
}

export interface DiagnosisResult {
  id: string;
  diagnosis: string;
  confidence: number;
  recommendations: string[];
  followUp?: string;
  metadata?: Record<string, unknown>;
}

// 用户配置类型
export interface UserPreferences {
  theme: light" | "dark | "auto";
  language: zh" | "en;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  accessibility: AccessibilitySettings;
}

export interface NotificationSettings {
  enabled: boolean;
  types: {
    health_reminders: boolean;
    agent_messages: boolean;
    system_updates: boolean;
    emergency_alerts: boolean;
  };
  schedule: {
    start_time: string;
    end_time: string;
    timezone: string;
  };
}

export interface PrivacySettings {
  data_sharing: boolean;
  analytics: boolean;
  personalization: boolean;
  third_party_integrations: boolean;
}

export interface AccessibilitySettings {
  font_size: "small" | medium" | "large | "extra_large";
  high_contrast: boolean;
  screen_reader: boolean;
  voice_commands: boolean;
  haptic_feedback: boolean;
}
`;

  const typesPath = src/types/api.ts";
  fs.writeFileSync(typesPath, typesContent);
  }

// 6. 更新ESLint配置
function updateESLintConfig() {
  const eslintPath = .eslintrc.js";
  if (fs.existsSync(eslintPath)) {
    let content = fs.readFileSync(eslintPath, "utf8);

    // 添加react-hooks/exhaustive-deps规则
if (!content.includes("react-hooks/exhaustive-deps")) {
      content = content.replace(
        react-hooks/exhaustive-deps": "warn",
        "react-hooks/exhaustive-deps": "error"
      );
    }

    // 添加TypeScript严格规则
const newRules = `
    // TypeScript严格规则
    "@typescript-eslint/no-explicit-any": error",
    "@typescript-eslint/no-unused-vars: ["error", { argsIgnorePattern: ^_" }],
    "@typescript-eslint/explicit-function-return-type: "warn",
    @typescript-eslint/no-non-null-assertion": "error,

    // React性能规则
    "react/jsx-no-bind": warn",
    "react/jsx-no-literals: "off",
    react/no-array-index-key": "warn,

    // 内存泄漏预防
    "react-hooks/exhaustive-deps": error",`;

    content = content.replace(
      "privacy/no-plain-sensitive-data": "warn",,
      `privacy/no-plain-sensitive-data": "warn",${newRules}`
    );

    fs.writeFileSync(eslintPath, content);
    }
}

// 7. 创建性能监控Hook
function createPerformanceMonitoringHook() {
  const hookContent = `import { useEffect, useRef, useState  } from "react;
import { log } from ";../services/Logger";

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  componentName: string;
}

interface UsePerformanceMonitorOptions {
  componentName: string;
  enableMemoryMonitoring?: boolean;
  threshold?: number; // 渲染时间阈值(ms)
}

export const usePerformanceMonitor = ({
  componentName,
  enableMemoryMonitoring = false,
  threshold = 16, // 60fps = 16.67ms per frame
}: UsePerformanceMonitorOptions) => {
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

  useEffect(() => {
    renderStartTime.current = performance.now();
  });

  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;

    const newMetrics: PerformanceMetrics = {
      renderTime,
      componentName};

    // 获取内存使用情况（如果支持）
    if (enableMemoryMonitoring && memory" in performance) {
      newMetrics.memoryUsage = (performance as any).memory?.usedJSHeapSize
    }

    setMetrics(newMetrics);

    // 如果渲染时间超过阈值，记录警告
if (renderTime > threshold) {
      log.warn(\`组件 \${componentName} 渲染时间过长: \${renderTime.toFixed(2)}ms\`, {
        renderTime,
        threshold,
        memoryUsage: newMetrics.memoryUsage});
    }

    // 在开发环境记录性能指标
if (__DEV__) {
      log.debug(\`组件 \${componentName} 性能指标\`, newMetrics);
    }
  });

  return metrics;
};

// 高阶组件版本
export const withPerformanceMonitor = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: UsePerformanceMonitorOptions
) => {
  const WithPerformanceMonitor = (props: P) => {;
    usePerformanceMonitor(options);
    return <WrappedComponent {...props} />;
  };

  WithPerformanceMonitor.displayName = \`withPerformanceMonitor(\${WrappedComponent.displayName || WrappedComponent.name})\`;

  return WithPerformanceMonitor;
};
`;

  const hookPath = "src/hooks/usePerformanceMonitor.ts;
  fs.writeFileSync(hookPath, hookContent);
  }

// 8. 创建内存泄漏检测工具
function createMemoryLeakDetector() {
  const detectorContent = `/**
 * 内存泄漏检测工具
 * 帮助识别和预防常见的内存泄漏问题
 */
;
import { useEffect, useRef  } from "react;
import { log } from ";../services/Logger";

// 全局引用跟踪器
class ReferenceTracker {
  private static instance: ReferenceTracker;
  private references = new Map<string, WeakRef<any>>();
  private timers = new Set<NodeJS.Timeout>();
  private intervals = new Set<NodeJS.Timeout>();
  private listeners = new Map<string, { element: any; event: string; handler: any }>();

  static getInstance(): ReferenceTracker {
    if (!ReferenceTracker.instance) {
      ReferenceTracker.instance = new ReferenceTracker();
    }
    return ReferenceTracker.instance;
  }

  // 跟踪定时器
trackTimer(timer: NodeJS.Timeout, componentName: string): void {
    this.timers.add(timer);
    log.debug(\`定时器已创建: \${componentName}\`, { timerId: timer });
  }

  // 清理定时器
clearTimer(timer: NodeJS.Timeout): void {
    clearTimeout(timer);
    this.timers.delete(timer);
  }

  // 跟踪间隔器
trackInterval(interval: NodeJS.Timeout, componentName: string): void {
    this.intervals.add(interval);
    log.debug(\`间隔器已创建: \${componentName}\`, { intervalId: interval });
  }

  // 清理间隔器
clearInterval(interval: NodeJS.Timeout): void {
    clearInterval(interval);
    this.intervals.delete(interval);
  }

  // 跟踪事件监听器
trackListener(
    element: any,
    event: string,
    handler: any,
    componentName: string
  ): void {
    const key = \`\${componentName}_\${event}_\${Date.now()}\`;
    this.listeners.set(key, { element, event, handler });
    log.debug(\`事件监听器已添加: \${componentName}\`, { event, key });
  }

  // 移除事件监听器
removeListener(key: string): void {
    const listener = this.listeners.get(key);
    if (listener) {
      listener.element.removeEventListener(listener.event, listener.handler);
      this.listeners.delete(key);
    }
  }

  // 获取泄漏报告
getLeakReport(): any {
    return {
      activeTimers: this.timers.size,
      activeIntervals: this.intervals.size,
      activeListeners: this.listeners.size,
      details: {
        timers: Array.from(this.timers),
        intervals: Array.from(this.intervals),
        listeners: Array.from(this.listeners.keys())}};
  }

  // 清理所有引用
cleanup(): void {
    this.timers.forEach(timer => clearTimeout(timer));
    this.intervals.forEach(interval => clearInterval(interval));
    this.listeners.forEach((listener, key) => {
      this.removeListener(key);
    });

    this.timers.clear();
    this.intervals.clear();
    this.listeners.clear();
  }
}

// Hook: 检测内存泄漏
export const useMemoryLeakDetector = (componentName: string) => {;
  const tracker = useRef(ReferenceTracker.getInstance());
  const mountTime = useRef(Date.now());

  useEffect(() => {
    log.debug(\`组件挂载: \${componentName}\`);

    return () => {
      const unmountTime = Date.now();
      const lifeTime = unmountTime - mountTime.current;

      log.debug(\`组件卸载: \${componentName}\`, {
        lifeTime: \`\${lifeTime}ms\`,
        leakReport: tracker.current.getLeakReport()});

      // 检查是否有潜在的内存泄漏
const report = tracker.current.getLeakReport();
      if (report.activeTimers > 0 || report.activeIntervals > 0 || report.activeListeners > 0) {
        log.warn(\`潜在内存泄漏检测到: \${componentName}\`, report);
      }
    };
  }, [componentName]);

  // 返回安全的清理函数
return {
    trackTimer: (timer: NodeJS.Timeout) => tracker.current.trackTimer(timer, componentName),
    clearTimer: (timer: NodeJS.Timeout) => tracker.current.clearTimer(timer),
    trackInterval: (interval: NodeJS.Timeout) => tracker.current.trackInterval(interval, componentName),
    clearInterval: (interval: NodeJS.Timeout) => tracker.current.clearInterval(interval),
    trackListener: (element: any, event: string, handler: any) =>
      tracker.current.trackListener(element, event, handler, componentName),
    getLeakReport: () => tracker.current.getLeakReport()};
};

// Hook: 安全的定时器
export const useSafeTimer = (componentName: string) => {;
  const { trackTimer, clearTimer } = useMemoryLeakDetector(componentName);
  const timers = useRef<Set<NodeJS.Timeout>>(new Set());

  const setTimeout = (callback: () => void, delay: number): NodeJS.Timeout => {
    const timer = global.setTimeout(() => {;
      callback();
      timers.current.delete(timer);
    }, delay);

    timers.current.add(timer);
    trackTimer(timer);
    return timer;
  };

  const clearTimeout = (timer: NodeJS.Timeout): void => {
    if (timers.current.has(timer)) {;
      clearTimer(timer);
      timers.current.delete(timer);
    }
  };

  // 组件卸载时清理所有定时器
useEffect(() => {
    return () => {
      timers.current.forEach(timer => clearTimer(timer));
      timers.current.clear();
    };
  }, [clearTimer]);

  return { setTimeout, clearTimeout };
};

// Hook: 安全的事件监听器
export const useSafeEventListener = (
  element: any,
  event: string,
  handler: any,
  options?: any,
  componentName: string = Unknown"
) => {;
  const { trackListener } = useMemoryLeakDetector(componentName);

  useEffect(() => {
    if (!element) return;

    element.addEventListener(event, handler, options);
    trackListener(element, event, handler);

    return () => {
      element.removeEventListener(event, handler, options);
    };
  }, [element, event, handler, options, trackListener]);
};
`;

  const detectorPath = "src/utils/memoryLeakDetector.ts;
  fs.writeFileSync(detectorPath, detectorContent);
  }

// 主执行函数
async function main() {
  try {
    // 确保目录存在
const dirs = [src/services", "src/types, "src/hooks", src/utils"];
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });

    // 执行修复
fixErrorBoundary();
    createLoggerService();
    fixUseHealthDataHook();
    updateAppWithLogger();
    createTypeSafeApiInterfaces();
    updateESLintConfig();
    createPerformanceMonitoringHook();
    createMemoryLeakDetector();

    } catch (error) {
    process.exit(1);
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  fixErrorBoundary,
  createLoggerService,
  fixUseHealthDataHook,
  updateAppWithLogger,
  createTypeSafeApiInterfaces,
  updateESLintConfig,
  createPerformanceMonitoringHook,
  createMemoryLeakDetector};