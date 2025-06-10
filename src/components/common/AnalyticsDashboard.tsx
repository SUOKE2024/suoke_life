import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';
import { analyticsService, PerformanceMetrics, UserBehavior, ServiceUsage } from '../../services/analyticsService';
import { syncService, SyncStatus } from '../../services/syncService';
const { width } = Dimensions.get('window');
interface AnalyticsDashboardProps {
  visible?: boolean;
  onClose?: () => void;
}
interface DashboardTab {
  id: string;
  title: string;
  icon: string;
}
const TABS: DashboardTab[] = [
  {
      id: "performance";

  {
      id: "usage";

  {
      id: "behavior";

  {
      id: "sync";

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  visible = true,
  onClose;}) => {
  const [activeTab, setActiveTab] = useState('performance');
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [serviceUsage, setServiceUsage] = useState<ServiceUsage[]>([]);
  const [userBehavior, setUserBehavior] = useState<UserBehavior[]>([]);
  const [syncStatus, setSyncStatus] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  useEffect() => {
    if (visible) {
      loadAnalyticsData();
      const interval = setInterval(loadAnalyticsData, 30000); // 每30秒刷新
      return () => clearInterval(interval);
    }
  }, [visible]);
  const loadAnalyticsData = async () => {
    try {
      setRefreshing(true);
      // 加载性能指标
      const metrics = analyticsService.getPerformanceMetrics();
      setPerformanceMetrics(metrics);
      // 加载服务使用统计
      const usage = analyticsService.getServiceUsage();
      setServiceUsage(usage);
      // 加载用户行为数据
      const behavior = analyticsService.getUserBehavior();
      setUserBehavior(behavior);
      // 加载同步状态
      const sync = syncService.getSyncStatus();
      setSyncStatus(sync);
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setRefreshing(false);
    }
  };
  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0);}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };
  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };
  const renderPerformanceTab = () => {
    if (!performanceMetrics) {
      return (
  <View style={styles.emptyState}>
          <Text style={styles.emptyText}>暂无性能数据</Text>
        </View>
      );
    }
    return (
  <ScrollView style={styles.tabContent}>
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>平均响应时间</Text>
            <Text style={styles.metricValue}>
              {formatDuration(performanceMetrics.responseTime)}
            </Text>
            <Text style={styles.metricSubtext}>


            </Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>吞吐量</Text>
            <Text style={styles.metricValue}>
              {performanceMetrics.throughput}
            </Text>
            <Text style={styles.metricSubtext}>请求/分钟</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>错误率</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.errorRate > 5 ? '#ff4444' : '#00aa00' ;}}]}>
              {performanceMetrics.errorRate.toFixed(1)}%
            </Text>
            <Text style={styles.metricSubtext}>


            </Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>缓存命中率</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.cacheHitRate > 80 ? '#00aa00' : '#ff8800' ;}}]}>
              {performanceMetrics.cacheHitRate.toFixed(1)}%
            </Text>
            <Text style={styles.metricSubtext}>


            </Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>内存使用</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.memoryUsage > 80 ? '#ff4444' : '#00aa00' ;}}]}>
              {performanceMetrics.memoryUsage.toFixed(1)}%
            </Text>
            <Text style={styles.metricSubtext}>


            </Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricTitle}>CPU使用</Text>
            <Text style={styles.metricValue}>
              {performanceMetrics.cpuUsage.toFixed(1)}%
            </Text>
            <Text style={styles.metricSubtext}>浏览器环境不可用</Text>
          </View>
        </View>
      </ScrollView>
    );
  };
  const renderUsageTab = () => {
    if (serviceUsage.length === 0) {
      return (
  <View style={styles.emptyState}>
          <Text style={styles.emptyText}>暂无服务使用数据</Text>
        </View>
      );
    }
    return (
  <ScrollView style={styles.tabContent}>
        <Text style={styles.sectionTitle}>服务使用统计</Text>
        {serviceUsage.map(service, index) => ())
          <View key={service.service} style={styles.serviceCard}>
            <View style={styles.serviceHeader}>
              <Text style={styles.serviceName}>{service.service}</Text>
              <Text style={styles.serviceStatus}>
                {service.errors === 0 ? '✅' : '⚠️'}
              </Text>
            </View>
            <View style={styles.serviceStats}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>调用次数</Text>
                <Text style={styles.statValue}>{service.calls}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>错误次数</Text>
                <Text style={[
                  styles.statValue,
                  { color: service.errors > 0 ? '#ff4444' : '#666' ;}}]}>
                  {service.errors}
                </Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>平均响应时间</Text>
                <Text style={styles.statValue}>
                  {formatDuration(service.avgResponseTime)}
                </Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>最后使用</Text>
                <Text style={styles.statValue}>
                  {formatTimestamp(service.lastUsed)}
                </Text>
              </View>
            </View>
            <View style={styles.serviceMetrics}>
              <Text style={styles.metricLabel}>
                成功率: {(service.calls - service.errors) / service.calls * 100).toFixed(1)}%
              </Text>
              <View style={styles.progressBar}>
                <View;
                  style={[
                    styles.progressFill,
                    {
                      width: `${(service.calls - service.errors) / service.calls * 100;}}%`,
                      backgroundColor: service.errors === 0 ? '#00aa00' : '#ff8800';}]}
                />
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    );
  };
  const renderBehaviorTab = () => {
    if (userBehavior.length === 0) {
      return (
  <View style={styles.emptyState}>
          <Text style={styles.emptyText}>暂无用户行为数据</Text>
        </View>
      );
    }
    return (
  <ScrollView style={styles.tabContent}>
        <Text style={styles.sectionTitle}>用户行为分析</Text>
        {userBehavior.map(behavior, index) => ())
          <View key={`${behavior.userId}_${behavior.sessionId}`} style={styles.behaviorCard}>
            <View style={styles.behaviorHeader}>
              <Text style={styles.behaviorUser}>用户 {behavior.userId}</Text>
              <Text style={styles.behaviorDuration}>

              </Text>
            </View>
            <View style={styles.behaviorStats}>
              <View style={styles.behaviorStat}>
                <Text style={styles.behaviorStatLabel}>操作次数</Text>
                <Text style={styles.behaviorStatValue}>{behavior.actions.length}</Text>
              </View>
              <View style={styles.behaviorStat}>
                <Text style={styles.behaviorStatLabel}>访问页面</Text>
                <Text style={styles.behaviorStatValue}>{behavior.screens.length}</Text>
              </View>
              <View style={styles.behaviorStat}>
                <Text style={styles.behaviorStatLabel}>错误次数</Text>
                <Text style={[
                  styles.behaviorStatValue,
                  { color: behavior.errors > 0 ? '#ff4444' : '#666' ;}}]}>
                  {behavior.errors}
                </Text>
              </View>
            </View>
            <View style={styles.behaviorDetails}>
              <Text style={styles.behaviorDetailTitle}>最近操作:</Text>
              <Text style={styles.behaviorDetailText}>
                {behavior.actions.slice(-3).join(' → ')}
              </Text>
              <Text style={styles.behaviorDetailTitle}>访问页面:</Text>
              <Text style={styles.behaviorDetailText}>
                {behavior.screens.join(' → ')}
              </Text>
            </View>
          </View>
        ))}
      </ScrollView>
    );
  };
  const renderSyncTab = () => {
    if (!syncStatus) {
      return (
  <View style={styles.emptyState}>
          <Text style={styles.emptyText}>暂无同步状态数据</Text>
        </View>
      );
    }
    return (
  <ScrollView style={styles.tabContent}>
        <Text style={styles.sectionTitle}>数据同步状态</Text>
        <View style={styles.syncCard}>
          <View style={styles.syncHeader}>
            <Text style={styles.syncTitle}>同步状态</Text>
            <Text style={[
              styles.syncStatus,
              {
                color: syncStatus.isSyncing ? '#ff8800' : '#00aa00';
                backgroundColor: syncStatus.isSyncing ? '#fff3e0' : '#e8f5e8';}}]}>

            </Text>
          </View>
          <View style={styles.syncStats}>
            <View style={styles.syncStat}>
              <Text style={styles.syncStatLabel}>最后同步时间</Text>
              <Text style={styles.syncStatValue}>
                {syncStatus.lastSyncTime > 0;
                  ? formatTimestamp(syncStatus.lastSyncTime)

                }
              </Text>
            </View>
            <View style={styles.syncStat}>
              <Text style={styles.syncStatLabel}>待处理冲突</Text>
              <Text style={[
                styles.syncStatValue,
                { color: syncStatus.conflicts > 0 ? '#ff4444' : '#666' ;}}]}>
                {syncStatus.conflicts}
              </Text>
            </View>
            <View style={styles.syncStat}>
              <Text style={styles.syncStatLabel}>自动同步</Text>
              <Text style={[
                styles.syncStatValue,
                { color: syncStatus.autoSync ? '#00aa00' : '#ff8800' ;}}]}>

              </Text>
            </View>
          </View>
          {syncStatus.conflicts > 0  && <View style={styles.conflictWarning}>
              <Text style={styles.conflictText}>

              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    );
  };
  const renderTabContent = () => {
    switch (activeTab) {
      case 'performance':
        return renderPerformanceTab();
      case 'usage':
        return renderUsageTab();
      case 'behavior':
        return renderBehaviorTab();
      case 'sync':
        return renderSyncTab();
      default:
        return null;
    }
  };
  if (!visible) return null;
  return (
  <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>分析仪表板</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity;
            style={styles.refreshButton}
            onPress={loadAnalyticsData}
            disabled={refreshing}
          >
            <Text style={styles.refreshText}>

            </Text>
          </TouchableOpacity>
          {onClose  && <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
      <View style={styles.tabBar}>
        {TABS.map(tab => ()))
          <TouchableOpacity;
            key={tab.id}
            style={[
              styles.tab, activeTab === tab.id && styles.activeTab]}}
            onPress={() => setActiveTab(tab.id)}
          >
            <Text style={styles.tabIcon}>{tab.icon}</Text>
            <Text style={[
              styles.tabText,
              activeTab === tab.id && styles.activeTabText]}}>
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={styles.content}>
        {renderTabContent()}
      </View>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f5f5f5';},
  header: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    padding: 16;
    backgroundColor: '#fff';
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';},
  title: {,
  fontSize: 20;
    fontWeight: 'bold';
    color: '#333';},
  headerActions: {,
  flexDirection: 'row';
    alignItems: 'center';},
  refreshButton: {,
  paddingHorizontal: 12;
    paddingVertical: 6;
    backgroundColor: '#007AFF';
    borderRadius: 6;
    marginRight: 8;},
  refreshText: {,
  color: '#fff';
    fontSize: 14;
    fontWeight: '500';},
  closeButton: {,
  padding: 8;},
  closeText: {,
  fontSize: 18;
    color: '#666';},
  tabBar: {,
  flexDirection: 'row';
    backgroundColor: '#fff';
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';},
  tab: {,
  flex: 1;
    alignItems: 'center';
    paddingVertical: 12;
    paddingHorizontal: 8;},
  activeTab: {,
  borderBottomWidth: 2;
    borderBottomColor: '#007AFF';},
  tabIcon: {,
  fontSize: 16;
    marginBottom: 4;},
  tabText: {,
  fontSize: 12;
    color: '#666';},
  activeTabText: {,
  color: '#007AFF';
    fontWeight: '500';},
  content: {,
  flex: 1;},
  tabContent: {,
  flex: 1;
    padding: 16;},
  emptyState: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';},
  emptyText: {,
  fontSize: 16;
    color: '#999';},
  sectionTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 16;},
  metricsGrid: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between';},
  metricCard: {,
  width: (width - 48) / 2;
    backgroundColor: '#fff';
    padding: 16;
    borderRadius: 8;
    marginBottom: 16;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 2;},
  metricTitle: {,
  fontSize: 14;
    color: '#666';
    marginBottom: 8;},
  metricValue: {,
  fontSize: 24;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 4;},
  metricSubtext: {,
  fontSize: 12;
    color: '#999';},
  serviceCard: {,
  backgroundColor: '#fff';
    padding: 16;
    borderRadius: 8;
    marginBottom: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 2;},
  serviceHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 12;},
  serviceName: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333';},
  serviceStatus: {,
  fontSize: 16;},
  serviceStats: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    marginBottom: 12;},
  statItem: {,
  width: '50%';
    marginBottom: 8;},
  statLabel: {,
  fontSize: 12;
    color: '#666';
    marginBottom: 2;},
  statValue: {,
  fontSize: 14;
    fontWeight: '500';
    color: '#333';},
  serviceMetrics: {,
  marginTop: 8;},
  metricLabel: {,
  fontSize: 12;
    color: '#666';
    marginBottom: 4;},
  progressBar: {,
  height: 4;
    backgroundColor: '#e0e0e0';
    borderRadius: 2;
    overflow: 'hidden';},
  progressFill: {,
  height: '100%';
    borderRadius: 2;},
  behaviorCard: {,
  backgroundColor: '#fff';
    padding: 16;
    borderRadius: 8;
    marginBottom: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 2;},
  behaviorHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 12;},
  behaviorUser: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333';},
  behaviorDuration: {,
  fontSize: 12;
    color: '#666';},
  behaviorStats: {,
  flexDirection: 'row';
    justifyContent: 'space-around';
    marginBottom: 12;},
  behaviorStat: {,
  alignItems: 'center';},
  behaviorStatLabel: {,
  fontSize: 12;
    color: '#666';
    marginBottom: 2;},
  behaviorStatValue: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333';},
  behaviorDetails: {,
  marginTop: 8;},
  behaviorDetailTitle: {,
  fontSize: 12;
    fontWeight: 'bold';
    color: '#666';
    marginTop: 8;
    marginBottom: 4;},
  behaviorDetailText: {,
  fontSize: 12;
    color: '#333';},
  syncCard: {,
  backgroundColor: '#fff';
    padding: 16;
    borderRadius: 8;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 2;},
  syncHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 16;},
  syncTitle: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333';},
  syncStatus: {,
  fontSize: 12;
    fontWeight: '500';
    paddingHorizontal: 8;
    paddingVertical: 4;
    borderRadius: 4;},
  syncStats: {,
  marginBottom: 16;},
  syncStat: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8;},
  syncStatLabel: {,
  fontSize: 14;
    color: '#666';},
  syncStatValue: {,
  fontSize: 14;
    fontWeight: '500';
    color: '#333';},
  conflictWarning: {,
  backgroundColor: '#fff3e0';
    padding: 12;
    borderRadius: 6;
    borderLeftWidth: 4;
    borderLeftColor: '#ff8800';},
  conflictText: {,
  fontSize: 14;
    color: '#e65100';}});
export default AnalyticsDashboard;