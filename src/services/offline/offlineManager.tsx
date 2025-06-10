react";";
const importAsyncStorage = from "@react-native-async-storage/async-storage";/../graphql/client"; 索克生活 - 离线模式管理器   完整的离线数据存储和同步功能""/;"/g"/;
//;"/;,"/g"/;
y"; /    ""/;"/g"/;
// 离线操作接口 * export interface OfflineOperation {/;,}id: string,;,/g,/;
  type: OfflineOperationType,;
entity: string,;
data: unknown,;
timestamp: number,;
}
}
  retryCount: number,maxRetries: number,priority: number;}
}";"";
//;"/;,"/g"/;
d"; /    ""/;"/g"/;
//;"/;,"/g"/;
s"; /    ""/;"/g"/;
  | "server-wins"";"";
  | "merge"";"";
  | "manual";";"";
// 冲突数据接口 * export interface ConflictData {/;,}id: string,;,/g,/;
  entity: string,;
clientData: unknown,;
serverData: unknown,;
timestamp: number,;
}
}
  const strategy = ConflictResolutionStrategy;}
}
// 同步配置接口 * export interface SyncConfig {/;,}batchSize: number,;,/g,/;
  retryDelay: number,;
}
}
  maxRetries: number,conflictStrategy: ConflictResolutionStrategy,syncInterval: number;}
}
// 网络状态接口 * export interface NetworkState {/;,}isConnected: boolean,;,/g,/;
  connectionType: string,;
}
}
  const isInternetReachable = boolean;}
}";"";
//;"/;,"/g,"/;
  OFFLINE_OPERATIONS: "@suoke_offline_operations",OFFLINE_DATA: "@suoke_offline_data",SYNC_METADATA: "@suoke_sync_metadata",CONFLICTS: "@suoke_conflicts";};";,"";
export class OfflineManager extends EventEmitter   {private operations: Map<string, OfflineOperation> = new Map();,}private offlineData: Map<string, any> = new Map();";,"";
private conflicts: Map<string, ConflictData> = new Map();";,"";
private syncStatus: SyncStatus = "idle";
private networkState: NetworkState = {,";,}isConnected: false,";"";
}
    connectionType: "unknown";",}";
const isInternetReachable = false;}
  private syncConfig: SyncConfig = {batchSize: 10,;
retryDelay: 5000,";,"";
maxRetries: 3,";"";
}
    conflictStrategy: "client-wins";",}";
const syncInterval = 30000;}
  private syncTimer: number | null = null;
private isInitialized: boolean = false;
constructor(config?: Partial<SyncConfig  />) {/;}/        super();/;/g/;
}
    if (config) {}
      this.syncConfig = { ...this.syncConfig, ...config };
    }
  }
  // 初始化离线管理器  async initialize(): Promise<void> {/;,}if (this.isInitialized) retu;r;n;,/g/;
try {const await = Promise.all([;));,]this.loadOperations()}this.loadOfflineData(),;
];
this.loadConflicts();];);
this.setupNetworkListener();
this.startAutoSync();";,"";
this.isInitialized = true;";"";
}
this.emit("initialized");"}"";"";
      } catch (error) {}}
      const throw = error;}
    }
  }
  // 设置网络监听  private setupNetworkListener(): void {/;}/ 模拟网络状态变化* ///"/;,"/g,"/;
  isConnected: true,";"";
}
      connectionType: "wifi";",}";
const isInternetReachable = true;}";,"";
this.emit("networkStateChange", this.networkState);";"";
  }
  // 开始自动同步  private startAutoSync(): void {/;,}if (this.syncTimer) {}}/g/;
      clearInterval(this.syncTimer);}
    }
    this.syncTimer = setInterval() => {";}  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(offlineManager", {")";,}trackRender: true,;"";
}
    trackMemory: false,}";,"";
warnThreshold: 100, // ms ;};);"/;,"/g"/;
if (this.networkState.isConnected && this.syncStatus === "idle") {"}";
this.sync().catch(error) => {}
          });
      }
    }, this.syncConfig.syncInterval);
  }
  // 停止自动同步  private stopAutoSync(): void {/;,}if (this.syncTimer) {clearInterval(this.syncTimer);}}/g/;
      this.syncTimer = null;}
    }
  }
  // 添加离线操作  async addOperation(type: OfflineOperationType,)/;,/g,/;
  entity: string,;
data: unknown,;
priority: number = 5);: Promise<string>  {const operation: OfflineOperation = {id: this.generateId();,}type,;
entity,;
data,;
timestamp: Date.now(),;
retryCount: 0,;
const maxRetries = this.syncConfig.maxRetries;
}
      priority;}
    };
this.operations.set(operation.id, operation);";,"";
const await = this.saveOperations;(;)";,"";
this.emit("operationAdded", operation);";,"";
if (this.networkState.isConnected && this.syncStatus === "idle") {"}";
this.sync().catch(error) => {}
        });
    }
    return operation.;i;d;
  }
  // 存储离线数据  async storeData(key: string, data: unknown): Promise<void>  {/;,}this.offlineData.set(key, {);,}data,);/g/;
}
      timestamp: Date.now(),}
      const synced = false;});";,"";
const await = this.saveOfflineData;(;)";,"";
this.emit("dataStored", { key, data });";"";
  }
  // 获取离线数据  getData(key: string): unknown | null  {/;,}const item = this.offlineData.get(key);/g/;
}
    return item ? item.data : nu;l;l;}
  }
  // 删除离线数据  async removeData(key: string): Promise<void>  {/;,}this.offlineData.delete(key);";"/g"/;
}
    const await = this.saveOfflineData;(;)"}";
this.emit("dataRemoved", { key });";"";
  }";"";
  // 执行同步  async sync(): Promise<void> {/;}";,"/g"/;
if (this.syncStatus === "syncing") {";}}"";
      return;}
    }
    if (!this.networkState.isConnected) {}}
      return;}";"";
    }";,"";
this.syncStatus = "syncing";
this.emit("syncStart");";,"";
try {const sortedOperations = Array.from(this.operations.values).sort(;);}        (a, b) => a.priority - b.priority;
      );
const batches = this.createBatches(;);
sortedOperations,this.syncConfig.batchSiz;e;);
for (const batch of batches) {}};
const await = this.processBatch(batc;h;);}";"";
      }";,"";
this.syncStatus = "completed";
this.emit("syncComplete");";"";
    } catch (error) {";,}this.syncStatus = "error";
this.emit("syncError", error);";"";
}
      const throw = error;}
    }
  }
  // 处理操作批次  private async processBatch(operations: OfflineOperation[]): Promise<void>  {/;,}const promises = useMemo(() => operations.map(operatio;n;); =>;,/g/;
this.processOperation(operation);
    );
}
    await: Promise.allSettled(promise;s;), []);}
  }
  // 处理单个操作  private async processOperation(operation: OfflineOperation): Promise<void>  {/;,}try {const let = query: string;,}const let = variables: unknown;";,"/g"/;
switch (operation.type) {";,}case "create": ";"";
}
          query = this.generateCreateMutation(operation.entity);}
          variables = { input: operation.data;};";,"";
break;";,"";
case "update": ";,"";
query = this.generateUpdateMutation(operation.entity);
variables = { id: operation.data.id, input: operation.data;};";,"";
break;";,"";
case "delete": ";,"";
query = this.generateDeleteMutation(operation.entity);
variables = { id: operation.data.id;};";,"";
break;";,"";
case "query": ";,"";
query = this.generateQuery(operation.entity);
variables = operation.data;
break;

      }
      response: await graphqlClient.mutate(query, variab;l;e;s;);
if (response.data) {this.operations.delete(operation.id);";}}"";
        const await = this.saveOperations;(;)"}";
this.emit("operationSuccess", { operation, response });";"";
      } else {}}
}
      }
    } catch (error) {operation.retryCount++;,}if (operation.retryCount >= operation.maxRetries) {";}}"";
        this.operations.delete(operation.id);"}";
this.emit("operationFailed", { operation, error });";"";
      } else {";}}"";
        this.operations.set(operation.id, operation);"}";
this.emit("operationRetry", { operation, error });";"";
      }
      const await = this.saveOperations;
const throw = error;
    }
  }
  // 检测并解决冲突  async detectConflicts(entity: string,)/;,/g,/;
  clientData: unknown,;
const serverData = unknown);: Promise<ConflictData | null /    >  {/;,}const clientTimestamp = clientData.updatedAt || clientData.timestamp || ;0;,/g/;
const serverTimestamp = serverData.updatedAt || serverData.timestamp |;| ;0;
if (clientTimestamp !== serverTimestamp) {const conflict: ConflictData = {id: this.generateId();,}entity,;
clientData,;
serverData,;
}
        timestamp: Date.now(),}
        const strategy = this.syncConfig.conflictStrategy;};
this.conflicts.set(conflict.id, conflict);";,"";
const await = this.saveConflicts;(;)";,"";
this.emit("conflictDetected", conflict);";,"";
return confli;c;t;
    }
    return nu;l;l;
  }
  // 解决冲突  async resolveConflict(conflictId: string,)/;,/g/;
strategy?: ConflictResolutionStrategy;
  );: Promise<any>  {const conflict = this.conflicts.get(conflictI;d;);,}if (!conflict) {}}
}
    }
    const resolveStrategy = strategy || conflict.strate;g;y;
const let = resolvedData: unknown;";,"";
switch (resolveStrategy) {";,}case "client-wins": ";,"";
resolvedData = conflict.clientData;";,"";
break;";,"";
case "server-wins": ";,"";
resolvedData = conflict.serverData;";,"";
break;";,"";
case "merge": ";,"";
resolvedData = this.mergeData(conflict.clientData, conflict.serverData);";,"";
break;";,"";
case "manual": ";,"";
this.emit("manualResolutionRequired", conflict);";,"";
return confli;c;t;
}
}
    }
    this.conflicts.delete(conflictId);";,"";
const await = this.saveConflicts;(;)";,"";
this.emit("conflictResolved", { conflict, resolvedData });";,"";
return resolvedDa;t;a;
  }
  // 合并数据  private mergeData(clientData: unknown, serverData: unknown): unknown  {}/;,/g/;
return {...serverData,...clientData,updatedAt: Math.max(clientData.updatedAt || 0, serverData.updatedAt || 0);};
  }
  // 创建批次  private createBatches<T>(items: T[], batchSize: number): T[][]  {/;,}const batches: T[][] = [];,/g/;
for (let i = 0; i < items.length; i += batchSize) {}}
      batches.push(items.slice(i, i + batchSize););}
    }
    return batch;e;s;
  }
  // 生成GraphQL查询  private generateQuery(entity: string): string  {/;}}/g/;
    return `;``}```;,```;
const query = Get${entity}s($filter: ${entity;}Filter) {${entity.toLowerCase()}s(filter: $filter) {id;,}createdAt;
}
          updatedAt;}
        };}
    ;`;`````;```;
  }
  // 生成创建变更  private generateCreateMutation(entity: string): string  {/;}}/g/;
    return `;``}```;,```;
const mutation = Create${entity}($input: Create${entity;}Input!) {create${entity}(input: $input) {id;,}createdAt;
}
          updatedAt;}
        };}
    ;`;`````;```;
  }
  // 生成更新变更  private generateUpdateMutation(entity: string): string  {/;}}/g/;
    return `;``}```;,```;
mutation: Update${entity}($id: ID!, $input: Update${entity;}Input!) {update${entity}(id: $id, input: $input) {id;,}createdAt;
}
          updatedAt;}
        };}
    ;`;`````;```;
  }
  // 生成删除变更  private generateDeleteMutation(entity: string): string  {/;}}/g/;
    return `;``}```;,```;
const mutation = Delete${entity}($id: ID!) {delete${entity;}(id: $id) {id;}
        };}
    ;`;`````;```;
  }
  // 生成唯一ID  private generateId(): string {}/;,/g/;
return `${Date.now()}_${Math.random().toString(36).substr(2, 9)};`;````;```;
  }
  // 加载操作队列  private async loadOperations(): Promise<void> {/;,}try {const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_OPERATI;O;N;S;);,}if (data) {}}/g/;
        const operations = JSON.parse(dat;a;);}
        Object.entries(operations).forEach([id, operation]: [string, any]); => {}
          this.operations.set(id, operation);
        });
      }
    } catch (error) {}
      }
  }
  // 保存操作队列  private async saveOperations(): Promise<void> {/;}}/g/;
    try {}
      const operations: Record<string, OfflineOperation> = {;};
this.operations.forEach(value, key); => {}
        operations[key] = value;
      });
const await = AsyncStorage.setItem();
STORAGE_KEYS.OFFLINE_OPERATIONS,;
JSON.stringify(operation;s;);
      );
    } catch (error) {}
      }
  }
  // 加载离线数据  private async loadOfflineData(): Promise<void> {/;,}try {const data = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_D;A;T;A;);,}if (data) {}}/g/;
        const offlineData = JSON.parse(dat;a;);}
        Object.entries(offlineData).forEach([key, value]: [string, any]); => {}
          this.offlineData.set(key, value);
        });
      }
    } catch (error) {}
      }
  }
  // 保存离线数据  private async saveOfflineData(): Promise<void> {/;}}/g/;
    try {}
      const data: Record<string, any> = {;};
this.offlineData.forEach(value, key); => {}
        data[key] = value;
      });
const await = AsyncStorage.setItem();
STORAGE_KEYS.OFFLINE_DATA,;
JSON.stringify(dat;a;);
      );
    } catch (error) {}
      }
  }
  // 加载冲突数据  private async loadConflicts(): Promise<void> {/;,}try {const data = await AsyncStorage.getItem(STORAGE_KEYS.CONFLI;C;T;S;);,}if (data) {}}/g/;
        const conflicts = JSON.parse(dat;a;);}
        Object.entries(conflicts).forEach([id, conflict]: [string, any]); => {}
          this.conflicts.set(id, conflict);
        });
      }
    } catch (error) {}
      }
  }
  // 保存冲突数据  private async saveConflicts(): Promise<void> {/;}}/g/;
    try {}
      const conflicts: Record<string, ConflictData> = {;};
this.conflicts.forEach(value, key); => {}
        conflicts[key] = value;
      });
const await = AsyncStorage.setItem();
STORAGE_KEYS.CONFLICTS,;
JSON.stringify(conflict;s;);
      );
    } catch (error) {}
      }
  }
  // 获取同步状态  getSyncStatus(): SyncStatus {/;}}/g/;
    return this.syncStat;u;s;}
  }
  // 获取网络状态  getNetworkState(): NetworkState {/;}}/g/;
    return this.networkSta;t;e;}
  }
  // 获取操作队列统计  getOperationStats(): { total: number, byType: Record<string, number> ;} {/;}}/g,/;
  const: stats = {total: this.operations.size,}
      byType: {;} as Record<string, number;>;
    ;};
this.operations.forEach(operation); => {}
      stats.byType[operation.type] = (stats.byType[operation.type] || 0) + 1;
    });
return sta;t;s;
  }
  // 获取冲突列表  getConflicts(): ConflictData[] {/;}}/g/;
    return Array.from(this.conflicts.values);}
  }
  // 清除所有数据  async clear(): Promise<void> {/;,}this.operations.clear();,/g/;
this.offlineData.clear();
this.conflicts.clear();
const await = Promise.all([;));,]AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_OPERATIONS),;
AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_DATA),";"";
];
AsyncStorage.removeItem(STORAGE_KEYS.CONFLICTS);];)";"";
}
    this.emit("cleared");"}"";"";
  }
  // 销毁实例  destroy(): void {/;,}this.stopAutoSync();,/g/;
this.removeAllListeners();
}
    this.isInitialized = false;}
  }
}";"";
//   ;"/"/g"/;