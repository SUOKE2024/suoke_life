import { performanceMonitor, cacheManager, handleError } from "./index";

/**
 * 网络请求优化工具
 * 提供请求去重、批量处理、重试机制、缓存等功能
 */

export interface RequestConfig {
  url: string;
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
  cacheTTL?: number;
  dedupe?: boolean;
}

export interface RequestResponse<T = any> {
  data: T;
  status: number;
  headers: Record<string, string>;
  cached: boolean;
  duration: number;
}

export interface BatchRequest {
  id: string;
  config: RequestConfig;
  resolve: (response: RequestResponse) => void;
  reject: (error: any) => void;
}

/**
 * 网络优化器类
 */
export class NetworkOptimizer {
  private static instance: NetworkOptimizer;
  private pendingRequests: Map<string, Promise<RequestResponse>> = new Map();
  private batchQueue: BatchRequest[] = [];
  private batchTimer: any = null;
  private readonly batchDelay = 50; // 50ms批量延迟
  private readonly maxBatchSize = 10; // 最大批量大小

  private constructor() {}

  static getInstance(): NetworkOptimizer {
    if (!NetworkOptimizer.instance) {
      NetworkOptimizer.instance = new NetworkOptimizer();
    }
    return NetworkOptimizer.instance;
  }

  /**
   * 发送优化的网络请求
   */
  async request<T = any>(config: RequestConfig): Promise<RequestResponse<T>> {
    const requestKey = this.generateRequestKey(config);

    // 请求去重
    if (config.dedupe !== false && this.pendingRequests.has(requestKey)) {
      return this.pendingRequests.get(requestKey)! as Promise<
        RequestResponse<T>
      >;
    }

    // 检查缓存
    if (config.cache !== false && config.method === "GET") {
      const cached = await this.getCachedResponse<T>(requestKey);
      if (cached) {
        return cached;
      }
    }

    const requestPromise = this.executeRequest<T>(config);

    if (config.dedupe !== false) {
      this.pendingRequests.set(requestKey, requestPromise);

      // 请求完成后清理
      requestPromise.finally(() => {
        this.pendingRequests.delete(requestKey);
      });
    }

    return requestPromise;
  }

  /**
   * 批量请求
   */
  async batchRequest<T = any>(
    config: RequestConfig
  ): Promise<RequestResponse<T>> {
    return new Promise((resolve, reject) => {
      const batchRequest: BatchRequest = {
        id: Math.random().toString(36).substr(2, 9),
        config,
        resolve: resolve as (response: RequestResponse) => void,
        reject,
      };

      this.batchQueue.push(batchRequest);

      // 如果队列满了，立即处理
      if (this.batchQueue.length >= this.maxBatchSize) {
        this.processBatch();
      } else {
        // 否则设置定时器
        if (!this.batchTimer) {
          this.batchTimer = setTimeout(() => {
            this.processBatch();
          }, this.batchDelay);
        }
      }
    });
  }

  /**
   * 执行单个请求
   */
  private async executeRequest<T>(
    config: RequestConfig
  ): Promise<RequestResponse<T>> {
    const startTime = performance.now();
    let attempt = 0;
    const maxRetries = config.retries || 3;
    const retryDelay = config.retryDelay || 1000;

    while (attempt <= maxRetries) {
      try {
        const controller = new AbortController();
        const timeoutId = config.timeout
          ? setTimeout(() => {
              controller.abort();
            }, config.timeout)
          : null;

        const fetchConfig: RequestInit = {
          method: config.method,
          headers: {
            "Content-Type": "application/json",
            ...config.headers,
          },
          signal: controller.signal,
        };

        if (config.body && config.method !== "GET") {
          fetchConfig.body =
            typeof config.body === "string"
              ? config.body
              : JSON.stringify(config.body);
        }

        const response = await fetch(config.url, fetchConfig);

        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        const endTime = performance.now();
        const duration = endTime - startTime;

        // 记录性能指标
        let requestSize = 0;
        if (fetchConfig.body) {
          try {
            if (typeof fetchConfig.body === "string") {
              requestSize = new Blob([fetchConfig.body]).size;
            } else {
              requestSize = 0; // 对于其他类型，暂时设为0
            }
          } catch (error) {
            requestSize = 0;
          }
        }

        performanceMonitor.recordNetworkRequest(
          config.url,
          config.method,
          startTime,
          endTime,
          response.status,
          parseInt(response.headers.get("content-length") || "0"),
          requestSize
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const headers: Record<string, string> = {};
        response.headers.forEach((value, key) => {
          headers[key] = value;
        });

        const result: RequestResponse<T> = {
          data,
          status: response.status,
          headers,
          cached: false,
          duration,
        };

        // 缓存GET请求的响应
        if (config.cache !== false && config.method === "GET") {
          await this.cacheResponse(
            this.generateRequestKey(config),
            result,
            config.cacheTTL
          );
        }

        return result;
      } catch (error: any) {
        attempt++;

        if (attempt > maxRetries) {
          // 记录错误
          handleError(error, {
            url: config.url,
            method: config.method,
            attempt,
          });
          throw error;
        }

        // 等待重试
        if (attempt <= maxRetries) {
          await this.delay(retryDelay * attempt);
        }
      }
    }

    throw new Error("Max retries exceeded");
  }

  /**
   * 处理批量请求
   */
  private async processBatch(): Promise<void> {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    const currentBatch = [...this.batchQueue];
    this.batchQueue = [];

    // 按域名分组
    const groupedRequests = this.groupRequestsByDomain(currentBatch);

    // 并发处理每个域名的请求
    const promises = Object.entries(groupedRequests).map(([domain, requests]) =>
      this.processDomainRequests(domain, requests)
    );

    await Promise.allSettled(promises);
  }

  /**
   * 按域名分组请求
   */
  private groupRequestsByDomain(
    requests: BatchRequest[]
  ): Record<string, BatchRequest[]> {
    const grouped: Record<string, BatchRequest[]> = {};

    requests.forEach((request) => {
      const url = new URL(request.config.url);
      const domain = url.hostname;

      if (!grouped[domain]) {
        grouped[domain] = [];
      }
      grouped[domain].push(request);
    });

    return grouped;
  }

  /**
   * 处理单个域名的请求
   */
  private async processDomainRequests(
    domain: string,
    requests: BatchRequest[]
  ): Promise<void> {
    // 限制并发数，避免过载
    const concurrency = 5;
    const chunks = this.chunkArray(requests, concurrency);

    for (const chunk of chunks) {
      const promises = chunk.map(async (request) => {
        try {
          const response = await this.executeRequest(request.config);
          request.resolve(response);
        } catch (error) {
          request.reject(error);
        }
      });

      await Promise.allSettled(promises);
    }
  }

  /**
   * 生成请求键
   */
  private generateRequestKey(config: RequestConfig): string {
    const { url, method, body } = config;
    const bodyStr = body ? JSON.stringify(body) : "";
    return `${method}:${url}:${bodyStr}`;
  }

  /**
   * 获取缓存的响应
   */
  private async getCachedResponse<T>(
    key: string
  ): Promise<RequestResponse<T> | null> {
    try {
      const cached = await cacheManager.get<RequestResponse<T>>(key);
      if (cached) {
        return {
          ...cached,
          cached: true,
        };
      }
    } catch (error) {
      console.warn("Failed to get cached response:", error);
    }
    return null;
  }

  /**
   * 缓存响应
   */
  private async cacheResponse(
    key: string,
    response: RequestResponse,
    ttl?: number
  ): Promise<void> {
    try {
      await cacheManager.set(key, response, { ttl });
    } catch (error) {
      console.warn("Failed to cache response:", error);
    }
  }

  /**
   * 延迟函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * 数组分块
   */
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  /**
   * 取消所有待处理的请求
   */
  cancelAllRequests(): void {
    this.pendingRequests.clear();

    // 拒绝所有批量请求
    this.batchQueue.forEach((request) => {
      request.reject(new Error("Request cancelled"));
    });
    this.batchQueue = [];

    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
  }

  /**
   * 获取网络状态统计
   */
  getNetworkStats(): {
    pendingRequests: number;
    queuedBatchRequests: number;
    cacheHitRate: number;
  } {
    const performanceStats = performanceMonitor.getNetworkStats();
    const cacheStats = cacheManager.getStats();

    return {
      pendingRequests: this.pendingRequests.size,
      queuedBatchRequests: this.batchQueue.length,
      cacheHitRate: cacheStats.hitRate,
    };
  }
}

// 导出单例实例
export const networkOptimizer = NetworkOptimizer.getInstance();

// 便捷函数
export const optimizedRequest = <T = any>(
  config: RequestConfig
): Promise<RequestResponse<T>> => {
  return networkOptimizer.request<T>(config);
};

export const batchRequest = <T = any>(
  config: RequestConfig
): Promise<RequestResponse<T>> => {
  return networkOptimizer.batchRequest<T>(config);
};

export const cancelAllNetworkRequests = () => {
  networkOptimizer.cancelAllRequests();
};

export const getNetworkStats = () => {
  return networkOptimizer.getNetworkStats();
};
