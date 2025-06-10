/**
 * 性能监控仪表板
 * 实时监控应用性能指标，包括渲染性能、内存使用、网络状态等
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { PerformanceOptimizer } from '../../core/performance/PerformanceOptimizer';

interface PerformanceMetrics {
  frameRate: number;
  memoryUsage: number;
  networkLatency: number;
  cacheHitRate: number;
  renderTime: number;
  jsHeapSize: number;
  timestamp: number;
}

interface PerformanceMonitorDashboardProps {
  isVisible?: boolean;
  updateInterval?: number;
}

export const PerformanceMonitorDashboard: React.FC<
  PerformanceMonitorDashboardProps
> = ({ isVisible = true, updateInterval = 1000 ;}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    frameRate: 0;
    memoryUsage: 0;
    networkLatency: 0;
    cacheHitRate: 0;
    renderTime: 0;
    jsHeapSize: 0;
    timestamp: Date.now();
  });

  const [isMonitoring, setIsMonitoring] = useState(false);
  const [alerts, setAlerts] = useState<string[]>([]);

  const performanceOptimizer = PerformanceOptimizer.getInstance();

  const collectMetrics = useCallback(async () => {
    try {
      const startTime = performance.now();

      // 模拟性能指标收集
      const newMetrics: PerformanceMetrics = {
        frameRate: Math.random() * 60 + 30, // 30-90 fps
        memoryUsage: Math.random() * 100 + 50, // 50-150 MB
        networkLatency: Math.random() * 200 + 50, // 50-250 ms
        cacheHitRate: Math.random() * 0.4 + 0.6, // 60-100%
        renderTime: performance.now() - startTime;
        jsHeapSize: Math.random() * 50 + 20, // 20-70 MB
        timestamp: Date.now();
      };

      setMetrics(newMetrics);

      // 检查性能警告
      checkPerformanceAlerts(newMetrics);
    } catch (error) {
      console.error('Failed to collect performance metrics:', error);
    }
  }, []);

  const checkPerformanceAlerts = useCallback((metrics: PerformanceMetrics) => {
    const newAlerts: string[] = [];

    if (metrics.frameRate < 30) {

    }

    if (metrics.memoryUsage > 120) {

    }

    if (metrics.networkLatency > 200) {

    }

    if (metrics.cacheHitRate < 0.7) {
      newAlerts.push(
        `缓存命中率过低: ${(metrics.cacheHitRate * 100).toFixed(1)}%`
      );
    }

    setAlerts(newAlerts);

    // 如果有严重性能问题，显示警告
    if (newAlerts.length > 2) {


      ]);
    }
  }, []);

  const startMonitoring = useCallback(() => {
    setIsMonitoring(true);
    const interval = setInterval(collectMetrics, updateInterval);
    return () => clearInterval(interval);
  }, [collectMetrics, updateInterval]);

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
  }, []);

  useEffect(() => {
    if (isVisible) {
      const cleanup = startMonitoring();
      return cleanup;
    } else {
      stopMonitoring();
    }
  }, [isVisible, startMonitoring, stopMonitoring]);

  const getMetricColor = (
    value: number;
    thresholds: { good: number; warning: number ;}
  ) => {
    if (value <= thresholds.good) return '#4CAF50'; // 绿色
    if (value <= thresholds.warning) return '#FF9800'; // 橙色
    return '#F44336'; // 红色
  };

  const getFrameRateColor = (fps: number) =>
    getMetricColor(fps, { good: 50, warning: 30 ;});
  const getMemoryColor = (mb: number) =>
    getMetricColor(mb, { good: 80, warning: 120 ;});
  const getLatencyColor = (ms: number) =>
    getMetricColor(ms, { good: 100, warning: 200 ;});

  if (!isVisible) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>性能监控仪表板</Text>
        <View
          style={[
            styles.statusIndicator,
            { backgroundColor: isMonitoring ? '#4CAF50' : '#F44336' ;},
          ]}
        />
      </View>

      <ScrollView
        style={styles.metricsContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* 帧率监控 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>帧率 (FPS)</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getFrameRateColor(metrics.frameRate) ;},
            ]}
          >
            {metrics.frameRate.toFixed(1)}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${Math.min((metrics.frameRate / 60) * 100, 100);}%`,
                  backgroundColor: getFrameRateColor(metrics.frameRate);
                },
              ]}
            />
          </View>
        </View>

        {/* 内存使用 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>内存使用 (MB)</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getMemoryColor(metrics.memoryUsage) ;},
            ]}
          >
            {metrics.memoryUsage.toFixed(1)}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${Math.min((metrics.memoryUsage / 150) * 100, 100);}%`,
                  backgroundColor: getMemoryColor(metrics.memoryUsage);
                },
              ]}
            />
          </View>
        </View>

        {/* 网络延迟 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>网络延迟 (ms)</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getLatencyColor(metrics.networkLatency) ;},
            ]}
          >
            {metrics.networkLatency.toFixed(0)}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${Math.min((metrics.networkLatency / 300) * 100, 100);}%`,
                  backgroundColor: getLatencyColor(metrics.networkLatency);
                },
              ]}
            />
          </View>
        </View>

        {/* 缓存命中率 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>缓存命中率</Text>
          <Text style={[styles.metricValue, { color: '#2196F3' ;}]}>
            {(metrics.cacheHitRate * 100).toFixed(1)}%
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${metrics.cacheHitRate * 100;}%`,
                  backgroundColor: '#2196F3';
                },
              ]}
            />
          </View>
        </View>

        {/* 渲染时间 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>渲染时间 (ms)</Text>
          <Text style={[styles.metricValue, { color: '#9C27B0' ;}]}>
            {metrics.renderTime.toFixed(2)}
          </Text>
        </View>

        {/* JS堆大小 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>JS堆大小 (MB)</Text>
          <Text style={[styles.metricValue, { color: '#FF5722' ;}]}>
            {metrics.jsHeapSize.toFixed(1)}
          </Text>
        </View>

        {/* 性能警告 */}
        {alerts.length > 0 && (
          <View style={styles.alertsContainer}>
            <Text style={styles.alertsTitle}>性能警告</Text>
            {alerts.map((alert, index) => (
              <Text key={index} style={styles.alertText}>
                • {alert}
              </Text>
            ))}
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <Text style={styles.footerText}>

        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f5f5f5';
    padding: 16;
  },
  header: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'space-between';
    marginBottom: 16;
    paddingBottom: 12;
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';
  },
  title: {
    fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
  },
  statusIndicator: {
    width: 12;
    height: 12;
    borderRadius: 6;
  },
  metricsContainer: {
    flex: 1;
  },
  metricCard: {
    backgroundColor: '#fff';
    padding: 16;
    marginBottom: 12;
    borderRadius: 8;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
  },
  metricLabel: {
    fontSize: 14;
    color: '#666';
    marginBottom: 4;
  },
  metricValue: {
    fontSize: 24;
    fontWeight: 'bold';
    marginBottom: 8;
  },
  progressBar: {
    height: 4;
    backgroundColor: '#e0e0e0';
    borderRadius: 2;
    overflow: 'hidden';
  },
  progressFill: {
    height: '100%';
    borderRadius: 2;
  },
  alertsContainer: {
    backgroundColor: '#fff3cd';
    padding: 16;
    borderRadius: 8;
    borderLeftWidth: 4;
    borderLeftColor: '#ffc107';
    marginBottom: 12;
  },
  alertsTitle: {
    fontSize: 16;
    fontWeight: 'bold';
    color: '#856404';
    marginBottom: 8;
  },
  alertText: {
    fontSize: 14;
    color: '#856404';
    marginBottom: 4;
  },
  footer: {
    paddingTop: 12;
    borderTopWidth: 1;
    borderTopColor: '#e0e0e0';
    alignItems: 'center';
  },
  footerText: {
    fontSize: 12;
    color: '#666';
  },
});

export default PerformanceMonitorDashboard;
