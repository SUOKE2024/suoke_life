import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from 'react-native';
import { unifiedApiService } from '../../services/unifiedApiService';
import { apiClient } from '../../services/apiClient';

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  instances: number;
  responseTime?: number;
  lastCheck?: string;
  error?: string;
}

interface GatewayStats {
  cacheStats: { size: number };
  circuitBreakerState: string;
  gatewayHealth: boolean;
}

export const GatewayMonitor: React.FC = () => {
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [gatewayStats, setGatewayStats] = useState<GatewayStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadGatewayStatus = async () => {
    try {
      setError(null);

      // 获取网关状态
      const [healthResponse, statsResponse] = await Promise.allSettled([
        unifiedApiService.getServiceHealth(),
        unifiedApiService.getApiStats(),
      ]);

      // 处理服务健康状态
      if (healthResponse.status === 'fulfilled' && healthResponse.value.success) {
        const serviceData = Array.isArray(healthResponse.value.data)
          ? healthResponse.value.data
          : Object.entries(healthResponse.value.data || {}).map(([name, data]: [string, any]) => ({
              name,
              status: data.status || 'unknown',
              instances: data.instances || 0,
              responseTime: data.responseTime,
              lastCheck: data.lastCheck,
            }));
        setServices(serviceData);
      } else {
        // 如果无法获取服务状态，显示默认服务列表
        const defaultServices = [
          'AUTH', 'USER', 'HEALTH_DATA', 'AGENTS', 'DIAGNOSIS',
          'RAG', 'BLOCKCHAIN', 'MESSAGE_BUS', 'MEDICAL_RESOURCE',
          'CORN_MAZE', 'ACCESSIBILITY', 'SUOKE_BENCH',
        ].map(name => ({
          name,
          status: 'unknown' as const,
          instances: 0,
          error: '无法连接到服务',
        }));
        setServices(defaultServices);
      }

      // 处理网关统计信息
      if (statsResponse.status === 'fulfilled') {
        setGatewayStats(statsResponse.value);
      }

    } catch (err: any) {
      console.error('Failed to load gateway status:', err);
      setError(err.message || '加载网关状态失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadGatewayStatus();
  };

  const clearCache = () => {
    apiClient.clearCache();
    loadGatewayStatus();
  };

  useEffect(() => {
    loadGatewayStatus();

    // 每30秒自动刷新
    const interval = setInterval(loadGatewayStatus, 30000);
    return () => clearInterval(interval);
  }, []);  // 检查是否需要添加依赖项;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#4CAF50';
      case 'unhealthy': return '#F44336';
      case 'unknown': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy': return '健康';
      case 'unhealthy': return '异常';
      case 'unknown': return '未知';
      default: return '离线';
    }
  };

  const getCircuitBreakerColor = (state: string) => {
    switch (state) {
      case 'CLOSED': return '#4CAF50';
      case 'OPEN': return '#F44336';
      case 'HALF_OPEN': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>加载网关状态中...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>API Gateway 监控</Text>
        <TouchableOpacity style={styles.clearButton} onPress={clearCache}>
          <Text style={styles.clearButtonText}>清除缓存</Text>
        </TouchableOpacity>
      </View>

      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>⚠️ {error}</Text>
        </View>
      )}

      {/* 网关统计信息 */}
      {gatewayStats && (
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>网关统计</Text>

          <View style={styles.statRow}>
            <Text style={styles.statLabel}>网关状态:</Text>
            <View style={[styles.statusDot, {
              backgroundColor: gatewayStats.gatewayHealth ? '#4CAF50' : '#F44336',
            }]} />
            <Text style={styles.statValue}>
              {gatewayStats.gatewayHealth ? '在线' : '离线'}
            </Text>
          </View>

          <View style={styles.statRow}>
            <Text style={styles.statLabel}>熔断器状态:</Text>
            <View style={[styles.statusDot, {
              backgroundColor: getCircuitBreakerColor(gatewayStats.circuitBreakerState),
            }]} />
            <Text style={styles.statValue}>{gatewayStats.circuitBreakerState}</Text>
          </View>

          <View style={styles.statRow}>
            <Text style={styles.statLabel}>缓存大小:</Text>
            <Text style={styles.statValue}>{gatewayStats.cacheStats.size} 项</Text>
          </View>
        </View>
      )}

      {/* 服务状态列表 */}
      <View style={styles.servicesContainer}>
        <Text style={styles.sectionTitle}>微服务状态</Text>

        {services.map((service, index) => (
          <View key={index} style={styles.serviceItem}>
            <View style={styles.serviceHeader}>
              <View style={[styles.statusDot, { backgroundColor: getStatusColor(service.status) }]} />
              <Text style={styles.serviceName}>{service.name}</Text>
              <Text style={[styles.serviceStatus, { color: getStatusColor(service.status) }]}>
                {getStatusText(service.status)}
              </Text>
            </View>

            <View style={styles.serviceDetails}>
              <Text style={styles.serviceDetail}>实例数: {service.instances}</Text>
              {service.responseTime && (
                <Text style={styles.serviceDetail}>响应时间: {service.responseTime}ms</Text>
              )}
              {service.lastCheck && (
                <Text style={styles.serviceDetail}>
                  最后检查: {new Date(service.lastCheck).toLocaleTimeString()}
                </Text>
              )}
              {service.error && (
                <Text style={styles.errorDetail}>错误: {service.error}</Text>
              )}
            </View>
          </View>
        ))}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          最后更新: {new Date().toLocaleTimeString()}
        </Text>
        <Text style={styles.footerText}>
          自动刷新间隔: 30秒
        </Text>
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
  clearButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
  },
  loadingText: {
    textAlign: 'center',
    marginTop: 50,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    margin: 16,
    padding: 12,
    backgroundColor: '#ffebee',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#f44336',
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
  },
  statsContainer: {
    margin: 16,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    minWidth: 100,
  },
  statValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    marginLeft: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  servicesContainer: {
    margin: 16,
    marginTop: 0,
  },
  serviceItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  serviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  serviceStatus: {
    fontSize: 14,
    fontWeight: '500',
  },
  serviceDetails: {
    paddingLeft: 16,
  },
  serviceDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  errorDetail: {
    fontSize: 12,
    color: '#f44336',
    marginTop: 4,
  },
  footer: {
    padding: 16,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
});

export default GatewayMonitor;
