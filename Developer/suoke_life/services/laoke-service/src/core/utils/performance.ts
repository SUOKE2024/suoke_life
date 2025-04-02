import { performance } from 'perf_hooks';
import os from 'os';
import * as metrics from '../metrics';
import logger from './logger';

/**
 * 性能监控器类
 * 用于监控各种操作的性能
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private marks: Map<string, number>;
  private timers: Map<string, NodeJS.Timeout>;
  private cpuUsageHistory: number[];
  private memoryUsageHistory: number[];
  private historySize: number = 10;
  private cpuCheckInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.marks = new Map();
    this.timers = new Map();
    this.cpuUsageHistory = [];
    this.memoryUsageHistory = [];
    this.startSystemMonitoring();
  }

  /**
   * 获取单例实例
   */
  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * 启动系统资源监控
   */
  private startSystemMonitoring(): void {
    if (this.cpuCheckInterval) {
      clearInterval(this.cpuCheckInterval);
    }

    // 每5秒检查一次系统资源
    this.cpuCheckInterval = setInterval(() => {
      this.checkSystemResources();
    }, 5000);
  }

  /**
   * 检查系统资源使用情况
   */
  private checkSystemResources(): void {
    // 内存使用率
    const memoryUsage = process.memoryUsage();
    const memoryUsagePercent = (memoryUsage.heapUsed / memoryUsage.heapTotal) * 100;
    
    // 添加到历史记录
    this.memoryUsageHistory.push(memoryUsagePercent);
    if (this.memoryUsageHistory.length > this.historySize) {
      this.memoryUsageHistory.shift();
    }
    
    // CPU使用率计算
    const cpus = os.cpus();
    const cpuUsage = cpus.reduce((acc, cpu) => {
      const total = Object.values(cpu.times).reduce((total, time) => total + time, 0);
      const idle = cpu.times.idle;
      return acc + ((total - idle) / total);
    }, 0) / cpus.length * 100;
    
    // 添加到历史记录
    this.cpuUsageHistory.push(cpuUsage);
    if (this.cpuUsageHistory.length > this.historySize) {
      this.cpuUsageHistory.shift();
    }
    
    // 如果CPU或内存使用率过高，记录警告
    if (cpuUsage > 80) {
      logger.warn(`高CPU使用率: ${cpuUsage.toFixed(2)}%`);
    }
    
    if (memoryUsagePercent > 85) {
      logger.warn(`高内存使用率: ${memoryUsagePercent.toFixed(2)}%`);
    }
    
    // 更新性能指标
    this.updatePerformanceMetrics(cpuUsage, memoryUsagePercent);
  }

  /**
   * 更新性能指标
   */
  private updatePerformanceMetrics(cpuUsage: number, memoryUsage: number): void {
    // 假设metrics模块有这些方法
    if (metrics.updateGauge) {
      metrics.updateGauge('cpu_usage', cpuUsage);
      metrics.updateGauge('memory_usage', memoryUsage);
    }
  }

  /**
   * 标记开始时间
   * @param name 标记名称
   */
  public mark(name: string): void {
    this.marks.set(name, performance.now());
  }

  /**
   * 测量从标记到当前的时间
   * @param name 标记名称
   * @returns 时间间隔（毫秒）
   */
  public measure(name: string): number {
    const start = this.marks.get(name);
    if (!start) {
      throw new Error(`标记 ${name} 不存在`);
    }
    const end = performance.now();
    const duration = end - start;
    return duration;
  }

  /**
   * 测量并记录操作持续时间
   * @param name 标记名称
   * @param type 操作类型
   * @param status 操作状态
   * @returns 时间间隔（毫秒）
   */
  public measureAndRecord(name: string, type: string, status: string): number {
    const duration = this.measure(name);
    this.recordOperation(type, status, duration);
    return duration;
  }

  /**
   * 开始计时操作
   * @param name 计时名称
   * @param timeout 超时时间（毫秒）
   * @param callback 超时回调
   */
  public startTimer(name: string, timeout: number, callback?: () => void): void {
    this.mark(name);
    
    // 设置超时检查
    const timer = setTimeout(() => {
      const duration = this.measure(name);
      logger.warn(`操作 ${name} 超时，已运行 ${duration.toFixed(2)} ms`);
      if (callback) {
        callback();
      }
    }, timeout);
    
    this.timers.set(name, timer);
  }

  /**
   * 停止计时操作
   * @param name 计时名称
   * @param type 操作类型
   * @param status 操作状态
   * @returns 时间间隔（毫秒）
   */
  public stopTimer(name: string, type?: string, status?: string): number {
    const timer = this.timers.get(name);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(name);
    }
    
    const duration = this.measure(name);
    
    if (type && status) {
      this.recordOperation(type, status, duration);
    }
    
    return duration;
  }

  /**
   * 记录操作
   * @param type 操作类型
   * @param status 操作状态
   * @param duration 持续时间（毫秒）
   */
  public recordOperation(type: string, status: string, duration: number): void {
    // 根据操作类型分发到不同的记录函数
    if (type.startsWith('media_')) {
      metrics.recordMediaProcessing(type, status, duration);
    } else if (type.startsWith('dialect_')) {
      const dialectParts = type.split('_');
      if (dialectParts.length > 1) {
        metrics.recordDialectProcessing(
          dialectParts[1], 
          dialectParts.slice(2).join('_'), 
          status, 
          duration
        );
      }
    } else {
      metrics.recordAiProcessing(type, status, duration);
    }
    
    // 记录日志
    if (status === 'success') {
      if (duration > 5000) {
        logger.warn(`长时间操作: ${type} 花费 ${duration.toFixed(2)} ms`);
      } else {
        logger.debug(`操作完成: ${type} 花费 ${duration.toFixed(2)} ms`);
      }
    } else {
      logger.error(`操作失败: ${type} 花费 ${duration.toFixed(2)} ms`);
    }
  }

  /**
   * 获取CPU使用率
   * @returns CPU使用率百分比
   */
  public getCpuUsage(): number {
    return this.cpuUsageHistory.length > 0 
      ? this.cpuUsageHistory[this.cpuUsageHistory.length - 1] 
      : 0;
  }

  /**
   * 获取内存使用率
   * @returns 内存使用率百分比
   */
  public getMemoryUsage(): number {
    return this.memoryUsageHistory.length > 0 
      ? this.memoryUsageHistory[this.memoryUsageHistory.length - 1] 
      : 0;
  }

  /**
   * 获取平均CPU使用率
   * @returns 平均CPU使用率百分比
   */
  public getAverageCpuUsage(): number {
    if (this.cpuUsageHistory.length === 0) return 0;
    const sum = this.cpuUsageHistory.reduce((acc, val) => acc + val, 0);
    return sum / this.cpuUsageHistory.length;
  }

  /**
   * 获取平均内存使用率
   * @returns 平均内存使用率百分比
   */
  public getAverageMemoryUsage(): number {
    if (this.memoryUsageHistory.length === 0) return 0;
    const sum = this.memoryUsageHistory.reduce((acc, val) => acc + val, 0);
    return sum / this.memoryUsageHistory.length;
  }

  /**
   * 检查系统是否处于高负载状态
   * @returns 是否高负载
   */
  public isHighLoad(): boolean {
    const avgCpu = this.getAverageCpuUsage();
    const avgMem = this.getAverageMemoryUsage();
    return avgCpu > 70 || avgMem > 80;
  }

  /**
   * 清理资源
   */
  public cleanup(): void {
    // 清除所有计时器
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers.clear();
    
    // 停止系统监控
    if (this.cpuCheckInterval) {
      clearInterval(this.cpuCheckInterval);
      this.cpuCheckInterval = null;
    }
  }
}

/**
 * 简单获取性能监控实例
 */
export const getPerformanceMonitor = (): PerformanceMonitor => {
  return PerformanceMonitor.getInstance();
};

/**
 * 节流函数：限制函数调用频率
 * @param func 要节流的函数
 * @param limit 时间限制（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => ReturnType<T> | undefined {
  let lastFunc: NodeJS.Timeout;
  let lastRan: number = 0;
  
  return function(this: any, ...args: Parameters<T>): ReturnType<T> | undefined {
    const context = this;
    
    if (!lastRan) {
      const result = func.apply(context, args);
      lastRan = Date.now();
      return result;
    } else {
      clearTimeout(lastFunc);
      lastFunc = setTimeout(() => {
        if (Date.now() - lastRan >= limit) {
          const result = func.apply(context, args);
          lastRan = Date.now();
          return result;
        }
      }, limit - (Date.now() - lastRan));
    }
  };
}

/**
 * 防抖函数：延迟函数执行，直到一段时间过去
 * @param func 要防抖的函数
 * @param wait 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return function(this: any, ...args: Parameters<T>): void {
    const context = this;
    clearTimeout(timeout);
    
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

/**
 * 缓存函数结果
 * @param func 要缓存的函数
 * @param ttl 缓存有效期（毫秒）
 * @returns 缓存包装后的函数
 */
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  ttl: number = 0
): (...args: Parameters<T>) => ReturnType<T> {
  const cache = new Map<string, { value: ReturnType<T>, timestamp: number }>();
  
  return function(this: any, ...args: Parameters<T>): ReturnType<T> {
    const key = JSON.stringify(args);
    const cachedItem = cache.get(key);
    
    if (cachedItem) {
      const now = Date.now();
      if (ttl === 0 || now - cachedItem.timestamp < ttl) {
        return cachedItem.value;
      }
    }
    
    const result = func.apply(this, args);
    cache.set(key, { value: result, timestamp: Date.now() });
    return result;
  };
}

/**
 * 批处理函数
 * @param func 要批处理的函数
 * @param batchSize 批处理大小
 * @returns 批处理包装后的函数
 */
export function batchProcess<T, R>(
  func: (items: T[]) => Promise<R[]>,
  batchSize: number = 10
): (items: T[]) => Promise<R[]> {
  return async function(items: T[]): Promise<R[]> {
    const results: R[] = [];
    
    // 分批处理
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchResults = await func(batch);
      results.push(...batchResults);
    }
    
    return results;
  };
}

/**
 * 重试函数
 * @param func 要重试的函数
 * @param maxRetries 最大重试次数
 * @param delay 重试间隔（毫秒）
 * @returns 重试包装后的函数
 */
export function retry<T>(
  func: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): () => Promise<T> {
  return async function(): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await func();
      } catch (error) {
        lastError = error as Error;
        
        // 如果不是最后一次尝试，等待后重试
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay));
          // 指数退避
          delay *= 2;
        }
      }
    }
    
    throw lastError;
  };
}

/**
 * 并行处理函数
 * @param items 要处理的项目
 * @param func 处理单个项目的函数
 * @param concurrency 并发数
 * @returns 处理结果
 */
export async function parallelProcess<T, R>(
  items: T[],
  func: (item: T) => Promise<R>,
  concurrency: number = 5
): Promise<R[]> {
  // 如果项目数小于并发数，直接并行处理
  if (items.length <= concurrency) {
    return Promise.all(items.map(item => func(item)));
  }
  
  const results: R[] = [];
  const executing: Promise<void>[] = [];
  
  for (const item of items) {
    // 创建处理任务
    const process = async () => {
      const result = await func(item);
      results.push(result);
    };
    
    // 添加到执行队列
    const execution = process();
    executing.push(execution);
    
    // 如果达到并发限制，等待一个任务完成
    if (executing.length >= concurrency) {
      await Promise.race(executing);
      // 清理已完成的任务
      for (let i = executing.length - 1; i >= 0; i--) {
        if (executing[i].isFulfilled) {
          executing.splice(i, 1);
        }
      }
    }
  }
  
  // 等待所有剩余任务完成
  await Promise.all(executing);
  
  return results;
}

// 添加Promise.isFulfilled属性（类型增强）
declare global {
  interface Promise<T> {
    isFulfilled?: boolean;
  }
} 