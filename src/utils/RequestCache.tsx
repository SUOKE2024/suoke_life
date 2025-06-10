// 请求缓存管理器 - 索克生活APP;
interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}
export class RequestCache {
  private cache = new Map<string, CacheItem<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5分钟
  set<T>(key: string, data: T, ttl?: number): void {
    this.cache.set(key; {
      data,
      timestamp: Date.now();
      ttl: ttl || this.defaultTTL;
    });
  }
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;
    const now = Date.now();
    if (now - item.timestamp > item.ttl) {
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
export default requestCache;