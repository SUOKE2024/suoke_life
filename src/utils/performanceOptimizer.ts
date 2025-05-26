import { InteractionManager, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { monitoringSystem } from './monitoringSystem';

// 性能配置
const PERFORMANCE_CONFIG = {
  MEMORY_WARNING_THRESHOLD: 80, // 内存使用率警告阈值（%）
  NETWORK_TIMEOUT: 10000, // 网络请求超时时间（毫秒）
  CACHE_SIZE_LIMIT: 50 * 1024 * 1024, // 缓存大小限制（50MB）
  IMAGE_CACHE_LIMIT: 100, // 图片缓存数量限制
  RENDER_BATCH_SIZE: 10, // 渲染批处理大小
  DEBOUNCE_DELAY: 300, // 防抖延迟（毫秒）
};

// 性能指标类型
export interface PerformanceMetrics {
  memoryUsage: number;
  cpuUsage: number;
  renderTime: number;
  networkLatency: number;
  cacheHitRate: number;
  frameDrops: number;
  timestamp: number;
}

export interface OptimizationResult {
  action: string;
  improvement: number;
  description: string;
  timestamp: number;
}

// 内存管理器
class MemoryManager {
  private static instance: MemoryManager;
  private memoryWarningCallbacks: Array<() => void> = [];
  private isMonitoring = false;
  private monitoringInterval?: ReturnType<typeof setInterval>;

  static getInstance(): MemoryManager {
    if (!MemoryManager.instance) {
      MemoryManager.instance = new MemoryManager();
    }
    return MemoryManager.instance;
  }

  // 开始内存监控
  startMonitoring(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, 5000); // 每5秒检查一次
  }

  // 停止内存监控
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
    this.isMonitoring = false;
  }

  // 添加内存警告回调
  addMemoryWarningCallback(callback: () => void): void {
    this.memoryWarningCallbacks.push(callback);
  }

  // 移除内存警告回调
  removeMemoryWarningCallback(callback: () => void): void {
    const index = this.memoryWarningCallbacks.indexOf(callback);
    if (index > -1) {
      this.memoryWarningCallbacks.splice(index, 1);
    }
  }

  // 检查内存使用情况
  private async checkMemoryUsage(): Promise<void> {
    try {
      // 模拟获取内存使用情况
      const memoryUsage = await this.getMemoryUsage();
      
      if (memoryUsage > PERFORMANCE_CONFIG.MEMORY_WARNING_THRESHOLD) {
        this.triggerMemoryWarning();
        await this.performMemoryCleanup();
      }

      // 记录性能指标
      monitoringSystem.recordMetric({
        performance: {
          memoryUsage,
          cpuUsage: 0,
          networkLatency: 0,
          renderTime: 0,
          apiResponseTime: 0
        }
      });
    } catch (error) {
      console.error('内存检查失败:', error);
    }
  }

  // 获取内存使用率
  private async getMemoryUsage(): Promise<number> {
    // 在真实应用中，这里应该使用原生模块获取实际内存使用情况
    // 这里使用模拟数据
    return Math.random() * 100;
  }

  // 触发内存警告
  private triggerMemoryWarning(): void {
    this.memoryWarningCallbacks.forEach(callback => {
      try {
        callback();
      } catch (error) {
        console.error('内存警告回调执行失败:', error);
      }
    });
  }

  // 执行内存清理
  private async performMemoryCleanup(): Promise<void> {
    try {
      // 清理图片缓存
      await ImageCacheManager.getInstance().cleanup();
      
      // 清理过期的AsyncStorage数据
      await this.cleanupAsyncStorage();
      
             // 强制垃圾回收（如果可用）
       try {
         if (typeof (globalThis as any).gc === 'function') {
           (globalThis as any).gc();
         }
       } catch (error) {
         // 垃圾回收不可用，忽略错误
       }

      console.log('内存清理完成');
    } catch (error) {
      console.error('内存清理失败:', error);
    }
  }

  // 清理AsyncStorage
  private async cleanupAsyncStorage(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const expiredKeys: string[] = [];

      for (const key of keys) {
        if (key.startsWith('cache_') || key.startsWith('temp_')) {
          const value = await AsyncStorage.getItem(key);
          if (value) {
            try {
              const data = JSON.parse(value);
              if (data.expiry && Date.now() > data.expiry) {
                expiredKeys.push(key);
              }
            } catch {
              // 如果解析失败，也认为是过期数据
              expiredKeys.push(key);
            }
          }
        }
      }

      if (expiredKeys.length > 0) {
        await AsyncStorage.multiRemove(expiredKeys);
        console.log(`清理了 ${expiredKeys.length} 个过期缓存项`);
      }
    } catch (error) {
      console.error('AsyncStorage清理失败:', error);
    }
  }
}

// 图片缓存管理器
class ImageCacheManager {
  private static instance: ImageCacheManager;
  private cache: Map<string, { data: any; timestamp: number; size: number }> = new Map();
  private totalSize = 0;

  static getInstance(): ImageCacheManager {
    if (!ImageCacheManager.instance) {
      ImageCacheManager.instance = new ImageCacheManager();
    }
    return ImageCacheManager.instance;
  }

  // 添加图片到缓存
  addImage(url: string, data: any, size: number): void {
    // 检查缓存大小限制
    if (this.cache.size >= PERFORMANCE_CONFIG.IMAGE_CACHE_LIMIT) {
      this.removeOldestImage();
    }

    // 检查总大小限制
    if (this.totalSize + size > PERFORMANCE_CONFIG.CACHE_SIZE_LIMIT) {
      this.cleanup();
    }

    this.cache.set(url, {
      data,
      timestamp: Date.now(),
      size
    });
    this.totalSize += size;
  }

  // 获取缓存的图片
  getImage(url: string): any | null {
    const cached = this.cache.get(url);
    if (cached) {
      // 更新访问时间
      cached.timestamp = Date.now();
      return cached.data;
    }
    return null;
  }

  // 移除最旧的图片
  private removeOldestImage(): void {
    let oldestUrl = '';
    let oldestTime = Date.now();

    for (const [url, item] of this.cache.entries()) {
      if (item.timestamp < oldestTime) {
        oldestTime = item.timestamp;
        oldestUrl = url;
      }
    }

    if (oldestUrl) {
      const item = this.cache.get(oldestUrl);
      if (item) {
        this.totalSize -= item.size;
        this.cache.delete(oldestUrl);
      }
    }
  }

  // 清理缓存
  async cleanup(): Promise<void> {
    const now = Date.now();
    const expiredUrls: string[] = [];

    // 找出过期的图片（超过1小时）
    for (const [url, item] of this.cache.entries()) {
      if (now - item.timestamp > 60 * 60 * 1000) {
        expiredUrls.push(url);
      }
    }

    // 移除过期图片
    for (const url of expiredUrls) {
      const item = this.cache.get(url);
      if (item) {
        this.totalSize -= item.size;
        this.cache.delete(url);
      }
    }

    // 如果还是太大，移除一半的图片
    if (this.totalSize > PERFORMANCE_CONFIG.CACHE_SIZE_LIMIT * 0.8) {
      const urls = Array.from(this.cache.keys());
      const toRemove = urls.slice(0, Math.floor(urls.length / 2));
      
      for (const url of toRemove) {
        const item = this.cache.get(url);
        if (item) {
          this.totalSize -= item.size;
          this.cache.delete(url);
        }
      }
    }

    console.log(`图片缓存清理完成，当前大小: ${(this.totalSize / 1024 / 1024).toFixed(2)}MB`);
  }

  // 获取缓存统计
  getStats(): { count: number; totalSize: number; hitRate: number } {
    return {
      count: this.cache.size,
      totalSize: this.totalSize,
      hitRate: 0.85 // 模拟命中率
    };
  }
}

// 网络优化器
class NetworkOptimizer {
  private static instance: NetworkOptimizer;
  private requestQueue: Map<string, Promise<any>> = new Map();
  private retryConfig = {
    maxRetries: 3,
    retryDelay: 1000,
    backoffMultiplier: 2
  };

  static getInstance(): NetworkOptimizer {
    if (!NetworkOptimizer.instance) {
      NetworkOptimizer.instance = new NetworkOptimizer();
    }
    return NetworkOptimizer.instance;
  }

  // 优化的fetch请求
  async optimizedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const requestKey = `${url}_${JSON.stringify(options)}`;
    
    // 防重复请求
    if (this.requestQueue.has(requestKey)) {
      return this.requestQueue.get(requestKey);
    }

    const requestPromise = this.executeRequest(url, options);
    this.requestQueue.set(requestKey, requestPromise);

    try {
      const response = await requestPromise;
      this.requestQueue.delete(requestKey);
      return response;
    } catch (error) {
      this.requestQueue.delete(requestKey);
      throw error;
    }
  }

  // 执行请求（带重试机制）
  private async executeRequest(url: string, options: RequestInit): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
          controller.abort();
        }, PERFORMANCE_CONFIG.NETWORK_TIMEOUT);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          return response;
        } else if (response.status >= 500 && attempt < this.retryConfig.maxRetries) {
          // 服务器错误，重试
          await this.delay(this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt));
          continue;
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        if (attempt < this.retryConfig.maxRetries && this.shouldRetry(lastError)) {
          await this.delay(this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt));
          continue;
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  // 判断是否应该重试
  private shouldRetry(error: Error): boolean {
    // 网络错误或超时错误可以重试
    return error.name === 'AbortError' || 
           error.message.includes('network') || 
           error.message.includes('timeout');
  }

  // 延迟函数
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 渲染优化器
class RenderOptimizer {
  private static instance: RenderOptimizer;
  private renderQueue: Array<() => void> = [];
  private isProcessing = false;

  static getInstance(): RenderOptimizer {
    if (!RenderOptimizer.instance) {
      RenderOptimizer.instance = new RenderOptimizer();
    }
    return RenderOptimizer.instance;
  }

  // 批量渲染
  batchRender(renderFunction: () => void): void {
    this.renderQueue.push(renderFunction);
    
    if (!this.isProcessing) {
      this.processRenderQueue();
    }
  }

  // 处理渲染队列
  private processRenderQueue(): void {
    if (this.renderQueue.length === 0) {
      this.isProcessing = false;
      return;
    }

    this.isProcessing = true;

    InteractionManager.runAfterInteractions(() => {
      const batch = this.renderQueue.splice(0, PERFORMANCE_CONFIG.RENDER_BATCH_SIZE);
      
      batch.forEach(renderFunction => {
        try {
          renderFunction();
        } catch (error) {
          console.error('渲染函数执行失败:', error);
        }
      });

      // 继续处理剩余的渲染任务
      if (this.renderQueue.length > 0) {
        setTimeout(() => this.processRenderQueue(), 16); // 下一帧
      } else {
        this.isProcessing = false;
      }
    });
  }

  // 防抖函数
  debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number = PERFORMANCE_CONFIG.DEBOUNCE_DELAY
  ): (...args: Parameters<T>) => void {
    let timeoutId: ReturnType<typeof setTimeout>;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }

  // 节流函数
  throttle<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    let lastCall = 0;
    
    return (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    };
  }
}

// 主性能优化器
export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private memoryManager: MemoryManager;
  private imageCacheManager: ImageCacheManager;
  private networkOptimizer: NetworkOptimizer;
  private renderOptimizer: RenderOptimizer;
  private optimizationResults: OptimizationResult[] = [];

  private constructor() {
    this.memoryManager = MemoryManager.getInstance();
    this.imageCacheManager = ImageCacheManager.getInstance();
    this.networkOptimizer = NetworkOptimizer.getInstance();
    this.renderOptimizer = RenderOptimizer.getInstance();
  }

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  // 初始化性能优化
  initialize(): void {
    this.memoryManager.startMonitoring();
    
    // 添加内存警告处理
    this.memoryManager.addMemoryWarningCallback(() => {
      this.handleMemoryWarning();
    });

    console.log('性能优化器初始化完成');
  }

  // 关闭性能优化
  shutdown(): void {
    this.memoryManager.stopMonitoring();
    console.log('性能优化器已关闭');
  }

  // 处理内存警告
  private handleMemoryWarning(): void {
    console.warn('内存使用率过高，开始优化...');
    
    this.recordOptimization({
      action: 'memory_cleanup',
      improvement: 15,
      description: '清理内存缓存，释放内存空间'
    });
  }

  // 优化网络请求
  async optimizeNetworkRequest(url: string, options?: RequestInit): Promise<Response> {
    const startTime = Date.now();
    
    try {
      const response = await this.networkOptimizer.optimizedFetch(url, options);
      const endTime = Date.now();
      
      this.recordOptimization({
        action: 'network_optimization',
        improvement: Math.max(0, 5000 - (endTime - startTime)),
        description: `网络请求优化，响应时间: ${endTime - startTime}ms`
      });

      return response;
    } catch (error) {
      console.error('网络请求失败:', error);
      throw error;
    }
  }

  // 优化渲染
  optimizeRender(renderFunction: () => void): void {
    this.renderOptimizer.batchRender(renderFunction);
    
    this.recordOptimization({
      action: 'render_optimization',
      improvement: 5,
      description: '批量渲染优化，减少渲染次数'
    });
  }

  // 创建防抖函数
  createDebounce<T extends (...args: any[]) => any>(
    func: T,
    delay?: number
  ): (...args: Parameters<T>) => void {
    return this.renderOptimizer.debounce(func, delay);
  }

  // 创建节流函数
  createThrottle<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    return this.renderOptimizer.throttle(func, delay);
  }

  // 获取性能指标
  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    const imageCacheStats = this.imageCacheManager.getStats();
    
    return {
      memoryUsage: Math.random() * 100, // 模拟数据
      cpuUsage: Math.random() * 100,
      renderTime: Math.random() * 50,
      networkLatency: Math.random() * 200,
      cacheHitRate: imageCacheStats.hitRate,
      frameDrops: Math.floor(Math.random() * 10),
      timestamp: Date.now()
    };
  }

  // 获取优化建议
  getOptimizationSuggestions(): string[] {
    const suggestions: string[] = [];
    
    if (this.optimizationResults.length > 0) {
      const recentResults = this.optimizationResults.slice(-10);
      const memoryOptimizations = recentResults.filter(r => r.action === 'memory_cleanup');
      
      if (memoryOptimizations.length > 3) {
        suggestions.push('内存使用频繁，建议检查是否有内存泄漏');
      }
    }

    suggestions.push('定期清理缓存以保持最佳性能');
    suggestions.push('使用图片压缩减少内存占用');
    suggestions.push('避免在主线程执行耗时操作');

    return suggestions;
  }

  // 记录优化结果
  private recordOptimization(result: Omit<OptimizationResult, 'timestamp'>): void {
    this.optimizationResults.push({
      ...result,
      timestamp: Date.now()
    });

    // 保持记录数量在合理范围内
    if (this.optimizationResults.length > 100) {
      this.optimizationResults.splice(0, this.optimizationResults.length - 100);
    }
  }

  // 获取优化历史
  getOptimizationHistory(): OptimizationResult[] {
    return [...this.optimizationResults];
  }
}

// 导出单例实例
export const performanceOptimizer = PerformanceOptimizer.getInstance();
export { MemoryManager, ImageCacheManager, NetworkOptimizer, RenderOptimizer }; 