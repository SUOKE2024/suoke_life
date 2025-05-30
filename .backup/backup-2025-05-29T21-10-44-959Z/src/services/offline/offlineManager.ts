import AsyncStorage from "@react-native-async-storage/async-storage";
import { EventEmitter } from "../../utils/eventEmitter";
import { graphqlClient } from "../graphql/client";


/**
 * 索克生活 - 离线模式管理器
 * 完整的离线数据存储和同步功能
 */

// 离线操作类型
export type OfflineOperationType = "create" | "update" | "delete" | "query";

// 离线操作接口
export interface OfflineOperation {
  id: string;
  type: OfflineOperationType;
  entity: string;
  data: any;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  priority: number; // 优先级，数字越小优先级越高
}

// 同步状态
export type SyncStatus = "idle" | "syncing" | "error" | "completed";

// 冲突解决策略
export type ConflictResolutionStrategy =
  | "client-wins"
  | "server-wins"
  | "merge"
  | "manual";

// 冲突数据接口
export interface ConflictData {
  id: string;
  entity: string;
  clientData: any;
  serverData: any;
  timestamp: number;
  strategy: ConflictResolutionStrategy;
}

// 同步配置接口
export interface SyncConfig {
  batchSize: number;
  retryDelay: number;
  maxRetries: number;
  conflictStrategy: ConflictResolutionStrategy;
  syncInterval: number; // 自动同步间隔（毫秒）
}

// 网络状态接口
export interface NetworkState {
  isConnected: boolean;
  connectionType: string;
  isInternetReachable: boolean;
}

// 存储键常量
const STORAGE_KEYS = {
  OFFLINE_OPERATIONS: "@suoke_offline_operations",
  OFFLINE_DATA: "@suoke_offline_data",
  SYNC_METADATA: "@suoke_sync_metadata",
  CONFLICTS: "@suoke_conflicts",
};

export class OfflineManager extends EventEmitter {
  private operations: Map<string, OfflineOperation> = new Map();
  private offlineData: Map<string, any> = new Map();
  private conflicts: Map<string, ConflictData> = new Map();
  private syncStatus: SyncStatus = "idle";
  private networkState: NetworkState = {
    isConnected: false,
    connectionType: "unknown",
    isInternetReachable: false,
  };
  private syncConfig: SyncConfig = {
    batchSize: 10,
    retryDelay: 5000,
    maxRetries: 3,
    conflictStrategy: "client-wins",
    syncInterval: 30000, // 30秒
  };
  private syncTimer: number | null = null;
  private isInitialized: boolean = false;

  constructor(config?: Partial<SyncConfig>) {
    super();
    if (config) {
      this.syncConfig = { ...this.syncConfig, ...config };
    }
  }

  /**
   * 初始化离线管理器
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      await Promise.all([
        this.loadOperations(),
        this.loadOfflineData(),
        this.loadConflicts(),
      ]);

      this.setupNetworkListener();
      this.startAutoSync();
      this.isInitialized = true;

      this.emit("initialized");
      console.log("离线管理器初始化完成");
    } catch (error) {
      console.error("离线管理器初始化失败:", error);
      throw error;
    }
  }

  /**
   * 设置网络监听
   */
  private setupNetworkListener(): void {
    // 这里可以集成NetInfo来监听网络状态
    // 模拟网络状态变化
    this.networkState = {
      isConnected: true,
      connectionType: "wifi",
      isInternetReachable: true,
    };

    this.emit("networkStateChange", this.networkState);
  }

  /**
   * 开始自动同步
   */
  private startAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }

    this.syncTimer = setInterval(() => {
      if (this.networkState.isConnected && this.syncStatus === "idle") {
        this.sync().catch((error) => {
          console.error("自动同步失败:", error);
        });
      }
    }, this.syncConfig.syncInterval);
  }

  /**
   * 停止自动同步
   */
  private stopAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
  }

  /**
   * 添加离线操作
   */
  async addOperation(
    type: OfflineOperationType,
    entity: string,
    data: any,
    priority: number = 5
  ): Promise<string> {
    const operation: OfflineOperation = {
      id: this.generateId(),
      type,
      entity,
      data,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: this.syncConfig.maxRetries,
      priority,
    };

    this.operations.set(operation.id, operation);
    await this.saveOperations();

    this.emit("operationAdded", operation);

    // 如果在线，立即尝试同步
    if (this.networkState.isConnected && this.syncStatus === "idle") {
      this.sync().catch((error) => {
        console.error("即时同步失败:", error);
      });
    }

    return operation.id;
  }

  /**
   * 存储离线数据
   */
  async storeData(key: string, data: any): Promise<void> {
    this.offlineData.set(key, {
      data,
      timestamp: Date.now(),
      synced: false,
    });

    await this.saveOfflineData();
    this.emit("dataStored", { key, data });
  }

  /**
   * 获取离线数据
   */
  getData(key: string): any | null {
    const item = this.offlineData.get(key);
    return item ? item.data : null;
  }

  /**
   * 删除离线数据
   */
  async removeData(key: string): Promise<void> {
    this.offlineData.delete(key);
    await this.saveOfflineData();
    this.emit("dataRemoved", { key });
  }

  /**
   * 执行同步
   */
  async sync(): Promise<void> {
    if (this.syncStatus === "syncing") {
      console.log("同步正在进行中，跳过此次同步");
      return;
    }

    if (!this.networkState.isConnected) {
      console.log("网络未连接，跳过同步");
      return;
    }

    this.syncStatus = "syncing";
    this.emit("syncStart");

    try {
      // 按优先级排序操作
      const sortedOperations = Array.from(this.operations.values()).sort(
        (a, b) => a.priority - b.priority
      );

      // 分批处理操作
      const batches = this.createBatches(
        sortedOperations,
        this.syncConfig.batchSize
      );

      for (const batch of batches) {
        await this.processBatch(batch);
      }

      this.syncStatus = "completed";
      this.emit("syncComplete");
    } catch (error) {
      this.syncStatus = "error";
      this.emit("syncError", error);
      throw error;
    }
  }

  /**
   * 处理操作批次
   */
  private async processBatch(operations: OfflineOperation[]): Promise<void> {
    const promises = operations.map((operation) =>
      this.processOperation(operation)
    );
    await Promise.allSettled(promises);
  }

  /**
   * 处理单个操作
   */
  private async processOperation(operation: OfflineOperation): Promise<void> {
    try {
      let query: string;
      let variables: any;

      switch (operation.type) {
        case "create":
          query = this.generateCreateMutation(operation.entity);
          variables = { input: operation.data };
          break;
        case "update":
          query = this.generateUpdateMutation(operation.entity);
          variables = { id: operation.data.id, input: operation.data };
          break;
        case "delete":
          query = this.generateDeleteMutation(operation.entity);
          variables = { id: operation.data.id };
          break;
        case "query":
          query = this.generateQuery(operation.entity);
          variables = operation.data;
          break;
        default:
          throw new Error(`不支持的操作类型: ${operation.type}`);
      }

      const response = await graphqlClient.mutate(query, variables);

      if (response.data) {
        // 操作成功，移除队列
        this.operations.delete(operation.id);
        await this.saveOperations();
        this.emit("operationSuccess", { operation, response });
      } else {
        throw new Error("操作失败，无响应数据");
      }
    } catch (error) {
      operation.retryCount++;

      if (operation.retryCount >= operation.maxRetries) {
        // 达到最大重试次数，移除操作
        this.operations.delete(operation.id);
        this.emit("operationFailed", { operation, error });
      } else {
        // 更新重试次数
        this.operations.set(operation.id, operation);
        this.emit("operationRetry", { operation, error });
      }

      await this.saveOperations();
      throw error;
    }
  }

  /**
   * 检测并解决冲突
   */
  async detectConflicts(
    entity: string,
    clientData: any,
    serverData: any
  ): Promise<ConflictData | null> {
    // 简单的冲突检测：比较时间戳
    const clientTimestamp = clientData.updatedAt || clientData.timestamp || 0;
    const serverTimestamp = serverData.updatedAt || serverData.timestamp || 0;

    if (clientTimestamp !== serverTimestamp) {
      const conflict: ConflictData = {
        id: this.generateId(),
        entity,
        clientData,
        serverData,
        timestamp: Date.now(),
        strategy: this.syncConfig.conflictStrategy,
      };

      this.conflicts.set(conflict.id, conflict);
      await this.saveConflicts();
      this.emit("conflictDetected", conflict);

      return conflict;
    }

    return null;
  }

  /**
   * 解决冲突
   */
  async resolveConflict(
    conflictId: string,
    strategy?: ConflictResolutionStrategy
  ): Promise<any> {
    const conflict = this.conflicts.get(conflictId);
    if (!conflict) {
      throw new Error(`冲突不存在: ${conflictId}`);
    }

    const resolveStrategy = strategy || conflict.strategy;
    let resolvedData: any;

    switch (resolveStrategy) {
      case "client-wins":
        resolvedData = conflict.clientData;
        break;
      case "server-wins":
        resolvedData = conflict.serverData;
        break;
      case "merge":
        resolvedData = this.mergeData(conflict.clientData, conflict.serverData);
        break;
      case "manual":
        // 需要手动解决，返回冲突数据
        this.emit("manualResolutionRequired", conflict);
        return conflict;
      default:
        throw new Error(`不支持的冲突解决策略: ${resolveStrategy}`);
    }

    // 移除已解决的冲突
    this.conflicts.delete(conflictId);
    await this.saveConflicts();

    this.emit("conflictResolved", { conflict, resolvedData });
    return resolvedData;
  }

  /**
   * 合并数据
   */
  private mergeData(clientData: any, serverData: any): any {
    // 简单的合并策略：客户端数据优先，但保留服务器的时间戳
    return {
      ...serverData,
      ...clientData,
      updatedAt: Math.max(clientData.updatedAt || 0, serverData.updatedAt || 0),
    };
  }

  /**
   * 创建批次
   */
  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  /**
   * 生成GraphQL查询
   */
  private generateQuery(entity: string): string {
    return `
      query Get${entity}s($filter: ${entity}Filter) {
        ${entity.toLowerCase()}s(filter: $filter) {
          id
          createdAt
          updatedAt
        }
      }
    `;
  }

  /**
   * 生成创建变更
   */
  private generateCreateMutation(entity: string): string {
    return `
      mutation Create${entity}($input: Create${entity}Input!) {
        create${entity}(input: $input) {
          id
          createdAt
          updatedAt
        }
      }
    `;
  }

  /**
   * 生成更新变更
   */
  private generateUpdateMutation(entity: string): string {
    return `
      mutation Update${entity}($id: ID!, $input: Update${entity}Input!) {
        update${entity}(id: $id, input: $input) {
          id
          createdAt
          updatedAt
        }
      }
    `;
  }

  /**
   * 生成删除变更
   */
  private generateDeleteMutation(entity: string): string {
    return `
      mutation Delete${entity}($id: ID!) {
        delete${entity}(id: $id) {
          id
        }
      }
    `;
  }

  /**
   * 生成唯一ID
   */
  private generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 加载操作队列
   */
  private async loadOperations(): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_OPERATIONS);
      if (data) {
        const operations = JSON.parse(data);
        Object.entries(operations).forEach(([id, operation]: [string, any]) => {
          this.operations.set(id, operation);
        });
      }
    } catch (error) {
      console.warn("加载离线操作失败:", error);
    }
  }

  /**
   * 保存操作队列
   */
  private async saveOperations(): Promise<void> {
    try {
      const operations: Record<string, OfflineOperation> = {};
      this.operations.forEach((value, key) => {
        operations[key] = value;
      });
      await AsyncStorage.setItem(
        STORAGE_KEYS.OFFLINE_OPERATIONS,
        JSON.stringify(operations)
      );
    } catch (error) {
      console.warn("保存离线操作失败:", error);
    }
  }

  /**
   * 加载离线数据
   */
  private async loadOfflineData(): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_DATA);
      if (data) {
        const offlineData = JSON.parse(data);
        Object.entries(offlineData).forEach(([key, value]: [string, any]) => {
          this.offlineData.set(key, value);
        });
      }
    } catch (error) {
      console.warn("加载离线数据失败:", error);
    }
  }

  /**
   * 保存离线数据
   */
  private async saveOfflineData(): Promise<void> {
    try {
      const data: Record<string, any> = {};
      this.offlineData.forEach((value, key) => {
        data[key] = value;
      });
      await AsyncStorage.setItem(
        STORAGE_KEYS.OFFLINE_DATA,
        JSON.stringify(data)
      );
    } catch (error) {
      console.warn("保存离线数据失败:", error);
    }
  }

  /**
   * 加载冲突数据
   */
  private async loadConflicts(): Promise<void> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.CONFLICTS);
      if (data) {
        const conflicts = JSON.parse(data);
        Object.entries(conflicts).forEach(([id, conflict]: [string, any]) => {
          this.conflicts.set(id, conflict);
        });
      }
    } catch (error) {
      console.warn("加载冲突数据失败:", error);
    }
  }

  /**
   * 保存冲突数据
   */
  private async saveConflicts(): Promise<void> {
    try {
      const conflicts: Record<string, ConflictData> = {};
      this.conflicts.forEach((value, key) => {
        conflicts[key] = value;
      });
      await AsyncStorage.setItem(
        STORAGE_KEYS.CONFLICTS,
        JSON.stringify(conflicts)
      );
    } catch (error) {
      console.warn("保存冲突数据失败:", error);
    }
  }

  /**
   * 获取同步状态
   */
  getSyncStatus(): SyncStatus {
    return this.syncStatus;
  }

  /**
   * 获取网络状态
   */
  getNetworkState(): NetworkState {
    return this.networkState;
  }

  /**
   * 获取操作队列统计
   */
  getOperationStats(): { total: number; byType: Record<string, number> } {
    const stats = {
      total: this.operations.size,
      byType: {} as Record<string, number>,
    };

    this.operations.forEach((operation) => {
      stats.byType[operation.type] = (stats.byType[operation.type] || 0) + 1;
    });

    return stats;
  }

  /**
   * 获取冲突列表
   */
  getConflicts(): ConflictData[] {
    return Array.from(this.conflicts.values());
  }

  /**
   * 清除所有数据
   */
  async clear(): Promise<void> {
    this.operations.clear();
    this.offlineData.clear();
    this.conflicts.clear();

    await Promise.all([
      AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_OPERATIONS),
      AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_DATA),
      AsyncStorage.removeItem(STORAGE_KEYS.CONFLICTS),
    ]);

    this.emit("cleared");
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    this.stopAutoSync();
    this.removeAllListeners();
    this.isInitialized = false;
  }
}

// 创建默认实例
export const offlineManager = new OfflineManager();
