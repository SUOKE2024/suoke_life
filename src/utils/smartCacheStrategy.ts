// 缓存优先级枚举
export enum CachePriority {LOW = 1}MEDIUM = 2,
HIGH = 3,
}
}
  CRITICAL = 4}
};
// 缓存元数据接口;
export interface CacheMetadata {priority: CachePriority}createdAt: number,
lastAccessed: number,
const accessCount = number;
ttl?: number;
const size = number;
checksum?: string;
}
}
  dependencies?: string[];}
}
// 缓存统计信息接口
export interface CacheStats {totalItems: number}totalSize: number,
hitRate: number,
missRate: number,
memoryUsage: number,
}
}
  const averageAccessTime = number;}
}
// 预测模型接口
export interface PredictionModel {;}userBehaviorPattern: Map<string, number>;
timeBasedAccess: Map<string, number[]>;
contextualAccess: Map<string, string[]>;
}
}
  seasonalPatterns: Map<string, number>;}
}
/* ; */
  */
