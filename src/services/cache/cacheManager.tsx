react";";
const importAsyncStorage = from "@react-native-async-storage/async-storage";/import { EventEmitter } from "../../utils/eventEmitter"; 索克生活 - 缓存管理器   完整的多层缓存策略和管理系统"/;"/g"/;
//;"/;,"/g"/;
u;";"";
  | "ttl"";"";
  | "lfu"";"";
  | "fifo"";"";
  | "memory"";"";
  | "persistent";";"";
///     > {/;,}key: string;/g/;
* , value: T,;
const timestamp = number;
ttl?: number;
accessCount: number,;
}
  lastAccessed: number,}
  const size = number;}
// 缓存配置接口 * export interface CacheConfig {/;};,/g,/;
  strategy: CacheStrategy,   ;
}
}
  maxSize: number;  maxMemory: number  / 最大内存使用量（字节）*  persistent: boolean  * / 是否持久化*  , cleanupInterval: number  * / 清理间隔（毫秒）* //;}/;/g/;
} * //;/g/;
// 缓存统计接口 * export interface CacheStats {/;,}size: number,;,/g,/;
  memoryUsage: number,;
hitRate: number,;
missRate: number,;
totalHits: number,totalMisses: number,totalRequests: number;
oldestItem?: number;
}
}
  newestItem?: number;}
}
///     > {/;,}key: string,;,/g,/;
  value: CacheItem<T>,;
}
  prev: LRUNode<T> | null,}
  const next = LRUNode<T> | null;}
export class CacheManager<T = any  /> extends EventEmitter {/;}/  private cache: Map<string, CacheItem<T> /    > = new Map();/;/g/;
/      private config: CacheConfig;/;,/g/;
private stats: CacheStats = {size: 0,;
memoryUsage: 0,;
hitRate: 0,;
missRate: 0,;
totalHits: 0,;
totalMisses: 0,;
}
    const totalRequests = 0;}
  };
private lruHead: LRUNode<T  /     > | null = null;/;,/g/;
private lruTail: LRUNode<T> | null = null;
private lruMap: Map<string, LRUNode<T> /> = new Map();//;,/g/;
private cleanupTimer: number | null = null;
constructor(config: Partial<CacheConfig  /> = {;}) {/;}/        super();"/;,"/g"/;
this.config = {;";,}strategy: "lru";",";
maxSize: 1000,";,"";
maxMemory: 50 * 1024 * 1024,  defaultTTL: 300000,  / 5分钟* ///"/;,"/g,"/;
  storageKey: "@suoke_cache";","";"";
}
      cleanupInterval: 60000,  ...config;}
    }
    this.initialize();
  }
  // 初始化缓存管理器  private async initialize(): Promise<void> {/;,}if (this.config.persistent) {}}/g/;
      const await = this.loadFromStorage;}
    }";,"";
this.startCleanupTimer();";,"";
this.emit("initialized");";"";
  }
  ///;,/g,/;
  const: item: CacheItem<T> = {key}value,;
timestamp: Date.now(),;
ttl: ttl || this.config.defaultTTL,;
accessCount: 0,;
}
      lastAccessed: Date.now(),}
      const size = this.calculateSize(value);};
if (this.stats.memoryUsage + item.size > this.config.maxMemory) {}}
      const await = this.evictItems(item.size;);}
    }";,"";
switch (this.config.strategy) {";,}case "lru": ";,"";
this.setLRU(key, item);";,"";
break;";,"";
case "lfu": ";,"";
this.setLFU(key, item);";,"";
break;";,"";
case "fifo": ";,"";
this.setFIFO(key, item);
break;
}
      default: this.cache.set(key, item);}
    }";,"";
this.updateStats();";,"";
this.emit("set", { key, value, item });";,"";
if (this.config.persistent) {}}
      const await = this.saveToStorage;}
    }
  }
  ///    >  {/;,}this.stats.totalRequests++;,/g/;
const item = this.cache.get(key);
if (!item) {this.stats.totalMisses++;";}}"";
      this.updateHitRate();"}";
this.emit("miss", { key });";,"";
return nu;l;l;
    }
    if (this.isExpired(item)) {const await = this.delete(key);,}this.stats.totalMisses++;";"";
}
      this.updateHitRate();"}";
this.emit("expired", { key, item });";,"";
return nu;l;l;
    }
    item.accessCount++";,"";
item.lastAccessed = Date.now();";,"";
if (this.config.strategy === "lru") {";"";}}"";
      this.moveToHead(key);}
    }
    this.stats.totalHits++;";,"";
this.updateHitRate();";,"";
this.emit("hit", { key, value: item.value, item ;});";,"";
return item.val;u;e;
  }
  // 删除缓存项  async delete(key: string): Promise<boolean>  {/;,}const item = this.cache.get(key);,/g/;
if (!item) return f;a;l;s;e;";,"";
this.cache.delete(key);";,"";
if (this.config.strategy === "lru") {";"";}}"";
      this.removeLRUNode(key);}
    }
    this.stats.memoryUsage -= item.size;";,"";
this.updateStats();";,"";
this.emit("delete", { key, item });";,"";
if (this.config.persistent) {}}
      const await = this.saveToStorage;}
    }
    return tr;u;e;
  }
  // 检查缓存项是否存在  has(key: string): boolean  {/;}}/g/;
    const item = this.cache.get(key);}
    return item ? !this.isExpired(ite;m;);: false}
  // 清空缓存  async clear(): Promise<void>  {/;,}this.cache.clear();,/g/;
this.lruMap.clear();
this.lruHead = null;
this.lruTail = null;
this.stats = {;,}size: 0,;
memoryUsage: 0,;
hitRate: 0,;
missRate: 0,;
totalHits: 0,;
totalMisses: 0,;
}
      const totalRequests = 0;}";"";
    }";,"";
this.emit("clear");";,"";
if (this.config.persistent) {}}
      const await = AsyncStorage.removeItem(this.config.storageKe;y;);}
    }
  }
  // 获取缓存大小  size(): number {/;}}/g/;
    return this.cache.si;z;e;}
  }
  // 获取所有键  keys(): string[] {/;}}/g/;
    return Array.from(this.cache.keys);}
  }
  // 获取所有值  values(): T[] {/;}}/g/;
    return Array.from(this.cache.values).map(item); => item.value);}
  }
  // 获取缓存统计  getStats(): CacheStats {}/;,/g/;
return { ...this.stat;s ;};
  }";"";
  ///        this.config = { ...this.config, ...config };"/;,"/g"/;
this.emit("configChanged", this.config);";"";
  }
  // LRU设置  private setLRU(key: string, item: CacheItem<T>): void  {/;,}if (this.cache.has(key)) {}}/g/;
      this.removeLRUNode(key);}
    }
    if (this.cache.size >= this.config.maxSize) {}}
      this.evictLRU();}
    }
    this.cache.set(key, item);
this.addToHead(key, item);
  }
  // LFU设置  private setLFU(key: string, item: CacheItem<T>): void  {/;,}if (this.cache.size >= this.config.maxSize) {}}/g/;
      this.evictLFU();}
    }
    this.cache.set(key, item);
  }
  // FIFO设置  private setFIFO(key: string, item: CacheItem<T>): void  {/;,}if (this.cache.size >= this.config.maxSize) {}}/g/;
      this.evictFIFO();}
    }
    this.cache.set(key, item);
  }
  // 添加到LRU头部  private addToHead(key: string, item: CacheItem<T>): void  {/;,}const: node: LRUNode<T> = {key}value: item,;,/g,/;
  prev: null,;
}
      const next = this.lruHead;}
    };
if (this.lruHead) {}}
      this.lruHead.prev = node;}
    }
    this.lruHead = node;
if (!this.lruTail) {}}
      this.lruTail = node;}
    }
    this.lruMap.set(key, node);
  }
  // 移动到LRU头部  private moveToHead(key: string): void  {/;,}const node = this.lruMap.get(key);,/g/;
if (!node || node === this.lruHead) retu;r;n;
if (node.prev) {}}
      node.prev.next = node.next;}
    }
    if (node.next) {}}
      node.next.prev = node.prev;}
    }
    if (node === this.lruTail) {;}}
      this.lruTail = node.prev;}
    }
    node.prev = null;
node.next = this.lruHead;
if (this.lruHead) {}}
      this.lruHead.prev = node;}
    }
    this.lruHead = node;
  }
  // 移除LRU节点  private removeLRUNode(key: string): void  {/;,}const node = this.lruMap.get(key);,/g/;
if (!node) retu;r;n;
if (node.prev) {}}
      node.prev.next = node.next;}
    } else {}}
      this.lruHead = node.next;}
    }
    if (node.next) {}}
      node.next.prev = node.prev;}
    } else {}}
      this.lruTail = node.prev;}
    }
    this.lruMap.delete(key);
  }
  // LRU淘汰  private evictLRU(): void {/;,}if (!this.lruTail) retu;r;n;,/g/;
const key = this.lruTail.k;e;y;
const item = this.cache.get(key);
this.cache.delete(key);
this.removeLRUNode(key);
if (item) {";}}"";
      this.stats.memoryUsage -= item.size;"}";
this.emit("evicted", { key, item, reason: "lru";});";"";
    }
  }
  // LFU淘汰  private evictLFU(): void {/;,}let minAccessCount = Infini;t;y;,/g/;
const let = evictKey = ;
for (const [key, item] of this.cache) {if (item.accessCount < minAccessCount) {;,}minAccessCount = item.accessCount;
}
        evictKey = key;}
      }
    }
    if (evictKey) {const item = this.cache.get(evictKe;y;);,}this.cache.delete(evictKey);
if (item) {";}}"";
        this.stats.memoryUsage -= item.size;"}";
this.emit("evicted", { key: evictKey, item, reason: "lfu";});";"";
      }
    }
  }
  // FIFO淘汰  private evictFIFO(): void {/;,}let oldestTimestamp = Infini;t;y;,/g/;
const let = evictKey = ;
for (const [key, item] of this.cache) {if (item.timestamp < oldestTimestamp) {;,}oldestTimestamp = item.timestamp;
}
        evictKey = key;}
      }
    }
    if (evictKey) {const item = this.cache.get(evictKe;y;);,}this.cache.delete(evictKey);
if (item) {";}}"";
        this.stats.memoryUsage -= item.size;"}";
this.emit("evicted", { key: evictKey, item, reason: "fifo";});";"";
      }
    }
  }
  // 淘汰项目以释放内存  private async evictItems(requiredSize: number): Promise<void>  {/;,}let freedSize = 0;,/g/;
const itemsToEvict: string[] = [];";,"";
switch (this.config.strategy) {";,}case "lru": ";,"";
let current = this.lruTai;l;
while (current && freedSize < requiredSize) {const item = this.cache.get(current.key);,}if (item) {freedSize += item.size;}}
            itemsToEvict.push(current.key);}
          }
          current = current.prev;
        }";,"";
break;";,"";
case "lfu": ";,"";
const sortedByAccess = Array.from(this.cache.entries).sort(;);
          ([ a], [ b]); => a.accessCount - b.accessCount;
        );
for (const [key, item] of sortedByAccess) {;,}if (freedSize >= requiredSize) bre;a;k;
freedSize += item.size;
}
          itemsToEvict.push(key);}
        }";,"";
break;";,"";
case "fifo": ";,"";
const sortedByTime = Array.from(this.cache.entries).sort(;);
          ([ a], [ b]); => a.timestamp - b.timestamp;
        );
for (const [key, item] of sortedByTime) {;,}if (freedSize >= requiredSize) bre;a;k;
freedSize += item.size;
}
          itemsToEvict.push(key);}
        }
        break;
    }
    for (const key of itemsToEvict) {}};
const await = this.delete(key;);}
    }
  }
  // 检查是否过期  private isExpired(item: CacheItem<T>): boolean  {/;,}if (!item.ttl) return f;a;l;s;e;/g/;
}
    return Date.now - item.timestamp > item.ttl;}
  }
  // 计算数据大小  private calculateSize(value: T): number  {/;}}/g/;
    try {}
      return JSON.stringify(value).length ;* ;2;  } catch {}
      return 102;4;  }
  }
  // 更新统计信息  private updateStats(): void {/;,}this.stats.size = this.cache.size;,/g/;
this.stats.memoryUsage = Array.from(this.cache.values();).reduce(total, item); => total + item.size,;
      0;
    );
if (this.cache.size > 0) {const timestamps = Array.from(this.cache.values).map(;);}        (item); => item.timestamp;
      );
this.stats.oldestItem = Math.min(...timestamps);
}
      this.stats.newestItem = Math.max(...timestamps);}
    }
  }
  // 更新命中率  private updateHitRate(): void {/;}}/g/;
    if (this.stats.totalRequests > 0) {}
      this.stats.hitRate = this.stats.totalHits / this.stats.totalRequests;/      this.stats.missRate = this.stats.totalMisses / this.stats.totalRequests;/        }/;/g/;
  }
  // 开始清理定时器  private startCleanupTimer(): void {/;,}if (this.cleanupTimer) {}}/g/;
      clearInterval(this.cleanupTimer);}
    }
    this.cleanupTimer = setInterval() => {;";}  // 性能监控"/;,"/g,"/;
  performanceMonitor: usePerformanceMonitor(cacheManager", {")";"";}}"";
    trackRender: true,}
    trackMemory: false,warnThreshold: 100, // ms ;};);/;,/g/;
this.cleanup();
    }, this.config.cleanupInterval);
  }
  // 清理过期项目  private async cleanup(): Promise<void> {/;,}const expiredKeys: string[] = [];,/g/;
for (const [key, item] of this.cache) {;,}if (this.isExpired(item);) {}}
        expiredKeys.push(key);}
      }
    }
    for (const key of expiredKeys) {}};
const await = this.delete(key);}
    }";,"";
if (expiredKeys.length > 0) {"}";
this.emit("cleanup", { expiredCount: expiredKeys.length;});";"";
    }
  }
  // 从存储加载  private async loadFromStorage(): Promise<void> {/;,}try {const data = await AsyncStorage.getItem(this.config.storage;K;e;y;);,}if (data) {const parsed = JSON.parse(dat;a;);,}for (const [key, item] of Object.entries(parsed);) {if (!this.isExpired(item as CacheItem<T>);) {}}/g/;
            this.cache.set(key, item as CacheItem<T>);}
          }
        }";,"";
this.updateStats();";,"";
this.emit("loaded", { count: this.cache.size;});";"";
      }
    } catch (error) {}
      }
  }
  // 保存到存储  private async saveToStorage(): Promise<void> {/;}}/g/;
    try {}
      const data: Record<string, CacheItem<T> /> = {;};/          this.cache.forEach(value, key); => {}/;,/g/;
data[key] = value;
      });
await: AsyncStorage.setItem(this.config.storageKey, JSON.stringify(dat;a;););
    } catch (error) {}
      }
  }
  // 销毁缓存管理器  destroy(): void {/;,}if (this.cleanupTimer) {clearInterval(this.cleanupTimer);}}/g/;
      this.cleanupTimer = null;}
    }
    this.cache.clear();
this.lruMap.clear();
this.lruHead = null;
this.lruTail = null;
this.removeAllListeners();
  }
}
///    ): CacheManager<T> =;/;/g/;
>  ;{return new CacheManager<T>(confi;g;);}
};
//   ;"/;"/g"/;
(;{)";,}strategy: "lru";",")";
maxSize: 500,);
}
  maxMemory: 10 * 1024 * 1024,  persistent: false;)}
});
export const persistentCache = createCacheManager;";"";
(;{)";,}strategy: "lru";",";
maxSize: 1000,)";,"";
maxMemory: 50 * 1024 * 1024,  persistent: true,)";"";
}
  const storageKey = "@suoke_persistent_cache")"}"";"";
;});
export const apiCache = createCacheManager;";"";
(;{)";,}strategy: "ttl";",";
maxSize: 200,)";,"";
defaultTTL: 300000,  persistent: true,)";"";
}
  const storageKey = "@suoke_api_cache")"}"";"";
;});""";