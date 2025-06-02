import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

export interface SystemMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  threshold: {
    warning: number;
    critical: number;
  };
  lastUpdated: Date;
}

export interface ServiceStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'degraded';
  uptime: number;
  responseTime: number;
  errorRate: number;
  lastCheck: Date;
}

export interface SystemAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  resolved: boolean;
}

export interface SystemMonitorDashboardProps {
  onMetricPress?: (metric: SystemMetric) => void;
  onServicePress?: (service: ServiceStatus) => void;
  onAlertPress?: (alert: SystemAlert) => void;
}

/**
 * 系统监控仪表板组件
 * 展示系统性能指标、服务状态和告警信息
 */
export const SystemMonitorDashboard: React.FC<SystemMonitorDashboardProps> = ({
  onMetricPress,
  onServicePress,
  onAlertPress
}) => {
  const [metrics, setMetrics] = useState<SystemMetric[]>([]);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSystemData();
    const interval = setInterval(loadSystemData, 30000); // 每30秒刷新
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      // 模拟加载系统监控数据
      const mockMetrics: SystemMetric[] = [
        {
          id: 'cpu-usage',
          name: 'CPU使用率',
          value: 45,
          unit: '%',
          status: 'healthy',
          threshold: { warning: 70, critical: 90 },
          lastUpdated: new Date()
        },
        {
          id: 'memory-usage',
          name: '内存使用率',
          value: 68,
          unit: '%',
          status: 'healthy',
          threshold: { warning: 80, critical: 95 },
          lastUpdated: new Date()
        },
        {
          id: 'disk-usage',
          name: '磁盘使用率',
          value: 82,
          unit: '%',
          status: 'warning',
          threshold: { warning: 80, critical: 95 },
          lastUpdated: new Date()
        },
        {
          id: 'network-latency',
          name: '网络延迟',
          value: 25,
          unit: 'ms',
          status: 'healthy',
          threshold: { warning: 100, critical: 200 },
          lastUpdated: new Date()
        }
      ];

      const mockServices: ServiceStatus[] = [
        {
          id: 'api-gateway',
          name: 'API网关',
          status: 'online',
          uptime: 99.8,
          responseTime: 120,
          errorRate: 0.1,
          lastCheck: new Date()
        },
        {
          id: 'user-service',
          name: '用户服务',
          status: 'online',
          uptime: 99.9,
          responseTime: 85,
          errorRate: 0.05,
          lastCheck: new Date()
        },
        {
          id: 'health-service',
          name: '健康服务',
          status: 'degraded',
          uptime: 98.5,
          responseTime: 250,
          errorRate: 1.2,
          lastCheck: new Date()
        },
        {
          id: 'ai-service',
          name: 'AI服务',
          status: 'online',
          uptime: 99.7,
          responseTime: 180,
          errorRate: 0.3,
          lastCheck: new Date()
        }
      ];

      const mockAlerts: SystemAlert[] = [
        {
          id: 'alert-001',
          type: 'warning',
          title: '磁盘空间不足',
          message: '系统磁盘使用率已达到82%，建议清理日志文件',
          timestamp: new Date(Date.now() - 10 * 60 * 1000),
          resolved: false
        },
        {
          id: 'alert-002',
          type: 'warning',
          title: '健康服务响应缓慢',
          message: '健康服务平均响应时间超过200ms',
          timestamp: new Date(Date.now() - 5 * 60 * 1000),
          resolved: false
        },
        {
          id: 'alert-003',
          type: 'info',
          title: '系统更新完成',
          message: 'API网关已成功更新到v2.1.0',
          timestamp: new Date(Date.now() - 60 * 60 * 1000),
          resolved: true
        }
      ];

      setMetrics(mockMetrics);
      setServices(mockServices);
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('加载系统监控数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMetricStatusColor = (status: SystemMetric['status']): string => {
    switch (status) {
      case 'healthy':
        return '#4CAF50';
      case 'warning':
        return '#FF9800';
      case 'critical':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const getServiceStatusColor = (status: ServiceStatus['status']): string => {
    switch (status) {
      case 'online':
        return '#4CAF50';
      case 'degraded':
        return '#FF9800';
      case 'offline':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const getAlertTypeColor = (type: SystemAlert['type']): string => {
    switch (type) {
      case 'error':
        return '#F44336';
      case 'warning':
        return '#FF9800';
      case 'info':
        return '#2196F3';
      default:
        return '#757575';
    }
  };

  const getAlertIcon = (type: SystemAlert['type']): string => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📋';
    }
  };

  const renderMetricCard = (metric: SystemMetric) => (
    <TouchableOpacity
      key={metric.id}
      style={styles.metricCard}
      onPress={() => onMetricPress?.(metric)}
    >
      <View style={styles.metricHeader}>
        <Text style={styles.metricName}>{metric.name}</Text>
        <View style={[styles.statusDot, { backgroundColor: getMetricStatusColor(metric.status) }]} />
      </View>
      <View style={styles.metricValue}>
        <Text style={[styles.valueText, { color: getMetricStatusColor(metric.status) }]}>
          {metric.value}
        </Text>
        <Text style={styles.unitText}>{metric.unit}</Text>
      </View>
      <View style={styles.thresholdInfo}>
        <Text style={styles.thresholdText}>
          警告: {metric.threshold.warning}{metric.unit} | 严重: {metric.threshold.critical}{metric.unit}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderServiceCard = (service: ServiceStatus) => (
    <TouchableOpacity
      key={service.id}
      style={styles.serviceCard}
      onPress={() => onServicePress?.(service)}
    >
      <View style={styles.serviceHeader}>
        <Text style={styles.serviceName}>{service.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getServiceStatusColor(service.status) }]}>
          <Text style={styles.statusText}>{service.status.toUpperCase()}</Text>
        </View>
      </View>
      <View style={styles.serviceMetrics}>
        <View style={styles.serviceMetric}>
          <Text style={styles.metricLabel}>可用性</Text>
          <Text style={styles.serviceMetricValue}>{service.uptime}%</Text>
        </View>
        <View style={styles.serviceMetric}>
          <Text style={styles.metricLabel}>响应时间</Text>
          <Text style={styles.serviceMetricValue}>{service.responseTime}ms</Text>
        </View>
        <View style={styles.serviceMetric}>
          <Text style={styles.metricLabel}>错误率</Text>
          <Text style={styles.serviceMetricValue}>{service.errorRate}%</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderAlertCard = (alert: SystemAlert) => (
    <TouchableOpacity
      key={alert.id}
      style={[styles.alertCard, alert.resolved && styles.resolvedAlert]}
      onPress={() => onAlertPress?.(alert)}
    >
      <View style={styles.alertHeader}>
        <Text style={styles.alertIcon}>{getAlertIcon(alert.type)}</Text>
        <View style={styles.alertInfo}>
          <Text style={[styles.alertTitle, { color: getAlertTypeColor(alert.type) }]}>
            {alert.title}
          </Text>
          <Text style={styles.alertTimestamp}>
            {alert.timestamp.toLocaleTimeString()}
          </Text>
        </View>
        {alert.resolved && (
          <View style={styles.resolvedBadge}>
            <Text style={styles.resolvedText}>已解决</Text>
          </View>
        )}
      </View>
      <Text style={styles.alertMessage}>{alert.message}</Text>
    </TouchableOpacity>
  );

  const renderOverview = () => {
    const healthyMetrics = metrics.filter(m => m.status === 'healthy').length;
    const onlineServices = services.filter(s => s.status === 'online').length;
    const unresolvedAlerts = alerts.filter(a => !a.resolved).length;

    return (
      <View style={styles.overviewContainer}>
        <Text style={styles.sectionTitle}>系统概览</Text>
        <View style={styles.overviewGrid}>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{healthyMetrics}/{metrics.length}</Text>
            <Text style={styles.overviewLabel}>健康指标</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{onlineServices}/{services.length}</Text>
            <Text style={styles.overviewLabel}>在线服务</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{unresolvedAlerts}</Text>
            <Text style={styles.overviewLabel}>待处理告警</Text>
          </View>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>加载系统监控数据中...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {renderOverview()}

      <Text style={styles.sectionTitle}>系统指标</Text>
      <View style={styles.metricsGrid}>
        {metrics.map(renderMetricCard)}
      </View>

      <Text style={styles.sectionTitle}>服务状态</Text>
      <View style={styles.servicesContainer}>
        {services.map(renderServiceCard)}
      </View>

      <Text style={styles.sectionTitle}>系统告警</Text>
      <View style={styles.alertsContainer}>
        {alerts.map(renderAlertCard)}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    marginTop: 16,
  },
  overviewContainer: {
    marginBottom: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  overviewCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  overviewValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 4,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: (width - 48) / 2,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  metricHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricName: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
    flex: 1,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  metricValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  valueText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  unitText: {
    fontSize: 12,
    color: '#999',
    marginLeft: 4,
  },
  thresholdInfo: {
    marginTop: 4,
  },
  thresholdText: {
    fontSize: 10,
    color: '#999',
  },
  servicesContainer: {
    marginBottom: 16,
  },
  serviceCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: '600',
  },
  serviceMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  serviceMetric: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  serviceMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  alertsContainer: {
    marginBottom: 16,
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  resolvedAlert: {
    opacity: 0.7,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  alertInfo: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  alertTimestamp: {
    fontSize: 12,
    color: '#999',
  },
  resolvedBadge: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  resolvedText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: '500',
  },
  alertMessage: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});

export default SystemMonitorDashboard; 