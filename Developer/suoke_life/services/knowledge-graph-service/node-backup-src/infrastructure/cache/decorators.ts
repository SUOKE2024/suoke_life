import { CacheFactory, CacheType } from './CacheFactory';
import { CacheOptions } from './ICache';
import logger from '../logger';

/**
 * 缓存装饰器选项
 */
interface CacheDecoratorOptions extends CacheOptions {
  keyPrefix?: string;
  keyGenerator?: (args: any[]) => string;
}

/**
 * 缓存结果装饰器
 * @param options 缓存选项
 */
export function Cacheable(options: CacheDecoratorOptions = {}) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const cache = CacheFactory.getInstance().getCache(CacheType.REDIS);
      
      // 生成缓存键
      const key = options.keyGenerator
        ? options.keyGenerator(args)
        : `${propertyKey}:${JSON.stringify(args)}`;
      
      const finalKey = options.keyPrefix
        ? `${options.keyPrefix}:${key}`
        : key;

      try {
        // 尝试从缓存获取
        const cachedResult = await cache.get(finalKey);
        if (cachedResult !== null) {
          logger.debug(`缓存命中: ${finalKey}`);
          return cachedResult;
        }

        // 执行原方法
        const result = await originalMethod.apply(this, args);

        // 存入缓存
        await cache.set(finalKey, result, {
          ttl: options.ttl,
          prefix: options.prefix
        });

        return result;
      } catch (error) {
        logger.error(`缓存操作失败: ${error}`);
        // 发生错误时直接执行原方法
        return originalMethod.apply(this, args);
      }
    };

    return descriptor;
  };
}

/**
 * 缓存清除装饰器
 * @param patterns 要清除的缓存键模式
 */
export function CacheEvict(patterns: string[] = []) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const cache = CacheFactory.getInstance().getCache(CacheType.REDIS);

      try {
        // 执行原方法
        const result = await originalMethod.apply(this, args);

        // 清除指定的缓存
        for (const pattern of patterns) {
          await cache.clearByPrefix(pattern);
        }

        return result;
      } catch (error) {
        logger.error(`缓存清除失败: ${error}`);
        throw error;
      }
    };

    return descriptor;
  };
}

/**
 * 缓存预热装饰器
 * @param options 缓存选项
 */
export function CacheWarmup(options: CacheDecoratorOptions = {}) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const cache = CacheFactory.getInstance().getCache(CacheType.REDIS);

      try {
        // 执行原方法获取数据
        const results = await originalMethod.apply(this, args);

        if (Array.isArray(results)) {
          // 准备预热数据
          const warmupItems = results.map((item: any) => ({
            key: options.keyGenerator
              ? options.keyGenerator([item])
              : `${propertyKey}:${JSON.stringify(item)}`,
            value: item
          }));

          // 执行预热
          await cache.warmup(warmupItems, {
            ttl: options.ttl,
            prefix: options.prefix
          });
        }

        return results;
      } catch (error) {
        logger.error(`缓存预热失败: ${error}`);
        return originalMethod.apply(this, args);
      }
    };

    return descriptor;
  };
}