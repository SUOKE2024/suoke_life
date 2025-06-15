/**
 * AI装饰器
 * 利用TypeScript 5.1+的装饰器支持
 */

import { AIDecoratorMetadata, AITaskType, LLMModelType } from '../types/AITypes';

// 装饰器元数据存储
const metadataMap = new WeakMap<any, AIDecoratorMetadata>();

/**
 * AI模型装饰器
 * @param modelType LLM模型类型
 */
export function AIModel(modelType: LLMModelType) {
  return function <T extends { new (...args: any[]): {} }>(constructor: T) {
    const metadata = metadataMap.get(constructor) || {};
    metadata.modelType = modelType;
    metadataMap.set(constructor, metadata);
    return constructor;
  };
}

/**
 * AI任务装饰器
 * @param taskType AI任务类型
 */
export function AITask(taskType: AITaskType) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const metadata = metadataMap.get(target.constructor) || {};
    metadata.taskType = taskType;
    metadataMap.set(target.constructor, metadata);
    return descriptor;
  };
}

/**
 * AI缓存装饰器
 * @param enabled 是否启用缓存
 */
export function AICache(enabled: boolean = true) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    const cacheMap = new Map<string, any>();

    descriptor.value = async function (...args: any[]) {
      if (!enabled) {
        return originalMethod.apply(this, args);
      }

      const cacheKey = JSON.stringify(args);
      if (cacheMap.has(cacheKey)) {
        return cacheMap.get(cacheKey);
      }

      const result = await originalMethod.apply(this, args);
      cacheMap.set(cacheKey, result);
      return result;
    };

    const metadata = metadataMap.get(target.constructor) || {};
    metadata.cacheEnabled = enabled;
    metadataMap.set(target.constructor, metadata);

    return descriptor;
  };
}

/**
 * AI重试装饰器
 * @param attempts 重试次数
 */
export function AIRetry(attempts: number = 3) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: Error;
      
      for (let i = 0; i < attempts; i++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error as Error;
          if (i === attempts - 1) {
            throw lastError;
          }
          // 指数退避
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
      }
      
      throw lastError!;
    };

    const metadata = metadataMap.get(target.constructor) || {};
    metadata.retryAttempts = attempts;
    metadataMap.set(target.constructor, metadata);

    return descriptor;
  };
}

/**
 * AI超时装饰器
 * @param timeout 超时时间（毫秒）
 */
export function AITimeout(timeout: number) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      return Promise.race([
        originalMethod.apply(this, args),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error(`AI operation timeout after ${timeout}ms`)), timeout)
        )
      ]);
    };

    const metadata = metadataMap.get(target.constructor) || {};
    metadata.timeout = timeout;
    metadataMap.set(target.constructor, metadata);

    return descriptor;
  };
}

/**
 * AI性能监控装饰器
 */
export function AIPerformance() {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const startTime = Date.now();
      const startMemory = process.memoryUsage();

      try {
        const result = await originalMethod.apply(this, args);
        const endTime = Date.now();
        const endMemory = process.memoryUsage();

        console.log(`[AI Performance] ${target.constructor.name}.${propertyKey}:`, {
          duration: endTime - startTime,
          memoryDelta: {
            rss: endMemory.rss - startMemory.rss,
            heapUsed: endMemory.heapUsed - startMemory.heapUsed,
          }
        });

        return result;
      } catch (error) {
        const endTime = Date.now();
        console.error(`[AI Performance] ${target.constructor.name}.${propertyKey} failed:`, {
          duration: endTime - startTime,
          error: (error as Error).message
        });
        throw error;
      }
    };

    return descriptor;
  };
}

/**
 * 获取装饰器元数据
 * @param target 目标类
 */
export function getAIMetadata(target: any): AIDecoratorMetadata | undefined {
  return metadataMap.get(target);
} 