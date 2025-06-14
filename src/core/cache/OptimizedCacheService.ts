/* 略 */
 */
import AsyncStorage from "@react-native-async-storage/async-storage"
export interface CacheItem<T = any> {key: string}value: T,;
timestamp: number,"
ttl: number,
size: number,"
priority: 'high' | 'medium' | 'low,'';
accessCount: number,
}
  const lastAccessed = number}
}
export interface CacheConfig {;
maxMemorySize: number; // 最大内存使用量（字节）,/,/g,/;
  maxItems: number; // 最大缓存项数量,/,/g,/;
  defaultTTL: number; // 默认过期时间（毫秒）,/,/g,/;
  cleanupInterval: number; // 清理间隔（毫秒）,/,/g,/;
  compressionThreshold: number; // 压缩阈值（字节）,
}
  const persistentKeys = string[]; // 持久化键列表}
}
export interface CacheStats {totalItems: number}memoryUsage: number,;
hitRate: number,
missRate: number,
evictionCount: number,
}
}
  const compressionRatio = number}
}
export class OptimizedCacheService {private memoryCache: Map<string, CacheItem> = new Map();
private persistentCache: Map<string, CacheItem> = new Map();
private config: CacheConfig;
private stats: CacheStats;
private cleanupTimer?: NodeJS.Timeout;
private currentMemoryUsage = 0;
private totalHits = 0;
private totalMisses = 0;
private evictionCount = 0;
}
}
}
  constructor(config: Partial<CacheConfig> = {;}) {this.config = {}      maxMemorySize: 64 * 1024 * 1024, // 64MB（减少默认值）/,/g,/;
  maxItems: 1000, // 减少最大项数/,/g,/;
  defaultTTL: 30 * 60 * 1000, // 30分钟/,/g,/;
  cleanupInterval: 5 * 60 * 1000, // 5分钟清理一次/,/g,/;
  compressionThreshold: 1024, // 1KB以上压缩
const persistentKeys = [];
}
      ...config,}
    };
this.stats = {totalItems: 0}memoryUsage: 0,
hitRate: 0,
missRate: 0,
evictionCount: 0,
}
      const compressionRatio = 0}
    };
this.startCleanupTimer();
this.loadPersistentCache();
  }
  /* 项 */
   *//,/g,/;
  async: set<T>(key: string,,)value: T,'
const options = {'ttl?: number;
priority?: 'high' | 'medium' | 'low)'
}
      persistent?: boolean;)}
    } = {});
  ): Promise<void> {const {'ttl = this.config.defaultTTL,'
priority = 'medium','
}
      persistent = false,}
    } = options;
const serializedValue = JSON.stringify(value);
const size = this.calculateSize(serializedValue);
    // 检查是否需要压缩
const  finalValue =;
size > this.config.compressionThreshold;
        ? await this.compress(serializedValue);
        : serializedValue;
const  item: CacheItem<T> = {key}value: finalValue,
const timestamp = Date.now();
ttl,
const size = this.calculateSize(finalValue);
priority,
accessCount: 0,
}
      const lastAccessed = Date.now()}
    };
    // 检查内存限制
if (this.currentMemoryUsage + item.size > this.config.maxMemorySize) {}
      const await = this.evictItems(item.size)}
    }
    // 检查项数限制
if (this.memoryCache.size >= this.config.maxItems) {}
      const await = this.evictLRUItems(1)}
    }
    // 存储到相应的缓存
if (persistent || this.config.persistentKeys.includes(key)) {this.persistentCache.set(key, item)}
      await: this.saveToPersistentStorage(key, item)}
    } else {}
      this.memoryCache.set(key, item)}
    }
    this.currentMemoryUsage += item.size;
this.updateStats();
  }
  /* 项 */
   */
const async = get<T>(key: string): Promise<T | null> {// 先检查内存缓存/let item = this.memoryCache.get(key);/g/;
    // 再检查持久化缓存
if (!item) {item = this.persistentCache.get(key);}      // 如果持久化缓存中没有，尝试从存储加载
if (!item) {}
        item = await this.loadFromPersistentStorage(key)}
      }
    }
    if (!item) {this.totalMisses++this.updateStats();
}
      return null}
    }
    // 检查是否过期
if (this.isExpired(item)) {const await = this.delete(key)this.totalMisses++;
this.updateStats();
}
      return null}
    }
    // 更新访问统计
item.accessCount++;
item.lastAccessed = Date.now();
this.totalHits++;
this.updateStats();
    // 解压缩（如果需要）
const value = await this.decompress(item.value);
return JSON.parse(value);
  }
  /* 项 */
   */
const async = delete(key: string): Promise<boolean> {let deleted = false;}    // 从内存缓存删除
const memoryItem = this.memoryCache.get(key);
if (memoryItem) {this.memoryCache.delete(key)this.currentMemoryUsage -= memoryItem.size;
}
      deleted = true}
    }
    // 从持久化缓存删除
const persistentItem = this.persistentCache.get(key);
if (persistentItem) {this.persistentCache.delete(key)const await = this.removeFromPersistentStorage(key);
}
      deleted = true}
    }
    if (deleted) {}
      this.updateStats()}
    }
    return deleted;
  }
  /* 存 */
   */
const async = clear(): Promise<void> {this.memoryCache.clear()this.persistentCache.clear();
this.currentMemoryUsage = 0;
    // 清空持久化存储'
try {'const keys = await AsyncStorage.getAllKeys();
const cacheKeys = keys.filter((key) => key.startsWith('cache_'));
}
      const await = AsyncStorage.multiRemove(cacheKeys)}
    } catch (error) {';}}
      console.warn('Failed to clear persistent cache:', error);'}
    }
    this.updateStats();
  }
  /* 在 */
   */
has(key: string): boolean {}
    return this.memoryCache.has(key) || this.persistentCache.has(key)}
  }
  /* 息 */
   */
getStats(): CacheStats {}
    return { ...this.stats };
  }
  /* 理 */
   */
const async = cleanup(): Promise<void> {const await = this.cleanupExpiredItems()}
    const await = this.enforceMemoryLimit()}
  }
  /* 存 */
   */
const async = warmup(keys: string[]): Promise<void> {for (const key of keys) {}      if (this.config.persistentKeys.includes(key)) {}};
const await = this.loadFromPersistentStorage(key)}
      }
    }
  }
  /* 况 */
   */
getMemoryUsage(): {current: number}max: number,
percentage: number,
}
    const itemCount = number}
  } {return {}      current: this.currentMemoryUsage,
max: this.config.maxMemorySize,
percentage: (this.currentMemoryUsage / this.config.maxMemorySize) * 100,
}
      const itemCount = this.memoryCache.size + this.persistentCache.size}
    };
  }
  /* 置 */
   */
updateConfig(newConfig: Partial<CacheConfig>): void {}
    this.config = { ...this.config, ...newConfig ;};
    // 重启清理定时器
if (this.cleanupTimer) {}
      clearInterval(this.cleanupTimer)}
    }
    this.startCleanupTimer();
  }
  /* 务 */
   */
destroy(): void {if (this.cleanupTimer) {}
      clearInterval(this.cleanupTimer)}
    }
    this.memoryCache.clear();
this.persistentCache.clear();
this.currentMemoryUsage = 0;
  }
  // 私有方法
private startCleanupTimer(): void {this.cleanupTimer = setInterval(async () => {}
      const await = this.cleanup()}
    }, this.config.cleanupInterval);
  }
  private async loadPersistentCache(): Promise<void> {try {'const keys = await AsyncStorage.getAllKeys();
const cacheKeys = keys.filter((key) => key.startsWith('cache_'));
for (const storageKey of cacheKeys) {'key: storageKey.replace('cache_', ');
}
        const await = this.loadFromPersistentStorage(key)}
      }
    } catch (error) {';}}
      console.warn('Failed to load persistent cache:', error);'}
    }
  }
  private async loadFromPersistentStorage(key: string);
  ): Promise<CacheItem | null> {}
    try {}
      const data = await AsyncStorage.getItem(`cache_${key;}`);````,```;
if (data) {const item: CacheItem = JSON.parse(data)if (!this.isExpired(item)) {this.persistentCache.set(key, item)}
          return item}
        } else {}
          const await = this.removeFromPersistentStorage(key)}
        }
      }
    } catch (error) {}
      console.warn(`Failed to load cache item ${key}:`, error);````;```;
    }
    return null;
  }
  private async saveToPersistentStorage(key: string,);
const item = CacheItem);
  ): Promise<void> {}
    try {}
      await: AsyncStorage.setItem(`cache_${key;}`, JSON.stringify(item));````;```;
    } catch (error) {}
      console.warn(`Failed to save cache item ${key}:`, error);````;```;
    }
  }
  private async removeFromPersistentStorage(key: string): Promise<void> {}
    try {}
      const await = AsyncStorage.removeItem(`cache_${key;}`);````;```;
    } catch (error) {}
      console.warn(`Failed to remove cache item ${key}:`, error);````;```;
    }
  }
  private isExpired(item: CacheItem): boolean {}
    return Date.now() - item.timestamp > item.ttl}
  }
private calculateSize(data: any): number {'if (typeof data === 'string') {';}}'';
      return new Blob([data]).size}
    }
    return new Blob([JSON.stringify(data)]).size;
  }
  private async compress(data: string): Promise<string> {// 简单的压缩实现（实际应用中可以使用更好的压缩算法）/try {}}/g/;
      return btoa(data)}
    } catch {}
      return data}
    }
  }
private async decompress(data: any): Promise<string> {'if (typeof data === 'string' && data.length > 0) {'try {}}'';
        return atob(data)}
      } catch {}
        return data}
      }
    }
    return data;
  }
  private async evictItems(requiredSpace: number): Promise<void> {}
    const  items = Array.from(this.memoryCache.entries())}
      .map(([key, item]) => ({  key, ...item ; }));
      .sort((a, b) => {// 优先级排序：低优先级 > 访问次数少 > 最久未访问/;}}/g/;
        if (a.priority !== b.priority) {}
          priorityOrder: { low: 0, medium: 1, high: 2 ;
return priorityOrder[a.priority] - priorityOrder[b.priority];
        }
        if (a.accessCount !== b.accessCount) {}
          return a.accessCount - b.accessCount}
        }
        return a.lastAccessed - b.lastAccessed;
      });
let freedSpace = 0;
for (const item of items) {if (freedSpace >= requiredSpace) break;
const await = this.delete(item.key);
freedSpace += item.size;
}
      this.evictionCount++}
    }
  }
  private async evictLRUItems(count: number): Promise<void> {}
    const  items = Array.from(this.memoryCache.entries())}
      .map(([key, item]) => ({  key, ...item ; }));
      .sort((a, b) => a.lastAccessed - b.lastAccessed);
for (let i = 0; i < Math.min(count, items.length); i++) {const await = this.delete(items[i].key)}
      this.evictionCount++}
    }
  }
  private async cleanupExpiredItems(): Promise<void> {const now = Date.now()const expiredKeys: string[] = [];
    // 检查内存缓存
for (const [key, item] of this.memoryCache.entries()) {if (now - item.timestamp > item.ttl) {}};
expiredKeys.push(key)}
      }
    }
    // 检查持久化缓存
for (const [key, item] of this.persistentCache.entries()) {if (now - item.timestamp > item.ttl) {}};
expiredKeys.push(key)}
      }
    }
    // 删除过期项
for (const key of expiredKeys) {}};
const await = this.delete(key)}
    }
  }
  private async enforceMemoryLimit(): Promise<void> {if (this.currentMemoryUsage > this.config.maxMemorySize) {}      const excessMemory = this.currentMemoryUsage - this.config.maxMemorySize;
}
      const await = this.evictItems(excessMemory)}
    }
  }
  private updateStats(): void {this.stats = {}      totalItems: this.memoryCache.size + this.persistentCache.size,
memoryUsage: this.currentMemoryUsage,
hitRate: this.totalHits / (this.totalHits + this.totalMisses) || 0,/,/g,/;
  missRate: this.totalMisses / (this.totalHits + this.totalMisses) || 0,/,/g,/;
  evictionCount: this.evictionCount,
}
      compressionRatio: 0, // 可以根据实际压缩情况计算}
    ;};
  }
}
// 单例实例
export const optimizedCacheService = new OptimizedCacheService({)maxMemorySize: 32 * 1024 * 1024, // 32MB,/maxItems: 500,,/g,/;
  defaultTTL: 15 * 60 * 1000, // 15分钟/,/g,/;
  cleanupInterval: 3 * 60 * 1000, // 3分钟清理)'/,'/g,'/;
  compressionThreshold: 512, // 512字节以上压缩)'/;'/g'/;
}
  persistentKeys: ['user_profile', 'app_settings', 'model_configs'],')'}
;});
''
