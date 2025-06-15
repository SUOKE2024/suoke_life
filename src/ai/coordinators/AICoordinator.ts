/**
 * AI协调器
 * 管理多个AI服务的协调工作
 */

import { getModelConfig, getRecommendedModels, mergeConfig } from '../config/AIConfig';
import { AIModel, AIPerformance, AIRetry } from '../decorators/AIDecorators';
import LLMService from '../services/LLMService';
import type {
    AIRequest,
    AIResponse,
    HealthAnalysisRequest,
    HealthAnalysisResponse,
    IAIService
} from '../types/AITypes';
import { AITaskType, LLMModelType } from '../types/AITypes';

@AIModel(LLMModelType.GPT4O)
export default class AICoordinator {
  private services: Map<string, IAIService> = new Map();
  private loadBalancer: Map<AITaskType, LLMModelType[]> = new Map();
  private healthChecker: NodeJS.Timeout | null = null;
  private initialized = false;

  constructor() {
    this.initializeServices();
    this.setupLoadBalancer();
  }

  private initializeServices(): void {
    // 初始化LLM服务
    this.services.set('llm', new LLMService());
    
    // 这里可以添加其他AI服务
    // this.services.set('transformers', new TransformersService());
    // this.services.set('onnx', new ONNXService());
    // this.services.set('mlkit', new MLKitService());
  }

  private setupLoadBalancer(): void {
    // 为不同任务类型设置负载均衡
    Object.values(AITaskType).forEach(taskType => {
      const recommendedModels = getRecommendedModels(taskType);
      this.loadBalancer.set(taskType, recommendedModels);
    });
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    // 初始化所有服务
    const initPromises = Array.from(this.services.values()).map(service => 
      service.initialize()
    );

    await Promise.all(initPromises);

    // 启动健康检查
    this.startHealthCheck();

    this.initialized = true;
  }

  private startHealthCheck(): void {
    this.healthChecker = setInterval(async () => {
      await this.performHealthCheck();
    }, 60000); // 每分钟检查一次
  }

  private async performHealthCheck(): Promise<void> {
    const healthPromises = Array.from(this.services.entries()).map(
      async ([name, service]) => {
        try {
          // 简单的健康检查请求
          const testRequest: AIRequest = {
            taskType: AITaskType.TEXT_GENERATION,
            input: 'health check',
            modelConfig: { maxTokens: 5 }
          };
          
          await service.process(testRequest);
          return { name, healthy: true };
        } catch (error) {
          console.warn(`Service ${name} health check failed:`, error);
          return { name, healthy: false };
        }
      }
    );

    const results = await Promise.all(healthPromises);
    const unhealthyServices = results.filter(r => !r.healthy);
    
    if (unhealthyServices.length > 0) {
      console.warn('Unhealthy AI services:', unhealthyServices.map(s => s.name));
    }
  }

  @AIPerformance()
  @AIRetry(3)
  async process(request: AIRequest): Promise<AIResponse> {
    if (!this.initialized) {
      await this.initialize();
    }

    // 选择最佳服务和模型
    const { service, modelType } = await this.selectBestService(request);
    
    // 更新请求配置
    const optimizedRequest = this.optimizeRequest(request, modelType);
    
    try {
      return await service.process(optimizedRequest);
    } catch (error) {
      // 如果主要服务失败，尝试备用服务
      return await this.handleFailover(request, error as Error);
    }
  }

  private async selectBestService(request: AIRequest): Promise<{
    service: IAIService;
    modelType: LLMModelType;
  }> {
    const taskType = request.taskType;
    const availableModels = this.loadBalancer.get(taskType) || [];
    
    // 选择第一个可用的模型（可以扩展为更智能的选择逻辑）
    const modelType = request.modelConfig?.modelType || availableModels[0] || LLMModelType.GPT4O;
    
    // 目前主要使用LLM服务，后续可以根据任务类型选择不同服务
    const service = this.services.get('llm')!;
    
    return { service, modelType };
  }

  private optimizeRequest(request: AIRequest, modelType: LLMModelType): AIRequest {
    const baseConfig = getModelConfig(modelType);
    const optimizedConfig = mergeConfig(baseConfig, request.modelConfig || {});
    
    return {
      ...request,
      modelConfig: optimizedConfig
    };
  }

  private async handleFailover(request: AIRequest, error: Error): Promise<AIResponse> {
    const taskType = request.taskType;
    const availableModels = this.loadBalancer.get(taskType) || [];
    
    // 尝试备用模型
    for (let i = 1; i < availableModels.length; i++) {
      try {
        const fallbackModel = availableModels[i];
        const fallbackRequest = {
          ...request,
          modelConfig: {
            ...request.modelConfig,
            modelType: fallbackModel
          }
        };
        
        const service = this.services.get('llm')!;
        return await service.process(fallbackRequest);
      } catch (fallbackError) {
        console.warn(`Fallback model ${availableModels[i]} also failed:`, fallbackError);
      }
    }
    
    // 所有备用方案都失败了
    return {
      success: false,
      error: `All AI services failed. Original error: ${error.message}`,
      metadata: {
        modelUsed: request.modelConfig?.modelType || LLMModelType.GPT4O,
        processingTime: 0
      }
    };
  }

  /**
   * 智能健康分析
   * 结合多个AI服务提供综合分析
   */
  @AIPerformance()
  async analyzeHealthIntelligently(request: HealthAnalysisRequest): Promise<HealthAnalysisResponse> {
    const llmService = this.services.get('llm') as LLMService;
    
    if (!llmService || !('analyzeHealth' in llmService)) {
      throw new Error('LLM service not available for health analysis');
    }

    // 使用最适合健康分析的模型
    const healthRequest: HealthAnalysisRequest = {
      ...request,
      modelConfig: {
        modelType: LLMModelType.GPT4O,
        temperature: 0.3,
        maxTokens: 2000,
        ...request.modelConfig
      }
    };

    return await llmService.analyzeHealth(healthRequest);
  }

  /**
   * 批量处理AI请求
   */
  async processBatch(requests: AIRequest[]): Promise<AIResponse[]> {
    const batchPromises = requests.map(request => this.process(request));
    return await Promise.all(batchPromises);
  }

  /**
   * 获取服务状态
   */
  getServiceStatus(): Record<string, boolean> {
    const status: Record<string, boolean> = {};
    
    this.services.forEach((service, name) => {
      // 简单的状态检查，实际应该有更复杂的逻辑
      status[name] = true;
    });
    
    return status;
  }

  /**
   * 获取负载均衡信息
   */
  getLoadBalancerInfo(): Record<string, LLMModelType[]> {
    const info: Record<string, LLMModelType[]> = {};
    
    this.loadBalancer.forEach((models, taskType) => {
      info[taskType] = [...models];
    });
    
    return info;
  }

  /**
   * 动态调整负载均衡
   */
  updateLoadBalancer(taskType: AITaskType, models: LLMModelType[]): void {
    this.loadBalancer.set(taskType, models);
  }

  /**
   * 清理资源
   */
  async dispose(): Promise<void> {
    // 停止健康检查
    if (this.healthChecker) {
      clearInterval(this.healthChecker);
      this.healthChecker = null;
    }

    // 清理所有服务
    const disposePromises = Array.from(this.services.values()).map(service => 
      service.dispose()
    );

    await Promise.all(disposePromises);

    this.services.clear();
    this.loadBalancer.clear();
    this.initialized = false;
  }
} 