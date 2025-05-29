import { ReactTestRenderer } from 'react-test-renderer';

// 全局类型声明
declare global {
  var gc: (() => void) | undefined;
}

// 简单的性能测试工具
export class TestUtils {
  /**
   * 测量渲染时间
   */
  static measureRenderTime(renderFn: () => void): number {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    return endTime - startTime;
  }

  /**
   * 测量多次渲染的平均时间
   */
  static measureAverageRenderTime(renderFn: () => void, iterations: number = 5): number {
    const times: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
      const time = this.measureRenderTime(renderFn);
      times.push(time);
    }
    
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }

  /**
   * 性能断言
   */
  static expectRenderTimeBelow(renderFn: () => void, maxTime: number): void {
    const renderTime = this.measureRenderTime(renderFn);
    expect(renderTime).toBeLessThan(maxTime);
  }

  /**
   * 批量性能测试
   */
  static expectBatchRenderTimeBelow(renderFn: () => void, count: number, maxTotalTime: number): void {
    const startTime = performance.now();
    
    for (let i = 0; i < count; i++) {
      renderFn();
    }
    
    const totalTime = performance.now() - startTime;
    expect(totalTime).toBeLessThan(maxTotalTime);
  }

  /**
   * 内存使用监控（简化版）
   */
  static getMemoryUsage(): number {
    if (typeof performance !== 'undefined' && (performance as any).memory) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return 0;
  }

  /**
   * 检测内存泄漏
   */
  static detectMemoryLeak(testFn: () => void, iterations: number = 10): boolean {
    const initialMemory = this.getMemoryUsage();
    
    for (let i = 0; i < iterations; i++) {
      testFn();
    }
    
    // 强制垃圾回收（如果可用）
    if (typeof globalThis !== 'undefined' && (globalThis as any).gc) {
      (globalThis as any).gc();
    }
    
    const finalMemory = this.getMemoryUsage();
    const memoryIncrease = finalMemory - initialMemory;
    
    // 如果内存增长超过10MB，可能存在内存泄漏
    return memoryIncrease > 10 * 1024 * 1024;
  }

  /**
   * 创建性能基准
   */
  static createPerformanceBenchmark(name: string, renderFn: () => void): PerformanceBenchmark {
    return new PerformanceBenchmark(name, renderFn);
  }
}

/**
 * 性能基准测试类
 */
export class PerformanceBenchmark {
  private name: string;
  private renderFn: () => void;
  private results: number[] = [];

  constructor(name: string, renderFn: () => void) {
    this.name = name;
    this.renderFn = renderFn;
  }

  /**
   * 运行基准测试
   */
  run(iterations: number = 10): PerformanceResult {
    this.results = [];
    
    for (let i = 0; i < iterations; i++) {
      const time = TestUtils.measureRenderTime(this.renderFn);
      this.results.push(time);
    }
    
    return this.getResults();
  }

  /**
   * 获取测试结果
   */
  private getResults(): PerformanceResult {
    const sorted = [...this.results].sort((a, b) => a - b);
    const sum = this.results.reduce((a, b) => a + b, 0);
    
    return {
      name: this.name,
      iterations: this.results.length,
      average: sum / this.results.length,
      min: Math.min(...this.results),
      max: Math.max(...this.results),
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
    };
  }
}

/**
 * 性能测试结果接口
 */
export interface PerformanceResult {
  name: string;
  iterations: number;
  average: number;
  min: number;
  max: number;
  median: number;
  p95: number;
  p99: number;
}

/**
 * Mock数据生成器
 */
export class MockDataGenerator {
  /**
   * 生成随机字符串
   */
  static randomString(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * 生成随机数字
   */
  static randomNumber(min: number = 0, max: number = 100): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  /**
   * 生成随机布尔值
   */
  static randomBoolean(): boolean {
    return Math.random() > 0.5;
  }

  /**
   * 生成随机日期
   */
  static randomDate(start: Date = new Date(2020, 0, 1), end: Date = new Date()): Date {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  }

  /**
   * 从数组中随机选择元素
   */
  static randomChoice<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }
} 