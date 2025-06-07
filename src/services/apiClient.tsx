import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG, ERROR_CODES, STORAGE_CONFIG } from '../constants/config';
import { EventEmitter } from '../utils/eventEmitter';
// 请求接口
interface ApiRequest {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: unknown;
  params?: unknown;
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
}
// 响应接口
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string,
  message: string;
    details?: unknown;
  };
  message?: string;
  code?: string;
  timestamp?: string;
}
// 错误接口
interface ApiError {
  code: string;
  message: string;
  details?: unknown;
  timestamp: string;
}
class ApiClient {
  private client: AxiosInstance;
  private eventEmitter: EventEmitter;
  private requestQueue: Map<string, Promise<any>> = new Map();
  constructor() {
    this.eventEmitter = new EventEmitter();
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        Accept: "application/json",X-Client-Version': "1.0.0",X-Platform': 'react-native'
      }
    });
    this.setupInterceptors();
  }
  // 设置请求和响应拦截器
  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      async config => {
        // 添加认证token;
        const token = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        // 添加设备ID;
        const deviceId = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.DEVICE_ID);
        if (deviceId) {
          config.headers['X-Device-ID'] = deviceId;
        }
        // 添加请求ID用于追踪
        const requestId = this.generateRequestId();
        config.headers['X-Request-ID'] = requestId;
        console.log(`API请求: ${config.method?.toUpperCase()} ${config.url}`, {
          requestId,
          headers: config.headers,
          data: config.data;
        });
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );
    // 响应拦截器
    this.client.interceptors.response.use(response: AxiosResponse) => {
        const requestId = response.config.headers['X-Request-ID'];
        console.log(`API响应: ${response.status} ${response.config.url}`, {
          requestId,
          data: response.data;
        });
        return response;
      },
      async error => {
        const requestId = error.config?.headers?.['X-Request-ID'];
        console.error(`API错误: ${error.config?.url}`, {
          requestId,
          status: error.response?.status,
          message: error.message;
        });
        // 处理认证错误
        if (error.response?.status === 401) {
          await this.handleAuthError();
        }
        // 处理网络错误
        if (!error.response) {
          return Promise.reject(this.createApiError(ERROR_CODES.NETWORK_ERROR, '网络连接失败'));
        }
        // 处理服务器错误
        const apiError = this.createApiError(;
          error.response.data?.code || ERROR_CODES.OPERATION_FAILED,error.response.data?.message || error.message,error.response.data;
        );
        return Promise.reject(apiError);
      }
    );
  }
  // 处理认证错误
  private async handleAuthError() {
    try {
      // 尝试刷新token;
      const refreshToken = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.REFRESH_TOKEN);
      if (refreshToken) {
        const response = await this.refreshToken(refreshToken);
        if (response.success) {
          await AsyncStorage.setItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN, response.data.accessToken);
          return;
        }
      }
    } catch (error) {
      console.error('刷新token失败:', error);
    }
    // 清除认证信息并触发登出事件
    await AsyncStorage.multiRemove([
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      STORAGE_CONFIG.KEYS.USER_ID;
    ]);
    this.eventEmitter.emit('auth:logout');
  }
  // 刷新token;
  private async refreshToken(refreshToken: string): Promise<ApiResponse> {
    const response = await axios.post(`${API_CONFIG.SERVICES.AUTH}/auth/refresh`, {refreshToken;
    });
    return response.data;
  }
  // 生成请求ID;
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  // 创建API错误对象
  private createApiError(code: string, message: string, details?: unknown): ApiError {
    return {code,message,details,timestamp: new Date().toISOString();
    };
  }
  // 请求去重
  private getRequestKey(config: ApiRequest): string {
    const { url, method = 'GET', data, params } = config;
    return `${method}:${url}:${JSON.stringify(data || {})}:${JSON.stringify(params || {})}`;
  }
  // 执行请求
  async request<T = any>(config: ApiRequest): Promise<ApiResponse<T>> {
    const requestKey = this.getRequestKey(config);
    // 检查是否有相同的请求正在进行
    if (this.requestQueue.has(requestKey)) {
      return this.requestQueue.get(requestKey);
    }
    // 创建请求Promise;
    const requestPromise = this.executeRequest<T>(config);
    // 添加到请求队列
    this.requestQueue.set(requestKey, requestPromise);
    try {
      const result = await requestPromise;
      return result;
    } finally {
      // 请求完成后从队列中移除
      this.requestQueue.delete(requestKey);
    }
  }
  // 执行实际请求
  private async executeRequest<T = any>(config: ApiRequest): Promise<ApiResponse<T>> {
    const { retries = API_CONFIG.RETRY_ATTEMPTS } = config;
    let lastError: unknown;
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const axiosConfig: AxiosRequestConfig = {,
  url: config.url,
          method: config.method || 'GET',
          data: config.data,
          params: config.params,
          headers: config.headers,
          timeout: config.timeout || API_CONFIG.TIMEOUT;
        };
        const response = await this.client.request(axiosConfig);
        // 标准化响应格式
        if (response.data && typeof response.data === 'object') {
          return {success: true,data: response.data.data || response.data,message: response.data.message,code: response.data.code,timestamp: new Date().toISOString();
          };
        }
        return {success: true,data: response.data,timestamp: new Date().toISOString();
        };
      } catch (error: unknown) {
        lastError = error;
        if (attempt < retries) {
          const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, attempt - 1); // 指数退避
          console.log(
            `请求失败，${delay}ms后重试 (${attempt}/${retries}):`,
            (error as Error).message || error;
          );
          await new Promise<void>(resolve => setTimeout(resolve, delay));
        }
      }
    }
    throw lastError;
  }
  // GET请求
  async get<T = any>(
    url: string,
    params?: unknown,
    config?: Partial<ApiRequest>
  ): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'GET',params,...config;
    });
  }
  // POST请求
  async post<T = any>(
    url: string,
    data?: unknown,
    config?: Partial<ApiRequest>
  ): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'POST',data,...config;
    });
  }
  // PUT请求
  async put<T = any>(
    url: string,
    data?: unknown,
    config?: Partial<ApiRequest>
  ): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'PUT',data,...config;
    });
  }
  // DELETE请求
  async delete<T = any>(url: string, config?: Partial<ApiRequest>): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'DELETE',...config;
    });
  }
  // PATCH请求
  async patch<T = any>(
    url: string,
    data?: unknown,
    config?: Partial<ApiRequest>
  ): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'PATCH',data,...config;
    });
  }
  // 上传文件
  async upload<T = any>(
    url: string,
    formData: FormData,
    config?: Partial<ApiRequest>
  ): Promise<ApiResponse<T>> {
    return this.request<T>({url,method: 'POST',data: formData,headers: {'Content-Type': 'multipart/form-data';
      },...config;
    });
  }
  // 下载文件
  async download(url: string, config?: Partial<ApiRequest>): Promise<Blob> {
    const response = await this.client.get(url, {responseType: 'blob',...config;
    });
    return response.data;
  }
  // 取消请求
  cancelRequest(requestKey: string) {
    if (this.requestQueue.has(requestKey)) {
      this.requestQueue.delete(requestKey);
    }
  }
  // 清空请求队列
  clearRequestQueue() {
    this.requestQueue.clear();
  }
  // 获取事件发射器
  getEventEmitter(): EventEmitter {
    return this.eventEmitter;
  }
}
// 导出单例实例
export const apiClient = new ApiClient();
export default apiClient;
