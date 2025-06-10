import { offlineService } from "./offlineService";""/;,"/g"/;
import { analyticsService } from "./analyticsService";""/;,"/g"/;
import { GatewayApiClient } from "./apiClient";""/;"/g"/;
// 创建API客户端实例/;,/g/;
const gatewayApiClient = new GatewayApiClient();
// 同步状态枚举"/;,"/g"/;
export enum SyncStatus {';,}IDLE = 'idle',';,'';
SYNCING = 'syncing',';,'';
SUCCESS = 'success',';,'';
ERROR = 'error',';'';
}
}
  CONFLICT = 'conflict'}'';'';
}
// 数据实体接口/;,/g/;
export interface DataEntity {id: string}type: string,;
data: any,;
version: number,;
const lastModified = number;
}
}
  checksum?: string;}
}
// 同步冲突接口/;,/g/;
export interface SyncConflict {id: string}type: string,;
localData: DataEntity,';,'';
remoteData: DataEntity,';,'';
conflictType: 'version' | 'content' | 'deleted';','';'';
}
}
  const timestamp = number;}
}
// 同步结果接口/;,/g/;
export interface SyncResult {status: SyncStatus}synced: number,;
conflicts: SyncConflict[],;
errors: string[],;
duration: number,;
}
}
  const timestamp = number;}
}
// 同步配置接口/;,/g/;
interface SyncConfig {enabled: boolean}autoSync: boolean,;
syncInterval: number,';,'';
batchSize: number,';,'';
conflictResolution: 'local' | 'remote' | 'manual' | 'merge';','';
retryAttempts: number,;
}
}
  const retryDelay = number;}
}
// 同步事件接口'/;,'/g'/;
interface SyncEvent {';,}const type = 'start' | 'progress' | 'complete' | 'error' | 'conflict';';,'';
data?: any;
}
}
  const timestamp = number;}
}
class SyncService {private config: SyncConfig;,}private syncTimer?: NodeJS.Timeout;
private isSyncing = false;
private lastSyncTime = 0;
private conflicts: SyncConflict[] = [];
private listeners: (event: SyncEvent) => void)[] = [];
constructor() {this.config = {}      enabled: true,;
autoSync: true,;
syncInterval: 300000, // 5分钟'/;,'/g,'/;
  batchSize: 50,';,'';
conflictResolution: 'manual';','';
retryAttempts: 3,;
}
}
      const retryDelay = 5000;}
    };
this.initializeAutoSync();
this.setupNetworkListener();
  }
  // 初始化自动同步/;,/g/;
private initializeAutoSync() {if (this.config.autoSync && this.config.enabled) {}}
      this.startAutoSync();}
    }
  }
  // 设置网络监听器'/;,'/g'/;
private setupNetworkListener() {';,}if (typeof window !== 'undefined' && 'navigator' in window) {';,}window.addEventListener('online', () => {';,}this.emitEvent({)';}}'';
      type: "start";",)"}";
const timestamp = Date.now() ;});
this.sync();
      });
    }
  }
  // 启动自动同步/;,/g/;
startAutoSync() {if (this.syncTimer) {}}
      clearInterval(this.syncTimer);}
    }
    this.syncTimer = setInterval() => {if (navigator.onLine && !this.isSyncing) {}}
        this.sync();}
      }
    }, this.config.syncInterval);
  }
  // 停止自动同步/;,/g/;
stopAutoSync() {if (this.syncTimer) {}      clearInterval(this.syncTimer);
}
      this.syncTimer = undefined;}
    }
  }
  // 添加事件监听器/;,/g/;
addEventListener(listener: (event: SyncEvent) => void) {}}
    this.listeners.push(listener);}
  }
  // 移除事件监听器/;,/g/;
removeEventListener(listener: (event: SyncEvent) => void) {const index = this.listeners.indexOf(listener);,}if (index > -1) {}}
      this.listeners.splice(index, 1);}
    }
  }
  // 发送事件/;,/g/;
private emitEvent(event: SyncEvent) {this.listeners.forEach(listener => {);,}try {);}}
        listener(event);}";"";
      } catch (error) {";}}"";
        console.error('Sync event listener error:', error);'}'';'';
      }
    });
  }
  // 主同步方法/;,/g/;
const async = sync(): Promise<SyncResult> {';,}if (this.isSyncing) {';}}'';
      const throw = new Error('Sync already in progress');'}'';'';
    }';,'';
if (!navigator.onLine) {';}}'';
      const throw = new Error('No network connection');'}'';'';
    }
    this.isSyncing = true;
const startTime = Date.now();';,'';
this.emitEvent({))';}}'';
      type: "start";",)"}";
const timestamp = startTime ;});
try {const result = await this.performSync();,}this.lastSyncTime = Date.now();";,"";
this.emitEvent({")"";,}type: "complete";",")";
data: result;),;
}
        const timestamp = Date.now()}";"";
      ;});";,"";
analyticsService.trackEvent('system', {)';,}action: "sync_complete";",";
duration: result.duration,);
synced: result.synced,);
}
        const conflicts = result.conflicts.length;)}
      });
return result;
    } catch (error) {const: errorResult: SyncResult = {status: SyncStatus.ERROR,;
synced: 0,;
conflicts: [],;
errors: [error instanceof Error ? error.message : String(error)],;
duration: Date.now() - startTime,;
}
        const timestamp = Date.now()}
      ;};";,"";
this.emitEvent({)")"";,}type: "error";",")";
data: error;),;
}
        const timestamp = Date.now()}
      ;});";,"";
analyticsService.trackError(error instanceof Error ? error : new Error(String(error)), {";}}"";
        const context = 'sync_service'}'';'';
      ;});
return errorResult;
    } finally {}}
      this.isSyncing = false;}
    }
  }
  // 执行同步逻辑/;,/g/;
private async performSync(): Promise<SyncResult> {const startTime = Date.now();,}let syncedCount = 0;
const conflicts: SyncConflict[] = [];
const errors: string[] = [];
try {// 1. 获取本地待同步数据/;,}const localData = await this.getLocalPendingData();/g/;
            // 2. 获取远程数据变更/;,/g/;
const remoteChanges = await this.getRemoteChanges();
            // 3. 上传本地数据/;,/g/;
const uploadResult = await this.uploadLocalData(localData);
syncedCount += uploadResult.synced;
conflicts.push(...uploadResult.conflicts);
errors.push(...uploadResult.errors);
      // 4. 下载远程数据/;,/g/;
const downloadResult = await this.downloadRemoteData(remoteChanges);
syncedCount += downloadResult.synced;
conflicts.push(...downloadResult.conflicts);
errors.push(...downloadResult.errors);
      // 5. 处理冲突/;,/g/;
if (conflicts.length > 0) {}}
        const await = this.handleConflicts(conflicts);}
      }
      const  status = conflicts.length > 0 ? SyncStatus.CONFLICT : ;
errors.length > 0 ? SyncStatus.ERROR : SyncStatus.SUCCESS;
return {status}const synced = syncedCount;
conflicts,;
errors,;
duration: Date.now() - startTime,;
}
        const timestamp = Date.now()}
      ;};
    } catch (error) {}}
      const throw = error;}
    }
  }
  // 获取本地待同步数据/;,/g/;
private async getLocalPendingData(): Promise<DataEntity[]> {const syncStatus = offlineService.getSyncStatus();,}const entities: DataEntity[] = [];
    // 由于OfflineService没有直接的getPendingOperations方法，/;/g/;
    // 我们使用同步状态中的待处理操作数量作为参考/;/g/;
    // 实际实现中需要扩展OfflineService来提供操作列表/;/g/;
        // 临时实现：从本地存储获取操作'/;,'/g'/;
try {';,}const storedOperations = localStorage.getItem('@suoke_life:offline_queue');';,'';
if (storedOperations) {const operations = JSON.parse(storedOperations);,}for (const operation of operations) {try {;,}const: entity: DataEntity = {id: operation.id,;
type: operation.type,;
data: operation.data,;
version: 1,;
lastModified: new Date(operation.timestamp).getTime(),;
}
              const checksum = this.calculateChecksum(operation.data)}
            ;};
entities.push(entity);';'';
          } catch (error) {';}}'';
            console.error('Error processing local operation:', error);'}'';'';
          }
        }
      }';'';
    } catch (error) {';}}'';
      console.error('Error loading pending operations:', error);'}'';'';
    }
    return entities;
  }
  // 获取远程数据变更/;,/g/;
private async getRemoteChanges(): Promise<DataEntity[]> {';,}try {';,}const: response = await gatewayApiClient.get("sync",/changes', {')'/;,}const headers = {)';}}'/g'/;
          'Last-Sync-Time': this.lastSyncTime.toString()'}'';'';
        ;}
      });
return response.data.changes || [];';'';
    } catch (error) {';,}console.error('Error fetching remote changes:', error);';'';
}
      return [];}
    }
  }
  // 上传本地数据/;,/g/;
private async uploadLocalData(entities: DataEntity[]): Promise<{synced: number,;
conflicts: SyncConflict[],;
}
  const errors = string[];}
  }> {let synced = 0;,}const conflicts: SyncConflict[] = [];
const errors: string[] = [];
    // 分批处理/;,/g/;
for (let i = 0; i < entities.length; i += this.config.batchSize) {batch: entities.slice(i, i + this.config.batchSize);';,}try {';,}const: response = await gatewayApiClient.post("sync",/upload', {')''/;}}'/g'/;
          const entities = batch;)}
        });
const result = response.data;
synced += result.synced || 0;
if (result.conflicts) {}}
          conflicts.push(...result.conflicts);}
        }
                // 标记已同步的操作为完成/;/g/;
        // 注意：OfflineService没有markOperationCompleted方法/;/g/;
        // 实际实现中需要扩展OfflineService来支持此功能/;,/g/;
for (const entity of batch) {;,}if (!result.conflicts?.some(c: any) => c.id === entity.id)) {// 临时实现：从本地存储中移除已完成的操作'/;,}try {';,}const storedOperations = localStorage.getItem('@suoke_life:offline_queue');';,'/g'/;
if (storedOperations) {const operations = JSON.parse(storedOperations);';,}const updatedOperations = operations.filter(op: any) => op.id !== entity.id);';'';
}
                localStorage.setItem('@suoke_life:offline_queue', JSON.stringify(updatedOperations));'}'';'';
              }';'';
            } catch (error) {';}}'';
              console.error('Error marking operation as completed:', error);'}'';'';
            }
          }
        }';,'';
this.emitEvent({)')'';}}'';
      type: "progress";",")}";
data: { uploaded: synced, total: entities.length ;},);
const timestamp = Date.now();
        ;});
      } catch (error) {}}
        const errorMsg = error instanceof Error ? error.message : String(error);}";,"";
errors.push(`Upload batch error: ${errorMsg;}`);``"`;,```;
console.error('Upload batch error:', error);';'';
      }
    }
    return { synced, conflicts, errors };
  }
  // 下载远程数据/;,/g/;
private async downloadRemoteData(entities: DataEntity[]): Promise<{synced: number,;
conflicts: SyncConflict[],;
}
  const errors = string[];}
  }> {let synced = 0;,}const conflicts: SyncConflict[] = [];
const errors: string[] = [];
for (const entity of entities) {try {}        // 检查本地是否有相同数据/;,/g,/;
  localEntity: await this.getLocalEntity(entity.id, entity.type);
if (localEntity) {// 检查冲突/;,}conflict: this.detectConflict(localEntity, entity);,/g/;
if (conflict) {conflicts.push(conflict);}}
            continue;}
          }
        }
        // 保存到本地/;,/g/;
const await = this.saveLocalEntity(entity);
synced++;';,'';
this.emitEvent({)')'';}}'';
      type: "progress";",")}";
data: { downloaded: synced, total: entities.length ;},);
const timestamp = Date.now();
        ;});
      } catch (error) {}}
        const errorMsg = error instanceof Error ? error.message : String(error);}";,"";
errors.push(`Download entity error: ${errorMsg;}`);``"`;,```;
console.error('Download entity error:', error);';'';
      }
    }
    return { synced, conflicts, errors };
  }
  // 检测冲突/;,/g/;
private detectConflict(local: DataEntity, remote: DataEntity): SyncConflict | null {// 版本冲突/;,}if (local.version !== remote.version) {return {}        id: local.id,;,/g,/;
  type: local.type,;
localData: local,';,'';
remoteData: remote,';,'';
conflictType: 'version';','';'';
}
        const timestamp = Date.now()}
      ;};
    }
    // 内容冲突/;,/g/;
if (local.checksum !== remote.checksum) {return {}        id: local.id,;
type: local.type,;
localData: local,';,'';
remoteData: remote,';,'';
conflictType: 'content';','';'';
}
        const timestamp = Date.now()}
      ;};
    }
    return null;
  }
  // 处理冲突/;,/g/;
private async handleConflicts(conflicts: SyncConflict[]) {this.conflicts.push(...conflicts);,}for (const conflict of conflicts) {';,}this.emitEvent({')'';,}type: "conflict";",")";
data: conflict;),;
}
        const timestamp = Date.now()}
      ;});";"";
      // 根据配置自动解决冲突"/;,"/g"/;
if (this.config.conflictResolution !== 'manual') {';}}'';
        await: this.resolveConflict(conflict, this.config.conflictResolution);}
      }
    }
  }';'';
  // 解决冲突'/;,'/g,'/;
  async: resolveConflict(conflict: SyncConflict, resolution: 'local' | 'remote' | 'merge') {';,}try {const let = resolvedEntity: DataEntity;';,}switch (resolution) {';,}case 'local': ';,'';
resolvedEntity = conflict.localData;';,'';
break;';,'';
case 'remote': ';,'';
resolvedEntity = conflict.remoteData;';,'';
break;';,'';
case 'merge': ';,'';
resolvedEntity = await this.mergeEntities(conflict.localData, conflict.remoteData);
break;
}
        const default = }
          const throw = new Error(`Unknown resolution strategy: ${resolution;}`);````;```;
      }
      // 保存解决后的数据/;,/g/;
const await = this.saveLocalEntity(resolvedEntity);';'';
            // 上传到服务器'/;,'/g,'/;
  await: gatewayApiClient.post("sync",/resolve', {/;)')'';,}conflictId: conflict.id,);'/g'/;
}
        const resolution = resolvedEntity;)}
      });
      // 从冲突列表中移除/;,/g/;
const index = this.conflicts.findIndex(c => c.id === conflict.id);
if (index > -1) {}}
        this.conflicts.splice(index, 1);}';'';
      }';,'';
analyticsService.trackEvent('system', {)';,}action: "conflict_resolved";",")";
const conflictType = conflict.conflictType;);
}
        resolution;)}
      });";"";
    } catch (error) {";,}console.error('Error resolving conflict:', error);';'';
}
      const throw = error;}
    }
  }
  // 合并实体/;,/g/;
private async mergeEntities(local: DataEntity, remote: DataEntity): Promise<DataEntity> {// 简单的合并策略：使用最新的时间戳/;,}const  merged: DataEntity = {...local}version: Math.max(local.version, remote.version) + 1,;/g/;
}
      const lastModified = Date.now()}
    ;};';'';
    // 合并数据字段'/;,'/g'/;
if (typeof local.data === 'object' && typeof remote.data === 'object') {'}'';
merged.data = { ...local.data, ...remote.data };
    } else {// 使用时间戳较新的数据/;}}/g/;
      merged.data = local.lastModified > remote.lastModified ? local.data : remote.data;}
    }
    merged.checksum = this.calculateChecksum(merged.data);
return merged;
  }
  // 获取本地实体/;,/g/;
private async getLocalEntity(id: string, type: string): Promise<DataEntity | null> {}}
    try {}
      const key = `entity_${type;}_${id}`;````;,```;
const cached = localStorage.getItem(key);
return cached ? JSON.parse(cached) : null;';'';
    } catch (error) {';,}console.error('Error getting local entity:', error);';'';
}
      return null;}
    }
  }
  // 保存本地实体/;,/g/;
private async saveLocalEntity(entity: DataEntity) {}}
    try {}
      const key = `entity_${entity.type;}_${entity.id}`;````;,```;
localStorage.setItem(key, JSON.stringify(entity));';'';
    } catch (error) {';,}console.error('Error saving local entity:', error);';'';
}
      const throw = error;}
    }
  }
  // 计算校验和/;,/g/;
private calculateChecksum(data: any): string {const str = JSON.stringify(data);,}let hash = 0;
for (let i = 0; i < str.length; i++) {const char = str.charCodeAt(i);,}hash = (hash << 5) - hash) + char;
}
      hash = hash & hash; // 转换为32位整数}/;/g/;
    }
    return hash.toString(16);
  }
  // 获取同步状态/;,/g/;
getSyncStatus(): {isSyncing: boolean}lastSyncTime: number,;
conflicts: number,;
}
  const autoSync = boolean;}
  } {return {}      isSyncing: this.isSyncing,;
lastSyncTime: this.lastSyncTime,;
conflicts: this.conflicts.length,;
}
      const autoSync = this.config.autoSync;}
    };
  }
  // 获取冲突列表/;,/g/;
getConflicts(): SyncConflict[] {}}
    return [...this.conflicts];}
  }
  // 强制同步/;,/g/;
const async = forcSync(): Promise<SyncResult> {this.lastSyncTime = 0; // 重置最后同步时间以获取所有数据/;}}/g/;
    return this.sync();}
  }
  // 更新配置/;,/g/;
updateConfig(newConfig: Partial<SyncConfig>) {}
    this.config = { ...this.config, ...newConfig ;};
if (newConfig.autoSync !== undefined) {if (newConfig.autoSync) {}}
        this.startAutoSync();}
      } else {}}
        this.stopAutoSync();}
      }
    }
  }
  // 获取配置/;,/g/;
getConfig(): SyncConfig {}
    return { ...this.config };
  }
  // 清理资源/;,/g/;
destroy() {this.stopAutoSync();,}this.listeners = [];
}
    this.conflicts = [];}
  }
}
// 导出单例实例'/;,'/g'/;
export const syncService = new SyncService();