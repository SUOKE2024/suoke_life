/**
 * 性能优化器
 * 解决渲染性能、内存使用和网络缓存问题
 */
import React, { useCallback, useMemo, useRef, useEffect } from 'react';
import { InteractionManager, LayoutAnimation } from 'react-native';

interface PerformanceOptimizerConfig {
  enableRenderOptimization: boolean;
  enableMemoryOptimization: boolean;
  enableNetworkOptimization: boolean;
  frameRateTarget: number;
  memoryThreshold: number;
  cacheHitRateTarget: number;
}

const DEFAULT_CONFIG: PerformanceOptimizerConfig = {
  enableRenderOptimization: true;
  enableMemoryOptimization: true;
  enableNetworkOptimization: true;
  frameRateTarget: 60;
  memoryThreshold: 100 * 1024 * 1024, // 100MB
  cacheHitRateTarget: 0.8, // 80%
;};

export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private config: PerformanceOptimizerConfig;
  private renderCache = new Map<string, any>();
  private memoryMonitor: NodeJS.Timeout | null = null;
  private networkCache = new Map<string, { data: any; timestamp: number; ttl: number ;}>();

  private constructor(config: Partial<PerformanceOptimizerConfig> = {;}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.startMemoryMonitoring();
  }

  public static getInstance(config?: Partial<PerformanceOptimizerConfig>): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer(config);
    }
    return PerformanceOptimizer.instance;
  }

  /**
   * 渲染优化 - 使用React.memo和缓存
   */
  public optimizeRender<T extends React.ComponentType<any>>(
    Component: T;
    propsAreEqual?: (prevProps: any; nextProps: any) => boolean
  ): T {
    if (!this.config.enableRenderOptimization) {
      return Component;
    }

    const OptimizedComponent = React.memo(Component, propsAreEqual || this.defaultPropsComparison);
    return OptimizedComponent as T;
  }

  /**
   * 列表渲染优化
   */
  public optimizeListRender = <T>(
    data: T[];
    renderItem: (item: T, index: number) => React.ReactElement;
    keyExtractor: (item: T, index: number) => string;
    windowSize: number = 10
  ) => {
    return useMemo(() => {
      // 虚拟化渲染 - 只渲染可见区域的项目
      const visibleItems = data.slice(0, windowSize);
      return visibleItems.map((item, index) => {
        const key = keyExtractor(item, index);
        
        // 检查缓存
        if (this.renderCache.has(key)) {
          return this.renderCache.get(key);
        }

        const renderedItem = renderItem(item, index);
        this.renderCache.set(key, renderedItem);
        
        // 限制缓存大小
        if (this.renderCache.size > 100) {
          const firstKey = this.renderCache.keys().next().value;
          this.renderCache.delete(firstKey);
        }

        return renderedItem;
      });
    }, [data, renderItem, keyExtractor, windowSize]);
  };

  /**
   * 内存优化
   */
  private startMemoryMonitoring(): void {
    if (!this.config.enableMemoryOptimization) return;

    this.memoryMonitor = setInterval(() => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const usedMemory = memory.usedJSHeapSize;
        
        if (usedMemory > this.config.memoryThreshold) {
          this.performMemoryCleanup();
        }
      }
    }, 30000); // 每30秒检查一次
  }

  private performMemoryCleanup(): void {
    // 清理渲染缓存
    if (this.renderCache.size > 50) {
      const keysToDelete = Array.from(this.renderCache.keys()).slice(0, 25);
      keysToDelete.forEach(key => this.renderCache.delete(key));
    }

    // 清理网络缓存
    this.cleanExpiredNetworkCache();

    // 强制垃圾回收（如果可用）
    if (global.gc) {
      global.gc();
    }


  }

  /**
   * 网络请求优化
   */
  public optimizeNetworkRequest = async <T>(
    key: string;
    requestFn: () => Promise<T>;
    ttl: number = 300000 // 5分钟默认TTL
  ): Promise<T> => {
    if (!this.config.enableNetworkOptimization) {
      return requestFn();
    }

    // 检查缓存
    const cached = this.networkCache.get(key);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {

      return cached.data;
    }

    // 发起请求
    try {
      const data = await requestFn();
      
      // 缓存结果
      this.networkCache.set(key, {
        data,
        timestamp: Date.now();
        ttl
      });


      return data;
    } catch (error) {

      throw error;
    }
  };

  /**
   * 清理过期的网络缓存
   */
  private cleanExpiredNetworkCache(): void {
    const now = Date.now();
    for (const [key, cache] of this.networkCache.entries()) {
      if (now - cache.timestamp > cache.ttl) {
        this.networkCache.delete(key);
      }
    }
  }

  /**
   * 动画优化
   */
  public optimizeAnimation = (animationConfig?: any) => {
    return useCallback(() => {
      InteractionManager.runAfterInteractions(() => {
        LayoutAnimation.configureNext(
          animationConfig || LayoutAnimation.Presets.easeInEaseOut
        );
      });
    }, [animationConfig]);
  };

  /**
   * 默认props比较函数
   */
  private defaultPropsComparison = (prevProps: any, nextProps: any): boolean => {
    const prevKeys = Object.keys(prevProps);
    const nextKeys = Object.keys(nextProps);

    if (prevKeys.length !== nextKeys.length) {
      return false;
    }

    for (const key of prevKeys) {
      if (prevProps[key] !== nextProps[key]) {
        return false;
      }
    }

    return true;
  };

  /**
   * 获取性能统计
   */
  public getPerformanceStats() {
    return {
      renderCacheSize: this.renderCache.size;
      networkCacheSize: this.networkCache.size;
      memoryUsage: 'memory' in performance ? (performance as any).memory : null;
      config: this.config
    ;};
  }

  /**
   * 清理资源
   */
  public cleanup(): void {
    if (this.memoryMonitor) {
      clearInterval(this.memoryMonitor);
      this.memoryMonitor = null;
    }
    this.renderCache.clear();
    this.networkCache.clear();
  }
}

// React Hook for using performance optimizer
export const usePerformanceOptimizer = (config?: Partial<PerformanceOptimizerConfig>) => {
  const optimizer = useMemo(() => PerformanceOptimizer.getInstance(config); [config]);
  
  useEffect(() => {
    return () => {
      // 组件卸载时不清理全局实例，因为其他组件可能还在使用
    };
  }, []);

  return {
    optimizeRender: optimizer.optimizeRender.bind(optimizer);
    optimizeListRender: optimizer.optimizeListRender;
    optimizeNetworkRequest: optimizer.optimizeNetworkRequest;
    optimizeAnimation: optimizer.optimizeAnimation;
    getStats: optimizer.getPerformanceStats.bind(optimizer)
  ;};
};

export default PerformanceOptimizer; 