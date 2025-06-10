

import React from "react";";
interface ApiResponse<T = any  /> {/;,}data: T,;,/g/;
const success = boolean;
}
  message?: string;}
  code?: number}
// 请求配置接口 * interface RequestConfig {/;,}headers?: Record<string; string>;,/g/;
timeout?: number;
}
}
  requireAuth?: boolean;}";"";
}";"";
// HTTP方法类型 * type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATC;H";"/;,"/g"/;
class ApiClient {private baseURL: string;,}private defaultTimeout: number;
constructor() {this.baseURL = API_CONFIG.BASE_URL;}}
}
    this.defaultTimeout = API_CONFIG.TIMEOUT;}
  }
  // 获取存储的认证令牌  private async getAuthToken(): Promise<string | null> {/;,}try {}}/g/;
      return await webStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);}
    } catch (error) {}}
      return null;}
    }
  }
  // 设置认证令牌  async setAuthToken(token: string): Promise<void>  {/;,}try {}}/g,/;
  await: webStorage.setItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN, token);}
    } catch (error) {}
      }
  }
  // 移除认证令牌  async removeAuthToken(): Promise<void> {/;,}try {}}/g/;
      const await = webStorage.removeItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);}
    } catch (error) {}
      }
  }
  // 构建请求头  private async buildHeaders(config?: RequestConfig;)/;/g/;
  ): Promise<Record<string, string >>  {";,}const: headers: Record<string, string> = {";}      "Content-Type": "application/json","/;,"/g"/;
const Accept = "application/json";"/;"/g"/;
}
      ...config?.headers;}
    }
    if (config?.requireAuth !== false) {const token = await this.getAuthToken();}}
      if (token) {}
        headers.Authorization = `Bearer ${token}`;````;```;
      }
    }
    return headers;
  }
  // 发送HTTP请求  private async request<T = any  />()/;,/g,/;
  method: HttpMethod,;
const endpoint = string;
data?: unknown;
config?: RequestConfig;
  ): Promise<ApiResponse<T>>  {}}
    try {}
      const url = `${this.baseURL}${endpoint};`;````;,```;
const headers = await this.buildHeaders(config);
const timeout = config?.timeout || this.defaultTimeout;
const controller = new AbortController;
timeoutId: setTimeout() => controller.abort(), timeout);
const  requestOptions: RequestInit = {";}  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(apiClient.web", {")";,}trackRender: true,;"";
}
    trackMemory: false,}
    warnThreshold: 100, // ms ;};);/;,/g/;
method,;
headers,;
const signal = controller.signal;";"";
      }";,"";
if (data && ["POST",PUT", "PATCH"].includes(method)) {"";}}"";
        requestOptions.body = JSON.stringify(data);}
      }
      response: await fetch(url, requestOptions);
clearTimeout(timeoutId);
const responseData = await response.json();
if (!response.ok) {}
        return {success: false,data: undefined,error: {code: response.status.toString(),message: responseData.message || `HTTP ${response.status;}`,details: responseData.details;};````;```;
        };
      }
      return {success: true,data: responseData.data || responseData,error: undefined;}
      };
    } catch (error: unknown) {";,}let errorCode = ERROR_CODES.NETWORK_ERR;";,"";
if (error.name === "AbortError") {";}}"";
        errorCode = ERROR_CODES.TIMEOUT;}
      } else if (error.message) {}}
        errorMessage = error.message;}
      }
      return {success: false,data: undefined,error: {code: errorCode,message: errorMessage,details: error.stack;};
      };
    }
  }
  // GET请求  async get<T = any  />()/;,/g/;
const endpoint = string;
config?: RequestConfig;";"";
  ): Promise<ApiResponse<T>>  {";}}"";
    return this.request<T>("GET", endpoint, undefined, config);"}"";"";
  }
  // POST请求  async post<T = any  />()/;,/g/;
const endpoint = string;
data?: unknown;
config?: RequestConfig;";"";
  ): Promise<ApiResponse<T>>  {";}}"";
    return this.request<T>("POST", endpoint, data, config);"}"";"";
  }
  // PUT请求  async put<T = any  />()/;,/g/;
const endpoint = string;
data?: unknown;
config?: RequestConfig;";"";
  ): Promise<ApiResponse<T>>  {";}}"";
    return this.request<T>("PUT", endpoint, data, config);"}"";"";
  }
  // DELETE请求  async delete<T = any  />()/;,/g/;
const endpoint = string;
config?: RequestConfig;";"";
  ): Promise<ApiResponse<T>>  {";}}"";
    return this.request<T>("DELETE", endpoint, undefined, config);"}"";"";
  }
  // PATCH请求  async patch<T = any  />()/;,/g/;
const endpoint = string;
data?: unknown;
config?: RequestConfig;";"";
  ): Promise<ApiResponse<T>>  {";}}"";
    return this.request<T>("PATCH", endpoint, data, config);"}"";"";
  }
  // 上传文件  async uploadFile<T = any  />()/;,/g,/;
  endpoint: string,;
const file = unknown;
config?: RequestConfig;
  ): Promise<ApiResponse<T>>  {}}
    try {}
      const url = `${this.baseURL}${endpoint};`;````;,```;
headers: await this.buildHeaders({...config,headers: { ...config?.headers;)}
        };";"";
      });";,"";
const delete = headers["Content-Type"]";,"";
const formData = new FormData();";,"";
formData.append("file", file);";,"";
response: await fetch(url, {method: "POST",headers,body: formData;)"}"";"";
      });
const responseData = await response.json();
if (!response.ok) {}
        return {success: false,data: undefined,error: {code: response.status.toString(),message: responseData.message || `HTTP ${response.status;}`,details: responseData.details;};````;```;
        };
      }
      return {success: true,data: responseData.data || responseData,error: undefined;}
      };
    } catch (error: unknown) {}}
}
      ;};
    }
  }
}
// 创建单例实例 * export const apiClient = new ApiClient;/;/g/;
// 导出便捷方法 * export const setApiAuthToken = (token: string) => apiClient.setAuthToken(token);"/;,"/g"/;
export const removeApiAuthToken = () => apiClient.removeAuthToken();""";