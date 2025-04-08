import { CacheManager } from '../cache';
import logger from '../logger';

export interface PaginationCursor {
  id: string;
  offset: number;
  limit: number;
  total: number;
  hasMore: boolean;
  expiresAt: number;
}

export interface PaginationOptions {
  cursor?: string;
  limit?: number;
  orderBy?: string;
  orderDirection?: 'ASC' | 'DESC';
}

export interface PaginatedResult<T> {
  items: T[];
  cursor: PaginationCursor;
  total: number;
  hasMore: boolean;
}

export class PaginationManager {
  private static instance: PaginationManager;
  private cacheManager: CacheManager;
  private readonly CURSOR_TTL = 300; // 5分钟
  private readonly CURSOR_PREFIX = 'cursor:';
  private readonly DEFAULT_LIMIT = 20;
  private readonly MAX_LIMIT = 100;

  private constructor() {
    this.cacheManager = CacheManager.getInstance();
  }

  public static getInstance(): PaginationManager {
    if (!PaginationManager.instance) {
      PaginationManager.instance = new PaginationManager();
    }
    return PaginationManager.instance;
  }

  /**
   * 创建分页游标
   */
  public async createCursor(total: number, options: PaginationOptions = {}): Promise<PaginationCursor> {
    const limit = Math.min(options.limit || this.DEFAULT_LIMIT, this.MAX_LIMIT);
    const cursor: PaginationCursor = {
      id: this.generateCursorId(),
      offset: 0,
      limit,
      total,
      hasMore: total > limit,
      expiresAt: Date.now() + this.CURSOR_TTL * 1000
    };

    await this.cacheManager.set(cursor.id, cursor, {
      ttl: this.CURSOR_TTL,
      prefix: this.CURSOR_PREFIX
    });

    return cursor;
  }

  /**
   * 获取游标
   */
  public async getCursor(cursorId: string): Promise<PaginationCursor | null> {
    try {
      return await this.cacheManager.get<PaginationCursor>(cursorId, this.CURSOR_PREFIX);
    } catch (error) {
      logger.error('获取游标失败:', error);
      return null;
    }
  }

  /**
   * 更新游标
   */
  public async updateCursor(cursor: PaginationCursor): Promise<void> {
    try {
      cursor.offset += cursor.limit;
      cursor.hasMore = cursor.offset < cursor.total;
      cursor.expiresAt = Date.now() + this.CURSOR_TTL * 1000;

      await this.cacheManager.set(cursor.id, cursor, {
        ttl: this.CURSOR_TTL,
        prefix: this.CURSOR_PREFIX
      });
    } catch (error) {
      logger.error('更新游标失败:', error);
      throw error;
    }
  }

  /**
   * 生成分页查询
   */
  public generatePaginatedQuery(baseQuery: string, options: PaginationOptions): string {
    const limit = Math.min(options.limit || this.DEFAULT_LIMIT, this.MAX_LIMIT);
    let query = baseQuery;

    if (options.orderBy) {
      query += ` ORDER BY ${options.orderBy} ${options.orderDirection || 'ASC'}`;
    }

    query += ` SKIP ${options.cursor ? parseInt(options.cursor) : 0}`;
    query += ` LIMIT ${limit}`;

    return query;
  }

  /**
   * 包装分页结果
   */
  public async wrapWithPagination<T>(
    items: T[],
    total: number,
    options: PaginationOptions
  ): Promise<PaginatedResult<T>> {
    let cursor: PaginationCursor;

    if (options.cursor) {
      cursor = await this.getCursor(options.cursor) || await this.createCursor(total, options);
      await this.updateCursor(cursor);
    } else {
      cursor = await this.createCursor(total, options);
    }

    return {
      items,
      cursor,
      total,
      hasMore: cursor.hasMore
    };
  }

  private generateCursorId(): string {
    return `cur_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}