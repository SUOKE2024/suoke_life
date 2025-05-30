import AsyncStorage from "@react-native-async-storage/async-storage";
import { EventEmitter } from "../../utils/eventEmitter";


/**
 * 索克生活 - GraphQL客户端
 * 完整的GraphQL API支持，包含查询、变更、订阅功能
 */

// GraphQL操作类型
export type GraphQLOperationType = "query" | "mutation" | "subscription";

// GraphQL变量类型
export interface GraphQLVariables {
  [key: string]: any;
}

// GraphQL请求接口
export interface GraphQLRequest {
  query: string;
  variables?: GraphQLVariables;
  operationName?: string;
}

// GraphQL响应接口
export interface GraphQLResponse<T = any> {
  data?: T;
  errors?: GraphQLError[];
  extensions?: any;
}

// GraphQL错误接口
export interface GraphQLError {
  message: string;
  locations?: Array<{
    line: number;
    column: number;
  }>;
  path?: Array<string | number>;
  extensions?: any;
}

// 缓存配置接口
export interface CacheConfig {
  ttl?: number; // 缓存时间（毫秒）
  key?: string; // 自定义缓存键
  enabled?: boolean; // 是否启用缓存
}

// 请求配置接口
export interface RequestConfig {
  cache?: CacheConfig;
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  offline?: boolean; // 是否支持离线
}

// 订阅配置接口
export interface SubscriptionConfig {
  onData?: (data: any) => void;
  onError?: (error: GraphQLError) => void;
  onComplete?: () => void;
}

// 缓存项接口
interface CacheItem {
  data: any;
  timestamp: number;
  ttl: number;
  key: string;
}

// GraphQL客户端事件
export interface GraphQLClientEvents {
  requestStart: { request: GraphQLRequest; config?: RequestConfig };
  requestEnd: {
    request: GraphQLRequest;
    response: GraphQLResponse;
    duration: number;
  };
  requestError: { request: GraphQLRequest; error: Error };
  cacheHit: { key: string; data: any };
  cacheMiss: { key: string };
  subscriptionData: { subscription: string; data: any };
  subscriptionError: { subscription: string; error: GraphQLError };
  connectionStateChange: { connected: boolean };
}

export class GraphQLClient extends EventEmitter {
  private endpoint: string;
  private headers: Record<string, string> = {};
  private cache: Map<string, CacheItem> = new Map();
  private subscriptions: Map<string, WebSocket> = new Map();
  private defaultTimeout: number = 30000;
  private defaultRetries: number = 3;
  private isOnline: boolean = true;

  constructor(endpoint: string, defaultHeaders: Record<string, string> = {}) {
    super();
    this.endpoint = endpoint;
    this.headers = { "Content-Type": "application/json", ...defaultHeaders };
    this.initializeCache();
    this.setupNetworkListener();
  }

  /**
   * 初始化缓存
   */
  private async initializeCache(): Promise<void> {
    try {
      const cachedData = await AsyncStorage.getItem("@graphql_cache");
      if (cachedData) {
        const parsed = JSON.parse(cachedData);
        Object.entries(parsed).forEach(([key, item]: [string, any]) => {
          if (item.timestamp + item.ttl > Date.now()) {
            this.cache.set(key, item);
          }
        });
      }
    } catch (error) {
      console.warn("GraphQL缓存初始化失败:", error);
    }
  }

  /**
   * 设置网络监听
   */
  private setupNetworkListener(): void {
    // 这里可以添加网络状态监听
    // 在React Native中可以使用NetInfo
  }

  /**
   * 设置认证令牌
   */
  setAuthToken(token: string): void {
    this.headers["Authorization"] = `Bearer ${token}`;
  }

  /**
   * 移除认证令牌
   */
  removeAuthToken(): void {
    delete this.headers["Authorization"];
  }

  /**
   * 设置自定义头部
   */
  setHeaders(headers: Record<string, string>): void {
    this.headers = { ...this.headers, ...headers };
  }

  /**
   * 执行GraphQL查询
   */
  async query<T = any>(
    query: string,
    variables?: GraphQLVariables,
    config?: RequestConfig
  ): Promise<GraphQLResponse<T>> {
    const request: GraphQLRequest = { query, variables };
    const cacheKey = this.generateCacheKey(request, config?.cache?.key);

    // 检查缓存
    if (config?.cache?.enabled !== false) {
      const cached = this.getFromCache(cacheKey);
      if (cached) {
        this.emit("cacheHit", { key: cacheKey, data: cached });
        return { data: cached };
      }
      this.emit("cacheMiss", { key: cacheKey });
    }

    // 执行请求
    const startTime = Date.now();
    this.emit("requestStart", { request, config });

    try {
      const response = await this.executeRequest<T>(request, config);
      const duration = Date.now() - startTime;

      // 缓存响应
      if (response.data && config?.cache?.enabled !== false) {
        this.setCache(cacheKey, response.data, config?.cache?.ttl || 300000); // 默认5分钟
      }

      this.emit("requestEnd", { request, response, duration });
      return response;
    } catch (error) {
      this.emit("requestError", { request, error: error as Error });
      throw error;
    }
  }

  /**
   * 执行GraphQL变更
   */
  async mutate<T = any>(
    mutation: string,
    variables?: GraphQLVariables,
    config?: RequestConfig
  ): Promise<GraphQLResponse<T>> {
    const request: GraphQLRequest = { query: mutation, variables };

    const startTime = Date.now();
    this.emit("requestStart", { request, config });

    try {
      const response = await this.executeRequest<T>(request, config);
      const duration = Date.now() - startTime;

      // 变更后清除相关缓存
      this.invalidateCache(mutation);

      this.emit("requestEnd", { request, response, duration });
      return response;
    } catch (error) {
      this.emit("requestError", { request, error: error as Error });
      throw error;
    }
  }

  /**
   * 创建GraphQL订阅
   */
  subscribe(
    subscription: string,
    variables?: GraphQLVariables,
    config?: SubscriptionConfig
  ): () => void {
    const subscriptionId = this.generateSubscriptionId(subscription, variables);
    const wsEndpoint = this.endpoint.replace(/^http/, "ws") + "/graphql";

    const ws = new WebSocket(wsEndpoint, "graphql-ws");

    ws.onopen = () => {
      // 发送连接初始化
      ws.send(
        JSON.stringify({
          type: "connection_init",
          payload: { Authorization: this.headers["Authorization"] },
        })
      );
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "connection_ack":
          // 发送订阅
          ws.send(
            JSON.stringify({
              id: subscriptionId,
              type: "start",
              payload: { query: subscription, variables },
            })
          );
          break;

        case "data":
          if (message.id === subscriptionId) {
            this.emit("subscriptionData", {
              subscription: subscriptionId,
              data: message.payload,
            });
            config?.onData?.(message.payload.data);
          }
          break;

        case "error":
          if (message.id === subscriptionId) {
            this.emit("subscriptionError", {
              subscription: subscriptionId,
              error: message.payload,
            });
            config?.onError?.(message.payload);
          }
          break;

        case "complete":
          if (message.id === subscriptionId) {
            config?.onComplete?.();
            this.subscriptions.delete(subscriptionId);
          }
          break;
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket错误:", error);
      config?.onError?.({ message: "WebSocket连接错误" });
    };

    this.subscriptions.set(subscriptionId, ws);

    // 返回取消订阅函数
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            id: subscriptionId,
            type: "stop",
          })
        );
      }
      ws.close();
      this.subscriptions.delete(subscriptionId);
    };
  }

  /**
   * 执行HTTP请求
   */
  private async executeRequest<T>(
    request: GraphQLRequest,
    config?: RequestConfig
  ): Promise<GraphQLResponse<T>> {
    const timeout = config?.timeout || this.defaultTimeout;
    const retries = config?.retries || this.defaultRetries;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(this.endpoint, {
          method: "POST",
          headers: this.headers,
          body: JSON.stringify(request),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(
            `HTTP错误: ${response.status} ${response.statusText}`
          );
        }

        const result: GraphQLResponse<T> = await response.json();

        if (result.errors && result.errors.length > 0) {
          throw new Error(
            `GraphQL错误: ${result.errors.map((e) => e.message).join(", ")}`
          );
        }

        return result;
      } catch (error) {
        if (attempt === retries) {
          throw error;
        }

        // 指数退避重试
        await new Promise<void>((resolve) =>
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }

    throw new Error("请求失败，已达到最大重试次数");
  }

  /**
   * 生成缓存键
   */
  private generateCacheKey(
    request: GraphQLRequest,
    customKey?: string
  ): string {
    if (customKey) return customKey;

    const queryHash = this.hashString(request.query);
    const variablesHash = request.variables
      ? this.hashString(JSON.stringify(request.variables))
      : "";
    return `gql_${queryHash}_${variablesHash}`;
  }

  /**
   * 生成订阅ID
   */
  private generateSubscriptionId(
    subscription: string,
    variables?: GraphQLVariables
  ): string {
    const subHash = this.hashString(subscription);
    const varHash = variables ? this.hashString(JSON.stringify(variables)) : "";
    return `sub_${subHash}_${varHash}_${Date.now()}`;
  }

  /**
   * 字符串哈希
   */
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // 转换为32位整数
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * 从缓存获取数据
   */
  private getFromCache(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.timestamp + item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  /**
   * 设置缓存
   */
  private setCache(key: string, data: any, ttl: number): void {
    const item: CacheItem = {
      data,
      timestamp: Date.now(),
      ttl,
      key,
    };

    this.cache.set(key, item);
    this.persistCache();
  }

  /**
   * 持久化缓存
   */
  private async persistCache(): Promise<void> {
    try {
      const cacheObject: Record<string, CacheItem> = {};
      this.cache.forEach((value, key) => {
        cacheObject[key] = value;
      });
      await AsyncStorage.setItem("@graphql_cache", JSON.stringify(cacheObject));
    } catch (error) {
      console.warn("GraphQL缓存持久化失败:", error);
    }
  }

  /**
   * 清除缓存
   */
  invalidateCache(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
    } else {
      const keysToDelete: string[] = [];
      this.cache.forEach((_, key) => {
        if (key.includes(pattern)) {
          keysToDelete.push(key);
        }
      });
      keysToDelete.forEach((key) => this.cache.delete(key));
    }
    this.persistCache();
  }

  /**
   * 获取缓存统计
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }

  /**
   * 关闭所有连接
   */
  close(): void {
    this.subscriptions.forEach((ws) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    });
    this.subscriptions.clear();
    this.removeAllListeners();
  }
}

// 创建默认客户端实例
export const graphqlClient = new GraphQLClient("http://localhost:4000/graphql");
