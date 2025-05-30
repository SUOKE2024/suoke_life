import { InteractionManager, Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { monitoringSystem } from "./monitoringSystem";


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
  cacheSize: number;
  networkRequests: number;
  averageResponseTime: number;
  lastOptimization: number;
}

export interface OptimizationResult {
  action: string;
  improvement: number;
  description: string;
  timestamp: number;
}

// 缓存配置
interface CacheConfig {
  maxSize: number; // 最大缓存大小 (MB)
  maxAge: number; // 最大缓存时间 (ms)
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
}

// 缓存项
interface CacheItem<T = any> {
  data: T;
  timestamp: number;
  size: number;
  accessCount: number;
  lastAccessed: number;
  compressed?: boolean;
  encrypted?: boolean;
}

// 图片优化配置
interface ImageOptimizationConfig {
  quality: number;
  maxWidth: number;
  maxHeight: number;
  format: "jpeg" | "png" | "webp";
  enableLazyLoading: boolean;
  enablePlaceholder: boolean;
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
    if (this.isMonitoring) {
      return;
    }

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
          apiResponseTime: 0,
        },
      });
    } catch (error) {
      console.error("内存检查失败:", error);
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
    this.memoryWarningCallbacks.forEach((callback) => {
      try {
        callback();
      } catch (error) {
        console.error("内存警告回调执行失败:", error);
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
        if (typeof (globalThis as any).gc === "function") {
          (globalThis as any).gc();
        }
      } catch (error) {
        // 垃圾回收不可用，忽略错误
      }

      console.log("内存清理完成");
    } catch (error) {
      console.error("内存清理失败:", error);
    }
  }

  // 清理AsyncStorage
  private async cleanupAsyncStorage(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const expiredKeys: string[] = [];

      for (const key of keys) {
        if (key.startsWith("cache_") || key.startsWith("temp_")) {
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
      console.error("AsyncStorage清理失败:", error);
    }
  }
}

// 图片缓存管理器
class ImageCacheManager {
  private static instance: ImageCacheManager;
  private cache: Map<string, { data: any; timestamp: number; size: number }> =
    new Map();
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
      size,
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
    let oldestUrl = "";
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

    console.log(
      `图片缓存清理完成，当前大小: ${(this.totalSize / 1024 / 1024).toFixed(
        2
      )}MB`
    );
  }

  // 获取缓存统计
  getStats(): { count: number; totalSize: number; hitRate: number } {
    return {
      count: this.cache.size,
      totalSize: this.totalSize,
      hitRate: 0.85, // 模拟命中率
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
    backoffMultiplier: 2,
  };

  static getInstance(): NetworkOptimizer {
    if (!NetworkOptimizer.instance) {
      NetworkOptimizer.instance = new NetworkOptimizer();
    }
    return NetworkOptimizer.instance;
  }

  // 优化的fetch请求
  async optimizedFetch(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
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
  private async executeRequest(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
          controller.abort();
        }, PERFORMANCE_CONFIG.NETWORK_TIMEOUT);

        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          return response;
        } else if (
          response.status >= 500 &&
          attempt < this.retryConfig.maxRetries
        ) {
          // 服务器错误，重试
          await this.delay(
            this.retryConfig.retryDelay *
              Math.pow(this.retryConfig.backoffMultiplier, attempt)
          );
          continue;
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        lastError = error instanceof Error ? error : new Error("Unknown error");

        if (
          attempt < this.retryConfig.maxRetries &&
          this.shouldRetry(lastError)
        ) {
          await this.delay(
            this.retryConfig.retryDelay *
              Math.pow(this.retryConfig.backoffMultiplier, attempt)
          );
          continue;
        }
      }
    }

    throw lastError || new Error("Request failed");
  }

  // 判断是否应该重试
  private shouldRetry(error: Error): boolean {
    // 网络错误或超时错误可以重试
    return (
      error.name === "AbortError" ||
      error.message.includes("network") ||
      error.message.includes("timeout")
    );
  }

  // 延迟函数
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
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
      const batch = this.renderQueue.splice(
        0,
        PERFORMANCE_CONFIG.RENDER_BATCH_SIZE
      );

      batch.forEach((renderFunction) => {
        try {
          renderFunction();
        } catch (error) {
          console.error("渲染函数执行失败:", error);
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
  private cache = new Map<string, CacheItem>();
  private config: CacheConfig;
  private metrics: PerformanceMetrics;
  private imageConfig: ImageOptimizationConfig;
  private requestQueue: Map<string, Promise<any>> = new Map();
  private memoryWarningThreshold = 0.8; // 80% 内存使用率警告

  private constructor() {
    this.memoryManager = MemoryManager.getInstance();
    this.imageCacheManager = ImageCacheManager.getInstance();
    this.networkOptimizer = NetworkOptimizer.getInstance();
    this.renderOptimizer = RenderOptimizer.getInstance();

    this.config = {
      maxSize: 50, // 50MB
      maxAge: 24 * 60 * 60 * 1000, // 24小时
      compressionEnabled: true,
      encryptionEnabled: false,
    };

    this.metrics = {
      memoryUsage: 0,
      cpuUsage: 0,
      renderTime: 0,
      networkLatency: 0,
      cacheHitRate: 0,
      frameDrops: 0,
      timestamp: Date.now(),
      cacheSize: 0,
      networkRequests: 0,
      averageResponseTime: 0,
      lastOptimization: Date.now(),
    };

    this.imageConfig = {
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
      format: "jpeg",
      enableLazyLoading: true,
      enablePlaceholder: true,
    };

    this.initializeOptimizer();
  }

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  private async initializeOptimizer() {
    // 加载持久化缓存
    await this.loadPersistedCache();

    // 启动定期优化
    this.startPeriodicOptimization();

    // 监听内存警告
    this.setupMemoryWarning();
  }

  // 缓存管理
  async set<T>(
    key: string,
    data: T,
    options?: Partial<CacheConfig>
  ): Promise<void> {
    const timestamp = Date.now();
    const serializedData = JSON.stringify(data);
    const size = this.calculateSize(serializedData);

    // 检查缓存空间
    await this.ensureCacheSpace(size);

    const cacheItem: CacheItem<T> = {
      data,
      timestamp,
      size,
      accessCount: 0,
      lastAccessed: timestamp,
      compressed: options?.compressionEnabled ?? this.config.compressionEnabled,
      encrypted: options?.encryptionEnabled ?? this.config.encryptionEnabled,
    };

    // 压缩数据
    if (cacheItem.compressed) {
      cacheItem.data = await this.compressData(data);
    }

    // 加密数据
    if (cacheItem.encrypted) {
      cacheItem.data = await this.encryptData(cacheItem.data);
    }

    this.cache.set(key, cacheItem);
    this.updateMetrics();

    // 持久化重要数据
    if (this.isImportantData(key)) {
      await this.persistCacheItem(key, cacheItem);
    }
  }

  async get<T>(key: string): Promise<T | null> {
    const startTime = Date.now();
    const cacheItem = this.cache.get(key);

    if (!cacheItem) {
      this.metrics.networkRequests++;
      return null;
    }

    // 检查过期
    if (this.isExpired(cacheItem)) {
      this.cache.delete(key);
      await this.removePersistentCacheItem(key);
      return null;
    }

    // 更新访问统计
    cacheItem.accessCount++;
    cacheItem.lastAccessed = Date.now();

    let data = cacheItem.data;

    // 解密数据
    if (cacheItem.encrypted) {
      data = await this.decryptData(data);
    }

    // 解压数据
    if (cacheItem.compressed) {
      data = await this.decompressData(data);
    }

    // 更新性能指标
    const responseTime = Date.now() - startTime;
    this.updateResponseTime(responseTime);

    return data as T;
  }

  async remove(key: string): Promise<void> {
    this.cache.delete(key);
    await this.removePersistentCacheItem(key);
    this.updateMetrics();
  }

  async clear(): Promise<void> {
    this.cache.clear();
    await AsyncStorage.multiRemove(await this.getPersistentCacheKeys());
    this.updateMetrics();
  }

  // 智能预加载
  async preloadData(
    keys: string[],
    priority: "high" | "medium" | "low" = "medium"
  ): Promise<void> {
    const promises = keys.map(async (key) => {
      if (!this.cache.has(key)) {
        // 根据优先级决定预加载策略
        if (priority === "high") {
          return this.loadDataImmediately(key);
        } else {
          return this.scheduleDataLoading(key, priority);
        }
      }
    });

    await Promise.allSettled(promises);
  }

  // 请求去重
  async deduplicateRequest<T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    if (this.requestQueue.has(key)) {
      return this.requestQueue.get(key) as Promise<T>;
    }

    const promise = requestFn().finally(() => {
      this.requestQueue.delete(key);
    });

    this.requestQueue.set(key, promise);
    return promise;
  }

  // 图片优化
  optimizeImageUrl(
    url: string,
    options?: Partial<ImageOptimizationConfig>
  ): string {
    const config = { ...this.imageConfig, ...options };

    // 根据设备像素密度调整尺寸
    const pixelRatio = Platform.select({
      ios: 2,
      android: 2,
      default: 1,
    });

    const optimizedWidth = Math.min(
      config.maxWidth * pixelRatio,
      config.maxWidth
    );
    const optimizedHeight = Math.min(
      config.maxHeight * pixelRatio,
      config.maxHeight
    );

    // 构建优化后的URL（假设使用CDN服务）
    const params = new URLSearchParams({
      w: optimizedWidth.toString(),
      h: optimizedHeight.toString(),
      q: (config.quality * 100).toString(),
      f: config.format,
    });

    return `${url}?${params.toString()}`;
  }

  // 内存优化
  async optimizeMemory(): Promise<void> {
    console.log("开始内存优化...");

    // 清理过期缓存
    await this.cleanExpiredCache();

    // LRU清理
    await this.performLRUCleanup();

    // 压缩大型缓存项
    await this.compressLargeCacheItems();

    // 更新指标
    this.updateMetrics();
    this.metrics.lastOptimization = Date.now();

    console.log("内存优化完成");
  }

  // 网络优化
  createOptimizedFetch() {
    return async (url: string, options?: RequestInit) => {
      // 添加缓存头
      const optimizedOptions: RequestInit = {
        ...options,
        headers: {
          ...options?.headers,
          "Cache-Control": "max-age=300", // 5分钟缓存
          "If-None-Match": await this.getETag(url),
        },
      };

      // 请求去重
      return this.deduplicateRequest(url, () => fetch(url, optimizedOptions));
    };
  }

  // 批量操作优化
  async batchOperations<T>(
    operations: Array<() => Promise<T>>,
    batchSize: number = 5
  ): Promise<T[]> {
    const results: T[] = [];

    for (let i = 0; i < operations.length; i += batchSize) {
      const batch = operations.slice(i, i + batchSize);
      const batchResults = await Promise.allSettled(batch.map((op) => op()));

      batchResults.forEach((result) => {
        if (result.status === "fulfilled") {
          results.push(result.value);
        }
      });

      // 批次间延迟，避免过载
      if (i + batchSize < operations.length) {
        await this.delay(100);
      }
    }

    return results;
  }

  // 获取性能指标
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  // 配置更新
  updateConfig(newConfig: Partial<CacheConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  updateImageConfig(newConfig: Partial<ImageOptimizationConfig>): void {
    this.imageConfig = { ...this.imageConfig, ...newConfig };
  }

  // 私有方法
  private calculateSize(data: string): number {
    return new Blob([data]).size / (1024 * 1024); // MB
  }

  private isExpired(cacheItem: CacheItem): boolean {
    return Date.now() - cacheItem.timestamp > this.config.maxAge;
  }

  private async ensureCacheSpace(requiredSize: number): Promise<void> {
    let currentSize = this.getCurrentCacheSize();

    while (currentSize + requiredSize > this.config.maxSize) {
      const lruKey = this.findLRUKey();
      if (!lruKey) {
        break;
      }

      await this.remove(lruKey);
      currentSize = this.getCurrentCacheSize();
    }
  }

  private getCurrentCacheSize(): number {
    return Array.from(this.cache.values()).reduce(
      (total, item) => total + item.size,
      0
    );
  }

  private findLRUKey(): string | null {
    let lruKey: string | null = null;
    let oldestAccess = Date.now();

    for (const [key, item] of this.cache.entries()) {
      if (item.lastAccessed < oldestAccess) {
        oldestAccess = item.lastAccessed;
        lruKey = key;
      }
    }

    return lruKey;
  }

  private async compressData<T>(data: T): Promise<T> {
    // 简单的压缩实现（实际项目中可使用更高效的压缩算法）
    try {
      const jsonString = JSON.stringify(data);
      // 这里可以集成 LZ-string 或其他压缩库
      return data; // 暂时返回原数据
    } catch {
      return data;
    }
  }

  private async decompressData<T>(data: T): Promise<T> {
    // 对应的解压实现
    return data;
  }

  private async encryptData<T>(data: T): Promise<T> {
    // 简单的加密实现（实际项目中应使用更安全的加密方法）
    return data;
  }

  private async decryptData<T>(data: T): Promise<T> {
    // 对应的解密实现
    return data;
  }

  private isImportantData(key: string): boolean {
    const importantPrefixes = ["user_", "health_", "diagnosis_"];
    return importantPrefixes.some((prefix) => key.startsWith(prefix));
  }

  private async persistCacheItem(key: string, item: CacheItem): Promise<void> {
    try {
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(item));
    } catch (error) {
      console.warn("Failed to persist cache item:", error);
    }
  }

  private async removePersistentCacheItem(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(`cache_${key}`);
    } catch (error) {
      console.warn("Failed to remove persistent cache item:", error);
    }
  }

  private async loadPersistedCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter((key) => key.startsWith("cache_"));

      const cacheItems = await AsyncStorage.multiGet(cacheKeys);

      for (const [key, value] of cacheItems) {
        if (value) {
          try {
            const cacheKey = key.replace("cache_", "");
            const cacheItem = JSON.parse(value);

            if (!this.isExpired(cacheItem)) {
              this.cache.set(cacheKey, cacheItem);
            } else {
              await AsyncStorage.removeItem(key);
            }
          } catch (error) {
            console.warn("Failed to parse cache item:", error);
            await AsyncStorage.removeItem(key);
          }
        }
      }
    } catch (error) {
      console.warn("Failed to load persisted cache:", error);
    }
  }

  private async getPersistentCacheKeys(): Promise<string[]> {
    const keys = await AsyncStorage.getAllKeys();
    return keys.filter((key) => key.startsWith("cache_"));
  }

  private async cleanExpiredCache(): Promise<void> {
    const expiredKeys: string[] = [];

    for (const [key, item] of this.cache.entries()) {
      if (this.isExpired(item)) {
        expiredKeys.push(key);
      }
    }

    await Promise.all(expiredKeys.map((key) => this.remove(key)));
  }

  private async performLRUCleanup(): Promise<void> {
    const cacheSize = this.getCurrentCacheSize();
    const targetSize = this.config.maxSize * 0.8; // 清理到80%

    if (cacheSize <= targetSize) {
      return;
    }

    const sortedEntries = Array.from(this.cache.entries()).sort(
      ([, a], [, b]) => a.lastAccessed - b.lastAccessed
    );

    let currentSize = cacheSize;
    for (const [key] of sortedEntries) {
      if (currentSize <= targetSize) {
        break;
      }

      const item = this.cache.get(key);
      if (item) {
        currentSize -= item.size;
        await this.remove(key);
      }
    }
  }

  private async compressLargeCacheItems(): Promise<void> {
    const largeItems = Array.from(this.cache.entries()).filter(
      ([, item]) => item.size > 1 && !item.compressed
    ); // 大于1MB且未压缩

    for (const [key, item] of largeItems) {
      try {
        const compressedData = await this.compressData(item.data);
        item.data = compressedData;
        item.compressed = true;
      } catch (error) {
        console.warn("Failed to compress cache item:", error);
      }
    }
  }

  private updateMetrics(): void {
    this.metrics.cacheSize = this.getCurrentCacheSize();
    this.metrics.memoryUsage = this.estimateMemoryUsage();

    // 计算缓存命中率
    const totalRequests = this.metrics.networkRequests + this.cache.size;
    this.metrics.cacheHitRate =
      totalRequests > 0 ? this.cache.size / totalRequests : 0;
  }

  private updateResponseTime(responseTime: number): void {
    const alpha = 0.1; // 平滑因子
    this.metrics.averageResponseTime =
      this.metrics.averageResponseTime * (1 - alpha) + responseTime * alpha;
  }

  private estimateMemoryUsage(): number {
    // 简单的内存使用估算
    return this.getCurrentCacheSize() / this.config.maxSize;
  }

  private async getETag(url: string): Promise<string | undefined> {
    // 从缓存中获取ETag
    const etag = await this.get(`etag_${url}`);
    return etag || undefined;
  }

  private async loadDataImmediately(key: string): Promise<void> {
    // 立即加载数据的实现
    console.log(`Immediately loading data for key: ${key}`);
  }

  private async scheduleDataLoading(
    key: string,
    priority: "medium" | "low"
  ): Promise<void> {
    // 调度数据加载的实现
    const delay = priority === "medium" ? 1000 : 5000;
    setTimeout(() => {
      console.log(`Scheduled loading data for key: ${key}`);
    }, delay);
  }

  private startPeriodicOptimization(): void {
    // 每30分钟执行一次优化
    setInterval(() => {
      this.optimizeMemory();
    }, 30 * 60 * 1000);
  }

  private setupMemoryWarning(): void {
    // 监听内存警告（在实际应用中可以使用更精确的内存监控）
    setInterval(() => {
      if (this.metrics.memoryUsage > this.memoryWarningThreshold) {
        console.warn("Memory usage high, triggering optimization");
        this.optimizeMemory();
      }
    }, 60 * 1000); // 每分钟检查一次
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// 单例实例
export const performanceOptimizer = PerformanceOptimizer.getInstance();

// 导出类型
export type {
  CacheConfig,
  CacheItem,
  PerformanceMetrics,
  ImageOptimizationConfig,
};

// 便捷函数
export const cache = {
  set: <T>(key: string, data: T, options?: Partial<CacheConfig>) =>
    performanceOptimizer.set(key, data, options),
  get: <T>(key: string) => performanceOptimizer.get<T>(key),
  remove: (key: string) => performanceOptimizer.remove(key),
  clear: () => performanceOptimizer.clear(),
};

export const optimizeImage = (
  url: string,
  options?: Partial<ImageOptimizationConfig>
) => performanceOptimizer.optimizeImageUrl(url, options);

export const createOptimizedFetch = () =>
  performanceOptimizer.createOptimizedFetch();

export const batchOperations = <T>(
  operations: Array<() => Promise<T>>,
  batchSize?: number
) => performanceOptimizer.batchOperations(operations, batchSize);

// 导出类型
export type PerformanceConfig = typeof PERFORMANCE_CONFIG;
export type OptimizationSuggestion = OptimizationResult;
