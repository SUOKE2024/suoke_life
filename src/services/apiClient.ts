import {;,}API_GATEWAY_CONFIG,;
getCurrentEnvConfig,;
ERROR_CODES,;
GATEWAY_PERFORMANCE_CONFIG,;
GATEWAY_FEATURES,;
buildApiUrl,;
}
  getServiceHealthUrl;}
} from "../constants/config";""/;,"/g"/;
import { errorHandler, AppError } from "./errorHandler";""/;,"/g"/;
import { offlineService, getCachedData, cacheData, addOfflineOperation } from "./offlineService";""/;,"/g"/;
import { performanceMonitor } from "./performanceMonitor";""/;,"/g"/;
import { securityService } from "./securityService";""/;,"/g"/;
import { configService } from "./configService";""/;"/g"/;
// API响应接口/;,/g/;
export interface ApiResponse<T = any> {data: T}status: number,;
statusText: string,;
const success = boolean;
message?: string;
timestamp?: string;
}
  requestId?: string;}
}
// 请求配置接口/;,/g/;
export interface RequestConfig {;,}headers?: Record<string; string>;
timeout?: number;
retries?: number;
cache?: boolean;
skipAuth?: boolean;
}
}
  signal?: AbortSignal;}
}
// 网关错误接口/;,/g/;
export interface GatewayError extends Error {;,}const code = string;
status?: number;
service?: string;
requestId?: string;
}
  timestamp?: string;}
}
// 服务状态接口/;,/g/;
export interface ServiceStatus {";,}name: string,';,'';
status: 'healthy' | 'unhealthy' | 'unknown';','';
const instances = number;
responseTime?: number;
}
}
  lastCheck?: string;}
}
// 认证令牌管理/;,/g/;
class TokenManager {private accessToken: string | null = null;,}private refreshToken: string | null = null;
private tokenExpiry: number | null = null;
setTokens(accessToken: string, refreshToken: string, expiresIn: number) {this.accessToken = accessToken;,}this.refreshToken = refreshToken;
this.tokenExpiry = Date.now() + (expiresIn * 1000);';'';
        // 存储到本地存储'/;,'/g'/;
if (typeof localStorage !== 'undefined') {';,}localStorage.setItem('access_token', accessToken);';,'';
localStorage.setItem('refresh_token', refreshToken);';'';
}
}
      localStorage.setItem('token_expiry', this.tokenExpiry.toString());'}'';'';
    }
  }';,'';
getAccessToken(): string | null {';,}if (!this.accessToken && typeof localStorage !== 'undefined') {';,}this.accessToken = localStorage.getItem('access_token');';,'';
const expiry = localStorage.getItem('token_expiry');';'';
}
      this.tokenExpiry = expiry ? parseInt(expiry) : null;}
    }
        // 检查令牌是否过期/;,/g/;
if (this.tokenExpiry && Date.now() > this.tokenExpiry) {this.clearTokens();}}
      return null;}
    }
        return this.accessToken;
  }';,'';
getRefreshToken(): string | null {';,}if (!this.refreshToken && typeof localStorage !== 'undefined') {';}}'';
      this.refreshToken = localStorage.getItem('refresh_token');'}'';'';
    }
    return this.refreshToken;
  }
  clearTokens() {this.accessToken = null;,}this.refreshToken = null;';,'';
this.tokenExpiry = null;';,'';
if (typeof localStorage !== 'undefined') {';,}localStorage.removeItem('access_token');';,'';
localStorage.removeItem('refresh_token');';'';
}
      localStorage.removeItem('token_expiry');'}'';'';
    }
  }
  isTokenExpired(): boolean {}}
    return this.tokenExpiry ? Date.now() > this.tokenExpiry : true;}
  }
}
// 缓存管理/;,/g/;
class CacheManager {}
  private cache = new Map<string, { data: any; timestamp: number; ttl: number ;}>();
set(key: string, data: any, ttl: number = 300000) {this.cache.set(key, {);,}data,);
const timestamp = Date.now();
}
      ttl;}
    });
  }
  get(key: string): any | null {const cached = this.cache.get(key);,}if (!cached) return null;
if (Date.now() - cached.timestamp > cached.ttl) {this.cache.delete(key);}}
      return null;}
    }
    return cached.data;
  }
  clear() {}}
    this.cache.clear();}
  }
  delete(key: string) {}}
    this.cache.delete(key);}
  }
  size(): number {}}
    return this.cache.size;}
  }
}
// 熔断器/;,/g/;
class CircuitBreaker {private failures = 0;';,}private lastFailureTime = 0;';,'';
private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';';,'';
constructor();
private failureThreshold: number = 5;
}
}
    private recoveryTimeout: number = 60000;}
  ) {}
  canExecute(): boolean {';,}const now = Date.now();';,'';
if (this.state === 'CLOSED') {';}}'';
      return true;'}'';'';
    } else if (this.state === 'OPEN') {';,}if (now - this.lastFailureTime > this.recoveryTimeout) {';,}this.state = 'HALF_OPEN';';'';
}
        return true;}
      }
      return false;
    } else {// HALF_OPEN;/;}}/g/;
      return true;}
    }
  }
  recordSuccess() {';,}this.failures = 0;';'';
}
    this.state = 'CLOSED';'}'';'';
  }
  recordFailure() {this.failures++;,}this.lastFailureTime = Date.now();';,'';
if (this.failures >= this.failureThreshold) {';}}'';
      this.state = 'OPEN';'}'';'';
    }
  }
  getState(): string {}}
    return this.state;}
  }
}
// 统一网关API客户端/;,/g/;
export class GatewayApiClient {;,}private tokenManager = new TokenManager();
private cacheManager = new CacheManager();
private circuitBreaker = new CircuitBreaker();
GATEWAY_PERFORMANCE_CONFIG.CIRCUIT_BREAKER.FAILURE_THRESHOLD,;
GATEWAY_PERFORMANCE_CONFIG.CIRCUIT_BREAKER.RECOVERY_TIMEOUT;
  );
private baseURL: string;
private defaultTimeout: number;
constructor() {const config = getCurrentEnvConfig();,}this.baseURL = config.GATEWAY_URL;
}
}
    this.defaultTimeout = GATEWAY_PERFORMANCE_CONFIG.TIMEOUT;}
  }';'';
  // 构建请求URL;'/;,'/g'/;
private buildUrl(service: string, endpoint: string = '): string {'';,}try {}}'';
      return buildApiUrl(service, endpoint);}
    } catch (error) {// 如果服务不在预定义列表中，直接构建URL;/;}}/g/;
      const config = getCurrentEnvConfig();}
      return `${config.GATEWAY_URL}${config.API_PREFIX}/${service}${endpoint}`;```/`;`/g`/`;
    }
  }
  // 生成缓存键/;,/g/;
private generateCacheKey(method: string, url: string, data?: any): string {}
    const key = `${method;}:${url}`;````;,```;
if (data) {}
      return `${key}:${JSON.stringify(data)}`;````;```;
    }
    return key;
  }
  // 准备请求头/;,/g/;
private async prepareHeaders(config: RequestConfig = {;}): Promise<Record<string, string>> {';,}const: headers: Record<string, string> = {';}}'';
      'Content-Type': "application/json",X-Client-Version': "1.0.0",X-Request-ID': this.generateRequestId(),'}''/;'/g'/;
      ...config.headers;};
    // 添加认证头/;,/g/;
if (!config.skipAuth && GATEWAY_FEATURES.ENABLE_AUTHENTICATION) {const token = this.tokenManager.getAccessToken();';}}'';
      if (token) {'}'';
headers['Authorization'] = `Bearer ${token}`;````;```;
      }
    }
    return headers;
  }
  // 生成请求ID;/;,/g/;
private generateRequestId(): string {}
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  // 处理响应/;,/g/;
private async handleResponse<T>(response: Response, requestId: string): Promise<ApiResponse<T>> {const timestamp = new Date().toISOString();}}
        if (!response.ok) {}
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;````;,```;
const let = service: string | undefined;
            // 尝试解析错误响应/;,/g/;
try {const errorData = await response.json();,}errorMessage = errorData.message || errorMessage;
}
        service = errorData.service;}
      } catch {}}
        // 忽略JSON解析错误}/;/g/;
      }';,'';
const  error = {';,}name: "HttpError";",";
message: errorMessage,;
const status = response.status;
requestId,;
}
        timestamp,}
        service};";"";
            // 使用错误处理器处理错误"/;,"/g,"/;
  appError: errorHandler.handleError(error, service || 'api-client');';,'';
const throw = appError;
    }
    const data = await response.json();
return {data: data.data || data}status: response.status,;
statusText: response.statusText,;
success: true,;
const message = data.message;
}
      timestamp,}
      requestId};
  }
  // 映射HTTP状态码到错误代码/;,/g/;
private mapStatusToErrorCode(status: number): string {switch (status) {}      case 400: return ERROR_CODES.VALIDATION_ERROR;
case 401: return ERROR_CODES.UNAUTHORIZED;
case 403: return ERROR_CODES.FORBIDDEN;
case 404: return ERROR_CODES.NOT_FOUND;
case 408: return ERROR_CODES.TIMEOUT;
case 500: return ERROR_CODES.SERVER_ERROR;
case 502: return ERROR_CODES.GATEWAY_ERROR;
case 503: return ERROR_CODES.SERVICE_UNAVAILABLE,;
}
  const default = return ERROR_CODES.OPERATION_FAILED;}
    }
  }
  // 重试机制/;,/g/;
private async withRetry<T>();
operation: () => Promise<T>,;
retries: number = GATEWAY_PERFORMANCE_CONFIG.RETRY_ATTEMPTS;
  ): Promise<T> {const let = lastError: Error;,}for (let attempt = 1; attempt <= retries; attempt++) {try {}}
        return await operation();}
      } catch (error) {lastError = error as Error;}                // 如果是认证错误，尝试刷新令牌/;,/g/;
if (error as GatewayError).code === ERROR_CODES.UNAUTHORIZED && attempt === 1) {try {}            const await = this.refreshToken();
}
            continue; // 重试当前请求}/;/g/;
          } catch {}}
            // 刷新失败，继续重试逻辑}/;/g/;
          }
        }
                // 最后一次尝试，抛出错误/;,/g/;
if (attempt === retries) {this.circuitBreaker.recordFailure();}}
          const throw = lastError;}
        }
                // 等待后重试/;,/g/;
const await = this.sleep(GATEWAY_PERFORMANCE_CONFIG.RETRY_DELAY * attempt);
      }
    }
        const throw = lastError!;
  }
  // 睡眠函数/;,/g/;
private sleep(ms: number): Promise<void> {}}
    return new Promise(resolve => setTimeout(resolve, ms));}
  }
  // 刷新令牌/;,/g/;
private async refreshToken(): Promise<void> {const refreshToken = this.tokenManager.getRefreshToken();';,}if (!refreshToken) {';}}'';
      const throw = new Error('No refresh token available');'}'';'';
    }';,'';
const: response = await fetch(`${this.baseURL}/api/v1/gateway/auth-service/auth/refresh`, {/`;)``'`;,}method: "POST";",")";"/g"/`;
}
      const headers = {)"}"";"";
        'Content-Type': 'application/json';},')''/;,'/g'/;
const body = JSON.stringify({ refresh_token: refreshToken ;})});
if (!response.ok) {';,}this.tokenManager.clearTokens();';'';
}
      const throw = new Error('Token refresh failed');'}'';'';
    }
    const data = await response.json();
this.tokenManager.setTokens();
data.access_token,;
data.refresh_token || refreshToken,;
data.expires_in || 3600;
    );
  }';'';
  // GET请求'/;,'/g,'/;
  async: get<T = any>(service: string, endpoint: string = ', config: RequestConfig = {;}): Promise<ApiResponse<T>> {'';,}const startTime = Date.now();';,'';
url: this.buildUrl(service, endpoint);';,'';
cacheKey: this.generateCacheKey('GET', url);';'';
        // 检查离线缓存/;,/g/;
if (GATEWAY_FEATURES.ENABLE_OFFLINE) {cachedData: getCachedData(service, endpoint);,}if (cachedData) {performanceMonitor.recordApiCall(Date.now() - startTime, true);,}return {data: cachedData,';,}status: 200,';,'';
statusText: 'OK (Cached)';','';
success: true,';,'';
message: 'Data from offline cache';','';'';
}
          timestamp: new Date().toISOString(),}
          const requestId = this.generateRequestId();};
      }
    }
        // 检查内存缓存/;,/g/;
if (config.cache !== false && GATEWAY_FEATURES.ENABLE_CACHING) {const cached = this.cacheManager.get(cacheKey);,}if (cached) {}}
        return cached;}
      }
    }
    // 检查熔断器/;,/g/;
if (GATEWAY_FEATURES.ENABLE_CIRCUIT_BREAKER && !this.circuitBreaker.canExecute()) {// 如果熔断器开启，尝试返回缓存数据/;,}if (GATEWAY_FEATURES.ENABLE_OFFLINE) {cachedData: getCachedData(service, endpoint);,}if (cachedData) {return {}            data: cachedData,';,'/g,'/;
  status: 200,';,'';
statusText: 'OK (Circuit Breaker Fallback)';','';
success: true,';,'';
message: 'Data from cache due to circuit breaker';','';'';
}
            timestamp: new Date().toISOString(),}
            const requestId = this.generateRequestId();};
        }
      }';,'';
const  error = errorHandler.handleError()';,'';
new: Error('Circuit breaker is open'),';,'';
service;
      );
const throw = error;
    }
    try {const return = await this.withRetry(async () => {';,}const headers = await this.prepareHeaders(config);';,'';
const requestId = headers['X-Request-ID'];';,'';
const: response = await fetch(url, {')'';,}const method = 'GET';')'';'';
}
          headers,)}
          const signal = config.signal || AbortSignal.timeout(config.timeout || this.defaultTimeout);});
result: await this.handleResponse<T>(response, requestId);
                // 缓存成功响应到内存/;,/g/;
if (config.cache !== false && GATEWAY_FEATURES.ENABLE_CACHING) {}}
          this.cacheManager.set(cacheKey, result);}
        }
                // 缓存到离线存储/;,/g/;
if (GATEWAY_FEATURES.ENABLE_OFFLINE) {}}
          await: cacheData(service, endpoint, result.data);}
        }
                this.circuitBreaker.recordSuccess();
performanceMonitor.recordApiCall(Date.now() - startTime, true);
return result;
      }, config.retries);
    } catch (error) {// 如果请求失败，尝试返回缓存数据/;,}if (GATEWAY_FEATURES.ENABLE_OFFLINE) {cachedData: getCachedData(service, endpoint);}}/g/;
        if (cachedData) {}
          console.warn(`Request failed, returning cached data for ${service}${endpoint}`);````;,```;
return {data: cachedData,';,}status: 200,';,'';
statusText: 'OK (Error Fallback)';','';
success: true,';,'';
message: 'Data from cache due to request failure';','';'';
}
            timestamp: new Date().toISOString(),}
            const requestId = this.generateRequestId();};
        }
      }
            performanceMonitor.recordApiCall(Date.now() - startTime, false);
const throw = error;
    }
  }';'';
  // POST请求'/;,'/g,'/;
  async: post<T = any>(service: string, endpoint: string = ', data?: any; config: RequestConfig = {;}): Promise<ApiResponse<T>> {'';,}url: this.buildUrl(service, endpoint);'';
    // 检查熔断器/;,/g/;
if (GATEWAY_FEATURES.ENABLE_CIRCUIT_BREAKER && !this.circuitBreaker.canExecute()) {// 如果启用离线模式，将操作添加到队列/;,}if (GATEWAY_FEATURES.ENABLE_OFFLINE) {';,}const await = addOfflineOperation({';,)const type = 'CREATE';';,}service,;,'/g'/;
endpoint,);
data,)';'';
}
          maxRetries: 3,)'}'';
const priority = 'medium';});';,'';
return {'}'';
data: { queued: true, message: 'Operation queued for later execution' ;} as T,';,'';
status: 202,';,'';
statusText: 'Accepted (Queued)';','';
success: true,';,'';
message: 'Operation added to offline queue';','';
timestamp: new Date().toISOString(),;
const requestId = this.generateRequestId();};
      }';,'';
const  error = errorHandler.handleError()';,'';
new: Error('Circuit breaker is open'),';,'';
service;
      );
const throw = error;
    }
    try {const return = await this.withRetry(async () => {';,}const headers = await this.prepareHeaders(config);';,'';
const requestId = headers['X-Request-ID'];';,'';
const: response = await fetch(url, {')'';,}const method = 'POST';')'';
headers,);
}
          body: data ? JSON.stringify(data) : undefined,}
          const signal = config.signal || AbortSignal.timeout(config.timeout || this.defaultTimeout);});
result: await this.handleResponse<T>(response, requestId);
this.circuitBreaker.recordSuccess();
return result;
      }, config.retries);
    } catch (error) {// 如果请求失败且启用离线模式，将操作添加到队列/;,}if (GATEWAY_FEATURES.ENABLE_OFFLINE && !config.skipAuth) {';,}const await = addOfflineOperation({';,)const type = 'CREATE';';,}service,;,'/g'/;
endpoint,);
data,)';'';
}
          maxRetries: 3,)'}'';
const priority = 'medium';});';,'';
return {'}'';
data: { queued: true, message: 'Operation queued due to network failure' ;} as T,';,'';
status: 202,';,'';
statusText: 'Accepted (Queued)';','';
success: true,';,'';
message: 'Operation added to offline queue due to failure';','';
timestamp: new Date().toISOString(),;
const requestId = this.generateRequestId();};
      }
            const throw = error;
    }
  }';'';
  // PUT请求'/;,'/g,'/;
  async: put<T = any>(service: string, endpoint: string = ', data?: any; config: RequestConfig = {;}): Promise<ApiResponse<T>> {'';,}url: this.buildUrl(service, endpoint);,'';
const return = this.withRetry(async () => {';,}const headers = await this.prepareHeaders(config);';,'';
const requestId = headers['X-Request-ID'];';,'';
const: response = await fetch(url, {')'';,}const method = 'PUT';')'';
headers,);
}
        body: data ? JSON.stringify(data) : undefined,}
        const signal = config.signal || AbortSignal.timeout(config.timeout || this.defaultTimeout);});
result: await this.handleResponse<T>(response, requestId);
this.circuitBreaker.recordSuccess();
return result;
    }, config.retries);
  }';'';
  // DELETE请求'/;,'/g,'/;
  async: delete<T = any>(service: string, endpoint: string = ', config: RequestConfig = {;}): Promise<ApiResponse<T>> {'';,}url: this.buildUrl(service, endpoint);,'';
const return = this.withRetry(async () => {';,}const headers = await this.prepareHeaders(config);';,'';
const requestId = headers['X-Request-ID'];';,'';
const: response = await fetch(url, {')'';,}const method = 'DELETE';')'';'';
}
        headers,)}
        const signal = config.signal || AbortSignal.timeout(config.timeout || this.defaultTimeout);});
result: await this.handleResponse<T>(response, requestId);
this.circuitBreaker.recordSuccess();
return result;
    }, config.retries);
  }
  // 认证相关方法'/;,'/g'/;
const async = login(credentials: { email: string; password: string ;}): Promise<ApiResponse<any>> {'}'';
result: await this.post("AUTH",/auth/login', credentials, { skipAuth: true ;});''/;,'/g'/;
if (result.success && result.data.access_token) {this.tokenManager.setTokens();,}result.data.access_token,;
result.data.refresh_token,;
result.data.expires_in || 3600;
}
      );}
    }
        return result;
  }
  const async = logout(): Promise<ApiResponse<any>> {';,}try {';,}result: await this.post("AUTH",/auth/logout');''/;'/g'/;
}
      return result;}
    } finally {this.tokenManager.clearTokens();}}
      this.cacheManager.clear();}
    }
  }
  // 服务发现'/;,'/g'/;
const async = getServices(): Promise<ApiResponse<ServiceStatus[]>> {'}'';
return this.get("",/services', { cache: false ;});''/;'/g'/;
  }';,'';
const async = getServiceHealth(service: string): Promise<ApiResponse<ServiceStatus>> {'}'';
return this.get(', `/services/${service;}/health`, { cache: false ;});``''/`;`/g`/`;
  }
  // 缓存管理/;,/g/;
clearCache(): void {}}
    this.cacheManager.clear();}
  }
  getCacheStats(): { size: number ;} {}
    return { size: this.cacheManager.size() ;};
  }
  // 获取熔断器状态/;,/g/;
getCircuitBreakerState(): string {}}
    return this.circuitBreaker.getState();}
  }
  // 健康检查/;,/g/;
const async = healthCheck(): Promise<boolean> {}}
    try {}';,'';
const: response = await fetch(`${this.baseURL}/health`, {/`;)``)'`;}}`/g,`/`;
  method: "GET";",)"}";
const signal = AbortSignal.timeout(5000);});
return response.ok;
    } catch {}}
      return false;}
    }
  }
}
// 导出单例实例/;,/g/;
export const apiClient = new GatewayApiClient();
// 向后兼容的旧API客户端类/;,/g/;
export class ApiClient {";,}const async = get<T = any>(url: string): Promise<ApiResponse<T>> {";,}console.warn('ApiClient.get is deprecated. Use GatewayApiClient instead.');';'';
}
}
    return apiClient.get(', url);'}'';'';
  }';,'';
async: post<T = any>(url: string, body?: any): Promise<ApiResponse<T>> {';,}console.warn('ApiClient.post is deprecated. Use GatewayApiClient instead.');';'';
}
    return apiClient.post(', url, body);'}'';'';
  }';'';
};