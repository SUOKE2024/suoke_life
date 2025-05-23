/**
 * 智能体服务监控仪表板
 * 提供实时服务状态监控和健康检查界面
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { agentMonitor, getDashboardData, ServiceHealth, MonitoringReport } from '../../utils/agentMonitor';
import { apiCache } from '../../utils/apiCache';

interface AgentDashboardProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const AgentDashboard: React.FC<AgentDashboardProps> = ({
  autoRefresh = true,
  refreshInterval = 30000,
}) => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取仪表板数据
  const fetchDashboardData = async () => {
    try {
      setError(null);
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
      console.error('获取仪表板数据失败:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 下拉刷新
  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  // 启动/停止监控
  const toggleMonitoring = () => {
    if (dashboardData?.isMonitoring) {
      agentMonitor.stopMonitoring();
      Alert.alert('提示', '监控已停止');
    } else {
      agentMonitor.startMonitoring(refreshInterval);
      Alert.alert('提示', '监控已启动');
    }
    fetchDashboardData();
  };

  // 清理缓存
  const clearCache = async () => {
    try {
      await apiCache.clear();
      Alert.alert('成功', '缓存已清理');
    } catch (err) {
      Alert.alert('错误', '清理缓存失败');
    }
  };

  // 生成监控报告
  const generateReport = async () => {
    try {
      const report = await agentMonitor.generateReport();
      Alert.alert(
        '监控报告',
        `整体状态: ${report.overallHealth}\n` +
        `健康服务: ${report.services.filter(s => s.status === 'healthy').length}\n` +
        `活跃警告: ${report.alerts.length}\n` +
        `成功率: ${report.performance.successRate}%`
      );
    } catch (err) {
      Alert.alert('错误', '生成报告失败');
    }
  };

  useEffect(() => {
    fetchDashboardData();

    // 自动刷新
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchDashboardData, refreshInterval);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval]);

  if (loading && !dashboardData) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>加载监控数据...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchDashboardData}>
          <Text style={styles.retryButtonText}>重试</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* 标题栏 */}
      <View style={styles.header}>
        <Text style={styles.title}>智能体服务监控</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity
            style={[
              styles.headerButton,
              dashboardData?.isMonitoring ? styles.stopButton : styles.startButton
            ]}
            onPress={toggleMonitoring}
          >
            <Text style={styles.headerButtonText}>
              {dashboardData?.isMonitoring ? '停止' : '启动'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 整体状态 */}
      <View style={styles.overallStatus}>
        <Text style={styles.sectionTitle}>整体状态</Text>
        <View style={[
          styles.statusBadge,
          getStatusColor(dashboardData?.report?.overallHealth || 'unknown')
        ]}>
          <Text style={styles.statusText}>
            {getStatusText(dashboardData?.report?.overallHealth || 'unknown')}
          </Text>
        </View>
      </View>

      {/* 服务状态 */}
      <View style={styles.servicesSection}>
        <Text style={styles.sectionTitle}>服务状态</Text>
        {dashboardData?.report?.services?.map((service: ServiceHealth) => (
          <ServiceStatusCard key={service.serviceName} service={service} />
        ))}
      </View>

      {/* 性能指标 */}
      <View style={styles.performanceSection}>
        <Text style={styles.sectionTitle}>性能指标</Text>
        <View style={styles.metricsGrid}>
          <MetricCard
            title="成功率"
            value={`${dashboardData?.report?.performance?.successRate || 0}%`}
            color="#4CAF50"
          />
          <MetricCard
            title="平均响应时间"
            value={`${dashboardData?.report?.performance?.avgResponseTime || 0}ms`}
            color="#2196F3"
          />
          <MetricCard
            title="总请求数"
            value={dashboardData?.report?.performance?.totalRequests || 0}
            color="#FF9800"
          />
          <MetricCard
            title="错误率"
            value={`${dashboardData?.report?.performance?.errorRate || 0}%`}
            color="#F44336"
          />
        </View>
      </View>

      {/* 活跃警告 */}
      {dashboardData?.report?.alerts?.length > 0 && (
        <View style={styles.alertsSection}>
          <Text style={styles.sectionTitle}>活跃警告</Text>
          {dashboardData.report.alerts.map((alert: any) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </View>
      )}

      {/* 操作按钮 */}
      <View style={styles.actionsSection}>
        <TouchableOpacity style={styles.actionButton} onPress={generateReport}>
          <Text style={styles.actionButtonText}>生成报告</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} onPress={clearCache}>
          <Text style={styles.actionButtonText}>清理缓存</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

// 服务状态卡片
const ServiceStatusCard: React.FC<{ service: ServiceHealth }> = ({ service }) => (
  <View style={styles.serviceCard}>
    <View style={styles.serviceHeader}>
      <Text style={styles.serviceName}>{getServiceDisplayName(service.serviceName)}</Text>
      <View style={[styles.statusDot, getStatusColor(service.status)]} />
    </View>
    <Text style={styles.serviceDetails}>
      响应时间: {service.responseTime}ms
    </Text>
    <Text style={styles.serviceDetails}>
      最后检查: {new Date(service.lastCheck).toLocaleTimeString()}
    </Text>
    {service.error && (
      <Text style={styles.errorMessage}>{service.error}</Text>
    )}
  </View>
);

// 指标卡片
const MetricCard: React.FC<{
  title: string;
  value: string | number;
  color: string;
}> = ({ title, value, color }) => (
  <View style={styles.metricCard}>
    <Text style={styles.metricTitle}>{title}</Text>
    <Text style={[styles.metricValue, { color }]}>{value}</Text>
  </View>
);

// 警告卡片
const AlertCard: React.FC<{ alert: any }> = ({ alert }) => (
  <View style={[styles.alertCard, getAlertColor(alert.type)]}>
    <View style={styles.alertHeader}>
      <Text style={styles.alertType}>{getAlertTypeText(alert.type)}</Text>
      <Text style={styles.alertTime}>
        {new Date(alert.timestamp).toLocaleTimeString()}
      </Text>
    </View>
    <Text style={styles.alertMessage}>{alert.message}</Text>
    <Text style={styles.alertService}>服务: {getServiceDisplayName(alert.service)}</Text>
  </View>
);

// 工具函数
const getServiceDisplayName = (serviceName: string): string => {
  const nameMap: { [key: string]: string } = {
    'xiaoai': '小艾 (四诊协调)',
    'xiaoke': '小克 (资源调度)',
    'laoke': '老克 (知识传播)',
    'soer': '索儿 (生活管理)',
  };
  return nameMap[serviceName] || serviceName;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy': return { backgroundColor: '#4CAF50' };
    case 'unhealthy': return { backgroundColor: '#F44336' };
    case 'degraded': return { backgroundColor: '#FF9800' };
    case 'critical': return { backgroundColor: '#D32F2F' };
    default: return { backgroundColor: '#9E9E9E' };
  }
};

const getStatusText = (status: string): string => {
  switch (status) {
    case 'healthy': return '健康';
    case 'unhealthy': return '异常';
    case 'degraded': return '降级';
    case 'critical': return '严重';
    default: return '未知';
  }
};

const getAlertColor = (type: string) => {
  switch (type) {
    case 'critical': return { borderLeftColor: '#D32F2F', borderLeftWidth: 4 };
    case 'error': return { borderLeftColor: '#F44336', borderLeftWidth: 4 };
    case 'warning': return { borderLeftColor: '#FF9800', borderLeftWidth: 4 };
    default: return { borderLeftColor: '#2196F3', borderLeftWidth: 4 };
  }
};

const getAlertTypeText = (type: string): string => {
  switch (type) {
    case 'critical': return '严重';
    case 'error': return '错误';
    case 'warning': return '警告';
    default: return '信息';
  }
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
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#F44336',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  headerButtons: {
    flexDirection: 'row',
  },
  headerButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
    marginLeft: 8,
  },
  startButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#F44336',
  },
  headerButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  overallStatus: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
  },
  statusText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  servicesSection: {
    marginBottom: 16,
  },
  serviceCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  serviceDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  errorMessage: {
    fontSize: 12,
    color: '#F44336',
    marginTop: 4,
  },
  performanceSection: {
    marginBottom: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    width: '48%',
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  metricTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  alertsSection: {
    marginBottom: 16,
  },
  alertCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  alertTime: {
    fontSize: 12,
    color: '#666',
  },
  alertMessage: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  alertService: {
    fontSize: 12,
    color: '#666',
  },
  actionsSection: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  actionButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    flex: 0.45,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
});