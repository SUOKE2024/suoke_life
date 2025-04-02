import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { Logger } from './logger';

const logger = new Logger('HttpClient');

/**
 * HTTP客户端，用于服务间通信
 */
export class HttpClient {
  private baseUrl: string;
  private timeout: number;
  
  constructor(baseUrl: string, timeout: number = 10000) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }
  
  /**
   * 发送GET请求
   */
  async get<T>(endpoint: string, params?: any, headers?: Record<string, string>): Promise<T> {
    try {
      const config: AxiosRequestConfig = {
        params,
        headers,
        timeout: this.timeout
      };
      
      logger.debug(`发送GET请求: ${this.baseUrl}${endpoint}`, { params });
      
      const response: AxiosResponse<T> = await axios.get(`${this.baseUrl}${endpoint}`, config);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'GET', endpoint);
      throw error;
    }
  }
  
  /**
   * 发送POST请求
   */
  async post<T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> {
    try {
      const config: AxiosRequestConfig = {
        headers,
        timeout: this.timeout
      };
      
      logger.debug(`发送POST请求: ${this.baseUrl}${endpoint}`, { dataSize: JSON.stringify(data).length });
      
      const response: AxiosResponse<T> = await axios.post(`${this.baseUrl}${endpoint}`, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'POST', endpoint);
      throw error;
    }
  }
  
  /**
   * 发送PUT请求
   */
  async put<T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> {
    try {
      const config: AxiosRequestConfig = {
        headers,
        timeout: this.timeout
      };
      
      logger.debug(`发送PUT请求: ${this.baseUrl}${endpoint}`, { dataSize: JSON.stringify(data).length });
      
      const response: AxiosResponse<T> = await axios.put(`${this.baseUrl}${endpoint}`, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'PUT', endpoint);
      throw error;
    }
  }
  
  /**
   * 发送DELETE请求
   */
  async delete<T>(endpoint: string, params?: any, headers?: Record<string, string>): Promise<T> {
    try {
      const config: AxiosRequestConfig = {
        params,
        headers,
        timeout: this.timeout
      };
      
      logger.debug(`发送DELETE请求: ${this.baseUrl}${endpoint}`, { params });
      
      const response: AxiosResponse<T> = await axios.delete(`${this.baseUrl}${endpoint}`, config);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError, 'DELETE', endpoint);
      throw error;
    }
  }
  
  /**
   * 处理请求错误
   */
  private handleError(error: AxiosError, method: string, endpoint: string): void {
    if (error.response) {
      // 服务器返回非2xx响应
      logger.error(`HTTP ${method} 请求错误 (${error.response.status}): ${this.baseUrl}${endpoint}`, {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // 请求已发送但未收到响应
      logger.error(`HTTP ${method} 请求未收到响应: ${this.baseUrl}${endpoint}`, {
        request: error.request,
        message: error.message
      });
    } else {
      // 请求配置出错
      logger.error(`HTTP ${method} 请求配置错误: ${this.baseUrl}${endpoint}`, {
        message: error.message,
        stack: error.stack
      });
    }
  }
} 