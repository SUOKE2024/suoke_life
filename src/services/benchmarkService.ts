import { apiClient } from './apiClient';
import { getCurrentEnvConfig } from '../constants/config';
// 基准测试配置接口
export interface BenchmarkConfig {
  benchmark_id: string;
  model_id: string;
  model_version: string;
  test_data: any[];
  config?: Record<string, any>;
}
// 基准测试任务接口
export interface BenchmarkTask {
  task_id: string;
  benchmark_id: string;
  model_id: string;
  model_version: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  results?: BenchmarkResult;
  error_message?: string;
}
// 基准测试结果接口
export interface BenchmarkResult {
  task_id: string;
  benchmark_id: string;
  model_id: string;
  model_version: string;
  metrics: Record<string, number>;
  predictions: ModelPrediction[];
  execution_time: number;
  timestamp: string;
  metadata: Record<string, any>;
}
// 模型预测接口
export interface ModelPrediction {
  input_data: any;
  prediction: any;
  confidence?: number;
  processing_time: number;
}
// 模型配置接口
export interface ModelConfig {
  model_id: string;
  model_version: string;
  model_type: string;
  description?: string;
  metadata?: Record<string, any>;
}
// 插件接口
export interface Plugin {
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  enabled: boolean;
}
// 基准测试状态接口
export interface BenchmarkStatus {
  task_id: string;
  status: string;
  progress: number;
  current_step?: string;
  estimated_remaining_time?: number;
  error_message?: string;
}
// 服务健康状态接口
export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  version: string;
  uptime: number;
  system_info: {;
    cpu_usage: number;
  memory_usage: number;
    disk_usage: number;
};
}
/**
* SuokeBench 服务客户端
*/
export class BenchmarkService {
  private baseUrl: string;
  constructor() {
    const envConfig = getCurrentEnvConfig();
    this.baseUrl = envConfig.API_BASE_URL || 'http://localhost:8000';
  }
  /**
  * 提交基准测试任务
  */
  async submitBenchmark(config: BenchmarkConfig): Promise<string> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/api/v1/benchmarks`, config);
      return response.data.task_id;
    } catch (error) {
      console.error('Failed to submit benchmark:', error);
      throw new Error('提交基准测试失败');
    }
  }
  /**
  * 获取基准测试状态
  */
  async getBenchmarkStatus(taskId: string): Promise<BenchmarkStatus> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/api/v1/benchmarks/${taskId}/status`);
      return response.data;
    } catch (error) {
      console.error('Failed to get benchmark status:', error);
      throw new Error('获取测试状态失败');
    }
  }
  /**
  * 获取基准测试结果
  */
  async getBenchmarkResult(taskId: string): Promise<BenchmarkResult> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/api/v1/benchmarks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get benchmark result:', error);
      throw new Error('获取测试结果失败');
    }
  }
  /**
  * 列出所有基准测试任务
  */
  async listBenchmarks(status?: string): Promise<BenchmarkTask[]> {
    try {
      const url = status;
        ? `${this.baseUrl}/api/v1/benchmarks?status=${status}`;
        : `${this.baseUrl}/api/v1/benchmarks`;
      const response = await apiClient.get(url);
      return response.data.tasks || [];
    } catch (error) {
      console.error('Failed to list benchmarks:', error);
      throw new Error('获取测试列表失败');
    }
  }
  /**
  * 注册模型
  */
  async registerModel(model: ModelConfig): Promise<string> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/api/v1/models/register`, model);
      return response.data.model_id;
    } catch (error) {
      console.error('Failed to register model:', error);
      throw new Error('注册模型失败');
    }
  }
  /**
  * 模型预测
  */
  async predictWithModel(modelId: string, data: any): Promise<ModelPrediction> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/api/v1/models/${modelId}/predict`, {input_data: data;
      });
      return response.data;
    } catch (error) {
      console.error('Failed to predict with model:', error);
      throw new Error('模型预测失败');
    }
  }
  /**
  * 列出可用插件
  */
  async listPlugins(): Promise<Plugin[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/api/v1/plugins`);
      return response.data.plugins || [];
    } catch (error) {
      console.error('Failed to list plugins:', error);
      throw new Error('获取插件列表失败');
    }
  }
  /**
  * 运行插件基准测试
  */
  async runPluginBenchmark(pluginName: string, config: any): Promise<string> {
    try {
      const response = await apiClient.post(;
        `${this.baseUrl}/api/v1/plugins/${pluginName}/benchmark`,config;
      );
      return response.data.task_id;
    } catch (error) {
      console.error('Failed to run plugin benchmark:', error);
      throw new Error('运行插件测试失败');
    }
  }
  /**
  * 获取服务健康状态
  */
  async getHealthStatus(): Promise<HealthStatus> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('Failed to get health status:', error);
      throw new Error('获取服务状态失败');
    }
  }
  /**
  * 取消基准测试任务
  */
  async cancelBenchmark(taskId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/benchmarks/${taskId}`, {
      method: "DELETE",
      headers: {'Content-Type': 'application/json';
        };
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to cancel benchmark:', error);
      throw new Error('取消测试失败');
    }
  }
  /**
  * 获取基准测试日志
  */
  async getBenchmarkLogs(taskId: string): Promise<string[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/api/v1/benchmarks/${taskId}/logs`);
      return response.data.logs || [];
    } catch (error) {
      console.error('Failed to get benchmark logs:', error);
      throw new Error('获取测试日志失败');
    }
  }
  /**
  * 生成基准测试报告
  */
  async generateReport(taskId: string, format: 'html' | 'json' = 'html'): Promise<string> {
    try {
      const url = `${this.baseUrl}/api/v1/benchmarks/${taskId}/report?format=${format}`;
      const response = await apiClient.get(url);
      return response.data.report_url || response.data.report;
    } catch (error) {
      console.error('Failed to generate report:', error);
      throw new Error('生成报告失败');
    }
  }
}
// 创建单例实例
export const benchmarkService = new BenchmarkService();
// 类型已在上面定义并导出，无需重复导出