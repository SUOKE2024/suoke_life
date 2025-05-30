/**
 * 性能监控工具
 * 监控应用性能指标，包括渲染性能、网络请求、内存使用等
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform, InteractionManager, AppState, AppStateStatus } from 'react-native';
import { deviceInfoManager, PerformanceMetrics } from './deviceInfo';

// 声明全局performance对象（React Native环境）
declare global {
  const performance: {
    now(): number;
    memory?: {
      usedJSHeapSize: number;
      totalJSHeapSize: number;
      jsHeapSizeLimit: number;
    };
  };
}

export interface PerformanceMetric {
  id: string;
  name: string;
  type: 'render' | 'network' | 'memory' | 'user_interaction' | 'custom';
  startTime: number;
  endTime?: number;
  duration?: number;
  metadata?: Record<string, any>;
  timestamp: Date;
}

export interface NetworkMetric extends PerformanceMetric {
  type: 'network';
  url: string;
  method: string;
  status?: number;
  responseSize?: number;
  requestSize?: number;
}

export interface RenderMetric extends PerformanceMetric {
  type: 'render';
  componentName: string;
  renderCount?: number;
  props?: Record<string, any>;
}

export interface MemoryMetric extends PerformanceMetric {
  type: 'memory';
  usedJSHeapSize?: number;
  totalJSHeapSize?: number;
  jsHeapSizeLimit?: number;
}

export interface UserInteractionMetric extends PerformanceMetric {
  type: 'user_interaction';
  action: string;
  target: string;
  coordinates?: { x: number; y: number };
}

export interface PerformanceBenchmark {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface MemoryWarning {
  timestamp: number;
  memoryUsage: number;
  threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface PerformanceAlert {
  type: 'memory' | 'cpu' | 'battery' | 'network' | 'render';
  severity: 'warning' | 'error' | 'critical';
  message: string;
  timestamp: number;
  metrics: any;
}

/**
 * 性能监控器类
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private activeMetrics: Map<string, PerformanceMetric> = new Map();
  private isEnabled: boolean = true;
  private maxMetrics: number = 1000;
  private benchmarks: Map<string, PerformanceBenchmark> = new Map();
  private memoryWarnings: MemoryWarning[] = [];
  private performanceAlerts: PerformanceAlert[] = [];
  private monitoringInterval: ReturnType<typeof setInterval> | null = null;
  private isMonitoring = false;
  
  // 性能阈值配置
  private thresholds = {
    memory: {
      warning: 70,    // 70%内存使用率警告
      error: 85,      // 85%内存使用率错误
      critical: 95,   // 95%内存使用率严重
    },
    cpu: {
      warning: 70,
      error: 85,
      critical: 95,
    },
    battery: {
      warning: 20,    // 20%电量警告
      error: 10,      // 10%电量错误
      critical: 5,    // 5%电量严重
    },
    network: {
      warning: 1000,  // 1秒网络延迟警告
      error: 3000,    // 3秒网络延迟错误
      critical: 5000, // 5秒网络延迟严重
    },
    render: {
      warning: 16,    // 16ms渲染时间警告
      error: 32,      // 32ms渲染时间错误
      critical: 50,   // 50ms渲染时间严重
    },
  };

  private constructor() {
    this.loadSettings();
    this.setupAppStateListener();
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * 启用/禁用性能监控
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * 开始性能测量
   */
  startMeasure(
    id: string,
    name: string,
    type: PerformanceMetric['type'],
    metadata?: Record<string, any>
  ): void {
    if (!this.isEnabled) {return;}

    const metric: PerformanceMetric = {
      id,
      name,
      type,
      startTime: performance.now(),
      metadata,
      timestamp: new Date(),
    };

    this.activeMetrics.set(id, metric);
  }

  /**
   * 结束性能测量
   */
  endMeasure(id: string, additionalMetadata?: Record<string, any>): void {
    if (!this.isEnabled) {return;}

    const metric = this.activeMetrics.get(id);
    if (!metric) {
      console.warn(`Performance metric with id "${id}" not found`);
      return;
    }

    metric.endTime = performance.now();
    metric.duration = metric.endTime - metric.startTime;
    
    if (additionalMetadata) {
      metric.metadata = { ...metric.metadata, ...additionalMetadata };
    }

    this.activeMetrics.delete(id);
    this.addMetric(metric);
  }

  /**
   * 记录网络请求性能
   */
  recordNetworkRequest(
    url: string,
    method: string,
    startTime: number,
    endTime: number,
    status?: number,
    responseSize?: number,
    requestSize?: number
  ): void {
    if (!this.isEnabled) {return;}

    const metric: NetworkMetric = {
      id: `network_${Date.now()}_${Math.random()}`,
      name: `${method} ${url}`,
      type: 'network',
      url,
      method,
      status,
      responseSize,
      requestSize,
      startTime,
      endTime,
      duration: endTime - startTime,
      timestamp: new Date(),
    };

    this.addMetric(metric);
  }

  /**
   * 记录组件渲染性能
   */
  recordRender(
    componentName: string,
    duration: number,
    renderCount?: number,
    props?: Record<string, any>
  ): void {
    if (!this.isEnabled) {return;}

    const metric: RenderMetric = {
      id: `render_${componentName}_${Date.now()}`,
      name: `Render ${componentName}`,
      type: 'render',
      componentName,
      renderCount,
      props,
      startTime: performance.now() - duration,
      endTime: performance.now(),
      duration,
      timestamp: new Date(),
    };

    this.addMetric(metric);
  }

  /**
   * 记录内存使用情况
   */
  recordMemoryUsage(): void {
    if (!this.isEnabled) {return;}

    // React Native中获取内存信息的方法有限
    // 这里提供一个基础框架，实际实现可能需要原生模块支持
    const metric: MemoryMetric = {
      id: `memory_${Date.now()}`,
      name: 'Memory Usage',
      type: 'memory',
      startTime: performance.now(),
      endTime: performance.now(),
      duration: 0,
      timestamp: new Date(),
      // 在Web环境中可以使用 performance.memory
      ...(performance.memory && {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
      }),
    };

    this.addMetric(metric);
  }

  /**
   * 记录用户交互
   */
  recordUserInteraction(
    action: string,
    target: string,
    coordinates?: { x: number; y: number },
    metadata?: Record<string, any>
  ): void {
    if (!this.isEnabled) {return;}

    const metric: UserInteractionMetric = {
      id: `interaction_${Date.now()}_${Math.random()}`,
      name: `${action} on ${target}`,
      type: 'user_interaction',
      action,
      target,
      coordinates,
      startTime: performance.now(),
      endTime: performance.now(),
      duration: 0,
      timestamp: new Date(),
      metadata,
    };

    this.addMetric(metric);
  }

  /**
   * 添加自定义指标
   */
  recordCustomMetric(
    name: string,
    duration: number,
    metadata?: Record<string, any>
  ): void {
    if (!this.isEnabled) {return;}

    const metric: PerformanceMetric = {
      id: `custom_${Date.now()}_${Math.random()}`,
      name,
      type: 'custom',
      startTime: performance.now() - duration,
      endTime: performance.now(),
      duration,
      timestamp: new Date(),
      metadata,
    };

    this.addMetric(metric);
  }

  /**
   * 添加指标到集合
   */
  private addMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric);

    // 限制指标数量，避免内存泄漏
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    // 在开发环境中输出性能警告
    if (__DEV__ && this.shouldWarnAboutPerformance(metric)) {
      console.warn(`Performance warning: ${metric.name} took ${metric.duration?.toFixed(2)}ms`);
    }
  }

  /**
   * 判断是否应该发出性能警告
   */
  private shouldWarnAboutPerformance(metric: PerformanceMetric): boolean {
    if (!metric.duration) {return false;}

    switch (metric.type) {
      case 'render':
        return metric.duration > 16; // 超过一帧的时间
      case 'network':
        return metric.duration > 5000; // 超过5秒
      case 'user_interaction':
        return metric.duration > 100; // 超过100ms
      default:
        return metric.duration > 1000; // 超过1秒
    }
  }

  /**
   * 获取性能统计
   */
  getStats(): {
    total: number;
    byType: Record<string, number>;
    averageDuration: Record<string, number>;
    slowestOperations: PerformanceMetric[];
    recentMetrics: PerformanceMetric[];
  } {
    const byType: Record<string, number> = {};
    const durationByType: Record<string, number[]> = {};
    
    this.metrics.forEach(metric => {
      byType[metric.type] = (byType[metric.type] || 0) + 1;
      
      if (metric.duration) {
        if (!durationByType[metric.type]) {
          durationByType[metric.type] = [];
        }
        durationByType[metric.type].push(metric.duration);
      }
    });

    const averageDuration: Record<string, number> = {};
    Object.keys(durationByType).forEach(type => {
      const durations = durationByType[type];
      averageDuration[type] = durations.reduce((a, b) => a + b, 0) / durations.length;
    });

    // 获取最慢的10个操作
    const slowestOperations = [...this.metrics]
      .filter(m => m.duration)
      .sort((a, b) => (b.duration || 0) - (a.duration || 0))
      .slice(0, 10);

    // 获取最近的50个指标
    const recentMetrics = this.metrics.slice(-50);

    return {
      total: this.metrics.length,
      byType,
      averageDuration,
      slowestOperations,
      recentMetrics,
    };
  }

  /**
   * 获取网络性能统计
   */
  getNetworkStats(): {
    totalRequests: number;
    averageResponseTime: number;
    successRate: number;
    slowestRequests: NetworkMetric[];
    errorRequests: NetworkMetric[];
  } {
    const networkMetrics = this.metrics.filter(m => m.type === 'network') as NetworkMetric[];
    
    const totalRequests = networkMetrics.length;
    const successfulRequests = networkMetrics.filter(m => m.status && m.status < 400).length;
    const errorRequests = networkMetrics.filter(m => m.status && m.status >= 400);
    
    const averageResponseTime = networkMetrics.reduce((sum, m) => sum + (m.duration || 0), 0) / totalRequests;
    const successRate = totalRequests > 0 ? (successfulRequests / totalRequests) * 100 : 0;
    
    const slowestRequests = [...networkMetrics]
      .sort((a, b) => (b.duration || 0) - (a.duration || 0))
      .slice(0, 10);

    return {
      totalRequests,
      averageResponseTime,
      successRate,
      slowestRequests,
      errorRequests,
    };
  }

  /**
   * 清除所有指标
   */
  clearMetrics(): void {
    this.metrics = [];
    this.activeMetrics.clear();
  }

  /**
   * 导出性能数据
   */
  exportData(): {
    timestamp: Date;
    metrics: PerformanceMetric[];
    stats: any;
    networkStats: any;
  } {
    return {
      timestamp: new Date(),
      metrics: [...this.metrics],
      stats: this.getStats(),
      networkStats: this.getNetworkStats(),
    };
  }

  /**
   * 保存设置
   */
  private async saveSettings(): Promise<void> {
    try {
      await AsyncStorage.setItem('performance_monitor_settings', JSON.stringify({
        isEnabled: this.isEnabled,
        maxMetrics: this.maxMetrics,
      }));
    } catch (error) {
      console.error('Failed to save performance monitor settings:', error);
    }
  }

  /**
   * 加载设置
   */
  private async loadSettings(): Promise<void> {
    try {
      const settings = await AsyncStorage.getItem('performance_monitor_settings');
      if (settings) {
        const parsed = JSON.parse(settings);
        this.isEnabled = parsed.isEnabled ?? true;
        this.maxMetrics = parsed.maxMetrics ?? 1000;
      }
    } catch (error) {
      console.error('Failed to load performance monitor settings:', error);
    }
  }

  /**
   * 设置最大指标数量
   */
  setMaxMetrics(max: number): void {
    this.maxMetrics = max;
    this.saveSettings();
  }

  /**
   * 开始性能监控
   */
  startMonitoring(interval: number = 5000): void {
    if (this.isMonitoring) {
      console.warn('性能监控已在运行中');
      return;
    }

    this.isMonitoring = true;
    console.log('🔍 开始性能监控...');

    this.monitoringInterval = setInterval(async () => {
      try {
        await this.collectPerformanceData();
      } catch (error) {
        console.error('性能数据收集失败:', error);
      }
    }, interval);
  }

  /**
   * 停止性能监控
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.log('⏹️ 性能监控已停止');
  }

  /**
   * 收集性能数据
   */
  private async collectPerformanceData(): Promise<void> {
    try {
      const metrics = await deviceInfoManager.getCurrentPerformanceMetrics();
      this.analyzePerformanceMetrics(metrics);
    } catch (error) {
      console.error('收集性能数据失败:', error);
    }
  }

  /**
   * 分析性能指标并生成警告
   */
  private analyzePerformanceMetrics(metrics: PerformanceMetrics): void {
    // 检查内存使用
    this.checkMemoryUsage(metrics.memoryUsage);
    
    // 检查CPU使用
    this.checkCpuUsage(metrics.cpuUsage);
    
    // 检查电池消耗
    this.checkBatteryDrain(metrics.batteryDrain);
    
    // 检查网络延迟
    this.checkNetworkLatency(metrics.networkLatency);
    
    // 检查渲染性能
    this.checkRenderTime(metrics.renderTime);
  }

  /**
   * 检查内存使用情况
   */
  private checkMemoryUsage(memoryUsage: PerformanceMetrics['memoryUsage']): void {
    const percentage = memoryUsage.percentage;
    let severity: MemoryWarning['severity'] = 'low';
    
    if (percentage >= this.thresholds.memory.critical) {
      severity = 'critical';
      this.addPerformanceAlert('memory', 'critical', `内存使用率达到${percentage.toFixed(1)}%，应用可能崩溃`, memoryUsage);
    } else if (percentage >= this.thresholds.memory.error) {
      severity = 'high';
      this.addPerformanceAlert('memory', 'error', `内存使用率过高：${percentage.toFixed(1)}%`, memoryUsage);
    } else if (percentage >= this.thresholds.memory.warning) {
      severity = 'medium';
      this.addPerformanceAlert('memory', 'warning', `内存使用率较高：${percentage.toFixed(1)}%`, memoryUsage);
    }

    if (severity !== 'low') {
      this.memoryWarnings.push({
        timestamp: Date.now(),
        memoryUsage: percentage,
        threshold: this.getThresholdForSeverity('memory', severity),
        severity,
      });
    }
  }

  /**
   * 检查CPU使用情况
   */
  private checkCpuUsage(cpuUsage: number): void {
    if (cpuUsage >= this.thresholds.cpu.critical) {
      this.addPerformanceAlert('cpu', 'critical', `CPU使用率过高：${cpuUsage.toFixed(1)}%`, { cpuUsage });
    } else if (cpuUsage >= this.thresholds.cpu.error) {
      this.addPerformanceAlert('cpu', 'error', `CPU使用率较高：${cpuUsage.toFixed(1)}%`, { cpuUsage });
    } else if (cpuUsage >= this.thresholds.cpu.warning) {
      this.addPerformanceAlert('cpu', 'warning', `CPU使用率偏高：${cpuUsage.toFixed(1)}%`, { cpuUsage });
    }
  }

  /**
   * 检查电池消耗
   */
  private checkBatteryDrain(batteryDrain: number): void {
    const batteryLevel = (1 - batteryDrain) * 100;
    
    if (batteryLevel <= this.thresholds.battery.critical) {
      this.addPerformanceAlert('battery', 'critical', `电池电量严重不足：${batteryLevel.toFixed(1)}%`, { batteryLevel });
    } else if (batteryLevel <= this.thresholds.battery.error) {
      this.addPerformanceAlert('battery', 'error', `电池电量不足：${batteryLevel.toFixed(1)}%`, { batteryLevel });
    } else if (batteryLevel <= this.thresholds.battery.warning) {
      this.addPerformanceAlert('battery', 'warning', `电池电量较低：${batteryLevel.toFixed(1)}%`, { batteryLevel });
    }
  }

  /**
   * 检查网络延迟
   */
  private checkNetworkLatency(networkLatency: number): void {
    if (networkLatency < 0) {return;} // 网络不可用

    if (networkLatency >= this.thresholds.network.critical) {
      this.addPerformanceAlert('network', 'critical', `网络延迟过高：${networkLatency}ms`, { networkLatency });
    } else if (networkLatency >= this.thresholds.network.error) {
      this.addPerformanceAlert('network', 'error', `网络延迟较高：${networkLatency}ms`, { networkLatency });
    } else if (networkLatency >= this.thresholds.network.warning) {
      this.addPerformanceAlert('network', 'warning', `网络延迟偏高：${networkLatency}ms`, { networkLatency });
    }
  }

  /**
   * 检查渲染时间
   */
  private checkRenderTime(renderTime: number): void {
    if (renderTime >= this.thresholds.render.critical) {
      this.addPerformanceAlert('render', 'critical', `渲染时间过长：${renderTime.toFixed(1)}ms`, { renderTime });
    } else if (renderTime >= this.thresholds.render.error) {
      this.addPerformanceAlert('render', 'error', `渲染时间较长：${renderTime.toFixed(1)}ms`, { renderTime });
    } else if (renderTime >= this.thresholds.render.warning) {
      this.addPerformanceAlert('render', 'warning', `渲染时间偏长：${renderTime.toFixed(1)}ms`, { renderTime });
    }
  }

  /**
   * 添加性能警告
   */
  private addPerformanceAlert(
    type: PerformanceAlert['type'],
    severity: PerformanceAlert['severity'],
    message: string,
    metrics: any
  ): void {
    const alert: PerformanceAlert = {
      type,
      severity,
      message,
      timestamp: Date.now(),
      metrics,
    };

    this.performanceAlerts.push(alert);
    console.warn(`⚠️ 性能警告 [${severity.toUpperCase()}]: ${message}`);

    // 保持警告列表大小
    if (this.performanceAlerts.length > 100) {
      this.performanceAlerts = this.performanceAlerts.slice(-50);
    }
  }

  /**
   * 获取严重程度对应的阈值
   */
  private getThresholdForSeverity(type: keyof typeof this.thresholds, severity: string): number {
    const thresholds = this.thresholds[type];
    switch (severity) {
      case 'critical': return thresholds.critical;
      case 'high': return thresholds.error;
      case 'medium': return thresholds.warning;
      default: return 0;
    }
  }

  /**
   * 开始性能基准测试
   */
  startBenchmark(name: string, metadata?: Record<string, any>): void {
    const benchmark: PerformanceBenchmark = {
      name,
      startTime: Date.now(),
      metadata,
    };
    
    this.benchmarks.set(name, benchmark);
    console.log(`🏁 开始基准测试: ${name}`);
  }

  /**
   * 结束性能基准测试
   */
  endBenchmark(name: string): PerformanceBenchmark | null {
    const benchmark = this.benchmarks.get(name);
    if (!benchmark) {
      console.warn(`基准测试 "${name}" 不存在`);
      return null;
    }

    benchmark.endTime = Date.now();
    benchmark.duration = benchmark.endTime - benchmark.startTime;
    
    console.log(`🏆 基准测试完成: ${name} - ${benchmark.duration}ms`);
    return benchmark;
  }

  /**
   * 测试应用启动性能
   */
  async testAppStartupPerformance(): Promise<{
    coldStart: number;
    warmStart: number;
    jsLoad: number;
    firstRender: number;
  }> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      
      // 测试JS加载时间
      InteractionManager.runAfterInteractions(() => {
        const jsLoadTime = Date.now() - startTime;
        
        // 测试首次渲染时间
        requestAnimationFrame(() => {
          const firstRenderTime = Date.now() - startTime;
          
          resolve({
            coldStart: startTime,
            warmStart: Date.now() - startTime,
            jsLoad: jsLoadTime,
            firstRender: firstRenderTime,
          });
        });
      });
    });
  }

  /**
   * 测试内存泄漏
   */
  async testMemoryLeaks(iterations: number = 10): Promise<{
    initialMemory: number;
    finalMemory: number;
    memoryGrowth: number;
    averageGrowthPerIteration: number;
  }> {
    const initialMetrics = await deviceInfoManager.getCurrentPerformanceMetrics();
    const initialMemory = initialMetrics.memoryUsage.used;

    // 模拟内存使用操作
    for (let i = 0; i < iterations; i++) {
      // 创建一些临时对象来模拟内存使用
      const tempData = new Array(1000).fill(0).map(() => ({
        id: Math.random(),
        data: new Array(100).fill(Math.random()),
      }));
      
             // 等待一小段时间
       await new Promise<void>(resolve => setTimeout(resolve, 100));
      
      // 清理引用
      tempData.length = 0;
    }

    const finalMetrics = await deviceInfoManager.getCurrentPerformanceMetrics();
    const finalMemory = finalMetrics.memoryUsage.used;
    const memoryGrowth = finalMemory - initialMemory;

    return {
      initialMemory,
      finalMemory,
      memoryGrowth,
      averageGrowthPerIteration: memoryGrowth / iterations,
    };
  }

  /**
   * 设置应用状态监听
   */
     private setupAppStateListener(): void {
     const handleAppStateChange = (nextAppState: AppStateStatus) => {
       if (nextAppState === 'background') {
         console.log('📱 应用进入后台，暂停性能监控');
         this.stopMonitoring();
       } else if (nextAppState === 'active') {
         console.log('📱 应用回到前台，恢复性能监控');
         this.startMonitoring();
       }
     };
     
     AppState.addEventListener('change', handleAppStateChange);
   }

  /**
   * 获取性能报告
   */
  getPerformanceReport(): {
    alerts: PerformanceAlert[];
    memoryWarnings: MemoryWarning[];
    benchmarks: PerformanceBenchmark[];
    summary: {
      totalAlerts: number;
      criticalAlerts: number;
      memoryIssues: number;
      averageBenchmarkTime: number;
    };
  } {
    const completedBenchmarks = Array.from(this.benchmarks.values()).filter(b => b.duration !== undefined);
    const averageBenchmarkTime = completedBenchmarks.length > 0
      ? completedBenchmarks.reduce((sum, b) => sum + (b.duration || 0), 0) / completedBenchmarks.length
      : 0;

    return {
      alerts: [...this.performanceAlerts],
      memoryWarnings: [...this.memoryWarnings],
      benchmarks: completedBenchmarks,
      summary: {
        totalAlerts: this.performanceAlerts.length,
        criticalAlerts: this.performanceAlerts.filter(a => a.severity === 'critical').length,
        memoryIssues: this.memoryWarnings.length,
        averageBenchmarkTime,
      },
    };
  }

  /**
   * 清除所有性能数据
   */
  clearPerformanceData(): void {
    this.performanceAlerts = [];
    this.memoryWarnings = [];
    this.benchmarks.clear();
    console.log('🧹 性能数据已清除');
  }

  /**
   * 获取性能优化建议
   */
  getOptimizationSuggestions(): string[] {
    const suggestions: string[] = [];
    const report = this.getPerformanceReport();

    // 基于警告生成建议
    if (report.summary.memoryIssues > 0) {
      suggestions.push('检测到内存使用问题，建议优化内存管理');
      suggestions.push('考虑使用React.memo()和useMemo()优化组件渲染');
      suggestions.push('及时清理不需要的事件监听器和定时器');
    }

    if (report.summary.criticalAlerts > 0) {
      suggestions.push('检测到严重性能问题，建议立即优化');
      suggestions.push('考虑使用懒加载和代码分割减少初始加载时间');
    }

    if (report.summary.averageBenchmarkTime > 1000) {
      suggestions.push('操作响应时间较长，建议优化算法和数据结构');
      suggestions.push('考虑使用Web Workers处理耗时操作');
    }

    // 网络相关建议
    const networkAlerts = report.alerts.filter(a => a.type === 'network');
    if (networkAlerts.length > 0) {
      suggestions.push('网络延迟较高，建议实现请求缓存和离线功能');
      suggestions.push('考虑使用CDN加速静态资源加载');
    }

    // 渲染相关建议
    const renderAlerts = report.alerts.filter(a => a.type === 'render');
    if (renderAlerts.length > 0) {
      suggestions.push('渲染性能不佳，建议优化组件结构和减少重渲染');
      suggestions.push('使用FlatList替代ScrollView处理大量数据');
    }

    return suggestions;
  }
}

// 导出单例实例
export const performanceMonitor = PerformanceMonitor.getInstance();

// 便捷函数
export const startPerformanceMeasure = (
  id: string,
  name: string,
  type: PerformanceMetric['type'],
  metadata?: Record<string, any>
) => {
  performanceMonitor.startMeasure(id, name, type, metadata);
};

export const endPerformanceMeasure = (id: string, metadata?: Record<string, any>) => {
  performanceMonitor.endMeasure(id, metadata);
};

export const recordNetworkPerformance = (
  url: string,
  method: string,
  startTime: number,
  endTime: number,
  status?: number,
  responseSize?: number,
  requestSize?: number
) => {
  performanceMonitor.recordNetworkRequest(url, method, startTime, endTime, status, responseSize, requestSize);
};

export const recordRenderPerformance = (
  componentName: string,
  duration: number,
  renderCount?: number,
  props?: Record<string, any>
) => {
  performanceMonitor.recordRender(componentName, duration, renderCount, props);
};

export const recordUserInteraction = (
  action: string,
  target: string,
  coordinates?: { x: number; y: number },
  metadata?: Record<string, any>
) => {
  performanceMonitor.recordUserInteraction(action, target, coordinates, metadata);
};

export const getPerformanceStats = () => {
  return performanceMonitor.getStats();
};

export const getNetworkPerformanceStats = () => {
  return performanceMonitor.getNetworkStats();
};

export const clearPerformanceMetrics = () => {
  performanceMonitor.clearMetrics();
};

export const startMonitoring = (interval: number = 5000) => {
  performanceMonitor.startMonitoring(interval);
};

export const stopMonitoring = () => {
  performanceMonitor.stopMonitoring();
};

export const getPerformanceReport = () => {
  return performanceMonitor.getPerformanceReport();
};

export const clearPerformanceData = () => {
  performanceMonitor.clearPerformanceData();
};

export const getOptimizationSuggestions = () => {
  return performanceMonitor.getOptimizationSuggestions();
}; 