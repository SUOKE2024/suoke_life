/**
 * 索克生活性能优化服务
 * 优化关键性能瓶颈，提升用户体验
 */

export interface PerformanceMetrics {
  /** 响应时间（毫秒） */
  responseTime: number;
  /** 内存使用（MB） */
  memoryUsage: number;
  /** CPU使用率（%） */
  cpuUsage: number;
  /** 网络延迟（毫秒） */
  networkLatency: number;
  /** 并发请求数 */
  concurrentRequests: number;
  /** 错误率（%） */
  errorRate: number;
}

export interface OptimizationConfig {
  /** 缓存配置 */
  cache: {
    enabled: boolean;
    ttl: number; // 缓存时间（秒）
    maxSize: number; // 最大缓存大小（MB）
  };
  /** 并发配置 */
  concurrency: {
    maxConcurrent: number;
    queueSize: number;
    timeout: number; // 超时时间（毫秒）
  };
  /** 预加载配置 */
  preload: {
    enabled: boolean;
    resources: string[];
  };
}

export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private cache: Map<string, { data: any; timestamp: number; ttl: number }>;
  private requestQueue: Array<{
    id: string;
    promise: Promise<any>;
    timestamp: number;
  }>;
  private metrics: PerformanceMetrics;
  private config: OptimizationConfig;

  private constructor() {
    this.cache = new Map();
    this.requestQueue = [];
    this.metrics = {
      responseTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkLatency: 0,
      concurrentRequests: 0,
      errorRate: 0,
    };
    this.config = {
      cache: {
        enabled: true,
        ttl: 300, // 5分钟
        maxSize: 100, // 100MB
      },
      concurrency: {
        maxConcurrent: 10,
        queueSize: 100,
        timeout: 30000, // 30秒
      },
      preload: {
        enabled: true,
        resources: ["user-profile", "health-data", "agent-models"],
      },
    };

    // 定期清理缓存
    setInterval(() => this.cleanupCache(), 60000); // 每分钟清理一次
  }

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  /**
   * 缓存管理
   */
  setCache(key: string, data: any, ttl?: number): void {
    if (!this.config.cache.enabled) return;

    const cacheEntry = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.cache.ttl * 1000,
    };

    this.cache.set(key, cacheEntry);
    this.enforceMaxCacheSize();
  }

  getCache(key: string): any | null {
    if (!this.config.cache.enabled) return null;

    const entry = this.cache.get(key);
    if (!entry) return null;

    // 检查是否过期
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clearCache(pattern?: string): void {
    if (pattern) {
      // 清理匹配模式的缓存
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      // 清理所有缓存
      this.cache.clear();
    }
  }

  private cleanupCache(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
      }
    }
  }

  private enforceMaxCacheSize(): void {
    // 简化的缓存大小控制，实际应该计算真实内存使用
    const maxEntries = this.config.cache.maxSize * 10; // 假设每MB可存储10个条目
    if (this.cache.size > maxEntries) {
      // 删除最旧的条目
      const entries = Array.from(this.cache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      const toDelete = entries.slice(0, this.cache.size - maxEntries);
      toDelete.forEach(([key]) => this.cache.delete(key));
    }
  }

  /**
   * 请求优化
   */
  async optimizeRequest<T>(
    key: string,
    requestFn: () => Promise<T>,
    options?: {
      useCache?: boolean;
      cacheTtl?: number;
      timeout?: number;
    }
  ): Promise<T> {
    const startTime = Date.now();
    const requestId = `${key}-${startTime}`;

    try {
      // 检查缓存
      if (options?.useCache !== false) {
        const cached = this.getCache(key);
        if (cached) {
          this.updateMetrics(Date.now() - startTime, true);
          return cached;
        }
      }

      // 检查并发限制
      if (this.requestQueue.length >= this.config.concurrency.maxConcurrent) {
        throw new Error("请求队列已满，请稍后重试");
      }

      // 执行请求
      const timeout = options?.timeout || this.config.concurrency.timeout;
      const promise = Promise.race([
        requestFn(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error("请求超时")), timeout)
        ),
      ]);

      this.requestQueue.push({ id: requestId, promise, timestamp: startTime });

      const result = await promise;

      // 缓存结果
      if (options?.useCache !== false) {
        this.setCache(key, result, options?.cacheTtl);
      }

      this.updateMetrics(Date.now() - startTime, false);
      this.removeFromQueue(requestId);

      return result;
    } catch (error) {
      this.updateMetrics(Date.now() - startTime, false, true);
      this.removeFromQueue(requestId);
      throw error;
    }
  }

  private removeFromQueue(requestId: string): void {
    const index = this.requestQueue.findIndex((req) => req.id === requestId);
    if (index !== -1) {
      this.requestQueue.splice(index, 1);
    }
  }

  private updateMetrics(
    responseTime: number,
    fromCache: boolean,
    isError = false
  ): void {
    this.metrics.responseTime = (this.metrics.responseTime + responseTime) / 2;
    this.metrics.concurrentRequests = this.requestQueue.length;

    if (isError) {
      this.metrics.errorRate = (this.metrics.errorRate + 1) / 2;
    }
  }

  /**
   * 设备连接优化
   */
  async optimizeDeviceConnection(deviceType: string): Promise<{
    connected: boolean;
    connectionTime: number;
    optimizations: string[];
  }> {
    const startTime = Date.now();
    const optimizations: string[] = [];

    try {
      // 检查设备缓存
      const cacheKey = `device-${deviceType}`;
      const cachedConnection = this.getCache(cacheKey);

      if (cachedConnection) {
        optimizations.push("使用缓存的设备连接");
        return {
          connected: true,
          connectionTime: Date.now() - startTime,
          optimizations,
        };
      }

      // 并行尝试多种连接方式
      const connectionPromises = [
        this.tryBluetoothConnection(deviceType),
        this.tryWiFiConnection(deviceType),
        this.tryUSBConnection(deviceType),
      ];

      optimizations.push("并行尝试多种连接方式");

      const result = await Promise.race(
        connectionPromises.map(async (promise, index) => {
          try {
            const connected = await promise;
            return { connected, method: ["蓝牙", "WiFi", "USB"][index] };
          } catch {
            return { connected: false, method: ["蓝牙", "WiFi", "USB"][index] };
          }
        })
      );

      if (result.connected) {
        optimizations.push(`成功通过${result.method}连接`);
        // 缓存成功的连接
        this.setCache(cacheKey, { connected: true, method: result.method }, 60); // 1分钟缓存
      }

      return {
        connected: result.connected,
        connectionTime: Date.now() - startTime,
        optimizations,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "未知错误";
      return {
        connected: false,
        connectionTime: Date.now() - startTime,
        optimizations: [...optimizations, `连接失败: ${errorMessage}`],
      };
    }
  }

  private async tryBluetoothConnection(deviceType: string): Promise<boolean> {
    // 模拟蓝牙连接
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 2000 + 1000)
    );
    return Math.random() > 0.3; // 70% 成功率
  }

  private async tryWiFiConnection(deviceType: string): Promise<boolean> {
    // 模拟WiFi连接
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 1500 + 500)
    );
    return Math.random() > 0.2; // 80% 成功率
  }

  private async tryUSBConnection(deviceType: string): Promise<boolean> {
    // 模拟USB连接
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 1000 + 300)
    );
    return Math.random() > 0.1; // 90% 成功率
  }

  /**
   * AI分析优化
   */
  async optimizeAIAnalysis(
    data: any,
    analysisType: string
  ): Promise<{
    result: any;
    processingTime: number;
    optimizations: string[];
  }> {
    const startTime = Date.now();
    const optimizations: string[] = [];

    try {
      // 数据预处理优化
      const preprocessedData = await this.preprocessData(data, analysisType);
      optimizations.push("数据预处理优化");

      // 检查分析缓存
      const cacheKey = `analysis-${analysisType}-${this.hashData(
        preprocessedData
      )}`;
      const cachedResult = this.getCache(cacheKey);

      if (cachedResult) {
        optimizations.push("使用缓存的分析结果");
        return {
          result: cachedResult,
          processingTime: Date.now() - startTime,
          optimizations,
        };
      }

      // 选择最优的分析模型
      const model = this.selectOptimalModel(analysisType, preprocessedData);
      optimizations.push(`选择优化模型: ${model.name}`);

      // 并行处理（如果数据量大）
      let result;
      if (this.shouldUseParallelProcessing(preprocessedData)) {
        result = await this.parallelAnalysis(preprocessedData, model);
        optimizations.push("使用并行处理");
      } else {
        result = await this.singleAnalysis(preprocessedData, model);
        optimizations.push("使用单线程处理");
      }

      // 缓存分析结果
      this.setCache(cacheKey, result, 1800); // 30分钟缓存
      optimizations.push("缓存分析结果");

      return {
        result,
        processingTime: Date.now() - startTime,
        optimizations,
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "未知错误";
      throw new Error(`AI分析优化失败: ${errorMessage}`);
    }
  }

  private async preprocessData(data: any, analysisType: string): Promise<any> {
    // 模拟数据预处理
    await new Promise((resolve) => setTimeout(resolve, 100));

    // 根据分析类型优化数据格式
    switch (analysisType) {
      case "health_analysis":
        return this.optimizeHealthData(data);
      case "tcm_diagnosis":
        return this.optimizeTCMData(data);
      default:
        return data;
    }
  }

  private optimizeHealthData(data: any): any {
    // 健康数据优化
    return {
      ...data,
      normalized: true,
      timestamp: Date.now(),
    };
  }

  private optimizeTCMData(data: any): any {
    // 中医数据优化
    return {
      ...data,
      tcmOptimized: true,
      timestamp: Date.now(),
    };
  }

  private hashData(data: any): string {
    // 简单的数据哈希
    return btoa(JSON.stringify(data)).slice(0, 16);
  }

  private selectOptimalModel(
    analysisType: string,
    data: any
  ): { name: string; config: any } {
    // 根据数据特征选择最优模型
    const dataSize = JSON.stringify(data).length;

    if (dataSize < 1000) {
      return { name: "lightweight-model", config: { fast: true } };
    } else if (dataSize < 10000) {
      return { name: "standard-model", config: { balanced: true } };
    } else {
      return { name: "heavy-model", config: { accurate: true } };
    }
  }

  private shouldUseParallelProcessing(data: any): boolean {
    // 判断是否需要并行处理
    const dataSize = JSON.stringify(data).length;
    return dataSize > 5000; // 5KB以上使用并行处理
  }

  private async parallelAnalysis(data: any, model: any): Promise<any> {
    // 模拟并行分析
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 1000 + 500)
    );
    return {
      analysis: "parallel_result",
      confidence: 0.9,
      model: model.name,
      parallel: true,
    };
  }

  private async singleAnalysis(data: any, model: any): Promise<any> {
    // 模拟单线程分析
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 2000 + 1000)
    );
    return {
      analysis: "single_result",
      confidence: 0.85,
      model: model.name,
      parallel: false,
    };
  }

  /**
   * 获取性能指标
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<OptimizationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 预加载资源
   */
  async preloadResources(): Promise<void> {
    if (!this.config.preload.enabled) return;

    const preloadPromises = this.config.preload.resources.map(
      async (resource) => {
        try {
          await this.optimizeRequest(
            `preload-${resource}`,
            () => this.loadResource(resource),
            { useCache: true, cacheTtl: 3600 } // 1小时缓存
          );
        } catch (error) {
          console.warn(`预加载资源失败: ${resource}`, error);
        }
      }
    );

    await Promise.allSettled(preloadPromises);
  }

  private async loadResource(resource: string): Promise<any> {
    // 模拟资源加载
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 1000 + 200)
    );
    return { resource, loaded: true, timestamp: Date.now() };
  }
}

export default PerformanceOptimizer;
