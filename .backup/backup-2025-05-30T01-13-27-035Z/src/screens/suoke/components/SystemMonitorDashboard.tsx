import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../../components/common/Icon';
import { colors, spacing } from '../../../constants/theme';
import { monitoringSystem, SystemMetrics, ErrorInfo, HealthCheckResult } from '../../../utils/monitoringSystem';

import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

interface SystemMonitorDashboardProps {
  visible: boolean;
  onClose: () => void;
}

interface DashboardData {
  performance: Partial<SystemMetrics>;
  errors: {
    total: number;
    bySeverity: Record<string, number>;
    byScreen: Record<string, number>;
    recentErrors: ErrorInfo[];
  };
  health: {
    overall: 'healthy' | 'degraded' | 'unhealthy';
    healthyServices: number;
    totalServices: number;
    averageResponseTime: number;
  };
  services: HealthCheckResult[];
}

export const SystemMonitorDashboard: React.FC<SystemMonitorDashboardProps> = ({
  visible,
  onClose,
}) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'performance' | 'errors' | 'health'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (visible) {
      loadDashboardData();
      // 每30秒自动刷新
      const interval = useMemo(() => useMemo(() => setInterval(loadDashboardData, 30000), []), []);
      return () => clearInterval(interval);
    }
  }, [visible]);

  const loadDashboardData = useMemo(() => useMemo(() => async () => {
    try {
      setLoading(true), []), []);
      
      // 初始化监控系统
      await monitoringSystem.initialize();
      
      // 获取系统状态
      const systemStatus = useMemo(() => useMemo(() => monitoringSystem.getSystemStatus(), []), []);
      
      // 模拟获取服务健康状态
      const services: HealthCheckResult[] = [
        {
          service: 'xiaoai-service',
          status: 'healthy',
          responseTime: 120,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '99.9%' },
        },
        {
          service: 'xiaoke-service',
          status: 'healthy',
          responseTime: 95,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '99.8%' },
        },
        {
          service: 'laoke-service',
          status: 'degraded',
          responseTime: 350,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '98.5%', issue: '响应时间较慢' },
        },
        {
          service: 'soer-service',
          status: 'healthy',
          responseTime: 80,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '99.9%' },
        },
        {
          service: 'eco-services-api',
          status: 'healthy',
          responseTime: 150,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '99.7%' },
        },
        {
          service: 'blockchain-service',
          status: 'healthy',
          responseTime: 200,
          lastCheck: Date.now(),
          details: { version: '1.0.0', uptime: '99.6%' },
        },
      ];

      setDashboardData({
        performance: systemStatus.performance,
        errors: systemStatus.errors,
        health: systemStatus.health,
        services,
      });
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
      Alert.alert('错误', '加载监控数据失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = useMemo(() => useMemo(() => async () => {
    setRefreshing(true), []), []);
    await loadDashboardData();
  };

  const getStatusColor = useMemo(() => useMemo(() => (status: string): string => {
    switch (status) {
      case 'healthy': return colors.success, []), []);
      case 'degraded': return colors.warning;
      case 'unhealthy': return colors.error;
      default: return colors.textSecondary;
    }
  };

  const getStatusIcon = useMemo(() => useMemo(() => (status: string): string => {
    switch (status) {
      case 'healthy': return 'check-circle', []), []);
      case 'degraded': return 'alert-triangle';
      case 'unhealthy': return 'x-circle';
      default: return 'help-circle';
    }
  };

  const renderOverviewTab = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!dashboardData) {return null;}

    return (
      <ScrollView style={styles.tabContent}>
        {/* 系统健康状态 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🏥 系统健康状态</Text>
          <View style={[styles.healthCard, { borderLeftColor: getStatusColor(dashboardData.health.overall) }]}>
            <View style={styles.healthHeader}>
              <Icon 
                name={getStatusIcon(dashboardData.health.overall)} 
                size={24} 
                color={getStatusColor(dashboardData.health.overall)} 
              />
              <Text style={[styles.healthStatus, { color: getStatusColor(dashboardData.health.overall) }]}>
                {dashboardData.health.overall === 'healthy' ? '健康' : 
                 dashboardData.health.overall === 'degraded' ? '降级' : '不健康'}
              </Text>
            </View>
            <Text style={styles.healthDesc}>
              {dashboardData.health.healthyServices}/{dashboardData.health.totalServices} 个服务正常运行
            </Text>
            <Text style={styles.healthDesc}>
              平均响应时间: {dashboardData.health.averageResponseTime.toFixed(0)}ms
            </Text>
          </View>
        </View>

        {/* 关键指标 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 关键指标</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Icon name="zap" size={20} color={colors.primary} />
              <Text style={styles.metricValue}>
                {dashboardData.performance.performance?.apiResponseTime?.toFixed(0) || 0}ms
              </Text>
              <Text style={styles.metricLabel}>API响应时间</Text>
            </View>
            <View style={styles.metricCard}>
              <Icon name="cpu" size={20} color={colors.warning} />
              <Text style={styles.metricValue}>
                {dashboardData.performance.performance?.memoryUsage?.toFixed(1) || 0}%
              </Text>
              <Text style={styles.metricLabel}>内存使用率</Text>
            </View>
            <View style={styles.metricCard}>
              <Icon name="alert-circle" size={20} color={colors.error} />
              <Text style={styles.metricValue}>{dashboardData.errors.total}</Text>
              <Text style={styles.metricLabel}>错误总数</Text>
            </View>
            <View style={styles.metricCard}>
              <Icon name="activity" size={20} color={colors.success} />
              <Text style={styles.metricValue}>
                {dashboardData.performance.user?.interactions || 0}
              </Text>
              <Text style={styles.metricLabel}>用户交互</Text>
            </View>
          </View>
        </View>

        {/* 服务状态 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔧 服务状态</Text>
          {dashboardData.services.map((service) => (
            <View key={service.service} style={styles.serviceCard}>
              <View style={styles.serviceHeader}>
                <Icon 
                  name={getStatusIcon(service.status)} 
                  size={16} 
                  color={getStatusColor(service.status)} 
                />
                <Text style={styles.serviceName}>{service.service}</Text>
                <Text style={styles.serviceResponseTime}>{service.responseTime}ms</Text>
              </View>
              <Text style={styles.serviceDetails}>
                版本: {service.details?.version || 'N/A'} | 
                运行时间: {service.details?.uptime || 'N/A'}
              </Text>
              {service.details?.issue && (
                <Text style={styles.serviceIssue}>⚠️ {service.details.issue}</Text>
              )}
            </View>
          ))}
        </View>
      </ScrollView>
    );
  };

  const renderPerformanceTab = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!dashboardData) {return null;}

    return (
      <ScrollView style={styles.tabContent}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚡ 性能指标</Text>
          
          {/* 性能图表区域 */}
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>API响应时间趋势</Text>
            <View style={styles.chartPlaceholder}>
              <Icon name="trending-up" size={48} color={colors.textSecondary} />
              <Text style={styles.chartPlaceholderText}>图表数据加载中...</Text>
            </View>
          </View>

          {/* 详细性能指标 */}
          <View style={styles.performanceDetails}>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>API响应时间</Text>
              <Text style={styles.performanceValue}>
                {dashboardData.performance.performance?.apiResponseTime?.toFixed(2) || 0}ms
              </Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>内存使用率</Text>
              <Text style={styles.performanceValue}>
                {dashboardData.performance.performance?.memoryUsage?.toFixed(1) || 0}%
              </Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>CPU使用率</Text>
              <Text style={styles.performanceValue}>
                {dashboardData.performance.performance?.cpuUsage?.toFixed(1) || 0}%
              </Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>网络延迟</Text>
              <Text style={styles.performanceValue}>
                {dashboardData.performance.performance?.networkLatency?.toFixed(0) || 0}ms
              </Text>
            </View>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceLabel}>渲染时间</Text>
              <Text style={styles.performanceValue}>
                {dashboardData.performance.performance?.renderTime?.toFixed(2) || 0}ms
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderErrorsTab = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!dashboardData) {return null;}

    return (
      <ScrollView style={styles.tabContent}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🚨 错误统计</Text>
          
          {/* 错误严重程度分布 */}
          <View style={styles.errorSeverityContainer}>
            <Text style={styles.subsectionTitle}>按严重程度分布</Text>
            <View style={styles.severityGrid}>
              {Object.entries(dashboardData.errors.bySeverity).map(([severity, count]) => (
                <View key={severity} style={styles.severityCard}>
                  <Text style={[styles.severityCount, { 
                    color: severity === 'critical' ? colors.error : 
                           severity === 'high' ? colors.warning :
                           severity === 'medium' ? colors.primary : colors.textSecondary, 
                  }]}>
                    {count}
                  </Text>
                  <Text style={styles.severityLabel}>
                    {severity === 'critical' ? '严重' :
                     severity === 'high' ? '高' :
                     severity === 'medium' ? '中' : '低'}
                  </Text>
                </View>
              ))}
            </View>
          </View>

          {/* 最近错误 */}
          <View style={styles.recentErrorsContainer}>
            <Text style={styles.subsectionTitle}>最近错误</Text>
            {dashboardData.errors.recentErrors.length === 0 ? (
              <View style={styles.noErrorsContainer}>
                <Icon name="check-circle" size={48} color={colors.success} />
                <Text style={styles.noErrorsText}>暂无错误记录</Text>
              </View>
            ) : (
              dashboardData.errors.recentErrors.map((error, index) => (
                <View key={index} style={styles.errorCard}>
                  <View style={styles.errorHeader}>
                    <Icon 
                      name="alert-circle" 
                      size={16} 
                      color={error.severity === 'critical' ? colors.error : colors.warning} 
                    />
                    <Text style={styles.errorMessage} numberOfLines={1}>
                      {error.message}
                    </Text>
                    <Text style={styles.errorTime}>
                      {new Date(error.timestamp).toLocaleTimeString()}
                    </Text>
                  </View>
                  <Text style={styles.errorScreen}>页面: {error.screen}</Text>
                </View>
              ))
            )}
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderHealthTab = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!dashboardData) {return null;}

    return (
      <ScrollView style={styles.tabContent}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🏥 健康检查</Text>
          
          {/* 整体健康状态 */}
          <View style={[styles.overallHealthCard, { 
            backgroundColor: getStatusColor(dashboardData.health.overall) + '20',
            borderColor: getStatusColor(dashboardData.health.overall),
          }]}>
            <Icon 
              name={getStatusIcon(dashboardData.health.overall)} 
              size={32} 
              color={getStatusColor(dashboardData.health.overall)} 
            />
            <Text style={[styles.overallHealthText, { 
              color: getStatusColor(dashboardData.health.overall), 
            }]}>
              系统整体状态: {dashboardData.health.overall === 'healthy' ? '健康' : 
                           dashboardData.health.overall === 'degraded' ? '降级' : '不健康'}
            </Text>
          </View>

          {/* 服务详细状态 */}
          <View style={styles.servicesContainer}>
            <Text style={styles.subsectionTitle}>服务详细状态</Text>
            {dashboardData.services.map((service) => (
              <TouchableOpacity 
                key={service.service} 
                style={styles.serviceDetailCard}
                onPress={() => Alert.alert('服务详情', JSON.stringify(service.details, null, 2))}
              >
                <View style={styles.serviceDetailHeader}>
                  <View style={styles.serviceDetailLeft}>
                    <Icon 
                      name={getStatusIcon(service.status)} 
                      size={20} 
                      color={getStatusColor(service.status)} 
                    />
                    <Text style={styles.serviceDetailName}>{service.service}</Text>
                  </View>
                  <View style={styles.serviceDetailRight}>
                    <Text style={styles.serviceDetailResponseTime}>
                      {service.responseTime}ms
                    </Text>
                    <Icon name="chevron-right" size={16} color={colors.textSecondary} />
                  </View>
                </View>
                
                <View style={styles.serviceDetailInfo}>
                  <Text style={styles.serviceDetailText}>
                    最后检查: {new Date(service.lastCheck).toLocaleString()}
                  </Text>
                  <Text style={styles.serviceDetailText}>
                    运行时间: {service.details?.uptime || 'N/A'}
                  </Text>
                </View>

                {service.details?.issue && (
                  <View style={styles.serviceIssueContainer}>
                    <Icon name="alert-triangle" size={14} color={colors.warning} />
                    <Text style={styles.serviceIssueText}>{service.details.issue}</Text>
                  </View>
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>
    );
  };

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      {[
        { key: 'overview', label: '概览', icon: 'home' },
        { key: 'performance', label: '性能', icon: 'zap' },
        { key: 'errors', label: '错误', icon: 'alert-circle' },
        { key: 'health', label: '健康', icon: 'heart' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tabButton, selectedTab === tab.key && styles.activeTabButton]}
          onPress={() => setSelectedTab(tab.key as any)}
        >
          <Icon 
            name={tab.icon} 
            size={20} 
            color={selectedTab === tab.key ? colors.primary : colors.textSecondary} 
          />
          <Text style={[
            styles.tabLabel,
            selectedTab === tab.key && styles.activeTabLabel,
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []);

  const renderContent = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (loading) {
      return (
        <View style={styles.loadingContainer}>
          <Icon name="loader" size={48} color={colors.primary} />
          <Text style={styles.loadingText}>加载监控数据中...</Text>
        </View>
      );
    }

    switch (selectedTab) {
      case 'overview': return renderOverviewTab();
      case 'performance': return renderPerformanceTab();
      case 'errors': return renderErrorsTab();
      case 'health': return renderHealthTab();
      default: return renderOverviewTab();
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.container}>
        {/* 头部 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Icon name="x" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.title}>系统监控</Text>
          <TouchableOpacity onPress={onRefresh} style={styles.refreshButton}>
            <Icon name="refresh-cw" size={24} color={colors.primary} />
          </TouchableOpacity>
        </View>

        {/* 标签栏 */}
        {renderTabBar()}

        {/* 内容区域 */}
        <View style={styles.content}>
          {renderContent()}
        </View>
      </SafeAreaView>
    </Modal>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  closeButton: {
    padding: spacing.sm,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
  },
  refreshButton: {
    padding: spacing.sm,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  activeTabButton: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  activeTabLabel: {
    color: colors.primary,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    flex: 1,
    padding: spacing.lg,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  section: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  subsectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  healthCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderLeftWidth: 4,
  },
  healthHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  healthStatus: {
    fontSize: 18,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
  healthDesc: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: (width - spacing.lg * 2 - spacing.md) / 2,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
    marginVertical: spacing.sm,
  },
  metricLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  serviceCard: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  serviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  serviceName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    flex: 1,
    marginLeft: spacing.sm,
  },
  serviceResponseTime: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  serviceDetails: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  serviceIssue: {
    fontSize: 12,
    color: colors.warning,
    marginTop: spacing.xs,
  },
  chartContainer: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  chartPlaceholder: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chartPlaceholderText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  performanceDetails: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
  },
  performanceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  performanceLabel: {
    fontSize: 14,
    color: colors.text,
  },
  performanceValue: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
  },
  errorSeverityContainer: {
    marginBottom: spacing.lg,
  },
  severityGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  severityCard: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: spacing.xs,
  },
  severityCount: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  severityLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  recentErrorsContainer: {
    marginBottom: spacing.lg,
  },
  noErrorsContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  noErrorsText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  errorCard: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  errorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  errorMessage: {
    fontSize: 14,
    color: colors.text,
    flex: 1,
    marginLeft: spacing.sm,
  },
  errorTime: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  errorScreen: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  overallHealthCard: {
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 1,
  },
  overallHealthText: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: spacing.sm,
  },
  servicesContainer: {
    marginBottom: spacing.lg,
  },
  serviceDetailCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  serviceDetailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  serviceDetailLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  serviceDetailName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginLeft: spacing.sm,
  },
  serviceDetailRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  serviceDetailResponseTime: {
    fontSize: 14,
    color: colors.textSecondary,
    marginRight: spacing.sm,
  },
  serviceDetailInfo: {
    marginBottom: spacing.sm,
  },
  serviceDetailText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  serviceIssueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.warning + '20',
    borderRadius: 6,
    padding: spacing.sm,
  },
  serviceIssueText: {
    fontSize: 12,
    color: colors.warning,
    marginLeft: spacing.xs,
  },
}), []), []);

export default SystemMonitorDashboard; 