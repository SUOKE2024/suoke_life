import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import { performanceMonitor, cacheManager, handleError } from "./    index";
import React from "react";
网络请求优化工具   提供请求去重、批量处理、重试机制、缓存等功能
export interface RequestConfig {
  url: string,method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
  cacheTTL?: number;
  dedupe?: boolean
}
export interface RequestResponse<T = any /> {/      data: T,status: number,headers: Record<string, string>;
  cached: boolean,
  duration: number}
export interface BatchRequest {
  id: string;
  config: RequestConfig;
  resolve: (response: RequestResponse) => void;
  reject: (error: unknown) => void;
}
// 网络优化器类export class NetworkOptimizer  {private static instance: NetworkOptimizer;
  private pendingRequests: Map<string, Promise<RequestResponse /> /> = new Map();/      private batchQueue: BatchRequest[] = [];
  private batchTimer: unknown = null;
  private readonly batchDelay = 50;  private readonly maxBatchSize = 10  / 最大批量大小* ///
  private constructor() {}
  static getInstance(): NetworkOptimizer {
    if (!NetworkOptimizer.instance) {
      NetworkOptimizer.instance = new NetworkOptimizer();
    }
    return NetworkOptimizer.instance;
  }
  ///        const requestKey = this.generateRequestKey(config;);
    if (config.dedupe !== false && this.pendingRequests.has(requestKey)) {
      return this.pendingRequests.get(requestKe;y;);! as Promise<
        RequestResponse<T> />/        }
    if (config.cache !== false && config.method === "GET") {
      const cached = await this.getCachedResponse<T>(requestK;e;y;);
      if (cached) {
        return cach;e;d;
      }
    }
    const requestPromise = this.executeRequest<T>(confi;g;);
    if (config.dedupe !== false) {
      this.pendingRequests.set(requestKey, requestPromise);
      requestPromise.finally() => {
  // 性能监控
const performanceMonitor = usePerformanceMonitor(networkOptimizer", {"
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
        this.pendingRequests.delete(requestKey);
      });
    }
    return requestPromi;s;e;
  }
  ///        config: RequestConfig): Promise<RequestResponse<T>>  {
    return new Promise(resolve, rejec;t;); => {}
      const batchRequest: BatchRequest = {id: Math.random().toString(36).substr(2, 9),
        config,
        resolve: resolve as (response: RequestResponse) => void,
        reject;
      };
      this.batchQueue.push(batchRequest);
      if (this.batchQueue.length >= this.maxBatchSize) {
        this.processBatch();
      } else {
        if (!this.batchTimer) {
          this.batchTimer = setTimeout() => {
            this.processBatch();
          }, this.batchDelay);
        }
      }
    });
  }
  // 执行单个请求  private async executeRequest<T>(config: RequestConfig): Promise<RequestResponse<T>>  {
    const startTime = performance.now();
    let attempt = 0;
    const maxRetries = config.retries |;| ;3;
    const retryDelay = config.retryDelay || 10;
    while (attempt <= maxRetries) {
      try {
        const controller = new AbortController;
        const timeoutId = config.timeout;
          ? setTimeout(); => {}
              controller.abort();
            }, config.timeout)
          : null;
const fetchConfig: RequestInit = {method: config.method,
          headers: {
            "Content-Type": "application/json",/                ...config.headers;
          },
          signal: controller.signal;
        }
        if (config.body && config.method !== "GET") {
          fetchConfig.body =
            typeof config.body === "string"
              ? config.body;
              : JSON.stringify(config.body)}
        const response = await fetch(config.url, fetchCon;f;i;g;);
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        const endTime = performance.now();
        const duration = endTime - startTi;m;e;
        let requestSize = 0;
        if (fetchConfig.body) {
          try {
            if (typeof fetchConfig.body === "string") {
              requestSize = new Blob([fetchConfig.body]).size;
            } else {
              requestSize = 0;  }
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
          requestSize;
        )
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`;);
        }
        const data = await response.js;o;n;
        const headers: Record<string, string> = {};
        response.headers.forEach(value, key); => {}
          headers[key] = value;
        });
        const result: RequestResponse<T> = {data,
          status: response.status,
          headers,
          cached: false,
          duration;
        }
        if (config.cache !== false && config.method === "GET") {
          await this.cacheResponse(
            this.generateRequestKey(config),
            result,
            config.cacheTTL;);
        }
        return result;
      } catch (error: unknown) {
        attempt++;
        if (attempt > maxRetries) {
          handleError(error, {
            url: config.url,
            method: config.method,
            attempt;
          });
          throw error;
        }
        if (attempt <= maxRetries) {
          await this.delay(retryDelay * attempt;);
        }
      }
    }
    throw new Error("Max retries exceeded;";);
  }
  // 处理批量请求  private async processBatch(): Promise<void> {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
    const currentBatch = [...this.batchQueu;e;];
    this.batchQueue = [];
    const groupedRequests = this.groupRequestsByDomain(currentBatch;);
    const promises = Object.entries(groupedRequests).map([domain, requests];); => {}
      this.processDomainRequests(domain, requests);
    );
    await Promise.allSettled(promise;s;);
  }
  // 按域名分组请求  private groupRequestsByDomain(requests: BatchRequest[]);: Record<string, BatchRequest[]>  {
    const grouped: Record<string, BatchRequest[]> = {};
    requests.forEach(request); => {}
      const url = new URL(request.config.ur;l;);
      const domain = url.hostna;m;e;
      if (!grouped[domain]) {
        grouped[domain] = [];
      }
      grouped[domain].push(request);
    });
    return group;e;d;
  }
  // 处理单个域名的请求  private async processDomainRequests(domain: string,
    requests: BatchRequest[]);: Promise<void>  {
    const concurrency = 5;
    const chunks = this.chunkArray(requests, concurrenc;y;);
    for (const chunk of chunks) {
      const promises = chunk.map(async (reques;t;); => {}
        try {
          const response = await this.executeRequest(request.con;f;i;g;);
          request.resolve(response);
        } catch (error) {
          request.reject(error);
        }
      });
      await Promise.allSettled(promise;s;);
    }
  }
  // 生成请求键  private generateRequestKey(config: RequestConfig): string  {
    const { url, method, body   } = conf;i;g;
    const bodyStr = body ? JSON.stringify(bod;y;):
    return `$ {method}:${url}:${bodyStr;};`;
  }
  // 获取缓存的响应  private async getCachedResponse<T>(key: string): Promise<RequestResponse<T> | null>  {
    try {
      const cached = await cacheManager.get<RequestResponse<T>>(;k;e;y;);/          if (cached) {return {...cached,
          cached: tru;e;}
      }
    } catch (error) {
      }
    return nu;l;l;
  }
  // 缓存响应  private async cacheResponse(key: string,
    response: RequestResponse,
    ttl?: number;
  ): Promise<void>  {
    try {
      await cacheManager.set(key, response, { ttl ;};);
    } catch (error) {
      }
  }
  // 延迟函数  private delay(ms: number): Promise<void>  {
    return new Promise(resolv;e;); => setTimeout(resolve, ms););
  }
  // 数组分块  private chunkArray<T>(array: T[], size: number): T[][]  {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size););
    }
    return chun;k;s;
  }
  // 取消所有待处理的请求  cancelAllRequests(): void {
    this.pendingRequests.clear();
    this.batchQueue.forEach(request) => {}
      request.reject(new Error("Request cancelled"));
    });
    this.batchQueue = [];
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
  }
  // 获取网络状态统计  getNetworkStats(): { pendingRequests: number,
    queuedBatchRequests: number,
    cacheHitRate: number} {
    const performanceStats = performanceMonitor.getNetworkStats;
    const cacheStats = cacheManager.getStats;
    return {pendingRequests: this.pendingRequests.size,queuedBatchRequests: this.batchQueue.length,cacheHitRate: cacheStats.hitRat;e;};
  }
}
//   ;
//   ;
i;g;): Promise<RequestResponse<T  /     >> => {}
  return networkOptimizer.request<T>(confi;g;);
};
export const batchRequest = <T = any />(/      config: RequestConf;
i;g;): Promise<RequestResponse<T>> => {}
  return networkOptimizer.batchRequest<T>(confi;g;);
};
export const cancelAllNetworkRequests = () =;
> ;{networkOptimizer.cancelAllRequests();
};
export const getNetworkStats = () =;
> ;{return networkOptimizer.getNetworkStats;
};