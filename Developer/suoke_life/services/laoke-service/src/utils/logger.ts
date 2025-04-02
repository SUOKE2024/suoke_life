/**
 * 日志工具
 * 负责老克服务的日志记录和管理
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
}

class Logger {
  private static instance: Logger;
  private logEntries: LogEntry[] = [];
  private maxLogEntries: number = 10000; // 最大保留日志条数

  private constructor() {
    // 单例模式，私有构造函数
  }

  /**
   * 获取Logger实例
   */
  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * 记录调试级别日志
   * @param message 日志消息
   * @param context 上下文信息
   */
  public debug(message: string, context?: Record<string, any>): void {
    this.log('debug', message, context);
  }

  /**
   * 记录信息级别日志
   * @param message 日志消息
   * @param context 上下文信息
   */
  public info(message: string, context?: Record<string, any>): void {
    this.log('info', message, context);
  }

  /**
   * 记录警告级别日志
   * @param message 日志消息
   * @param context 上下文信息
   */
  public warn(message: string, context?: Record<string, any>): void {
    this.log('warn', message, context);
  }

  /**
   * 记录错误级别日志
   * @param message 日志消息
   * @param context 上下文信息
   */
  public error(message: string, context?: Record<string, any>): void {
    this.log('error', message, context);
  }

  /**
   * 记录日志
   * @param level 日志级别
   * @param message 日志消息
   * @param context 上下文信息
   */
  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    const timestamp = new Date().toISOString();
    const logEntry: LogEntry = {
      timestamp,
      level,
      message,
      context
    };

    // 添加到内存日志
    this.addLogEntry(logEntry);

    // 根据环境输出到控制台
    this.consoleOutput(logEntry);
  }

  /**
   * 添加日志条目到内存
   * @param logEntry 日志条目
   */
  private addLogEntry(logEntry: LogEntry): void {
    this.logEntries.push(logEntry);
    
    // 如果超过最大日志条数，清理旧日志
    if (this.logEntries.length > this.maxLogEntries) {
      this.logEntries = this.logEntries.slice(-this.maxLogEntries);
    }
  }

  /**
   * 输出日志到控制台
   * @param logEntry 日志条目
   */
  private consoleOutput(logEntry: LogEntry): void {
    const { timestamp, level, message, context } = logEntry;
    const formattedMessage = `${timestamp} [${level.toUpperCase()}] ${message}`;
    
    switch (level) {
      case 'debug':
        console.debug(formattedMessage, context || '');
        break;
      case 'info':
        console.info(formattedMessage, context || '');
        break;
      case 'warn':
        console.warn(formattedMessage, context || '');
        break;
      case 'error':
        console.error(formattedMessage, context || '');
        break;
    }
  }

  /**
   * 获取最近的日志
   * @param count 获取条数
   * @param level 按级别筛选
   * @returns 日志条目数组
   */
  public getRecentLogs(count: number = 100, level?: LogLevel): LogEntry[] {
    let filteredLogs = this.logEntries;
    
    if (level) {
      filteredLogs = filteredLogs.filter(log => log.level === level);
    }
    
    return filteredLogs.slice(-count);
  }

  /**
   * 清空日志
   */
  public clearLogs(): void {
    this.logEntries = [];
  }
}

// 导出单例实例
export const logger = Logger.getInstance();