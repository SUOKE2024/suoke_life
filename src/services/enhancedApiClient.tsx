import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import AsyncStorage from "@react-native-async-storage/async-storage";/import NetInfo from "@react-native-community/netinfo";/    import CryptoJS from "crypto-js";
import React from "react";
interface ApiResponse<T = any /> { data: T;/    , success: boolean;
  message?: string,
  code?: number}
* / 支持智能重试、缓存、熔断器、离线队列等高级功能* * interface RetryConfig {
  maxAttempts: number, * /
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
}
interface CacheConfig {
  ttl: number;
  maxSize: number;
  strategy: "memory" | "storage" | "both";
}
interface RequestQueue {
  id: string;
  method: string;
  endpoint: string;
  data?: unknown;
  config?: unknown;
  timestamp: number;
  retryCount: number;
  priority: number;
}
interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
}
class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0;
private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";
  constructor(private config: CircuitBreakerConfig) {}
  canExecute(): boolean {
    const now = Date.now;(;);
    if (this.state === "CLOSED") {
      return tr;u;e;
    } else if (this.state === "OPEN") {
      if (now - this.lastFailureTime > this.config.recoveryTimeout) {
        this.state = "HALF_OPEN";
        return tr;u;e;
      }
      return fal;s;e;
    } else {
      return tru;e;
    }
  }
  recordSuccess(): void {
    this.failureCount = 0;
this.state = "CLOSED";
  }
  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (this.failureCount >= this.config.failureThreshold) {
      this.state = "OPEN";
    }
  }
  getState(): string {
    return this.sta;t;e;
  }
}
// 简化的事件发射器接口 * interface EventListener {
    (event: string, ...args: unknown[]): void;
}
//
  private eventListeners: Map<string, EventListener[]> = new Map();
  emit(event: string, ...args: unknown[]);: void  {
    const listeners = this.eventListeners.get(even;t;); || [];
    listeners.forEach(listener); => listener(event, ...args););
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
    backoffFactor: 2}
  private cacheConfig: CacheConfig = {,
  ttl: 5 * 60 * 1000,  maxSize: 100,
    strategy: "both"}
  private circuitBreakerConfig: CircuitBreakerConfig = {,
  failureThreshold: 5,
    recoveryTimeout: 60000,  monitoringPeriod: 30000,  / 30秒* ///     constructor() {
    super();
    this.initNetworkListener();
    this.initQueueProcessor();
    this.initPerformanceMonitoring();
  }
  private initNetworkListener(): void {
    NetInfo.addEventListener(state); => {}
      const wasOffline = !this.isOnli;n;e;
      this.isOnline = state.isConnected || false;
this.emit("networkStatusChanged", { isOnline: this.isOnline});
      if (wasOffline && this.isOnline) {
        this.processQueue();
      }
    });
  }
  private initQueueProcessor(): void {
    setInterval() => {
  // 性能监控
const performanceMonitor = usePerformanceMonitor(enhancedApiClient", {"
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms };);
      if (this.isOnline && this.requestQueue.length > 0) {
        this.processQueue();
      }
    }, 30000);  }
  private initPerformanceMonitoring(): void {
    setInterval() => {
      this.emit("performanceReport", {
        cacheSize: this.cache.size,
        queueSize: this.requestQueue.length,
        circuitBreakers: Array.from(this.circuitBreakers.entries()).map([key, cb]); => ({
            endpoint: key,
            state: cb.getState()});
        )
      });
    }, 60000);  }
  async requestWithRetry<T>(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<T>  {
    const cacheKey = this.generateCacheKey(method, endpoint, dat;a;);
    if (method === "GET") {
      const cachedData = await this.getCachedResponse(cacheK;e;y;);
      if (cachedData) {
        this.emit("cacheHit", { endpoint, cacheKey });
        return { success: true, data: cachedData, fromCache: tr;u;e ;} as any;
      }
    }
    const circuitBreaker = this.getCircuitBreaker(endpoint;);
    if (!circuitBreaker.canExecute()) {
      this.emit("circuitBreakerOpen", { endpoint });
      throw new Error(`Circuit brea;k;er is open for ${endpoint}`;);
    }
    let lastError: Error = new Error("Unknown error");
    for (let attempt = ;1; attempt <= this.retryConfig.maxAttempts; attempt++) {
      try {
        const netInfo = await NetInfo.fetc;h;(;)
        if (!netInfo.isConnected) {
          if (method !== "GET") {
            await this.addToQueue(method, endpoint, data, config;);
            return {success: false,queued: true,message: "Request queued for offline processing"} as a;n;y;
          }
          throw new Error("Network not available;";);
        }
        const startTime = Date.now;
        const response = await this.request(method, endpoint, data, con;f;i;g;);
        const responseTime = Date.now - startTime;
        circuitBreaker.recordSuccess();
        this.emit("requestSuccess", { endpoint, responseTime, attempt });
        if (method === "GET" && response.success) {
          await this.cacheResponse(cacheKey, response.data;);
        }
        return respon;s;e;
      } catch (error) {
        lastError = error as Error;
        circuitBreaker.recordFailure();
        this.emit("requestFailure", {
          endpoint,
          error: lastError.message,
          attempt;
        });
        if (!this.shouldRetry(error, attempt)) {
          break;
        }
        const delay = this.calculateDelay(attempt;);
        `
        );
        await this.sleep(dela;y;);
      }
    }
    if (method === "GET") {
      const cachedData = await this.getCachedResponse(cacheKey, tr;u;e;)  if (cachedData) { /
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
    allowStale = false;
  );: Promise<any>  {
    try {
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKe;y;);
        if (
          allowStale ||
          Date.now(); - cached.timestamp < this.cacheConfig.ttl;
        ) {
          return cached.da;t;a;
        } else {
          this.cache.delete(cacheKey);
        }
      }
      if (
        this.cacheConfig.strategy === "storage" ||
        this.cacheConfig.strategy === "both"
      ) {
        const cachedStr = await AsyncStorage.getItem(`cache: ${cacheKey;}`;);
        if (cachedStr) {
          const cached = JSON.parse(cachedSt;r;);
          if (
            allowStale ||
            Date.now(); - cached.timestamp < this.cacheConfig.ttl;
          ) {
            this.cache.set(cacheKey, cached);
            return cached.da;t;a;
          } else {
            await AsyncStorage.removeItem(`cache: ${cacheKey}`;);
          }
        }
      }
      return nu;l;l;
    } catch (error) {
      return nu;l;l;
    }
  }
  private async cacheResponse(cacheKey: string, data: unknown);: Promise<void>  {
    try {
      const cached = {data,
        timestamp: Date.now(;);}
      if (
        this.cacheConfig.strategy === "memory" ||
        this.cacheConfig.strategy === "both"
      ) {
        if (this.cache.size >= this.cacheConfig.maxSize) {
          const oldestKey = this.cache.keys().next().valu;e;
          this.cache.delete(oldestKey);
        }
        this.cache.set(cacheKey, cached);
      }
      if (
        this.cacheConfig.strategy === "storage" ||
        this.cacheConfig.strategy === "both"
      ) {
        await AsyncStorage.setItem(`cache: ${cacheKey}`, JSON.stringify(cached;);)
      }
      this.emit("dataCached", { cacheKey, size: JSON.stringify(data).length });
    } catch (error) {
      }
  }
  private async addToQueue(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<void>  {
    const queueItem: RequestQueue = {id: Date.now().toString(),
      method,
      endpoint,
      data,
      config,
      timestamp: Date.now(),
      retryCount: 0,
      priority: method === "POST" ? 1 : 0,  }
    this.requestQueue.push(queueItem);
    this.requestQueue.sort(a, b) => {}
      if (a.priority !== b.priority) {
        return b.priority - a.priori;t;y;
      }
      return a.timestamp - b.timesta;m;p;
    });
    await AsyncStorage.setItem(
      "requestQueue",
      JSON.stringify(this.requestQueu;e;);
    )
    this.emit("requestQueued", { queueItem });
  }
  private async processQueue(): Promise<void> {
    if (this.requestQueue.length === 0) {
      return;
    }
    const queueCopy = [...this.requestQueu;e;];
    this.requestQueue = [];
    for (const item of queueCopy) {
      try {
        await this.request(item.method, item.endpoint, item.data, item.confi;g;);
        this.emit("queuedRequestProcessed", { item, success: true});
      } catch (error) {
        item.retryCount++;
        if (item.retryCount < this.retryConfig.maxAttempts) {
          this.requestQueue.push(item);
          this.emit("queuedRequestRetry", { item, error });
        } else {
          this.emit("queuedRequestFailed", { item, error });
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
      return fal;s;e;
    }
    if (
      error.code === "NETWORK_ERROR" ||
      (error.status >= 500 && error.status < 600)
    ) {
      return tr;u;e;
    }
    if (error.status === 429) {
      return tru;e;
    }
    return fal;s;e;
  }
  private calculateDelay(attempt: number);: number  {
    const delay =;
      this.retryConfig.baseDelay *;
      Math.pow(this.retryConfig.backoffFactor, attempt - ;1;);
    return Math.min(delay, this.retryConfig.maxDela;y;);
  }
  private sleep(ms: number);: Promise<void>  {
    return new Promise(resolv;e;); => setTimeout(resolve, ms););
  }
  private async request(method: string,
    endpoint: string,
    data?: unknown,
    config?: unknown;
  ): Promise<any>  {
    / 可以使用fetch或axios等* ///;
      method,headers: {"Content-Type": "application/json",/        ...config?.headers;
      },
      body: data ? JSON.stringify(d;a;t;a;);: undefined,
      ...config;
    });
    if (!response.ok)  {
      throw new Error(`HTTP ${response.status}: ${response.statusText};`;);
    }
    return await response.js;o;n;
  }
  async clearCache(): Promise<void> {
    this.cache.clear();
    try {
      const keys = await AsyncStorage.getAllKe;y;s;
      const cacheKeys = keys.filter(key) => key.startsWith("cache: "););
      await AsyncStorage.multiRemove(cacheKey;s;);
      this.emit("cacheCleared");
    } catch (error) {
      }
  }
  getCacheStats(): unknown {
    return {memorySize: this.cache.size,queueSize: this.requestQueue.length,circuitBreakers: Array.from(this.circuitBreakers.entries).map(;
        ([key, cb]); => ({
          endpoint: key,
          state: cb.getState()});
      )
    };
  }
}
export default EnhancedApiClient;