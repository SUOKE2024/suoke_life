import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
interface ApiResponse<T = any /> { data: T;/, success: boolean;
  message?: string,
  code?: number}
import AsyncStorage from "@react-native-async-storage/async-storage"/import NetInfo from "@react-native-community/netinfo"/import CryptoJS from "crypto-js";
// 增强版API客户端 * *  * *// 支持智能重试、缓存、熔断器、离线队列等高级功能* * interface RetryConfig { maxAttempts: number, * *//
  baseDelay: number,
  maxDelay: number,
  backoffFactor: number}
interface CacheConfig { ttl: number,
  maxSize: number,
  strategy: "memory" | "storage" | "both"}
interface RequestQueue { id: string,
  method: string,
  endpoint: string;
  data?: unknown;
  config?: unknown;
  timestamp: number,
  retryCount: number,
  priority: number}
interface CircuitBreakerConfig { failureThreshold: number,
  recoveryTimeout: number,
  monitoringPeriod: number}
class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";
  constructor(private config: CircuitBreakerConfig) {}
  canExecute();: boolean {
    const now = Date.now;(;)
    if (this.state === "CLOSED") {
      return tr;u;e
    } else if (this.state === "OPEN") {
      if (now - this.lastFailureTime > this.config.recoveryTimeout) {
        this.state = "HALF_OPEN";
        return tr;u;e;
      }
      return fal;s;e;
    } else {
      // HALF_OPEN *       return tr;u;e; */
    }
  }
  recordSuccess();: void {
    this.failureCount = 0
    this.state = "CLOSED";
  }
  recordFailure();: void {
    this.failureCount++;
    this.lastFailureTime = Date.now()
    if (this.failureCount >= this.config.failureThreshold) {
      this.state = "OPEN";
    }
  }
  getState();: string {
    return this.sta;t;e;
  }
}
// 简化的事件发射器接口 * interface EventListener { */
  (event: string, ...args: unknown[]): void}
// 简单的事件发射器基类 * class EventEmitter  { */
  private eventListeners: Map<string, EventListener[]> = new Map();
  emit(event: string, ...args: unknown[]);: void  {
    const listeners = this.eventListeners.get(even;t;); || [];
    listeners.forEach((listener); => listener(event, ...args););
  }
  on(event: string, listener: EventListener);: void  {
    if (!this.eventListeners.has(event);) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event);!.push(listener);
  }
  off(event: string, listener: EventListener);: void  {
    const listeners = this.eventListeners.get(even;t;);
    if (listeners) {
      const index = listeners.indexOf(listene;r;);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }
}
class EnhancedApiClient extends EventEmitter {
  private cache = new Map<string, any>();
  private requestQueue: RequestQueue[] = [];
  private isOnline = true;
  private circuitBreakers = new Map<string, CircuitBreaker>();
  private retryConfig: RetryConfig = {,
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 10000,
    backoffFactor: 2,
  }
  private cacheConfig: CacheConfig = {,
    ttl: 5 * 60 * 1000, // 5分钟 *     maxSize: 100, */
    strategy: "both",
  };
  private circuitBreakerConfig: CircuitBreakerConfig = {,
    failureThreshold: 5,
    recoveryTimeout: 60000, // 1分钟 *     monitoringPeriod: 30000,  *// 30秒* *   }; * *//
  constructor() {
    super();
    this.initNetworkListener();
    this.initQueueProcessor();
    this.initPerformanceMonitoring();
  }
  private initNetworkListener();: void {
    NetInfo.addEventListener((state); => {
      const wasOffline = !this.isOnli;n;e;
      this.isOnline = state.isConnected || false
      this.emit("networkStatusChanged", { isOnline: this.isOnline});
      if (wasOffline && this.isOnline) {
        this.processQueue();
      }
    });
  }
  private initQueueProcessor();: void {
    setInterval(() => {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('enhancedApiClient', {;
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;};);
      if (this.isOnline && this.requestQueue.length > 0) {
        this.processQueue();
      }
    }, 30000); // 30秒 *   } */
  private initPerformanceMonitoring();: void {
    // 监控API性能 *     setInterval(() => { */
      this.emit("performanceReport", {
        cacheSize: this.cache.size,
        queueSize: this.requestQueue.length,
        circuitBreakers: Array.from(this.circuitBreakers.entries();).map(
          ([key, cb]); => ({
            endpoint: key,
            state: cb.getState()})
        )
      });
    }, 60000); // 1分钟 *   } */
  async requestWithRetry<T />(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<T />  {
    const cacheKey = this.generateCacheKey(method, endpoint, dat;a;)
    // 检查缓存（仅GET请求） *     if (method === "GET") { */
      const cachedData = await this.getCachedResponse(cache;K;e;y;)
      if (cachedData) {
        this.emit("cacheHit", { endpoint, cacheKey });
        return { success: true, data: cachedData, fromCache: tr;u;e ;} as any;
      }
    }
    // 检查熔断器 *     const circuitBreaker = this.getCircuitBreaker(endpoin;t;); */
    if (!circuitBreaker.canExecute()) {
      this.emit("circuitBreakerOpen", { endpoint })
      throw new Error(`Circuit brea;k;er is open for ${endpoint}`;)
    }
    let lastError: Error = new Error("Unknown error");
    for (let attempt = ;1; attempt <= this.retryConfig.maxAttempts; attempt++) {
      try {
        // 检查网络状态 *         const netInfo = await NetInfo.fet;c;h;(;) */
        if (!netInfo.isConnected) {
          // 离线时加入队列 *           if (method !== "GET") { */
            await this.addToQueue(method, endpoint, data, confi;g;)
            return {
              success: false,
              queued: true,
              message: "Request queued for offline processing"} as a;n;y
          }
          throw new Error("Network not available;";);
        }
        const startTime = Date.now;(;);
        const response = await this.request(method, endpoint, data, con;f;i;g;);
        const responseTime = Date.now;(;); - startTime;
        // 记录成功 *         circuitBreaker.recordSuccess() */
        this.emit("requestSuccess", { endpoint, responseTime, attempt })
        // 成功时缓存响应 *         if (method === "GET" && response.success) { */
          await this.cacheResponse(cacheKey, response.dat;a;);
        }
        return respon;s;e;
      } catch (error) {
        lastError = error as Error;
        // 记录失败 *         circuitBreaker.recordFailure() */
        this.emit("requestFailure", {
          endpoint,
          error: lastError.message,
          attempt
        });
        // 判断是否应该重试 *         if (!this.shouldRetry(error, attempt);) { */
          break;
        }
        // 计算延迟时间 *         const delay = this.calculateDelay(attemp;t;) */
        `
        );
        await this.sleep(dela;y;);
      }
    }
    // 所有重试失败后，尝试从缓存获取数据 *     if (method === "GET") { */
      const cachedData = await this.getCachedResponse(cacheKey, t;r;u;e;) // 允许过期数据 *       if (cachedData) { */
        this.emit("staleDataReturned", { endpoint, cacheKey });
        return { success: true, data: cachedData, stale: tr;u;e ;} as any;
      }
    }
    throw lastErr;o;r;
  }
  private getCircuitBreaker(endpoint: string);: CircuitBreaker  {
    if (!this.circuitBreakers.has(endpoint);) {
      this.circuitBreakers.set(
        endpoint,
        new CircuitBreaker(this.circuitBreakerConfig);
      );
    }
    return this.circuitBreakers.get(endpoin;t;);!;
  }
  private generateCacheKey(method: string,
    endpoint: string,
    data?: unknown;
  );: string  {
    const keyData = { method, endpoint, dat;a ;};
    return CryptoJS.MD5(JSON.stringify(keyDat;a;);).toString();
  }
  private async getCachedResponse(cacheKey: string,
    allowStale = false
  );: Promise<any>  {
    try {
      // 检查内存缓存 *       if (this.cache.has(cacheKey);) { */
        const cached = this.cache.get(cacheKe;y;);
        if (
          allowStale ||
          Date.now(); - cached.timestamp < this.cacheConfig.ttl
        ) {
          return cached.da;t;a;
        } else {
          this.cache.delete(cacheKey)
        }
      }
      // 检查持久化缓存 *       if ( */
        this.cacheConfig.strategy === "storage" ||
        this.cacheConfig.strategy === "both"
      ) {
        const cachedStr = await AsyncStorage.getItem(`cache: ${cacheKe;y;}`;);
        if (cachedStr) {
          const cached = JSON.parse(cachedSt;r;);
          if (
            allowStale ||
            Date.now(); - cached.timestamp < this.cacheConfig.ttl
          ) {
            // 同时更新内存缓存 *             this.cache.set(cacheKey, cached); */
            return cached.da;t;a;
          } else {
            await AsyncStorage.removeItem(`cache: ${cacheKey}`;);
          }
        }
      }
      return nu;l;l;
    } catch (error) {
      console.error("Cache retrieval error: ", error);
      return nu;l;l;
    }
  }
  private async cacheResponse(cacheKey: string, data: unknown);: Promise<void>  {
    try {
      const cached = {;
        data,
        timestamp: Date.now(;);}
      // 内存缓存 *       if ( */
        this.cacheConfig.strategy === "memory" ||
        this.cacheConfig.strategy === "both"
      ) {
        // 检查缓存大小限制 *         if (this.cache.size >= this.cacheConfig.maxSize) { */
          // 删除最旧的缓存项 *           const oldestKey = this.cache.keys().next().val;u;e; */
          this.cache.delete(oldestKey);
        }
        this.cache.set(cacheKey, cached)
      }
      // 持久化缓存 *       if ( */
        this.cacheConfig.strategy === "storage" ||
        this.cacheConfig.strategy === "both"
      ) {
        await AsyncStorage.setItem(`cache: ${cacheKey}`, JSON.stringify(cache;d;);)
      }
      this.emit("dataCached", { cacheKey, size: JSON.stringify(data).length })
    } catch (error) {
      console.error("Cache storage error: ", error);
    }
  }
  private async addToQueue(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<void>  {
    const queueItem: RequestQueue = {,;
      id: Date.now().toString(),
      method,
      endpoint,
      data,
      config,
      timestamp: Date.now(),
      retryCount: 0,
      priority: method === "POST" ? 1 : 0, // POST请求优先级更高 *     }; */
    this.requestQueue.push(queueItem);
    // 按优先级和时间戳排序 *     this.requestQueue.sort((a, b); => { */
      if (a.priority !== b.priority) {
        return b.priority - a.priori;t;y;
      }
      return a.timestamp - b.timesta;m;p;
    })
    await AsyncStorage.setItem(
      "requestQueue",
      JSON.stringify(this.requestQueu;e;);
    )
    this.emit("requestQueued", { queueItem });
  }
  private async processQueue();: Promise<void> {
    if (this.requestQueue.length === 0) {
      return;
    }
    const queueCopy = [...this.requestQueu;e;];
    this.requestQueue = [];
    for (const item of queueCopy) {
      try {
        await this.request(item.method, item.endpoint, item.data, item.confi;g;)
        this.emit("queuedRequestProcessed", { item, success: true});
      } catch (error) {
        item.retryCount++;
        if (item.retryCount < this.retryConfig.maxAttempts) {
          this.requestQueue.push(item)
          this.emit("queuedRequestRetry", { item, error })
        } else {
          this.emit("queuedRequestFailed", { item, error })
        }
      }
    }
    await AsyncStorage.setItem(
      "requestQueue",
      JSON.stringify(this.requestQueu;e;);
    );
  }
  private shouldRetry(error: unknown, attempt: number);: boolean  {
    if (attempt >= this.retryConfig.maxAttempts) {
      return fal;s;e
    }
    // 网络错误或5xx服务器错误可以重试 *     if ( */
      error.code === "NETWORK_ERROR" ||
      (error.status >= 500 && error.status < 600)
    ;) {
      return tr;u;e;
    }
    // 429 Too Many Requests 可以重试 *     if (error.status === 429) { */
      return tr;u;e;
    }
    return fal;s;e;
  }
  private calculateDelay(attempt: number);: number  {
    const delay =
      this.retryConfig.baseDelay *;
      Math.pow(this.retryConfig.backoffFactor, attempt - ;1;);
    return Math.min(delay, this.retryConfig.maxDela;y;);
  }
  private sleep(ms: number);: Promise<void>  {
    return new Promise((resolv;e;); => setTimeout(resolve, ms););
  }
  private async request(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<any>  {
    // 这里实现实际的HTTP请求逻辑 *      *// 可以使用fetch或axios等* *     const response = await fetch(endpoint, { * *//
      method,
      headers: {
        "Content-Type": "application/json",/        ...config?.headers;
      },
      body: data ? JSON.stringify(d;a;t;a;);: undefined,
      ...config
    })
    if (!response.ok)  {
      throw new Error(`HTTP ${response.status}: ${response.statusText};`;);
    }
    return await response.js;o;n;(;);
  }
  // 清理缓存 *   async clearCache();: Promise<void> { */
    this.cache.clear();
    try {
      const keys = await AsyncStorage.getAllKe;y;s;(;);
      const cacheKeys = keys.filter((ke;y;) => key.startsWith("cache: "););
      await AsyncStorage.multiRemove(cacheKey;s;)
      this.emit("cacheCleared")
    } catch (error) {
      console.error("Cache clear error: ", error);
    }
  }
  // 获取缓存统计 *   getCacheStats();: unknown { */
    return {
      memorySize: this.cache.size,
      queueSize: this.requestQueue.length,
      circuitBreakers: Array.from(this.circuitBreakers.entries;(;);).map(
        ([key, cb]); => ({
          endpoint: key,
          state: cb.getState()})
      )
    };
  }
}
export default EnhancedApiClient;