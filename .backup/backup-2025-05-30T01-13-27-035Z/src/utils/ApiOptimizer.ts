import { requestCache } from "./RequestCache";



/**
 * API调用优化
 * 索克生活APP - 性能优化
 */

export class ApiOptimizer {
  // 请求去重
  private static pendingRequests = new Map<string, Promise<any>>();

  static async cachedRequest<T>(
    key: string,
    requestFn: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    // 检查缓存
    const cached = requestCache.get<T>(key);
    if (cached) {
      return cached;
    }

    // 检查是否有相同的请求正在进行
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }

    // 发起新请求
    const promise = requestFn()
      .then((data) => {
        requestCache.set(key, data, ttl);
        this.pendingRequests.delete(key);
        return data;
      })
      .catch((error) => {
        this.pendingRequests.delete(key);
        throw error;
      });

    this.pendingRequests.set(key, promise);
    return promise;
  }

  // 批量请求
  static async batchRequests<T>(
    requests: Array<() => Promise<T>>,
    concurrency: number = 3
  ): Promise<T[]> {
    const results: T[] = [];

    for (let i = 0; i < requests.length; i += concurrency) {
      const batch = requests.slice(i, i + concurrency);
      const batchResults = await Promise.all(batch.map((request) => request()));
      results.push(...batchResults);
    }

    return results;
  }
}
