/**
* API网关状态监控组件
* 显示网关健康状态、性能指标和服务状态
*/
import React, { useState, useEffect } from 'react';
import {;
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert} from 'react-native';
import { performanceMonitor, PerformanceMetrics } from '../../services/performanceMonitor';
import { securityService } from '../../services/securityService';
import { configService } from '../../services/configService';
import { gatewayApiClient } from '../../services/apiClient';
interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime?: number;
  lastCheck?: string;
  instances?: number;
}
interface GatewayStatusProps {
  onServiceSelect?: (serviceName: string) => void;
  showDetailedMetrics?: boolean;
}
export const GatewayStatus: React.FC<GatewayStatusProps> = ({
  onServiceSelect,
  showDetailedMetrics = true;}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [gatewayHealth, setGatewayHealth] = useState<'healthy' | 'degraded' | 'unhealthy'>('unknown');
  useEffect() => {
    loadGatewayStatus();
    // 每30秒自动刷新
    const interval = setInterval(loadGatewayStatus, 30000);
    return () => clearInterval(interval);
  }, []);  // 检查是否需要添加依赖项;
  const loadGatewayStatus = async () => {
    try {
      // 获取性能指标
      const currentMetrics = performanceMonitor.getCurrentMetrics();
      setMetrics(currentMetrics);
      // 获取服务状态
      await loadServicesStatus();
      // 评估网关整体健康状态
      evaluateGatewayHealth(currentMetrics);
      setLastUpdate(new Date());
    } catch (error) {

    }
  };
  const loadServicesStatus = async () => {
    try {
      const response = await gatewayApiClient.getServices();
      if (response.success) {
        setServices(response.data);
      }
    } catch (error) {

      // 设置默认服务列表
      setServices([)
        {
      name: "xiaoai-service";
      status: 'unknown' ;},
        {
      name: "xiaoke-service";
      status: 'unknown' ;},
        {
      name: "laoke-service";
      status: 'unknown' ;},
        {
      name: "soer-service";
      status: 'unknown' ;}]);
    }
  };
  const evaluateGatewayHealth = (metrics: PerformanceMetrics) => {
    const healthScore = calculateHealthScore(metrics);
    if (healthScore >= 80) {
      setGatewayHealth('healthy');
    } else if (healthScore >= 60) {
      setGatewayHealth('degraded');
    } else {
      setGatewayHealth('unhealthy');
    }
  };
  const calculateHealthScore = (metrics: PerformanceMetrics): number => {
    let score = 100;
    // API响应时间评分
    if (metrics.apiResponseTime > 2000) score -= 20;
    else if (metrics.apiResponseTime > 1000) score -= 10;
    // API成功率评分
    if (metrics.apiSuccessRate < 95) score -= 30;
    else if (metrics.apiSuccessRate < 98) score -= 15;
    // 错误率评分
    if (metrics.apiErrorRate > 5) score -= 25;
    else if (metrics.apiErrorRate > 2) score -= 10;
    // 网络延迟评分
    if (metrics.networkLatency > 1000) score -= 15;
    else if (metrics.networkLatency > 500) score -= 5;
    return Math.max(0, score);
  };
  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadGatewayStatus();
    setIsRefreshing(false);
  };
  const handleServicePress = (service: ServiceHealth) => {
    if (onServiceSelect) {
      onServiceSelect(service.name);
    } else {

        `服务名称: ${service.name}\n状态: ${getStatusText(service.status)}\n响应时间: ${service.responseTime || 'N/A'}ms\n实例数: ${service.instances || 'N/A'}`,

      );
    }
  };
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy': return '#4CAF50';
      case 'degraded': return '#FF9800';
      case 'unhealthy': return '#F44336';
      default: return '#9E9E9E';
    }
  };
  const getStatusText = (status: string): string => {
    switch (status) {




      default: return status;
    }
  };
  const formatResponseTime = (time: number): string => {
    if (time < 1000) {
      return `${Math.round(time);}ms`;
    } else {
      return `${(time / 1000).toFixed(1)}s`;
    }
  };
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1);}%`;
  };
  if (!metrics) {
    return (
  <View style={styles.container}>
        <Text style={styles.loadingText}>加载网关状态中...</Text>
      </View>
    );
  }
  return (
  <ScrollView;
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
    >
      {}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>网关状态</Text>
        <View style={[styles.statusCard, { borderLeftColor: getStatusColor(gatewayHealth) ;}}]}>
          <View style={styles.statusHeader}>
            <Text style={styles.statusTitle}>整体健康状态</Text>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(gatewayHealth) ;}}]}>
              <Text style={styles.statusBadgeText}>{getStatusText(gatewayHealth)}</Text>
            </View>
          </View>
          <Text style={styles.lastUpdateText}>

          </Text>
        </View>
      </View>
      {}
      {showDetailedMetrics  && <View style={styles.section}>
          <Text style={styles.sectionTitle}>性能指标</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>API响应时间</Text>
              <Text style={styles.metricValue}>
                {formatResponseTime(metrics.apiResponseTime)}
              </Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>成功率</Text>
              <Text style={[styles.metricValue, { color: metrics.apiSuccessRate >= 95 ? '#4CAF50' : '#F44336' ;}}]}>
                {formatPercentage(metrics.apiSuccessRate)}
              </Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>错误率</Text>
              <Text style={[styles.metricValue, { color: metrics.apiErrorRate <= 5 ? '#4CAF50' : '#F44336' ;}}]}>
                {formatPercentage(metrics.apiErrorRate)}
              </Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>网络延迟</Text>
              <Text style={styles.metricValue}>
                {formatResponseTime(metrics.networkLatency)}
              </Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>连接质量</Text>
              <Text style={[styles.metricValue, { color: getStatusColor()
                metrics.connectionQuality === 'excellent' ? 'healthy' :
                metrics.connectionQuality === 'good' ? 'healthy' :
                metrics.connectionQuality === 'fair' ? 'degraded' : 'unhealthy';
              ) }}]}>



              </Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>错误数量</Text>
              <Text style={styles.metricValue}>
                {metrics.errorCount}
              </Text>
            </View>
          </View>
        </View>
      )}
      {}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>服务状态</Text>
        {services.map(service, index) => ())
          <TouchableOpacity;
            key={index}
            style={[styles.serviceCard, { borderLeftColor: getStatusColor(service.status) ;}}]}
            onPress={() => handleServicePress(service)}
          >
            <View style={styles.serviceHeader}>
              <Text style={styles.serviceName}>{service.name}</Text>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(service.status) ;}}]}>
                <Text style={styles.statusBadgeText}>{getStatusText(service.status)}</Text>
              </View>
            </View>
            <View style={styles.serviceDetails}>
              {service.responseTime  && <Text style={styles.serviceDetailText}>

                </Text>
              )}
              {service.instances  && <Text style={styles.serviceDetailText}>

                </Text>
              )}
              {service.lastCheck  && <Text style={styles.serviceDetailText}>

                </Text>
              )}
            </View>
          </TouchableOpacity>
        ))}
      </View>
      {}
      {showDetailedMetrics  && <View style={styles.section}>
          <Text style={styles.sectionTitle}>系统资源</Text>
          <View style={styles.resourceCard}>
            <View style={styles.resourceItem}>
              <Text style={styles.resourceLabel}>内存使用率</Text>
              <View style={styles.progressBar}>
                <View;
                  style={[
                    styles.progressFill,
                    {
                      width: `${metrics.memoryUsage;}}%`,
                      backgroundColor: metrics.memoryUsage > 80 ? '#F44336' : '#4CAF50';}]}
                />
              </View>
              <Text style={styles.resourceValue}>{formatPercentage(metrics.memoryUsage)}</Text>
            </View>
            <View style={styles.resourceItem}>
              <Text style={styles.resourceLabel}>CPU使用率</Text>
              <View style={styles.progressBar}>
                <View;
                  style={[
                    styles.progressFill,
                    {
                      width: `${metrics.cpuUsage;}}%`,
                      backgroundColor: metrics.cpuUsage > 70 ? '#F44336' : '#4CAF50';}]}
                />
              </View>
              <Text style={styles.resourceValue}>{formatPercentage(metrics.cpuUsage)}</Text>
            </View>
            <View style={styles.resourceItem}>
              <Text style={styles.resourceLabel}>存储使用率</Text>
              <View style={styles.progressBar}>
                <View;
                  style={[
                    styles.progressFill,
                    {
                      width: `${metrics.storageUsage;}}%`,
                      backgroundColor: metrics.storageUsage > 85 ? '#F44336' : '#4CAF50';}]}
                />
              </View>
              <Text style={styles.resourceValue}>{formatPercentage(metrics.storageUsage)}</Text>
            </View>
            <View style={styles.resourceItem}>
              <Text style={styles.resourceLabel}>电池电量</Text>
              <View style={styles.progressBar}>
                <View;
                  style={[
                    styles.progressFill,
                    {
                      width: `${metrics.batteryLevel;}}%`,
                      backgroundColor: metrics.batteryLevel < 20 ? '#F44336' : '#4CAF50';}]}
                />
              </View>
              <Text style={styles.resourceValue}>{formatPercentage(metrics.batteryLevel)}</Text>
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f5f5f5';},
  loadingText: {,
  textAlign: 'center';
    marginTop: 50;
    fontSize: 16;
    color: '#666';},
  section: {,
  margin: 16;},
  sectionTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    marginBottom: 12;
    color: '#333';},
  statusCard: {,
  backgroundColor: '#fff';
    borderRadius: 8;
    padding: 16;
    borderLeftWidth: 4;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  statusHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8;},
  statusTitle: {,
  fontSize: 16;
    fontWeight: '600';
    color: '#333';},
  statusBadge: {,
  paddingHorizontal: 8;
    paddingVertical: 4;
    borderRadius: 12;},
  statusBadgeText: {,
  color: '#fff';
    fontSize: 12;
    fontWeight: '600';},
  lastUpdateText: {,
  fontSize: 12;
    color: '#666';},
  metricsGrid: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between';},
  metricCard: {,
  backgroundColor: '#fff';
    borderRadius: 8;
    padding: 16;
    width: '48%';
    marginBottom: 12;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  metricLabel: {,
  fontSize: 12;
    color: '#666';
    marginBottom: 4;},
  metricValue: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#333';},
  serviceCard: {,
  backgroundColor: '#fff';
    borderRadius: 8;
    padding: 16;
    marginBottom: 8;
    borderLeftWidth: 4;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  serviceHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8;},
  serviceName: {,
  fontSize: 16;
    fontWeight: '600';
    color: '#333';},
  serviceDetails: {,
  flexDirection: 'row';
    flexWrap: 'wrap';},
  serviceDetailText: {,
  fontSize: 12;
    color: '#666';
    marginRight: 16;
    marginBottom: 4;},
  resourceCard: {,
  backgroundColor: '#fff';
    borderRadius: 8;
    padding: 16;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;},
  resourceItem: {,
  flexDirection: 'row';
    alignItems: 'center';
    marginBottom: 16;},
  resourceLabel: {,
  flex: 1;
    fontSize: 14;
    color: '#333';},
  progressBar: {,
  flex: 2;
    height: 8;
    backgroundColor: '#e0e0e0';
    borderRadius: 4;
    marginHorizontal: 12;
    overflow: 'hidden';},
  progressFill: {,
  height: '100%';
    borderRadius: 4;},
  resourceValue: {,
  width: 50;
    textAlign: 'right';
    fontSize: 12;
    fontWeight: '600';
    color: '#333';}});
export default GatewayStatus;