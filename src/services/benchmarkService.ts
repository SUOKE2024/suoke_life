import { apiClient } from "./apiClient";""/;,"/g"/;
import { getCurrentEnvConfig } from "../constants/config";""/;"/g"/;
// 基准测试配置接口/;,/g/;
export interface BenchmarkConfig {benchmark_id: string}model_id: string,;
model_version: string,;
const test_data = any[];
}
}
  config?: Record<string; any>;}
}
// 基准测试任务接口/;,/g/;
export interface BenchmarkTask {task_id: string}benchmark_id: string,;
model_id: string,";,"";
model_version: string,';,'';
status: 'pending' | 'running' | 'completed' | 'failed';','';
progress: number,;
const created_at = string;
results?: BenchmarkResult;
}
}
  error_message?: string;}
}
// 基准测试结果接口/;,/g/;
export interface BenchmarkResult {task_id: string}benchmark_id: string,;
model_id: string,;
model_version: string,;
metrics: Record<string, number>;
predictions: ModelPrediction[],;
execution_time: number,;
timestamp: string,;
}
}
  metadata: Record<string, any>;}
}
// 模型预测接口/;,/g/;
export interface ModelPrediction {input_data: any}const prediction = any;
confidence?: number;
}
}
  const processing_time = number;}
}
// 模型配置接口/;,/g/;
export interface ModelConfig {model_id: string}model_version: string,;
const model_type = string;
description?: string;
}
}
  metadata?: Record<string; any>;}
}
// 插件接口/;,/g/;
export interface Plugin {name: string}version: string,;
description: string,;
author: string,;
category: string,;
}
}
  const enabled = boolean;}
}
// 基准测试状态接口/;,/g/;
export interface BenchmarkStatus {task_id: string}status: string,;
const progress = number;
current_step?: string;
estimated_remaining_time?: number;
}
}
  error_message?: string;}
}
// 服务健康状态接口'/;,'/g'/;
export interface HealthStatus {';,}status: 'healthy' | 'unhealthy';','';
version: string,;
uptime: number,;
system_info: {cpu_usage: number,;
memory_usage: number,;
}
}
  const disk_usage = number;}
};
}
/* 端 *//;/g/;
*//;,/g/;
export class BenchmarkService {;,}private baseUrl: string;
constructor() {';,}const envConfig = getCurrentEnvConfig();';'';
}
}
    this.baseUrl = envConfig.API_BASE_URL || 'http: //localhost:8000';'}''/;'/g'/;
  }
  /* 务 *//;/g/;
  *//;,/g/;
const async = submitBenchmark(config: BenchmarkConfig): Promise<string> {}}
    try {}
      response: await apiClient.post(`${this.baseUrl;}/api/v1/benchmarks`, config);```/`;,`/g`/`;
return response.data.task_id;';'';
    } catch (error) {';,}console.error('Failed to submit benchmark:', error);';'';
}
}
    }
  }
  /* 态 *//;/g/;
  *//;,/g/;
const async = getBenchmarkStatus(taskId: string): Promise<BenchmarkStatus> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/api/v1/benchmarks/${taskId}/status`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get benchmark status:', error);';'';
}
}
    }
  }
  /* 果 *//;/g/;
  *//;,/g/;
const async = getBenchmarkResult(taskId: string): Promise<BenchmarkResult> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/api/v1/benchmarks/${taskId}`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get benchmark result:', error);';'';
}
}
    }
  }
  /* 务 *//;/g/;
  *//;,/g/;
const async = listBenchmarks(status?: string): Promise<BenchmarkTask[]> {try {}}
      const url = status;}
        ? `${this.baseUrl}/api/v1/benchmarks?status=${status}`;```/`;`/g`/`;
        : `${this.baseUrl}/api/v1/benchmarks`;```/`;,`/g`/`;
const response = await apiClient.get(url);
return response.data.tasks || [];';'';
    } catch (error) {';,}console.error('Failed to list benchmarks:', error);';'';
}
}
    }
  }
  /* 型 *//;/g/;
  *//;,/g/;
const async = registerModel(model: ModelConfig): Promise<string> {}}
    try {}
      response: await apiClient.post(`${this.baseUrl;}/api/v1/models/register`, model);```/`;,`/g`/`;
return response.data.model_id;';'';
    } catch (error) {';,}console.error('Failed to register model:', error);';'';
}
}
    }
  }
  /* 测 *//;/g/;
  *//;,/g,/;
  async: predictWithModel(modelId: string, data: any): Promise<ModelPrediction> {}}
    try {}
      response: await apiClient.post(`${this.baseUrl;}/api/v1/models/${modelId}/predict`, {input_data: data;)``}``/`;`/g`/`;
      });
return response.data;';'';
    } catch (error) {';,}console.error('Failed to predict with model:', error);';'';
}
}
    }
  }
  /* 件 *//;/g/;
  *//;,/g/;
const async = listPlugins(): Promise<Plugin[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/api/v1/plugins`);```/`;,`/g`/`;
return response.data.plugins || [];';'';
    } catch (error) {';,}console.error('Failed to list plugins:', error);';'';
}
}
    }
  }
  /* 试 *//;/g/;
  *//;,/g,/;
  async: runPluginBenchmark(pluginName: string, config: any): Promise<string> {try {}}
      const response = await apiClient.post(;)}
        `${this.baseUrl}/api/v1/plugins/${pluginName}/benchmark`,config;```/`;`/g`/`;
      );
return response.data.task_id;';'';
    } catch (error) {';,}console.error('Failed to run plugin benchmark:', error);';'';
}
}
    }
  }
  /* 态 *//;/g/;
  *//;,/g/;
const async = getHealthStatus(): Promise<HealthStatus> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/health`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get health status:', error);';'';
}
}
    }
  }
  /* 务 *//;/g/;
  *//;,/g/;
const async = cancelBenchmark(taskId: string): Promise<void> {}}
    try {}';,'';
response: await fetch(`${this.baseUrl;}/api/v1/benchmarks/${taskId}`, {/`;)``'`;,}method: "DELETE";",")";"/g"/`;
}
      const headers = {'Content-Type': 'application/json';')}''/;'/g'/;
        };);
      });
if (!response.ok) {}
        const throw = new Error(`HTTP ${response.status}: ${response.statusText}`);````;```;
      }';'';
    } catch (error) {';,}console.error('Failed to cancel benchmark:', error);';'';
}
}
    }
  }
  /* 志 *//;/g/;
  *//;,/g/;
const async = getBenchmarkLogs(taskId: string): Promise<string[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/api/v1/benchmarks/${taskId}/logs`);```/`;,`/g`/`;
return response.data.logs || [];';'';
    } catch (error) {';,}console.error('Failed to get benchmark logs:', error);';'';
}
}
    }
  }
  /* ' *//;'/g'/;
  */'/;,'/g,'/;
  async: generateReport(taskId: string, format: 'html' | 'json' = 'html'): Promise<string> {';}}'';
    try {}
      const url = `${this.baseUrl;}/api/v1/benchmarks/${taskId}/report?format=${format}`;```/`;,`/g`/`;
const response = await apiClient.get(url);
return response.data.report_url || response.data.report;';'';
    } catch (error) {';,}console.error('Failed to generate report:', error);';'';
}
}
    }
  }
}
// 创建单例实例/;,/g/;
export const benchmarkService = new BenchmarkService();';'';
// 类型已在上面定义并导出，无需重复导出'/'/g'/;