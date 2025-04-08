export interface CacheOptions {
  ttl?: number;        // 缓存过期时间（秒）
  prefix?: string;     // 缓存键前缀
}

export interface CacheStats {
  totalKeys: number;   // 缓存键总数
  memoryUsage: number; // 内存使用量（字节）
  hitRate: number;     // 缓存命中率
}

export interface ICache {
  /**
   * 设置缓存
   * @param key 缓存键
   * @param value 缓存值
   * @param options 缓存选项
   */
  set(key: string, value: any, options?: CacheOptions): Promise<void>;

  /**
   * 获取缓存
   * @param key 缓存键
   * @param prefix 可选的键前缀
   */
  get<T>(key: string, prefix?: string): Promise<T | null>;

  /**
   * 删除缓存
   * @param key 缓存键
   * @param prefix 可选的键前缀
   */
  delete(key: string, prefix?: string): Promise<void>;

  /**
   * 批量设置缓存
   * @param items 缓存项数组
   * @param options 缓存选项
   */
  mset(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void>;

  /**
   * 批量获取缓存
   * @param keys 缓存键数组
   * @param prefix 可选的键前缀
   */
  mget<T>(keys: string[], prefix?: string): Promise<Array<T | null>>;

  /**
   * 缓存预热
   * @param items 预热数据项数组
   * @param options 缓存选项
   */
  warmup(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void>;

  /**
   * 清除指定前缀的所有缓存
   * @param prefix 缓存键前缀
   */
  clearByPrefix(prefix: string): Promise<void>;

  /**
   * 获取缓存统计信息
   */
  getStats(): Promise<CacheStats>;
}