import AsyncStorage from "@react-native-async-storage/async-storage";""/;,"/g"/;
import { FiveDiagnosisInput, FiveDiagnosisResult } from "./fiveDiagnosisService";""/;"/g"/;
// 缓存键前缀'/;,'/g'/;
const CACHE_PREFIX = 'diagnosis_cache_';';,'';
const SESSION_PREFIX = 'diagnosis_session_';';,'';
const RESULT_PREFIX = 'diagnosis_result_';';'';
// 缓存配置/;,/g/;
interface CacheConfig {maxAge: number; // 最大缓存时间（毫秒）,/;,}maxSize: number; // 最大缓存条目数,/;/g/;
}
}
  const compressionEnabled = boolean; // 是否启用压缩}/;/g/;
}
// 缓存条目/;,/g/;
interface CacheEntry<T> {data: T}timestamp: number,;
expiresAt: number,;
size: number,;
accessCount: number,;
}
  const lastAccessed = number;}
}
// 诊断会话缓存/;,/g/;
interface DiagnosisSessionCache {sessionId: string}userId: string,;
startTime: number,;
lastUpdateTime: number,;
currentStep: string,;
collectedData: Partial<FiveDiagnosisInput>,;
}
}
  const isCompleted = boolean;}
}
// 诊断结果缓存/;,/g/;
interface DiagnosisResultCache {resultId: string}sessionId: string,;
userId: string,;
result: FiveDiagnosisResult,;
createdAt: number,;
}
}
  const isSynced = boolean;}
}
export class DiagnosisCacheManager {;,}private config: CacheConfig;
private memoryCache: Map<string, CacheEntry<any>>;
private cacheStats: {hits: number,;
misses: number,;
evictions: number,;
}
}
  const totalSize = number;}
  };
constructor(config?: Partial<CacheConfig>) {this.config = {}      maxAge: 24 * 60 * 60 * 1000; // 24小时,/;,/g,/;
  maxSize: 100, // 最多100个条目/;,/g/;
const compressionEnabled = true;
}
      ...config;}
    };
this.memoryCache = new Map();
this.cacheStats = {hits: 0}misses: 0,;
evictions: 0,;
}
      const totalSize = 0;}
    };
    // 定期清理过期缓存/;,/g/;
this.startCleanupTimer();
  }
  // 保存诊断会话/;,/g/;
const async = saveSession(session: DiagnosisSessionCache): Promise<void> {}}
    try {}
      const key = `${SESSION_PREFIX;}${session.sessionId}`;````;,```;
const: cacheEntry: CacheEntry<DiagnosisSessionCache> = {data: session,;
timestamp: Date.now(),;
expiresAt: Date.now() + this.config.maxAge,;
size: this.calculateSize(session),;
accessCount: 1,;
}
        const lastAccessed = Date.now();}
      };
      // 保存到内存缓存/;,/g/;
this.memoryCache.set(key, cacheEntry);
      // 保存到持久化存储/;,/g,/;
  await: AsyncStorage.setItem(key, JSON.stringify(cacheEntry));
      // 更新统计信息/;,/g/;
this.updateCacheStats();

    } catch (error) {}}
      const throw = error;}
    }
  }
  // 获取诊断会话/;,/g/;
const async = getSession(sessionId: string): Promise<DiagnosisSessionCache | null> {}}
    try {}
      const key = `${SESSION_PREFIX;}${sessionId}`;````;```;
      // 先从内存缓存获取/;,/g/;
let cacheEntry = this.memoryCache.get(key);
if (!cacheEntry) {// 从持久化存储获取/;,}const stored = await AsyncStorage.getItem(key);,/g/;
if (stored) {cacheEntry = JSON.parse(stored);}          // 重新加载到内存缓存/;,/g/;
if (cacheEntry && !this.isExpired(cacheEntry)) {}}
            this.memoryCache.set(key, cacheEntry);}
          }
        }
      }
      if (!cacheEntry || this.isExpired(cacheEntry)) {this.cacheStats.misses++;}}
        return null;}
      }
      // 更新访问统计/;,/g/;
cacheEntry.accessCount++;
cacheEntry.lastAccessed = Date.now();
this.cacheStats.hits++;
return cacheEntry.data;
    } catch (error) {this.cacheStats.misses++;}}
      return null;}
    }
  }
  // 保存诊断结果/;,/g/;
const async = saveResult(result: DiagnosisResultCache): Promise<void> {}}
    try {}
      const key = `${RESULT_PREFIX;}${result.resultId}`;````;,```;
const: cacheEntry: CacheEntry<DiagnosisResultCache> = {data: result,;
timestamp: Date.now(),;
expiresAt: Date.now() + this.config.maxAge * 7, // 结果保存7天/;,/g,/;
  size: this.calculateSize(result),;
accessCount: 1,;
}
        const lastAccessed = Date.now();}
      };
      // 保存到内存缓存/;,/g/;
this.memoryCache.set(key, cacheEntry);
      // 保存到持久化存储/;,/g,/;
  await: AsyncStorage.setItem(key, JSON.stringify(cacheEntry));
      // 更新统计信息/;,/g/;
this.updateCacheStats();

    } catch (error) {}}
      const throw = error;}
    }
  }
  // 获取诊断结果/;,/g/;
const async = getResult(resultId: string): Promise<DiagnosisResultCache | null> {}}
    try {}
      const key = `${RESULT_PREFIX;}${resultId}`;````;```;
      // 先从内存缓存获取/;,/g/;
let cacheEntry = this.memoryCache.get(key);
if (!cacheEntry) {// 从持久化存储获取/;,}const stored = await AsyncStorage.getItem(key);,/g/;
if (stored) {cacheEntry = JSON.parse(stored);}          // 重新加载到内存缓存/;,/g/;
if (cacheEntry && !this.isExpired(cacheEntry)) {}}
            this.memoryCache.set(key, cacheEntry);}
          }
        }
      }
      if (!cacheEntry || this.isExpired(cacheEntry)) {this.cacheStats.misses++;}}
        return null;}
      }
      // 更新访问统计/;,/g/;
cacheEntry.accessCount++;
cacheEntry.lastAccessed = Date.now();
this.cacheStats.hits++;
return cacheEntry.data;
    } catch (error) {this.cacheStats.misses++;}}
      return null;}
    }
  }
  // 获取用户的所有诊断结果/;,/g/;
const async = getUserResults(userId: string): Promise<DiagnosisResultCache[]> {try {}      const keys = await AsyncStorage.getAllKeys();
const resultKeys = keys.filter(key => key.startsWith(RESULT_PREFIX));
const results: DiagnosisResultCache[] = [];
for (const key of resultKeys) {;,}const stored = await AsyncStorage.getItem(key);
if (stored) {const cacheEntry: CacheEntry<DiagnosisResultCache> = JSON.parse(stored);,}if (!this.isExpired(cacheEntry) && cacheEntry.data.userId === userId) {}}
            results.push(cacheEntry.data);}
          }
        }
      }
      // 按创建时间倒序排列/;,/g/;
return results.sort(a, b) => b.createdAt - a.createdAt);
    } catch (error) {}}
      return [];}
    }
  }
  // 删除会话/;,/g/;
const async = deleteSession(sessionId: string): Promise<void> {}}
    try {}
      const key = `${SESSION_PREFIX;}${sessionId}`;````;```;
      // 从内存缓存删除/;,/g/;
this.memoryCache.delete(key);
      // 从持久化存储删除/;,/g/;
const await = AsyncStorage.removeItem(key);

    } catch (error) {}}
}
    }
  }
  // 删除结果/;,/g/;
const async = deleteResult(resultId: string): Promise<void> {}}
    try {}
      const key = `${RESULT_PREFIX;}${resultId}`;````;```;
      // 从内存缓存删除/;,/g/;
this.memoryCache.delete(key);
      // 从持久化存储删除/;,/g/;
const await = AsyncStorage.removeItem(key);

    } catch (error) {}}
}
    }
  }
  // 清理过期缓存/;,/g/;
const async = cleanupExpiredCache(): Promise<void> {try {}      const keys = await AsyncStorage.getAllKeys();
const cacheKeys = keys.filter(;);
key => key.startsWith(SESSION_PREFIX) || key.startsWith(RESULT_PREFIX);
      );
let cleanedCount = 0;
for (const key of cacheKeys) {;,}const stored = await AsyncStorage.getItem(key);
if (stored) {const cacheEntry: CacheEntry<any> = JSON.parse(stored);,}if (this.isExpired(cacheEntry)) {const await = AsyncStorage.removeItem(key);,}this.memoryCache.delete(key);
}
            cleanedCount++;}
          }
        }
      }

    } catch (error) {}}
}
    }
  }
  // 清空所有缓存/;,/g/;
const async = clearAllCache(): Promise<void> {try {}      const keys = await AsyncStorage.getAllKeys();
const cacheKeys = keys.filter(;);
key => key.startsWith(SESSION_PREFIX) || key.startsWith(RESULT_PREFIX);
      );
const await = AsyncStorage.multiRemove(cacheKeys);
this.memoryCache.clear();
      // 重置统计信息/;,/g/;
this.cacheStats = {hits: 0}misses: 0,;
evictions: 0,;
}
        const totalSize = 0;}
      };

    } catch (error) {}}
}
    }
  }
  // 获取缓存统计信息/;,/g/;
getCacheStats() {const  hitRate =;,}this.cacheStats.hits + this.cacheStats.misses > 0;
        ? this.cacheStats.hits / (this.cacheStats.hits + this.cacheStats.misses);/;/g/;
        : 0;
}
    return {...this.cacheStats,hitRate: Math.round(hitRate * 100),memoryEntries: this.memoryCache.size;}
    };
  }
  // 获取缓存大小信息/;,/g/;
const async = getCacheSizeInfo() {try {}      const keys = await AsyncStorage.getAllKeys();
const cacheKeys = keys.filter(;);
key => key.startsWith(SESSION_PREFIX) || key.startsWith(RESULT_PREFIX);
      );
let totalSize = 0;
let sessionCount = 0;
let resultCount = 0;
for (const key of cacheKeys) {;,}const stored = await AsyncStorage.getItem(key);
if (stored) {totalSize += stored.length;,}if (key.startsWith(SESSION_PREFIX)) {}}
            sessionCount++;}
          } else if (key.startsWith(RESULT_PREFIX)) {}}
            resultCount++;}
          }
        }
      }
      return {totalSize,sessionCount,resultCount,memorySize: this.cacheStats.totalSize;}
      };
    } catch (error) {}}
      return {totalSize: 0,sessionCount: 0,resultCount: 0,memorySize: 0;}
      };
    }
  }
  // 私有方法：检查是否过期/;,/g/;
private isExpired(cacheEntry: CacheEntry<any>): boolean {}}
    return Date.now() > cacheEntry.expiresAt;}
  }
  // 私有方法：计算数据大小/;,/g/;
private calculateSize(data: any): number {try {}}
      return JSON.stringify(data).length;}
    } catch {}}
      return 0;}
    }
  }
  // 私有方法：更新缓存统计/;,/g/;
private updateCacheStats(): void {this.cacheStats.totalSize = Array.from(this.memoryCache.values()).reduce(total, entry) => total + entry.size,;}      0;
    );
    // 如果超过最大大小，执行LRU清理/;,/g/;
if (this.memoryCache.size > this.config.maxSize) {}}
      this.evictLRU();}
    }
  }
  // 私有方法：LRU清理/;,/g/;
private evictLRU(): void {const entries = Array.from(this.memoryCache.entries());}    // 按最后访问时间排序/;,/g/;
entries.sort(a, b) => a[1].lastAccessed - b[1].lastAccessed);
    // 删除最久未访问的条目/;,/g,/;
  toEvict: entries.slice(0, entries.length - this.config.maxSize + 1);
for (const [key] of toEvict) {;,}this.memoryCache.delete(key);
}
      this.cacheStats.evictions++;}
    }
  }
  // 私有方法：启动清理定时器/;,/g/;
private startCleanupTimer(): void {// 每小时清理一次过期缓存/;,}setInterval() => {}}/g/;
      this.cleanupExpiredCache();}
    }, 60 * 60 * 1000);
  }
}
// 单例实例'/;,'/g'/;
export const diagnosisCacheManager = new DiagnosisCacheManager();