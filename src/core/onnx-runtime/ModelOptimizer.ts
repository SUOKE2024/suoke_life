import { EventEmitter } from 'events';
import {
  ONNXModel,
  ModelOptimizationOptions,
  OptimizationLevel,
  GraphOptimizationLevel,
  ExecutionMode,
  ONNXError,
  ONNXEvent,
  { PerformanceMetrics } from './types';
import { 
  OPTIMIZATION_LEVELS, 
  ERROR_MESSAGES,
  EVENT_NAMES,
  { PERFORMANCE_BENCHMARKS  } from './constants';
/**
 * 模型优化器 - 优化ONNX模型的性能和内存使用
 * 支持图优化、内存模式优化和执行优化
 */
export class ModelOptimizer extends EventEmitter {
  private isOptimizing: boolean = false;
  private optimizationQueue: OptimizationTask[] = [];
  private optimizationHistory: Map<string, OptimizationResult[]> = new Map();

  constructor() {
    super();
  }

  /**
   * 优化ONNX模型
   */
  async optimizeModel(
    model: ONNXModel,
    options: ModelOptimizationOptions
  ): Promise<ONNXModel> {
    if (this.isOptimizing) {
      throw new Error('优化器正忙，请稍后重试');
    }

    this.isOptimizing = true;
    const startTime = Date.now();

    try {
      console.log(`开始优化模型: ${model.name}`);

      // 验证优化选项
      this.validateOptimizationOptions(options);

      // 创建优化任务
      const task: OptimizationTask = {
        id: `opt_${Date.now()}`,
        model,
        options,
        status: 'pending',
        createdAt: new Date()
      };

      this.optimizationQueue.push(task);

      // 执行优化
      const optimizedModel = await this.executeOptimization(task);

      // 验证优化结果
      const result = await this.validateOptimizationResult(model, optimizedModel, options);

      const duration = Date.now() - startTime;
      console.log(`模型优化完成: ${optimizedModel.name}, 耗时: ${duration}ms`);

      // 记录优化历史
      this.recordOptimizationHistory(model.id, result);

      this.emit(EVENT_NAMES.OPTIMIZATION_COMPLETED, {
        type: 'optimization_completed',
        timestamp: new Date(),
        data: {
          originalModel: model,
          optimizedModel,
          options,
          result,
          duration
        }
      } as ONNXEvent);

      return optimizedModel;

    } catch (error) {
      const onnxError: ONNXError = {
        code: 'OPTIMIZATION_FAILED',
        message: `模型优化失败: ${error.message}`,
        details: error,
        timestamp: new Date(),
        modelId: model.id
      };

      this.emit('error', onnxError);
      throw onnxError;

    } finally {
      this.isOptimizing = false;
      this.optimizationQueue = this.optimizationQueue.filter(t => t.model.id !== model.id);
    }
  }

  /**
   * 批量优化模型
   */
  async optimizeModels(
    models: ONNXModel[],
    options: ModelOptimizationOptions[]
  ): Promise<ONNXModel[]> {
    if (models.length !== options.length) {
      throw new Error('模型数量与优化选项数量不匹配');
    }

    const results: ONNXModel[] = [];
    
    for (let i = 0; i < models.length; i++) {
      try {
        const optimizedModel = await this.optimizeModel(models[i], options[i]);
        results.push(optimizedModel);
      } catch (error) {
        console.error(`模型 ${models[i].name} 优化失败:`, error.message);
        // 继续处理其他模型
      }
    }

    return results;
  }

  /**
   * 获取优化建议
   */
  getOptimizationRecommendation(
    model: ONNXModel,
    targetPerformance: 'speed' | 'memory' | 'balanced'
  ): ModelOptimizationOptions {
    const baseOptions: ModelOptimizationOptions = {
      enableGraphOptimization: true,
      enableMemoryPattern: true,
      enableCPUMemArena: true,
      executionMode: 'parallel',
      graphOptimizationLevel: 'extended',
      enableProfiling: false,
      logSeverityLevel: 'warning'
    };

    // 根据目标性能调整配置
    switch (targetPerformance) {
      case 'speed':
        return {
          ...baseOptions,
          executionMode: 'parallel',
          graphOptimizationLevel: 'all',
          enableMemoryPattern: false, // 可能影响速度
          enableProfiling: false
        };
      
      case 'memory':
        return {
          ...baseOptions,
          executionMode: 'sequential',
          graphOptimizationLevel: 'basic',
          enableMemoryPattern: true,
          enableCPUMemArena: true
        };
      
      case 'balanced':
      default:
        return baseOptions;
    }
  }

  /**
   * 分析模型性能瓶颈
   */
  analyzePerformanceBottlenecks(
    model: ONNXModel,
    metrics: PerformanceMetrics
  ): BottleneckAnalysis {
    const bottlenecks: string[] = [];
    const recommendations: string[] = [];

    // 分析推理时间
    if (metrics.averageInferenceTime > PERFORMANCE_BENCHMARKS.INFERENCE_TIME.POOR) {
      bottlenecks.push('推理时间过长');
      recommendations.push('启用图优化和并行执行');
    }

    // 分析内存使用
    if (metrics.memoryPeakUsage > PERFORMANCE_BENCHMARKS.MEMORY_USAGE.HIGH) {
      bottlenecks.push('内存使用过高');
      recommendations.push('启用内存模式优化和CPU内存池');
    }

    // 分析CPU使用率
    if (metrics.cpuUsage > PERFORMANCE_BENCHMARKS.CPU_USAGE.HIGH) {
      bottlenecks.push('CPU使用率过高');
      recommendations.push('考虑使用GPU执行提供者或降低线程数');
    }

    // 分析热状态
    if (metrics.thermalState && metrics.thermalState !== 'nominal') {
      bottlenecks.push('设备过热');
      recommendations.push('启用功耗优化模式');
    }

    return {
      modelId: model.id,
      bottlenecks,
      recommendations,
      overallScore: this.calculatePerformanceScore(metrics),
      metrics
    };
  }

  /**
   * 获取优化历史
   */
  getOptimizationHistory(modelId: string): OptimizationResult[] {
    return this.optimizationHistory.get(modelId) || [];
  }

  /**
   * 清除优化历史
   */
  clearOptimizationHistory(modelId?: string): void {
    if (modelId) {
      this.optimizationHistory.delete(modelId);
    } else {
      this.optimizationHistory.clear();
    }
  }

  // 私有方法

  private validateOptimizationOptions(options: ModelOptimizationOptions): void {
    if (!options) {
      throw new Error('优化选项不能为空');
    }

    const validGraphLevels: GraphOptimizationLevel[] = ['disabled', 'basic', 'extended', 'all'];
    if (!validGraphLevels.includes(options.graphOptimizationLevel)) {
      throw new Error(`无效的图优化级别: ${options.graphOptimizationLevel}`);
    }

    const validExecutionModes: ExecutionMode[] = ['sequential', 'parallel'];
    if (!validExecutionModes.includes(options.executionMode)) {
      throw new Error(`无效的执行模式: ${options.executionMode}`);
    }
  }

  private async executeOptimization(task: OptimizationTask): Promise<ONNXModel> {
    task.status = 'running';
    
    const { model, options } = task;
    
    try {
      console.log('执行模型优化...');
      
      // 应用图优化
      const graphOptimizedModel = await this.applyGraphOptimization(model, options);
      
      // 应用内存优化
      const memoryOptimizedModel = await this.applyMemoryOptimization(graphOptimizedModel, options);
      
      // 应用执行优化
      const finalOptimizedModel = await this.applyExecutionOptimization(memoryOptimizedModel, options);
      
      task.status = 'completed';
      return finalOptimizedModel;
      
    } catch (error) {
      task.status = 'failed';
      task.error = error.message;
      throw error;
    }
  }

  private async applyGraphOptimization(
    model: ONNXModel,
    options: ModelOptimizationOptions
  ): Promise<ONNXModel> {
    if (!options.enableGraphOptimization) {
      return model;
    }

    console.log(`应用图优化: ${options.graphOptimizationLevel}`);
    
    // 模拟图优化过程
    await this.simulateOptimizationProcess(1000);

    const optimizedModel: ONNXModel = {
      ...model,
      id: `${model.id}_graph_opt`,
      name: `${model.name} (图优化)`,
      metadata: {
        ...model.metadata,
        description: `${model.metadata.description} - 图优化版本`,
        tags: [...model.metadata.tags, 'graph-optimized']
      }
    };

    return optimizedModel;
  }

  private async applyMemoryOptimization(
    model: ONNXModel,
    options: ModelOptimizationOptions
  ): Promise<ONNXModel> {
    if (!options.enableMemoryPattern && !options.enableCPUMemArena) {
      return model;
    }

    console.log('应用内存优化...');
    
    // 模拟内存优化过程
    await this.simulateOptimizationProcess(800);

    const optimizedModel: ONNXModel = {
      ...model,
      id: `${model.id}_mem_opt`,
      name: `${model.name} (内存优化)`,
      metadata: {
        ...model.metadata,
        description: `${model.metadata.description} - 内存优化版本`,
        tags: [...model.metadata.tags, 'memory-optimized']
      }
    };

    return optimizedModel;
  }

  private async applyExecutionOptimization(
    model: ONNXModel,
    options: ModelOptimizationOptions
  ): Promise<ONNXModel> {
    console.log(`应用执行优化: ${options.executionMode}`);
    
    // 模拟执行优化过程
    await this.simulateOptimizationProcess(600);

    const optimizedModel: ONNXModel = {
      ...model,
      id: `${model.id}_exec_opt`,
      name: `${model.name} (执行优化)`,
      metadata: {
        ...model.metadata,
        description: `${model.metadata.description} - 执行优化版本`,
        tags: [...model.metadata.tags, 'execution-optimized']
      }
    };

    return optimizedModel;
  }

  private async validateOptimizationResult(
    originalModel: ONNXModel,
    optimizedModel: ONNXModel,
    options: ModelOptimizationOptions
  ): Promise<OptimizationResult> {
    console.log('验证优化结果...');
    
    // 模拟性能测试
    await this.simulateOptimizationProcess(500);

    const result: OptimizationResult = {
      originalModelId: originalModel.id,
      optimizedModelId: optimizedModel.id,
      options,
      improvements: {
        inferenceSpeedGain: 1.2, // 20%提升
        memoryReduction: 0.15,   // 15%减少
        modelSizeChange: 0.05    // 5%增加（优化元数据）
      },
      timestamp: new Date(),
      success: true
    };

    return result;
  }

  private recordOptimizationHistory(modelId: string, result: OptimizationResult): void {
    if (!this.optimizationHistory.has(modelId)) {
      this.optimizationHistory.set(modelId, []);
    }
    
    const history = this.optimizationHistory.get(modelId)!;
    history.push(result);
    
    // 保留最近10次优化记录
    if (history.length > 10) {
      history.shift();
    }
  }

  private calculatePerformanceScore(metrics: PerformanceMetrics): number {
    let score = 100;
    
    // 推理时间评分
    if (metrics.averageInferenceTime > PERFORMANCE_BENCHMARKS.INFERENCE_TIME.POOR) {
      score -= 30;
    } else if (metrics.averageInferenceTime > PERFORMANCE_BENCHMARKS.INFERENCE_TIME.ACCEPTABLE) {
      score -= 15;
    } else if (metrics.averageInferenceTime > PERFORMANCE_BENCHMARKS.INFERENCE_TIME.GOOD) {
      score -= 5;
    }
    
    // 内存使用评分
    if (metrics.memoryPeakUsage > PERFORMANCE_BENCHMARKS.MEMORY_USAGE.HIGH) {
      score -= 25;
    } else if (metrics.memoryPeakUsage > PERFORMANCE_BENCHMARKS.MEMORY_USAGE.MEDIUM) {
      score -= 10;
    }
    
    // CPU使用评分
    if (metrics.cpuUsage > PERFORMANCE_BENCHMARKS.CPU_USAGE.HIGH) {
      score -= 20;
    } else if (metrics.cpuUsage > PERFORMANCE_BENCHMARKS.CPU_USAGE.MEDIUM) {
      score -= 10;
    }
    
    return Math.max(0, score);
  }

  private async simulateOptimizationProcess(duration: number): Promise<void> {
    // 模拟优化过程的时间消耗
    return new Promise(resolve => {
      setTimeout(resolve, duration);
    });
  }
}

// 辅助接口和类型

interface OptimizationTask {
  id: string;
  model: ONNXModel;
  options: ModelOptimizationOptions;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: Date;
  completedAt?: Date;
  error?: string;
}

interface OptimizationResult {
  originalModelId: string;
  optimizedModelId: string;
  options: ModelOptimizationOptions;
  improvements: {
    inferenceSpeedGain: number;  // 推理速度提升倍数
    memoryReduction: number;     // 内存减少比例
    modelSizeChange: number;     // 模型大小变化比例
  };
  timestamp: Date;
  success: boolean;
  error?: string;
}

interface BottleneckAnalysis {
  modelId: string;
  bottlenecks: string[];
  recommendations: string[];
  overallScore: number;
  metrics: PerformanceMetrics;
} 