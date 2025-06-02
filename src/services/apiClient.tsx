import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
importaxios,{ AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
importAsyncStorage from "@react-native-async-storage/async-storage"/import { API_CONFIG, ERROR_CODES, STORAGE_CONFIG } from "../constants/config"/import { EventEmitter } from "../utils/eventEmitter";/;
// 请求接口 * interface ApiRequest { */
  url: string,
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  data?: unknown;
  params?: unknown;
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number}
// 响应接口 * interface ApiResponse<T = any  *// > { success: boolean; *, data: T; */
  message?: string;
  code?: string;
  timestamp?: string}
// 错误接口 * interface ApiError { code: string, */
  message: string;
  details?: unknown;
  timestamp: string}
class ApiClient {
  private client: AxiosInstance;
  private eventEmitter: EventEmitter;
  private requestQueue: Map<string, Promise<any>> = new Map();
  constructor() {
    this.eventEmitter = new EventEmitter()
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        "Content-Type": "application/json",/        Accept: "application/json",/        "X-Client-Version": "1.0.0",
        "X-Platform": "react-native"
      }
    });
    this.setupInterceptors();
  }
  // /    设置请求和响应拦截器  private setupInterceptors() {
    // 请求拦截器 *     this.client.interceptors.request.use( */
      async (config); => {
        // 添加认证token *         const token = await AsyncStorage.getItem( */;
          STORAGE_CONFIG.KEYS.AUTH_TO;K;E;N
        ;)
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        // 添加设备ID *         const deviceId = await AsyncStorage.getItem( */;
          STORAGE_CONFIG.KEYS.DEVICE;_;I;D
        ;)
        if (deviceId) {
          config.headers["X-Device-ID"] = deviceId;
        }
        // 添加请求ID用于追踪 *         const requestId = this.generateRequestId;(;) */
        config.headers["X-Request-ID"] = requestId
        } ${config.url}`,
          {
            requestId,
            headers: config.headers,
            data: config.data,
          }
        );
        return conf;i;g;
      },
      (error) => {
        console.error("[API] 请求拦截器错误:", error);
        return Promise.reject(erro;r;);
      }
    );
    // 响应拦截器 *     this.client.interceptors.response.use( */
      (response: AxiosResponse) => {
        const requestId = response.config.headers["X-Request-ID;";];
        return respon;s;e
      },
      async (error) => {
        const requestId = error.config?.headers?.["X-Request-ID;";]
        console.error(`[API] 响应错误:`, {
          requestId,
          url: error.config?.url,
          status: error.response?.status,
          message: error.message,
          data: error.response?.data,
        });
        // 处理认证错误 *         if (error.response?.status === 401) { */
          await this.handleAuthError;(;);
        }
        // 处理网络错误 *         if (!error.response) { */
          return Promise.reject(
            this.createApiError(ERROR_CODES.NETWORK_ERROR, "网络连接失败;";);
          );
        }
        // 处理服务器错误 *         const apiError = this.createApiError( */
          error.response.data?.code || ERROR_CODES.OPERATION_FAILED,
          error.response.data?.message || error.message,
          error.response.dat;a
        ;);
        return Promise.reject(apiErro;r;);
      }
    );
  }
  // /    处理认证错误  private async handleAuthError() {
    try {
      // 尝试刷新token *       const refreshToken = await AsyncStorage.getItem( */;
        STORAGE_CONFIG.KEYS.REFRESH_TO;K;E;N
      ;);
      if (refreshToken) {
        const response = await this.refreshToken(refreshTo;k;e;n;);
        if (response.success) {
          await AsyncStorage.setItem(
            STORAGE_CONFIG.KEYS.AUTH_TOKEN,
            response.data.accessToke;n
          ;);
          return
        }
      }
    } catch (error) {
      console.error("[API] Token刷新失败:", error);
    }
    // 清除认证信息并触发登出事件 *     await AsyncStorage.multiRemove([ */
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      STORAGE_CONFIG.KEYS.USER_ID
    ;];)
    this.eventEmitter.emit("auth: logout")}
  // /    刷新token  private async refreshToken(refreshToken: string);: Promise<ApiResponse />  {
    const response = await axios.post(;
      `${API_CONFIG.SERVICES.AUTH}/auth/refresh`,/      {;
        refreshTok;e;n
      ;}
    ;);
    return response.da;t;a;
  }
  // /    生成请求ID  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9);};`;
  }
  // /    创建API错误对象  private createApiError(code: string,
    message: string,
    details?: unknown;
  );: ApiError  {
    return {
      code,
      message,
      details,
      timestamp: new Date().toISOString(;);};
  }
  // /    请求去重  private getRequestKey(config: ApiRequest): string  {
    const { url, method = "GET", data, params   } = conf;i;g
    return `${method}:${url}:${JSON.stringify(data || {})}:${JSON.stringify(
      params || {});};`;
  }
  // /    执行请求  async request<T = any />(config: ApiRequest): Promise<ApiResponse<T />>  {/    const requestKey = this.getRequestKey(confi;g;);
    // 检查是否有相同的请求正在进行 *     if (this.requestQueue.has(requestKey);) { */
      return this.requestQueue.get(requestKe;y;);
    }
    // 创建请求Promise *     const requestPromise = this.executeRequest<T  *// >(confi;g;);
    // 添加到请求队列 *     this.requestQueue.set(requestKey, requestPromise); */
    try {
      const result = await requestPro;m;i;s;e;
      return resu;l;t;
    } finally {
      // 请求完成后从队列中移除 *       this.requestQueue.delete(requestKey); */
    }
  }
  // /    执行实际请求  private async executeRequest<T = any />(/    config: ApiRequest;): Promise<ApiResponse<T />>  {
    const { retries = API_CONFIG.RETRY_ATTEMPTS   } = conf;i;g;
    let lastError: unknown;
    for (let attempt = ;1; attempt <= retries attempt++) {
      try {
        const axiosConfig: AxiosRequestConfig = {,;
          url: config.url,
          method: config.method || "GET",
          data: config.data,
          params: config.params,
          headers: config.headers,
          timeout: config.timeout || API_CONFIG.TIMEOUT,
        };
        const response = await this.client.request(axiosCon;f;i;g;)
        // 标准化响应格式 *         if (response.data && typeof response.data === "object") { */
          return {
            success: true,
            data: response.data.data || response.data,
            message: response.data.message,
            code: response.data.code,
            timestamp: new Date().toISOString(;);};
        }
        return {
          success: true,
          data: response.data,
          timestamp: new Date().toISOString(;);};
      } catch (error: unknown) {
        lastError = error;
        if (attempt < retries) {
          const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, attempt - ;1;) // 指数退避 *           :`, */
            error.message
          );
          await new Promise<void>((resolve) => setTimeout(resolve, dela;y;););
        }
      }
    }
    throw lastErr;o;r;
  }
  // /    GET请求  async get<T = any />(/    url: string,
    params?: unknown,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "GET",
      params,
      ...config;};)
  }
  // /    POST请求  async post<T = any />(/    url: string,
    data?: unknown,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "POST",
      data,
      ...config;};)
  }
  // /    PUT请求  async put<T = any />(/    url: string,
    data?: unknown,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "PUT",
      data,
      ...config;};)
  }
  // /    DELETE请求  async delete<T = any />(/    url: string,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "DELETE",
      ...config;};)
  }
  // /    PATCH请求  async patch<T = any />(/    url: string,
    data?: unknown,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "PATCH",
      data,
      ...config;};);
  }
  // /    上传文件  async upload<T = any />(/    url: string,
    file: unknown,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    const formData = new FormData;(;)
    formData.append("file", file)
    return this.request<T />({
      url,
      method: "POST",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",/      },
      ...config;};);
  }
  // /    批量请求  async batch<T = any />(requests: ApiRequest[]): Promise<ApiResponse<T />[]>  {/    const promises = requests.map((reques;t;); => this.request<T />(request));
    return Promise.all(promise;s;);
  }
  // /    取消所有请求  cancelAllRequests() {
    this.requestQueue.clear();
  }
  // /    获取事件发射器  getEventEmitter();: EventEmitter {
    return this.eventEmitt;e;r;
  }
  // /    设置基础URL  setBaseURL(baseURL: string) {
    this.client.defaults.baseURL = baseURL;
  }
  // /    设置默认headers  setDefaultHeaders(headers: Record<string, string>) {
    Object.assign(this.client.defaults.headers, headers);
  }
  // /    健康检查  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.get("/health", undefined, {/        retries: 1,;
        timeout: 50;0;0
      ;};);
      return response.succe;s;s
    } catch (error) {
      console.error("[API] 健康检查失败:", error);
      return fal;s;e
    }
  }
  // /    多模态POST请求（FormData）  async postMultiModal<T = any />(/    url: string,
    formData: FormData,
    config?: Partial<ApiRequest />/  ): Promise<ApiResponse<T />>  {
    return this.request<T />({
      url,
      method: "POST",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },/      ...config;};);
  }
}
// 创建单例实例 * export const apiClient = new ApiClient;(;); */;
// 导出类型 * export type { ApiRequest, ApiResponse, ApiError }; */;
export default apiClient;