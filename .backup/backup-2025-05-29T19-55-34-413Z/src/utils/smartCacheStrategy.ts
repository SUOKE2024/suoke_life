import AsyncStorage from "@react-native-async-storage/async-storage";

// 缓存优先级
export enum CachePriority {
  CRITICAL = "critical", // 关键数据，永不过期
  HIGH = "high", // 高优先级，长期缓存
  MEDIUM = "medium", // 中等优先级，中期缓存
  LOW = "low", // 低优先级，短期缓存
  TEMPORARY = "temporary", // 临时数据，会话级缓存
}

// 缓存策略类型
export enum CacheStrategy {
  LRU = "lru", // 最近最少使用
  LFU = "lfu", // 最少使用频率
  FIFO = "fifo", // 先进先出
  TTL = "ttl", // 基于时间
  ADAPTIVE = "adaptive", // 自适应策略
  PREDICTIVE = "predictive", // 预测性缓存
}

// 缓存项元数据
interface CacheMetadata {
  key: string;
  priority: CachePriority;
  strategy: CacheStrategy;
  createdAt: number;
  lastAccessed: number;
  accessCount: number;
  size: number;
  ttl?: number;
  tags: string[];
  dependencies: string[];
  version: string;
  checksum?: string;
}

// 缓存统计
interface CacheStats {
  totalItems: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  evictionCount: number;
  averageAccessTime: number;
  memoryUsage: number;
  lastOptimization: number;
}

// 预测模型
interface PredictionModel {
  userBehaviorPattern: Map<string, number>;
  timeBasedAccess: Map<string, number[]>;
  contextualAccess: Map<string, string[]>;
  seasonalPatterns: Map<string, number>;
}

// 智能缓存管理器
export class SmartCacheStrategy {
  private static instance: SmartCacheStrategy;
  private cache: Map<string, any> = new Map();
  private metadata: Map<string, CacheMetadata> = new Map();
  private stats: CacheStats;
  private predictionModel: PredictionModel;
  private optimizationTimer?: ReturnType<typeof setInterval>;
  private maxCacheSize: number = 100 * 1024 * 1024; // 100MB
  private maxItems: number = 1000;

  private constructor() {
    this.stats = {
      totalItems: 0,
      totalSize: 0,
      hitRate: 0,
      missRate: 0,
      evictionCount: 0,
      averageAccessTime: 0,
      memoryUsage: 0,
      lastOptimization: Date.now(),
    };

    this.predictionModel = {
      userBehaviorPattern: new Map(),
      timeBasedAccess: new Map(),
      contextualAccess: new Map(),
      seasonalPatterns: new Map(),
    };

    this.initializeCache();
  }

  static getInstance(): SmartCacheStrategy {
    if (!SmartCacheStrategy.instance) {
      SmartCacheStrategy.instance = new SmartCacheStrategy();
    }
    return SmartCacheStrategy.instance;
  }

  // 初始化缓存
  private async initializeCache(): Promise<void> {
    try {
      // 加载持久化的缓存元数据
      await this.loadCacheMetadata();

      // 启动定期优化
      this.startPeriodicOptimization();

      // 加载预测模型
      await this.loadPredictionModel();

      console.log("智能缓存策略初始化完成");
    } catch (error) {
      console.error("缓存初始化失败:", error);
    }
  }

  // 智能设置缓存
  async set<T>(
    key: string,
    data: T,
    options: {
      priority?: CachePriority;
      strategy?: CacheStrategy;
      ttl?: number;
      tags?: string[];
      dependencies?: string[];
      context?: string;
    } = {}
  ): Promise<void> {
    const startTime = Date.now();

    try {
      // 计算数据大小
      const serializedData = JSON.stringify(data);
      const size = new Blob([serializedData]).size;

      // 检查缓存空间
      await this.ensureCacheSpace(size);

      // 创建元数据
      const metadata: CacheMetadata = {
        key,
        priority: options.priority || CachePriority.MEDIUM,
        strategy: options.strategy || CacheStrategy.ADAPTIVE,
        createdAt: Date.now(),
        lastAccessed: Date.now(),
        accessCount: 0,
        size,
        ttl: options.ttl,
        tags: options.tags || [],
        dependencies: options.dependencies || [],
        version: "1.0.0",
        checksum: await this.calculateChecksum(serializedData),
      };

      // 存储数据和元数据
      this.cache.set(key, data);
      this.metadata.set(key, metadata);

      // 更新统计
      this.updateStats();

      // 更新预测模型
      this.updatePredictionModel(key, options.context);

      // 持久化关键数据
      if (
        metadata.priority === CachePriority.CRITICAL ||
        metadata.priority === CachePriority.HIGH
      ) {
        await this.persistCacheItem(key, data, metadata);
      }

      // 记录性能指标
      const accessTime = Date.now() - startTime;
      this.updateAccessTime(accessTime);
    } catch (error) {
      console.error("缓存设置失败:", error);
      throw error;
    }
  }

  // 智能获取缓存
  async get<T>(key: string, context?: string): Promise<T | null> {
    const startTime = Date.now();

    try {
      const metadata = this.metadata.get(key);

      if (!metadata) {
        this.stats.missRate++;
        this.updatePredictionModel(key, context, false);
        return null;
      }

      // 检查TTL
      if (metadata.ttl && Date.now() - metadata.createdAt > metadata.ttl) {
        await this.remove(key);
        this.stats.missRate++;
        return null;
      }

      // 检查依赖项
      if (await this.checkDependencies(metadata.dependencies)) {
        await this.remove(key);
        this.stats.missRate++;
        return null;
      }

      const data = this.cache.get(key);

      if (data) {
        // 更新访问统计
        metadata.lastAccessed = Date.now();
        metadata.accessCount++;
        this.stats.hitRate++;

        // 更新预测模型
        this.updatePredictionModel(key, context, true);

        // 记录访问时间
        const accessTime = Date.now() - startTime;
        this.updateAccessTime(accessTime);

        return data as T;
      }

      this.stats.missRate++;
      return null;
    } catch (error) {
      console.error("缓存获取失败:", error);
      this.stats.missRate++;
      return null;
    }
  }

  // 预测性预加载
  async predictivePreload(context?: string): Promise<void> {
    try {
      const predictions = this.generatePredictions(context);

      for (const [key, probability] of predictions) {
        if (probability > 0.7 && !this.cache.has(key)) {
          // 高概率访问的数据，尝试预加载
          await this.preloadData(key, context);
        }
      }
    } catch (error) {
      console.error("预测性预加载失败:", error);
    }
  }

  // 自适应缓存优化
  async adaptiveOptimization(): Promise<void> {
    try {
      const currentStats = this.getStats();

      // 根据命中率调整策略
      if (currentStats.hitRate < 0.6) {
        // 命中率低，增加缓存大小或调整策略
        await this.adjustCacheStrategy("increase_size");
      } else if (currentStats.hitRate > 0.9 && currentStats.memoryUsage > 0.8) {
        // 命中率高但内存使用率高，优化缓存内容
        await this.adjustCacheStrategy("optimize_content");
      }

      // 根据访问模式调整TTL
      await this.adjustTTLBasedOnPattern();

      // 清理无效缓存
      await this.cleanupInvalidCache();
    } catch (error) {
      console.error("自适应优化失败:", error);
    }
  }

  // 按标签清理缓存
  async clearByTags(tags: string[]): Promise<void> {
    const keysToRemove: string[] = [];

    for (const [key, metadata] of this.metadata.entries()) {
      if (metadata.tags.some((tag) => tags.includes(tag))) {
        keysToRemove.push(key);
      }
    }

    await Promise.all(keysToRemove.map((key) => this.remove(key)));
  }

  // 按优先级清理缓存
  async clearByPriority(priority: CachePriority): Promise<void> {
    const keysToRemove: string[] = [];

    for (const [key, metadata] of this.metadata.entries()) {
      if (metadata.priority === priority) {
        keysToRemove.push(key);
      }
    }

    await Promise.all(keysToRemove.map((key) => this.remove(key)));
  }

  // 获取缓存统计
  getStats(): CacheStats {
    return { ...this.stats };
  }

  // 获取缓存健康度
  getCacheHealth(): {
    score: number;
    issues: string[];
    recommendations: string[];
  } {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 100;

    // 检查命中率
    if (this.stats.hitRate < 0.5) {
      score -= 20;
      issues.push("缓存命中率过低");
      recommendations.push("考虑增加缓存大小或优化缓存策略");
    }

    // 检查内存使用
    if (this.stats.memoryUsage > 0.9) {
      score -= 15;
      issues.push("内存使用率过高");
      recommendations.push("清理低优先级缓存或增加内存限制");
    }

    // 检查访问时间
    if (this.stats.averageAccessTime > 100) {
      score -= 10;
      issues.push("平均访问时间过长");
      recommendations.push("优化数据序列化或使用更快的存储");
    }

    return { score, issues, recommendations };
  }

  // 导出缓存数据
  async exportCache(): Promise<{
    data: Record<string, any>;
    metadata: Record<string, CacheMetadata>;
    stats: CacheStats;
  }> {
    const data: Record<string, any> = {};
    const metadata: Record<string, CacheMetadata> = {};

    for (const [key, value] of this.cache.entries()) {
      data[key] = value;
    }

    for (const [key, meta] of this.metadata.entries()) {
      metadata[key] = meta;
    }

    return {
      data,
      metadata,
      stats: this.stats,
    };
  }

  // 导入缓存数据
  async importCache(cacheData: {
    data: Record<string, any>;
    metadata: Record<string, CacheMetadata>;
  }): Promise<void> {
    try {
      // 清空现有缓存
      this.cache.clear();
      this.metadata.clear();

      // 导入数据
      for (const [key, value] of Object.entries(cacheData.data)) {
        this.cache.set(key, value);
      }

      for (const [key, meta] of Object.entries(cacheData.metadata)) {
        this.metadata.set(key, meta);
      }

      // 更新统计
      this.updateStats();
    } catch (error) {
      console.error("缓存导入失败:", error);
      throw error;
    }
  }

  // 私有方法
  private async ensureCacheSpace(requiredSize: number): Promise<void> {
    let currentSize = this.getCurrentCacheSize();

    // 检查项目数量限制
    if (this.cache.size >= this.maxItems) {
      await this.evictItems(Math.floor(this.maxItems * 0.1)); // 清理10%
    }

    // 检查大小限制
    while (currentSize + requiredSize > this.maxCacheSize) {
      await this.evictItems(1);
      currentSize = this.getCurrentCacheSize();
    }
  }

  private async evictItems(count: number): Promise<void> {
    const candidates = Array.from(this.metadata.entries())
      .sort(
        (a, b) =>
          this.calculateEvictionScore(a[1]) - this.calculateEvictionScore(b[1])
      )
      .slice(0, count);

    for (const [key] of candidates) {
      await this.remove(key);
      this.stats.evictionCount++;
    }
  }

  private calculateEvictionScore(metadata: CacheMetadata): number {
    const now = Date.now();
    const age = now - metadata.createdAt;
    const timeSinceAccess = now - metadata.lastAccessed;

    // 优先级权重
    const priorityWeight = {
      [CachePriority.CRITICAL]: 1000,
      [CachePriority.HIGH]: 100,
      [CachePriority.MEDIUM]: 10,
      [CachePriority.LOW]: 1,
      [CachePriority.TEMPORARY]: 0.1,
    };

    // 计算综合分数（分数越低越容易被清理）
    const score =
      (metadata.accessCount * priorityWeight[metadata.priority]) /
      (timeSinceAccess + age + metadata.size);

    return score;
  }

  private getCurrentCacheSize(): number {
    return Array.from(this.metadata.values()).reduce(
      (total, meta) => total + meta.size,
      0
    );
  }

  private async remove(key: string): Promise<void> {
    this.cache.delete(key);
    this.metadata.delete(key);
    await this.removePersistentItem(key);
    this.updateStats();
  }

  private updateStats(): void {
    this.stats.totalItems = this.cache.size;
    this.stats.totalSize = this.getCurrentCacheSize();
    this.stats.memoryUsage = this.stats.totalSize / this.maxCacheSize;

    const totalRequests = this.stats.hitRate + this.stats.missRate;
    if (totalRequests > 0) {
      this.stats.hitRate = this.stats.hitRate / totalRequests;
      this.stats.missRate = this.stats.missRate / totalRequests;
    }
  }

  private updateAccessTime(accessTime: number): void {
    const alpha = 0.1; // 平滑因子
    this.stats.averageAccessTime =
      this.stats.averageAccessTime * (1 - alpha) + accessTime * alpha;
  }

  private updatePredictionModel(
    key: string,
    context?: string,
    hit: boolean = true
  ): void {
    // 更新用户行为模式
    const currentCount = this.predictionModel.userBehaviorPattern.get(key) || 0;
    this.predictionModel.userBehaviorPattern.set(
      key,
      currentCount + (hit ? 1 : -0.1)
    );

    // 更新时间基础访问模式
    const hour = new Date().getHours();
    const timeKey = `${key}_${hour}`;
    const timeAccess = this.predictionModel.timeBasedAccess.get(timeKey) || [];
    timeAccess.push(Date.now());
    this.predictionModel.timeBasedAccess.set(timeKey, timeAccess.slice(-10)); // 保留最近10次

    // 更新上下文访问模式
    if (context) {
      const contextAccess =
        this.predictionModel.contextualAccess.get(context) || [];
      if (!contextAccess.includes(key)) {
        contextAccess.push(key);
        this.predictionModel.contextualAccess.set(
          context,
          contextAccess.slice(-20)
        ); // 保留最近20个
      }
    }
  }

  private generatePredictions(context?: string): Map<string, number> {
    const predictions = new Map<string, number>();

    // 基于用户行为模式的预测
    for (const [key, count] of this.predictionModel.userBehaviorPattern) {
      const probability = Math.min(count / 100, 1); // 归一化到0-1
      predictions.set(key, probability);
    }

    // 基于时间模式的预测
    const currentHour = new Date().getHours();
    for (const [timeKey, accesses] of this.predictionModel.timeBasedAccess) {
      if (timeKey.endsWith(`_${currentHour}`)) {
        const key = timeKey.replace(`_${currentHour}`, "");
        const frequency = accesses.length / 10; // 频率
        const existing = predictions.get(key) || 0;
        predictions.set(key, Math.max(existing, frequency));
      }
    }

    // 基于上下文的预测
    if (context) {
      const contextKeys =
        this.predictionModel.contextualAccess.get(context) || [];
      for (const key of contextKeys) {
        const existing = predictions.get(key) || 0;
        predictions.set(key, Math.max(existing, 0.5)); // 上下文相关性权重
      }
    }

    return predictions;
  }

  private async preloadData(key: string, context?: string): Promise<void> {
    // 这里应该实现实际的数据预加载逻辑
    // 例如从API获取数据或从其他数据源加载
    console.log(`预加载数据: ${key}, 上下文: ${context}`);
  }

  private async adjustCacheStrategy(action: string): Promise<void> {
    switch (action) {
      case "increase_size":
        this.maxCacheSize = Math.min(
          this.maxCacheSize * 1.2,
          200 * 1024 * 1024
        ); // 最大200MB
        break;
      case "optimize_content":
        await this.clearByPriority(CachePriority.LOW);
        break;
    }
  }

  private async adjustTTLBasedOnPattern(): Promise<void> {
    for (const [key, metadata] of this.metadata.entries()) {
      const accessPattern =
        this.predictionModel.userBehaviorPattern.get(key) || 0;

      if (accessPattern > 50) {
        // 高频访问，延长TTL
        metadata.ttl = metadata.ttl ? metadata.ttl * 1.5 : 24 * 60 * 60 * 1000; // 24小时
      } else if (accessPattern < 5) {
        // 低频访问，缩短TTL
        metadata.ttl = metadata.ttl ? metadata.ttl * 0.5 : 60 * 60 * 1000; // 1小时
      }
    }
  }

  private async cleanupInvalidCache(): Promise<void> {
    const keysToRemove: string[] = [];

    for (const [key, metadata] of this.metadata.entries()) {
      // 检查数据完整性
      if (metadata.checksum) {
        const data = this.cache.get(key);
        if (data) {
          const currentChecksum = await this.calculateChecksum(
            JSON.stringify(data)
          );
          if (currentChecksum !== metadata.checksum) {
            keysToRemove.push(key);
          }
        }
      }
    }

    await Promise.all(keysToRemove.map((key) => this.remove(key)));
  }

  private async checkDependencies(dependencies: string[]): Promise<boolean> {
    for (const dep of dependencies) {
      if (!this.cache.has(dep)) {
        return true; // 依赖项不存在，需要清理
      }
    }
    return false;
  }

  private async calculateChecksum(data: string): Promise<string> {
    // 简单的校验和计算（实际项目中可使用更强的哈希算法）
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // 转换为32位整数
    }
    return hash.toString(16);
  }

  private async persistCacheItem(
    key: string,
    data: any,
    metadata: CacheMetadata
  ): Promise<void> {
    try {
      await AsyncStorage.setItem(
        `smart_cache_${key}`,
        JSON.stringify({ data, metadata })
      );
    } catch (error) {
      console.warn("持久化缓存项失败:", error);
    }
  }

  private async removePersistentItem(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(`smart_cache_${key}`);
    } catch (error) {
      console.warn("移除持久化缓存项失败:", error);
    }
  }

  private async loadCacheMetadata(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter((key) => key.startsWith("smart_cache_"));

      const items = await AsyncStorage.multiGet(cacheKeys);

      for (const [key, value] of items) {
        if (value) {
          try {
            const { data, metadata } = JSON.parse(value);
            const cacheKey = key.replace("smart_cache_", "");

            // 检查是否过期
            if (
              !metadata.ttl ||
              Date.now() - metadata.createdAt < metadata.ttl
            ) {
              this.cache.set(cacheKey, data);
              this.metadata.set(cacheKey, metadata);
            } else {
              await AsyncStorage.removeItem(key);
            }
          } catch (error) {
            console.warn("解析缓存项失败:", error);
            await AsyncStorage.removeItem(key);
          }
        }
      }
    } catch (error) {
      console.warn("加载缓存元数据失败:", error);
    }
  }

  private async loadPredictionModel(): Promise<void> {
    try {
      const modelData = await AsyncStorage.getItem("prediction_model");
      if (modelData) {
        const model = JSON.parse(modelData);
        this.predictionModel = {
          userBehaviorPattern: new Map(model.userBehaviorPattern || []),
          timeBasedAccess: new Map(model.timeBasedAccess || []),
          contextualAccess: new Map(model.contextualAccess || []),
          seasonalPatterns: new Map(model.seasonalPatterns || []),
        };
      }
    } catch (error) {
      console.warn("加载预测模型失败:", error);
    }
  }

  private async savePredictionModel(): Promise<void> {
    try {
      const model = {
        userBehaviorPattern: Array.from(
          this.predictionModel.userBehaviorPattern.entries()
        ),
        timeBasedAccess: Array.from(
          this.predictionModel.timeBasedAccess.entries()
        ),
        contextualAccess: Array.from(
          this.predictionModel.contextualAccess.entries()
        ),
        seasonalPatterns: Array.from(
          this.predictionModel.seasonalPatterns.entries()
        ),
      };
      await AsyncStorage.setItem("prediction_model", JSON.stringify(model));
    } catch (error) {
      console.warn("保存预测模型失败:", error);
    }
  }

  private startPeriodicOptimization(): void {
    this.optimizationTimer = setInterval(async () => {
      await this.adaptiveOptimization();
      await this.savePredictionModel();
      this.stats.lastOptimization = Date.now();
    }, 30 * 60 * 1000); // 每30分钟优化一次
  }

  // 清理资源
  destroy(): void {
    if (this.optimizationTimer) {
      clearInterval(this.optimizationTimer);
    }
    this.cache.clear();
    this.metadata.clear();
  }
}

// 单例实例
export const smartCache = SmartCacheStrategy.getInstance();

// 便捷函数
export const smartCacheUtils = {
  // 设置缓存
  set: <T>(
    key: string,
    data: T,
    options?: Parameters<typeof smartCache.set>[2]
  ) => smartCache.set(key, data, options),

  // 获取缓存
  get: <T>(key: string, context?: string) => smartCache.get<T>(key, context),

  // 预测性预加载
  preload: (context?: string) => smartCache.predictivePreload(context),

  // 按标签清理
  clearByTags: (tags: string[]) => smartCache.clearByTags(tags),

  // 获取统计
  getStats: () => smartCache.getStats(),

  // 获取健康度
  getHealth: () => smartCache.getCacheHealth(),
};
