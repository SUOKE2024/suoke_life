import { API_CONFIG, STORAGE_CONFIG, ERROR_CODES } from "../constants/config";
import { ApiResponse } from "../types";
import { webStorage } from "../utils/storage.web";


// 请求配置接口
interface RequestConfig {
  headers?: Record<string, string>;
  timeout?: number;
  requireAuth?: boolean;
}

// HTTP方法类型
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

class ApiClient {
  private baseURL: string;
  private defaultTimeout: number;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.defaultTimeout = API_CONFIG.TIMEOUT;
  }

  /**
   * 获取存储的认证令牌
   */
  private async getAuthToken(): Promise<string | null> {
    try {
      return await webStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error("获取认证令牌失败:", error);
      return null;
    }
  }

  /**
   * 设置认证令牌
   */
  async setAuthToken(token: string): Promise<void> {
    try {
      await webStorage.setItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN, token);
    } catch (error) {
      console.error("设置认证令牌失败:", error);
    }
  }

  /**
   * 移除认证令牌
   */
  async removeAuthToken(): Promise<void> {
    try {
      await webStorage.removeItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error("移除认证令牌失败:", error);
    }
  }

  /**
   * 构建请求头
   */
  private async buildHeaders(
    config?: RequestConfig
  ): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...config?.headers,
    };

    // 如果需要认证，添加Authorization头
    if (config?.requireAuth !== false) {
      const token = await this.getAuthToken();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * 发送HTTP请求
   */
  private async request<T = any>(
    method: HttpMethod,
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers = await this.buildHeaders(config);
      const timeout = config?.timeout || this.defaultTimeout;

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const requestOptions: RequestInit = {
        method,
        headers,
        signal: controller.signal,
      };

      // 为POST、PUT、PATCH请求添加body
      if (data && ["POST", "PUT", "PATCH"].includes(method)) {
        requestOptions.body = JSON.stringify(data);
      }

      console.log(`🚀 API请求: ${method} ${url}`);

      const response = await fetch(url, requestOptions);
      clearTimeout(timeoutId);
      const responseData = await response.json();

      console.log(`📡 API响应: ${response.status}`, responseData);

      if (!response.ok) {
        return {
          success: false,
          data: undefined,
          error: {
            code: response.status.toString(),
            message: responseData.message || `HTTP ${response.status}`,
            details: responseData.details,
          },
        };
      }

      return {
        success: true,
        data: responseData.data || responseData,
        error: undefined,
      };
    } catch (error: any) {
      console.error(`❌ API错误: ${method} ${endpoint}`, error);

      let errorMessage = "网络连接失败";
      let errorCode = ERROR_CODES.NETWORK_ERROR;

      if (error.name === "AbortError") {
        errorMessage = "请求超时";
        errorCode = ERROR_CODES.TIMEOUT;
      } else if (error.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        data: undefined,
        error: {
          code: errorCode,
          message: errorMessage,
          details: error.stack,
        },
      };
    }
  }

  /**
   * GET请求
   */
  async get<T = any>(
    endpoint: string,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>("GET", endpoint, undefined, config);
  }

  /**
   * POST请求
   */
  async post<T = any>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>("POST", endpoint, data, config);
  }

  /**
   * PUT请求
   */
  async put<T = any>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>("PUT", endpoint, data, config);
  }

  /**
   * DELETE请求
   */
  async delete<T = any>(
    endpoint: string,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>("DELETE", endpoint, undefined, config);
  }

  /**
   * PATCH请求
   */
  async patch<T = any>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>("PATCH", endpoint, data, config);
  }

  /**
   * 上传文件
   */
  async uploadFile<T = any>(
    endpoint: string,
    file: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers = await this.buildHeaders({
        ...config,
        headers: {
          // 不设置Content-Type，让浏览器自动设置
          ...config?.headers,
        },
      });

      // 移除Content-Type，让浏览器自动设置
      delete headers["Content-Type"];

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: formData,
      });

      const responseData = await response.json();

      if (!response.ok) {
        return {
          success: false,
          data: undefined,
          error: {
            code: response.status.toString(),
            message: responseData.message || `HTTP ${response.status}`,
            details: responseData.details,
          },
        };
      }

      return {
        success: true,
        data: responseData.data || responseData,
        error: undefined,
      };
    } catch (error: any) {
      console.error(`❌ 文件上传错误: ${endpoint}`, error);
      return {
        success: false,
        data: undefined,
        error: {
          code: ERROR_CODES.NETWORK_ERROR,
          message: error.message || "文件上传失败",
          details: error.stack,
        },
      };
    }
  }
}

// 创建单例实例
export const apiClient = new ApiClient();

// 导出便捷方法
export const setApiAuthToken = (token: string) => apiClient.setAuthToken(token);
export const removeApiAuthToken = () => apiClient.removeAuthToken();
