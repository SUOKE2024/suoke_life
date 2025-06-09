import React from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GATEWAY_FEATURES, GATEWAY_CACHE_CONFIG } from '../constants/config';
import { errorHandler, AppError } from './errorHandler';
// 离线操作类型
export interface OfflineOperation {
  id: string;,
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  service: string;,
  endpoint: string;
  data?: any;
  timestamp: string;,
  retryCount: number;
  maxRetries: number;,
  priority: 'low' | 'medium' | 'high';
}
// 缓存项接口
export interface CacheItem {
  key: string;,
  data: any;
  timestamp: string;,
  ttl: number;
  service: string;,
  endpoint: string;
  etag?: string;
}
// 同步状态
export interface SyncStatus {
  isOnline: boolean;,
  lastSyncTime: string | null;
  pendingOperations: number;,
  failedOperations: number;
  syncInProgress: boolean;
}
// 离线服务类
export class OfflineService {
  private static instance: OfflineService;
  private isOnline: boolean = true;
  private syncInProgress: boolean = false;
  private operationQueue: OfflineOperation[] = [];
  private cache: Map<string, CacheItem> = new Map();
  private syncListeners: (status: SyncStatus) => void)[] = [];
  // 存储键
  private readonly STORAGE_KEYS = {
      OPERATION_QUEUE: "@suoke_life:offline_queue",
      CACHE_DATA: '@suoke_life:cache_data',
    SYNC_STATUS: '@suoke_life:sync_status'};
  static getInstance(): OfflineService {
    if (!OfflineService.instance) {
      OfflineService.instance = new OfflineService();
    }
    return OfflineService.instance;
  }
  constructor() {
    this.initializeOfflineService();
    this.setupNetworkListener();
  }
  // 初始化离线服务
  private async initializeOfflineService(): Promise<void> {
    try {
      await this.loadOperationQueue();
      await this.loadCacheData();
            // 如果启用了离线功能，开始定期同步
      if (GATEWAY_FEATURES.ENABLE_OFFLINE) {
        this.startPeriodicSync();
      }
    } catch (error) {
      console.error('Failed to initialize offline service:', error);
    }
  }
  // 设置网络状态监听
  private setupNetworkListener(): void {
    // 在React Native中，可以使用@react-native-community/netinfo;
    // 这里提供基本的实现
    if (typeof window !== 'undefined' && window.navigator) {
      window.addEventListener('online', () => {
        this.setOnlineStatus(true);
      });
            window.addEventListener('offline', () => {
        this.setOnlineStatus(false);
      });
            this.isOnline = window.navigator.onLine;
    }
  }
  // 设置在线状态
  private setOnlineStatus(isOnline: boolean): void {
    const wasOffline = !this.isOnline;
    this.isOnline = isOnline;
        if (wasOffline && isOnline) {
      // 从离线恢复到在线，开始同步
      this.syncPendingOperations();
    }
        this.notifySyncListeners();
  }
  // 添加离线操作到队列
  async addOfflineOperation(operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const offlineOp: OfflineOperation = {
      ...operation,
      id: this.generateOperationId(),
      timestamp: new Date().toISOString(),
      retryCount: 0};
    this.operationQueue.push(offlineOp);
    await this.saveOperationQueue();
        // 如果在线，立即尝试执行
    if (this.isOnline) {
      this.syncPendingOperations();
    }
  }
  // 缓存数据
  async cacheData()
    service: string,
    endpoint: string,
    data: any,
    ttl: number = GATEWAY_CACHE_CONFIG.TTL,
    etag?: string;
  ): Promise<void> {
    const key = this.generateCacheKey(service, endpoint);
    const cacheItem: CacheItem = {
      key,
      data,
      timestamp: new Date().toISOString(),
      ttl,
      service,
      endpoint,
      etag};
    this.cache.set(key, cacheItem);
    await this.saveCacheData();
  }
  // 获取缓存数据
  getCachedData(service: string, endpoint: string): any | null {
    const key = this.generateCacheKey(service, endpoint);
    const cacheItem = this.cache.get(key);
        if (!cacheItem) {
      return null;
    }
    // 检查是否过期
    const now = Date.now();
    const cacheTime = new Date(cacheItem.timestamp).getTime();
        if (now - cacheTime > cacheItem.ttl) {
      this.cache.delete(key);
      this.saveCacheData(); // 异步保存
      return null;
    }
    return cacheItem.data;
  }
  // 检查缓存是否存在且有效
  isCacheValid(service: string, endpoint: string): boolean {
    return this.getCachedData(service, endpoint) !== null;
  }
  // 清除过期缓存
  async clearExpiredCache(): Promise<void> {
    const now = Date.now();
    const expiredKeys: string[] = [];
    this.cache.forEach((item, key) => {
      const cacheTime = new Date(item.timestamp).getTime();
      if (now - cacheTime > item.ttl) {
        expiredKeys.push(key);
      }
    });
    expiredKeys.forEach(key => this.cache.delete(key));
        if (expiredKeys.length > 0) {
      await this.saveCacheData();
    }
  }
  // 同步待处理操作
  async syncPendingOperations(): Promise<void> {
    if (this.syncInProgress || !this.isOnline || this.operationQueue.length === 0) {
      return;
    }
    this.syncInProgress = true;
    this.notifySyncListeners();
    try {
      // 按优先级排序
      const sortedOperations = [...this.operationQueue].sort(a, b) => {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      });
      const results = await Promise.allSettled()
        sortedOperations.map(operation => this.executeOperation(operation))
      );
      // 处理结果
      const successfulOperations: string[] = [];
      const failedOperations: OfflineOperation[] = [];
      results.forEach((result, index) => {
        const operation = sortedOperations[index];
                if (result.status === 'fulfilled') {
          successfulOperations.push(operation.id);
        } else {
          operation.retryCount++;
          if (operation.retryCount < operation.maxRetries) {
            failedOperations.push(operation);
          } else {
            console.error(`Operation ${operation.id} failed after ${operation.maxRetries} retries:`, result.reason);
          }
        }
      });
      // 更新操作队列
      this.operationQueue = this.operationQueue.filter()
        op => !successfulOperations.includes(op.id)
      );
            // 重新添加失败但还可以重试的操作
      failedOperations.forEach(op => {
        const index = this.operationQueue.findIndex(queueOp => queueOp.id === op.id);
        if (index >= 0) {
          this.operationQueue[index] = op;
        }
      });
      await this.saveOperationQueue();
          } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      this.syncInProgress = false;
      this.notifySyncListeners();
    }
  }
  // 执行单个操作
  private async executeOperation(operation: OfflineOperation): Promise<any> {
    // 这里需要调用实际的API客户端
    // 为了避免循环依赖，我们使用动态导入
    const { apiClient } = await import('./apiClient');
        switch (operation.type) {
      case 'CREATE':
        return apiClient.post(operation.service, operation.endpoint, operation.data);
      case 'UPDATE':
        return apiClient.put(operation.service, operation.endpoint, operation.data);
      case 'DELETE':
        return apiClient.delete(operation.service, operation.endpoint);
      default:
        throw new Error(`Unknown operation type: ${operation.type}`);
    }
  }
  // 获取同步状态
  getSyncStatus(): SyncStatus {
    return {
      isOnline: this.isOnline,
      lastSyncTime: this.getLastSyncTime(),
      pendingOperations: this.operationQueue.length,
      failedOperations: this.operationQueue.filter(op => op.retryCount >= op.maxRetries).length,
      syncInProgress: this.syncInProgress};
  }
  // 添加同步状态监听器
  addSyncListener(listener: (status: SyncStatus) => void): () => void {
    this.syncListeners.push(listener);
        // 返回取消监听的函数
    return () => {
      const index = this.syncListeners.indexOf(listener);
      if (index > -1) {
        this.syncListeners.splice(index, 1);
      }
    };
  }
  // 通知同步状态监听器
  private notifySyncListeners(): void {
    const status = this.getSyncStatus();
    this.syncListeners.forEach(listener => {
      try {
        listener(status);
      } catch (error) {
        console.error('Sync listener error:', error);
      }
    });
  }
  // 开始定期同步
  private startPeriodicSync(): void {
    setInterval() => {
      if (this.isOnline && this.operationQueue.length > 0) {
        this.syncPendingOperations();
      }
      this.clearExpiredCache();
    }, 30000); // 每30秒检查一次
  }
  // 强制同步
  async forcSync(): Promise<void> {
    if (!this.isOnline) {
      throw new Error('Cannot sync while offline');
    }
        await this.syncPendingOperations();
  }
  // 清除所有离线数据
  async clearOfflineData(): Promise<void> {
    this.operationQueue = [];
    this.cache.clear();
        await Promise.all([)
      AsyncStorage.removeItem(this.STORAGE_KEYS.OPERATION_QUEUE),
      AsyncStorage.removeItem(this.STORAGE_KEYS.CACHE_DATA),
      AsyncStorage.removeItem(this.STORAGE_KEYS.SYNC_STATUS)]);
  }
  // 获取缓存统计
  getCacheStats(): {
    totalItems: number,
  totalSize: number;,
  hitRate: number,
  expiredItems: number;
  } {
    const now = Date.now();
    let totalSize = 0;
    let expiredItems = 0;
    this.cache.forEach(item => {
      totalSize += JSON.stringify(item.data).length;
      const cacheTime = new Date(item.timestamp).getTime();
      if (now - cacheTime > item.ttl) {
        expiredItems++;
      }
    });
    return {
      totalItems: this.cache.size,
      totalSize,
      hitRate: 0, // 需要实际的命中率统计
      expiredItems};
  }
  // 生成操作ID;
  private generateOperationId(): string {
    return `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  // 生成缓存键
  private generateCacheKey(service: string, endpoint: string): string {
    return `${service}:${endpoint}`;
  }
  // 获取最后同步时间
  private getLastSyncTime(): string | null {
    // 从存储中获取或返回null;
    return null; // 简化实现
  }
  // 保存操作队列到存储
  private async saveOperationQueue(): Promise<void> {
    try {
      await AsyncStorage.setItem()
        this.STORAGE_KEYS.OPERATION_QUEUE,
        JSON.stringify(this.operationQueue)
      );
    } catch (error) {
      console.error('Failed to save operation queue:', error);
    }
  }
  // 从存储加载操作队列
  private async loadOperationQueue(): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(this.STORAGE_KEYS.OPERATION_QUEUE);
      if (data) {
        this.operationQueue = JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load operation queue:', error);
      this.operationQueue = [];
    }
  }
  // 保存缓存数据到存储
  private async saveCacheData(): Promise<void> {
    try {
      const cacheArray = Array.from(this.cache.entries());
      await AsyncStorage.setItem()
        this.STORAGE_KEYS.CACHE_DATA,
        JSON.stringify(cacheArray)
      );
    } catch (error) {
      console.error('Failed to save cache data:', error);
    }
  }
  // 从存储加载缓存数据
  private async loadCacheData(): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(this.STORAGE_KEYS.CACHE_DATA);
      if (data) {
        const cacheArray = JSON.parse(data);
        this.cache = new Map(cacheArray);
      }
    } catch (error) {
      console.error('Failed to load cache data:', error);
      this.cache = new Map();
    }
  }
  // 预加载关键数据
  async preloadCriticalData(): Promise<void> {
    if (!this.isOnline) {
      return;
    }
    try {
      // 预加载用户配置、健康数据等关键信息
      const { apiClient } = await import('./apiClient');
            const criticalEndpoints = [
        {
      service: "USER",
      endpoint: '/users/profile' },
        {
      service: "USER",
      endpoint: '/users/settings' },
        {
      service: "HEALTH_DATA",
      endpoint: '/health-data/recent' },
        {
      service: "AGENTS",
      endpoint: '/agents/status' }];
      await Promise.allSettled()
        criticalEndpoints.map(async ({ service, endpoint }) => {
          try {
            const response = await apiClient.get(service, endpoint);
            if (response.success) {
              await this.cacheData(service, endpoint, response.data, GATEWAY_CACHE_CONFIG.TTL);
            }
          } catch (error) {
            console.warn(`Failed to preload ${service}${endpoint}:`, error);
          }
        })
      );
    } catch (error) {
      console.error('Failed to preload critical data:', error);
    }
  }
}
// 导出单例实例
export const offlineService = OfflineService.getInstance();
// 导出便捷函数
export const addOfflineOperation = (operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retryCount'>) => {
  return offlineService.addOfflineOperation(operation);
};
export const getCachedData = (service: string, endpoint: string) => {
  return offlineService.getCachedData(service, endpoint);
};
export const cacheData = (service: string, endpoint: string, data: any, ttl?: number) => {
  return offlineService.cacheData(service, endpoint, data, ttl);
};
export const getSyncStatus = () => {
  return offlineService.getSyncStatus();
};
export const addSyncListener = (listener: (status: SyncStatus) => void) => {
  return offlineService.addSyncListener(listener);
};