/**
 * 请求缓存策略
 * 索克生活APP - 性能优化
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export class RequestCache {
  private cache = new Map<string, CacheItem<any>>();
  private maxSize: number = 100;
  
  set<T>(key: string, data: T, ttl: number = 300000): void { // 默认5分钟
    // 清理过期缓存
    this.cleanup();
    
    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  has(key: string): boolean {
    return this.get(key) !== null;
  }
  
  delete(key: string): void {
    this.cache.delete(key);
  }
  
  clear(): void {
    this.cache.clear();
  }
  
  private cleanup(): void {
    const now = Date.now();
    
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    }
  }
}

export const requestCache = new RequestCache();
