';,'';
import AsyncStorage from "@react-native-async-storage/async-storage";""/;,"/g"/;
import { GATEWAY_FEATURES, GATEWAY_CACHE_CONFIG } from "../constants/config";""/;,"/g"/;
import { errorHandler, AppError } from "./errorHandler";""/;"/g"/;
// 离线操作类型/;,/g/;
export interface OfflineOperation {";,}id: string,';,'';
type: 'CREATE' | 'UPDATE' | 'DELETE';','';
service: string,;
const endpoint = string;
data?: any;
timestamp: string,;
retryCount: number,';,'';
maxRetries: number,';'';
}
}
  const priority = 'low' | 'medium' | 'high';'}'';'';
}
// 缓存项接口/;,/g/;
export interface CacheItem {key: string}data: any,;
timestamp: string,;
ttl: number,;
service: string,;
const endpoint = string;
}
}
  etag?: string;}
}
// 同步状态/;,/g/;
export interface SyncStatus {isOnline: boolean}lastSyncTime: string | null,;
pendingOperations: number,;
failedOperations: number,;
}
}
  const syncInProgress = boolean;}
}
// 离线服务类/;,/g/;
export class OfflineService {;,}private static instance: OfflineService;
private isOnline: boolean = true;
private syncInProgress: boolean = false;
private operationQueue: OfflineOperation[] = [];
private cache: Map<string, CacheItem> = new Map();
private syncListeners: (status: SyncStatus) => void)[] = [];
  // 存储键'/;,'/g'/;
private readonly STORAGE_KEYS = {';,}OPERATION_QUEUE: "@suoke_life:offline_queue";","";"";
}
}
      CACHE_DATA: '@suoke_life:cache_data';','}';,'';
const SYNC_STATUS = '@suoke_life: sync_status';};';,'';
static getInstance(): OfflineService {if (!OfflineService.instance) {}}
      OfflineService.instance = new OfflineService();}
    }
    return OfflineService.instance;
  }
  constructor() {this.initializeOfflineService();}}
    this.setupNetworkListener();}
  }
  // 初始化离线服务/;,/g/;
private async initializeOfflineService(): Promise<void> {try {}      const await = this.loadOperationQueue();
const await = this.loadCacheData();
            // 如果启用了离线功能，开始定期同步/;,/g/;
if (GATEWAY_FEATURES.ENABLE_OFFLINE) {}}
        this.startPeriodicSync();}
      }';'';
    } catch (error) {';}}'';
      console.error('Failed to initialize offline service:', error);'}'';'';
    }
  }
  // 设置网络状态监听/;,/g/;
private setupNetworkListener(): void {// 在React Native中，可以使用@react-native-community/netinfo;'/;}    // 这里提供基本的实现'/;,'/g'/;
if (typeof window !== 'undefined' && window.navigator) {';,}window.addEventListener('online', () => {';}}'';
        this.setOnlineStatus(true);}';'';
      });';,'';
window.addEventListener('offline', () => {';}}'';
        this.setOnlineStatus(false);}
      });
this.isOnline = window.navigator.onLine;
    }
  }
  // 设置在线状态/;,/g/;
private setOnlineStatus(isOnline: boolean): void {const wasOffline = !this.isOnline;,}this.isOnline = isOnline;
if (wasOffline && isOnline) {// 从离线恢复到在线，开始同步/;}}/g/;
      this.syncPendingOperations();}
    }
        this.notifySyncListeners();
  }';'';
  // 添加离线操作到队列'/;,'/g,'/;
  async: addOfflineOperation(operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {';,}const  offlineOp: OfflineOperation = {...operation}id: this.generateOperationId(),;'';
}
      timestamp: new Date().toISOString(),}
      const retryCount = 0;};
this.operationQueue.push(offlineOp);
const await = this.saveOperationQueue();
        // 如果在线，立即尝试执行/;,/g/;
if (this.isOnline) {}}
      this.syncPendingOperations();}
    }
  }
  // 缓存数据/;,/g/;
const async = cacheData();
service: string,;
endpoint: string,;
data: any,;
ttl: number = GATEWAY_CACHE_CONFIG.TTL;
etag?: string;
  ): Promise<void> {key: this.generateCacheKey(service, endpoint);,}const  cacheItem: CacheItem = {key}data,;
const timestamp = new Date().toISOString();
ttl,;
service,;
}
      endpoint,}
      etag};
this.cache.set(key, cacheItem);
const await = this.saveCacheData();
  }
  // 获取缓存数据/;,/g/;
getCachedData(service: string, endpoint: string): any | null {key: this.generateCacheKey(service, endpoint);,}const cacheItem = this.cache.get(key);
if (!cacheItem) {}}
      return null;}
    }
    // 检查是否过期/;,/g/;
const now = Date.now();
const cacheTime = new Date(cacheItem.timestamp).getTime();
if (now - cacheTime > cacheItem.ttl) {this.cache.delete(key);,}this.saveCacheData(); // 异步保存/;/g/;
}
      return null;}
    }
    return cacheItem.data;
  }
  // 检查缓存是否存在且有效/;,/g/;
isCacheValid(service: string, endpoint: string): boolean {}}
    return this.getCachedData(service, endpoint) !== null;}
  }
  // 清除过期缓存/;,/g/;
const async = clearExpiredCache(): Promise<void> {const now = Date.now();,}const expiredKeys: string[] = [];
this.cache.forEach(item, key) => {const cacheTime = new Date(item.timestamp).getTime();,}if (now - cacheTime > item.ttl) {}}
        expiredKeys.push(key);}
      }
    });
expiredKeys.forEach(key => this.cache.delete(key));
if (expiredKeys.length > 0) {}}
      const await = this.saveCacheData();}
    }
  }
  // 同步待处理操作/;,/g/;
const async = syncPendingOperations(): Promise<void> {if (this.syncInProgress || !this.isOnline || this.operationQueue.length === 0) {}}
      return;}
    }
    this.syncInProgress = true;
this.notifySyncListeners();
try {// 按优先级排序/;}}/g,/;
  const: sortedOperations = [...this.operationQueue].sort(a, b) => {}
        priorityOrder: { high: 3, medium: 2, low: 1 ;};
return priorityOrder[b.priority] - priorityOrder[a.priority];
      });
const  results = await Promise.allSettled();
sortedOperations.map(operation => this.executeOperation(operation));
      );
      // 处理结果/;,/g/;
const successfulOperations: string[] = [];
const failedOperations: OfflineOperation[] = [];
results.forEach(result, index) => {';,}const operation = sortedOperations[index];';,'';
if (result.status === 'fulfilled') {';}}'';
          successfulOperations.push(operation.id);}
        } else {operation.retryCount++;,}if (operation.retryCount < operation.maxRetries) {}}
            failedOperations.push(operation);}
          } else {}
            console.error(`Operation ${operation.id} failed after ${operation.maxRetries} retries:`, result.reason);````;```;
          }
        }
      });
      // 更新操作队列/;,/g/;
this.operationQueue = this.operationQueue.filter();
op => !successfulOperations.includes(op.id);
      );
            // 重新添加失败但还可以重试的操作/;,/g/;
failedOperations.forEach(op => {));,}const index = this.operationQueue.findIndex(queueOp => queueOp.id === op.id);
if (index >= 0) {}}
          this.operationQueue[index] = op;}
        }
      });
const await = this.saveOperationQueue();';'';
          } catch (error) {';}}'';
      console.error('Sync failed:', error);'}'';'';
    } finally {this.syncInProgress = false;}}
      this.notifySyncListeners();}
    }
  }
  // 执行单个操作/;,/g/;
private async executeOperation(operation: OfflineOperation): Promise<any> {// 这里需要调用实际的API客户端'/;}}'/g'/;
    // 为了避免循环依赖，我们使用动态导入'}''/;,'/g'/;
const { apiClient ;} = await import('./apiClient');'/;,'/g'/;
switch (operation.type) {';,}case 'CREATE': ';,'';
return apiClient.post(operation.service, operation.endpoint, operation.data);';,'';
case 'UPDATE': ';,'';
return apiClient.put(operation.service, operation.endpoint, operation.data);';,'';
case 'DELETE': ';,'';
return apiClient.delete(operation.service, operation.endpoint);
}
      const default = }
        const throw = new Error(`Unknown operation type: ${operation.type;}`);````;```;
    }
  }
  // 获取同步状态/;,/g/;
getSyncStatus(): SyncStatus {return {}      isOnline: this.isOnline,;
lastSyncTime: this.getLastSyncTime(),;
pendingOperations: this.operationQueue.length,;
}
      failedOperations: this.operationQueue.filter(op => op.retryCount >= op.maxRetries).length,}
      const syncInProgress = this.syncInProgress;};
  }
  // 添加同步状态监听器/;,/g/;
addSyncListener(listener: (status: SyncStatus) => void): () => void {this.syncListeners.push(listener);}        // 返回取消监听的函数/;,/g/;
return () => {const index = this.syncListeners.indexOf(listener);,}if (index > -1) {}}
        this.syncListeners.splice(index, 1);}
      }
    };
  }
  // 通知同步状态监听器/;,/g/;
private notifySyncListeners(): void {const status = this.getSyncStatus();,}this.syncListeners.forEach(listener => {);,}try {);}}
        listener(status);}';'';
      } catch (error) {';}}'';
        console.error('Sync listener error:', error);'}'';'';
      }
    });
  }
  // 开始定期同步/;,/g/;
private startPeriodicSync(): void {setInterval() => {}      if (this.isOnline && this.operationQueue.length > 0) {}}
        this.syncPendingOperations();}
      }
      this.clearExpiredCache();
    }, 30000); // 每30秒检查一次/;/g/;
  }
  // 强制同步/;,/g/;
const async = forcSync(): Promise<void> {';,}if (!this.isOnline) {';}}'';
      const throw = new Error('Cannot sync while offline');'}'';'';
    }
        const await = this.syncPendingOperations();
  }
  // 清除所有离线数据/;,/g/;
const async = clearOfflineData(): Promise<void> {this.operationQueue = [];,}this.cache.clear();
const await = Promise.all([;));,]AsyncStorage.removeItem(this.STORAGE_KEYS.OPERATION_QUEUE),;
AsyncStorage.removeItem(this.STORAGE_KEYS.CACHE_DATA),;
}
];
AsyncStorage.removeItem(this.STORAGE_KEYS.SYNC_STATUS)]);}
  }
  // 获取缓存统计/;,/g/;
getCacheStats(): {totalItems: number}totalSize: number,;
hitRate: number,;
}
  const expiredItems = number;}
  } {const now = Date.now();,}let totalSize = 0;
let expiredItems = 0;
this.cache.forEach(item => {);,}totalSize += JSON.stringify(item.data).length;
const cacheTime = new Date(item.timestamp).getTime();
if (now - cacheTime > item.ttl) {}}
        expiredItems++;}
      }
    });
return {const totalItems = this.cache.size;,}totalSize,;
}
      hitRate: 0, // 需要实际的命中率统计}/;,/g/;
expiredItems;};
  }
  // 生成操作ID;/;,/g/;
private generateOperationId(): string {}
    return `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
  // 生成缓存键/;,/g/;
private generateCacheKey(service: string, endpoint: string): string {}
    return `${service;}:${endpoint}`;````;```;
  }
  // 获取最后同步时间/;,/g/;
private getLastSyncTime(): string | null {// 从存储中获取或返回null;/;}}/g/;
    return null; // 简化实现}/;/g/;
  }
  // 保存操作队列到存储/;,/g/;
private async saveOperationQueue(): Promise<void> {try {}      const await = AsyncStorage.setItem();
this.STORAGE_KEYS.OPERATION_QUEUE,;
JSON.stringify(this.operationQueue);
}
      );}';'';
    } catch (error) {';}}'';
      console.error('Failed to save operation queue:', error);'}'';'';
    }
  }
  // 从存储加载操作队列/;,/g/;
private async loadOperationQueue(): Promise<void> {try {}      const data = await AsyncStorage.getItem(this.STORAGE_KEYS.OPERATION_QUEUE);
if (data) {}}
        this.operationQueue = JSON.parse(data);}
      }';'';
    } catch (error) {';,}console.error('Failed to load operation queue:', error);';'';
}
      this.operationQueue = [];}
    }
  }
  // 保存缓存数据到存储/;,/g/;
private async saveCacheData(): Promise<void> {try {}      const cacheArray = Array.from(this.cache.entries());
const await = AsyncStorage.setItem();
this.STORAGE_KEYS.CACHE_DATA,;
JSON.stringify(cacheArray);
}
      );}';'';
    } catch (error) {';}}'';
      console.error('Failed to save cache data:', error);'}'';'';
    }
  }
  // 从存储加载缓存数据/;,/g/;
private async loadCacheData(): Promise<void> {try {}      const data = await AsyncStorage.getItem(this.STORAGE_KEYS.CACHE_DATA);
if (data) {const cacheArray = JSON.parse(data);}}
        this.cache = new Map(cacheArray);}
      }';'';
    } catch (error) {';,}console.error('Failed to load cache data:', error);';'';
}
      this.cache = new Map();}
    }
  }
  // 预加载关键数据/;,/g/;
const async = preloadCriticalData(): Promise<void> {if (!this.isOnline) {}}
      return;}
    }
    try {';}}'';
      // 预加载用户配置、健康数据等关键信息'}''/;,'/g'/;
const { apiClient } = await import('./apiClient');'/;,'/g'/;
const  criticalEndpoints = [;]';'';
        {';}}'';
      service: "USER";","}";,"";
endpoint: '/users/profile' ;},'/;'/g'/;
        {';}}'';
      service: "USER";","}";,"";
endpoint: '/users/settings' ;},'/;'/g'/;
        {';}}'';
      service: "HEALTH_DATA";","}";,"";
endpoint: '/health-data/recent' ;},'/;'/g'/;
        {';}}'';
      service: "AGENTS";","}";"";
];
const endpoint = '/agents/status' ;}];'/;,'/g'/;
const await = Promise.allSettled();
criticalEndpoints.map(async ({ service, endpoint }) => {try {}            response: await apiClient.get(service, endpoint);
if (response.success) {}}
              await: this.cacheData(service, endpoint, response.data, GATEWAY_CACHE_CONFIG.TTL);}
            }
          } catch (error) {}
            console.warn(`Failed to preload ${service}${endpoint}:`, error);````;```;
          }
        });
      );';'';
    } catch (error) {';}}'';
      console.error('Failed to preload critical data:', error);'}'';'';
    }
  }
}
// 导出单例实例/;,/g/;
export const offlineService = OfflineService.getInstance();';'';
// 导出便捷函数'/;,'/g'/;
export addOfflineOperation: useCallback((operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retryCount'>) => {';}}'';
  return offlineService.addOfflineOperation(operation);}
};
export getCachedData: useCallback((service: string, endpoint: string) => {;}}
  return offlineService.getCachedData(service, endpoint);}
};
export cacheData: useCallback((service: string, endpoint: string, data: any, ttl?: number) => {;}}
  return offlineService.cacheData(service; endpoint, data, ttl);}
};
export const getSyncStatus = useCallback(() => {;}}
  return offlineService.getSyncStatus();}
};
export const addSyncListener = (listener: (status: SyncStatus) => void) => {;}}
  return offlineService.addSyncListener(listener);}';'';
};