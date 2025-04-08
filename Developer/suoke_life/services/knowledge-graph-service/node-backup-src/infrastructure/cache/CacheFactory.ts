import { ICache } from './ICache';
import { RedisCache } from './RedisCache';
import logger from '../logger';

export enum CacheType {
  REDIS = 'redis',
  MEMORY = 'memory'  // 未来可能支持的内存缓存
}

export class CacheFactory {
  private static instance: CacheFactory;
  private cacheInstances: Map<CacheType, ICache>;

  private constructor() {
    this.cacheInstances = new Map();
  }

  public static getInstance(): CacheFactory {
    if (!CacheFactory.instance) {
      CacheFactory.instance = new CacheFactory();
    }
    return CacheFactory.instance;
  }

  /**
   * 获取缓存实例
   * @param type 缓存类型
   */
  public getCache(type: CacheType = CacheType.REDIS): ICache {
    if (!this.cacheInstances.has(type)) {
      this.createCacheInstance(type);
    }
    return this.cacheInstances.get(type)!;
  }

  private createCacheInstance(type: CacheType): void {
    let cache: ICache;

    switch (type) {
      case CacheType.REDIS:
        cache = RedisCache.getInstance();
        break;
      default:
        logger.error(`不支持的缓存类型: ${type}`);
        throw new Error(`不支持的缓存类型: ${type}`);
    }

    this.cacheInstances.set(type, cache);
  }
}