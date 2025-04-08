import { Session } from 'neo4j-driver';
import logger from '../logger';

export interface TimeoutConfig {
  timeout: number;      // 超时时间（毫秒）
  retryCount: number;   // 重试次数
  retryDelay: number;   // 重试延迟（毫秒）
}

export class TimeoutManager {
  private static instance: TimeoutManager;
  
  private readonly DEFAULT_CONFIG: TimeoutConfig = {
    timeout: 5000,      // 5秒
    retryCount: 3,      // 重试3次
    retryDelay: 1000    // 1秒延迟
  };

  private constructor() {}

  public static getInstance(): TimeoutManager {
    if (!TimeoutManager.instance) {
      TimeoutManager.instance = new TimeoutManager();
    }
    return TimeoutManager.instance;
  }

  /**
   * 执行带超时的查询
   */
  public async executeWithTimeout<T>(
    session: Session,
    query: string,
    params: Record<string, any> = {},
    config: Partial<TimeoutConfig> = {}
  ): Promise<T> {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= finalConfig.retryCount; attempt++) {
      try {
        const result = await Promise.race([
          session.run(query, params),
          this.createTimeout(finalConfig.timeout)
        ]);

        return this.processResult<T>(result);
      } catch (error) {
        lastError = error as Error;
        logger.warn(`查询执行失败 (尝试 ${attempt}/${finalConfig.retryCount}):`, error);

        if (error.message === 'TIMEOUT') {
          // 超时错误，等待后重试
          await this.delay(finalConfig.retryDelay);
          continue;
        }

        // 其他错误直接抛出
        throw error;
      }
    }

    throw new Error(`查询执行失败，已重试${finalConfig.retryCount}次: ${lastError?.message}`);
  }

  /**
   * 批量执行带超时的查询
   */
  public async executeBatchWithTimeout<T>(
    session: Session,
    queries: Array<{query: string; params?: Record<string, any>}>,
    config: Partial<TimeoutConfig> = {}
  ): Promise<T[]> {
    const finalConfig = { ...this.DEFAULT_CONFIG, ...config };
    const results: T[] = [];

    for (const {query, params} of queries) {
      try {
        const result = await this.executeWithTimeout<T>(
          session,
          query,
          params,
          finalConfig
        );
        results.push(result);
      } catch (error) {
        logger.error('批量查询执行失败:', error);
        throw error;
      }
    }

    return results;
  }

  private createTimeout(ms: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error('TIMEOUT'));
      }, ms);
    });
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private processResult<T>(result: any): T {
    if (!result || !result.records) {
      return [] as unknown as T;
    }

    return result.records.map((record: any) => {
      const fields = {};
      record.keys.forEach((key: string) => {
        fields[key] = record.get(key);
      });
      return fields;
    }) as unknown as T;
  }
}