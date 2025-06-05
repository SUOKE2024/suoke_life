import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { ragService } from '../../services/ragService';
import { useSelector } from 'react-redux';
import { selectPerformanceMetrics, selectCacheStats } from '../../store/slices/ragSlice';

interface PerformanceData {
  responseTime: number;
  cacheHitRate: number;
  errorRate: number;
  totalQueries: number;
  averageResponseTime: number;
  lastUpdateTime: number;
}

export const RAGPerformanceMonitor: React.FC = () => {
  const [performanceData, setPerformanceData] = useState<PerformanceData>({
    responseTime: 0,
    cacheHitRate: 0,
    errorRate: 0,
    totalQueries: 0,
    averageResponseTime: 0,
    lastUpdateTime: Date.now(),
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);

  const performanceMetrics = useSelector(selectPerformanceMetrics);
  const cacheStats = useSelector(selectCacheStats);

  // 更新性能数据
  const updatePerformanceData = useCallback(() => {
    const errorRate = performanceMetrics.totalQueries > 0 
      ? (performanceMetrics.failureCount / (performanceMetrics.totalQueries + performanceMetrics.failureCount)) * 100
      : 0;

    setPerformanceData({
      responseTime: performanceMetrics.averageResponseTime,
      cacheHitRate: cacheStats.hitRate,
      errorRate,
      totalQueries: performanceMetrics.totalQueries,
      averageResponseTime: performanceMetrics.averageResponseTime,
      lastUpdateTime: Date.now(),
    });
  }, [performanceMetrics, cacheStats]);

  // 监听性能事件
  useEffect(() => {
    const handlePerformanceUpdate = (data: any) => {
      updatePerformanceData();
    };

    ragService.on('performance', handlePerformanceUpdate);
    ragService.on('cache_hit', handlePerformanceUpdate);
    ragService.on('error', handlePerformanceUpdate);

    return () => {
      ragService.off('performance', handlePerformanceUpdate);
      ragService.off('cache_hit', handlePerformanceUpdate);
      ragService.off('error', handlePerformanceUpdate);
    };
  }, [updatePerformanceData]);

  // 定期更新数据
  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(updatePerformanceData, 5000); // 每5秒更新一次
      return () => clearInterval(interval);
    }
  }, [isMonitoring, updatePerformanceData]);

  // 刷新数据
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      // 获取最新的缓存统计
      const cacheStats = ragService.getCacheStats();
      updatePerformanceData();
    } catch (error) {
      Alert.alert('刷新失败', '无法获取最新性能数据');
    } finally {
      setIsRefreshing(false);
    }
  }, [updatePerformanceData]);

  // 清除性能数据
  const handleClearMetrics = useCallback(() => {
    Alert.alert(
      '确认清除',
      '确定要清除所有性能数据吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          style: 'destructive',
          onPress: () => {
            // 这里可以调用Redux action来重置性能指标
            setPerformanceData({
              responseTime: 0,
              cacheHitRate: 0,
              errorRate: 0,
              totalQueries: 0,
              averageResponseTime: 0,
              lastUpdateTime: Date.now(),
            });
          },
        },
      ]
    );
  }, []);

  // 切换监控状态
  const toggleMonitoring = useCallback(() => {
    setIsMonitoring(!isMonitoring);
  }, [isMonitoring]);

  // 获取性能状态颜色
  const getStatusColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return '#4caf50'; // 绿色
    if (value <= thresholds.warning) return '#ff9800'; // 橙色
    return '#f44336'; // 红色
  };

  // 格式化时间
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>RAG性能监控</Text>
        <TouchableOpacity
          style={[styles.monitorButton, isMonitoring && styles.monitorButtonActive]}
          onPress={toggleMonitoring}
        >
          <Text style={[styles.monitorButtonText, isMonitoring && styles.monitorButtonTextActive]}>
            {isMonitoring ? '停止监控' : '开始监控'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* 实时状态指示器 */}
      <View style={styles.statusIndicator}>
        <View style={[styles.statusDot, { backgroundColor: isMonitoring ? '#4caf50' : '#9e9e9e' }]} />
        <Text style={styles.statusText}>
          {isMonitoring ? '实时监控中' : '监控已停止'}
        </Text>
        <Text style={styles.lastUpdateText}>
          最后更新: {formatTime(performanceData.lastUpdateTime)}
        </Text>
      </View>

      {/* 性能指标卡片 */}
      <View style={styles.metricsContainer}>
        {/* 响应时间 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricTitle}>平均响应时间</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getStatusColor(performanceData.averageResponseTime, { good: 1000, warning: 3000 }) }
            ]}
          >
            {performanceData.averageResponseTime.toFixed(0)}ms
          </Text>
          <Text style={styles.metricDescription}>
            {performanceData.averageResponseTime <= 1000 ? '优秀' : 
             performanceData.averageResponseTime <= 3000 ? '良好' : '需要优化'}
          </Text>
        </View>

        {/* 缓存命中率 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricTitle}>缓存命中率</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getStatusColor(100 - performanceData.cacheHitRate, { good: 20, warning: 50 }) }
            ]}
          >
            {performanceData.cacheHitRate.toFixed(1)}%
          </Text>
          <Text style={styles.metricDescription}>
            {performanceData.cacheHitRate >= 80 ? '优秀' : 
             performanceData.cacheHitRate >= 50 ? '良好' : '需要优化'}
          </Text>
        </View>

        {/* 错误率 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricTitle}>错误率</Text>
          <Text
            style={[
              styles.metricValue,
              { color: getStatusColor(performanceData.errorRate, { good: 1, warning: 5 }) }
            ]}
          >
            {performanceData.errorRate.toFixed(1)}%
          </Text>
          <Text style={styles.metricDescription}>
            {performanceData.errorRate <= 1 ? '优秀' : 
             performanceData.errorRate <= 5 ? '良好' : '需要关注'}
          </Text>
        </View>

        {/* 总查询数 */}
        <View style={styles.metricCard}>
          <Text style={styles.metricTitle}>总查询数</Text>
          <Text style={[styles.metricValue, { color: '#2196f3' }]}>
            {performanceData.totalQueries}
          </Text>
          <Text style={styles.metricDescription}>
            累计查询次数
          </Text>
        </View>
      </View>

      {/* 缓存统计 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>缓存统计</Text>
        <View style={styles.cacheStats}>
          <View style={styles.cacheStatItem}>
            <Text style={styles.cacheStatLabel}>缓存大小</Text>
            <Text style={styles.cacheStatValue}>{cacheStats.size}</Text>
          </View>
          <View style={styles.cacheStatItem}>
            <Text style={styles.cacheStatLabel}>缓存键数量</Text>
            <Text style={styles.cacheStatValue}>{cacheStats.keys.length}</Text>
          </View>
          <View style={styles.cacheStatItem}>
            <Text style={styles.cacheStatLabel}>命中次数</Text>
            <Text style={styles.cacheStatValue}>{cacheStats.cacheHits}</Text>
          </View>
        </View>
      </View>

      {/* 操作按钮 */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton} onPress={handleRefresh}>
          <Text style={styles.actionButtonText}>刷新数据</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.actionButton, styles.clearButton]} 
          onPress={handleClearMetrics}
        >
          <Text style={[styles.actionButtonText, styles.clearButtonText]}>清除数据</Text>
        </TouchableOpacity>
      </View>

      {/* 性能建议 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>性能建议</Text>
        <View style={styles.suggestions}>
          {performanceData.averageResponseTime > 3000 && (
            <Text style={styles.suggestion}>
              • 响应时间较长，建议检查网络连接或服务器性能
            </Text>
          )}
          {performanceData.cacheHitRate < 50 && (
            <Text style={styles.suggestion}>
              • 缓存命中率较低，建议优化缓存策略
            </Text>
          )}
          {performanceData.errorRate > 5 && (
            <Text style={styles.suggestion}>
              • 错误率较高，建议检查服务稳定性
            </Text>
          )}
          {performanceData.averageResponseTime <= 1000 && 
           performanceData.cacheHitRate >= 80 && 
           performanceData.errorRate <= 1 && (
            <Text style={[styles.suggestion, { color: '#4caf50' }]}>
              • 性能表现优秀，系统运行良好
            </Text>
          )}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  monitorButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#2196f3',
  },
  monitorButtonActive: {
    backgroundColor: '#2196f3',
  },
  monitorButtonText: {
    color: '#2196f3',
    fontSize: 14,
    fontWeight: '600',
  },
  monitorButtonTextActive: {
    color: '#fff',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    marginTop: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  lastUpdateText: {
    fontSize: 12,
    color: '#666',
  },
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#fff',
    padding: 16,
    margin: '1%',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    elevation: 3,
  },
  metricTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  metricDescription: {
    fontSize: 10,
    color: '#999',
  },
  section: {
    backgroundColor: '#fff',
    margin: 8,
    padding: 16,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  cacheStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  cacheStatItem: {
    alignItems: 'center',
  },
  cacheStatLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  cacheStatValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196f3',
  },
  actions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#2196f3',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  clearButton: {
    backgroundColor: '#f44336',
  },
  clearButtonText: {
    color: '#fff',
  },
  suggestions: {
    gap: 8,
  },
  suggestion: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
}); 