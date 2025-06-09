import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface ServiceStatus {
  name: string;,
  status: 'online' | 'offline' | 'unknown';
  responseTime?: number;
  lastChecked: Date;,
  endpoint: string;,
  category: 'agent' | 'core' | 'diagnosis';
}

export const ServiceStatusScreen: React.FC = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const initialServices: ServiceStatus[] = [
    {
      name: '小艾服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8015',
      category: 'agent',
    },
    {
      name: '小克服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8016',
      category: 'agent',
    },
    {
      name: '老克服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8017',
      category: 'agent',
    },
    {
      name: '索儿服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8018',
      category: 'agent',
    },
    {
      name: '认证服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8001',
      category: 'core',
    },
    {
      name: '用户服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8002',
      category: 'core',
    },
    {
      name: '健康数据服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8003',
      category: 'core',
    },
    {
      name: '望诊服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8020',
      category: 'diagnosis',
    },
    {
      name: '闻诊服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8022',
      category: 'diagnosis',
    },
    {
      name: '问诊服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8021',
      category: 'diagnosis',
    },
    {
      name: '切诊服务',
      status: 'unknown',
      lastChecked: new Date(),
      endpoint: 'http://localhost:8024',
      category: 'diagnosis',
    },
  ];

  useEffect() => {
    setServices(initialServices);
    checkServicesStatus();
  }, []);

  const checkServicesStatus = useCallback(async () => {
    setLoading(true);
    try {
      const updatedServices = [
        ...(services.length > 0 ? services : initialServices),
      ];
      const controller = new AbortController();
      const timeoutId = setTimeout() => controller.abort(), 5000);

      const checkPromises = updatedServices.map(async (service) => {
        const startTime = Date.now();
        try {
          const response = await fetch(`${service.endpoint}/health`, {
            method: 'GET',
            headers: {,
  Accept: 'application/json',
            },
            signal: controller.signal,
          });
          const endTime = Date.now();
          const responseTime = endTime - startTime;

          return {
            ...service,
            status: response.ok;
              ? 'online'
              : ('offline' as 'online' | 'offline'),
            responseTime,
            lastChecked: new Date(),
          };
        } catch (error) {
          return {
            ...service,
            status: 'offline' as 'offline',
            responseTime: undefined,
            lastChecked: new Date(),
          };
        }
      });

      const results = await Promise.all(checkPromises);
      clearTimeout(timeoutId);

      setServices(results);
      setLastUpdate(new Date());
    } catch (error) {
      Alert.alert('错误', '服务状态检查失败，请稍后重试。');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [services]);

  const handleRefresh = useCallback() => {
    setRefreshing(true);
    checkServicesStatus();
  }, [checkServicesStatus]);

  const runQuickCheck = useCallback(async () => {
    setLoading(true);
    try {
      const onlineServices = services.filter(s) => s.status === 'online'
      ).length;
      const totalServices = services.length;
      const healthPercentage = (onlineServices / totalServices) * 100;

      let message = `系统健康度: ${healthPercentage.toFixed(1)}%\n`;
      message += `在线服务: ${onlineServices}/${totalServices}\n`;

      if (healthPercentage >= 80) {
        message += '系统运行良好';
      } else if (healthPercentage >= 60) {
        message += '系统运行正常，部分服务离线';
      } else {
        message += '系统存在问题，多个服务离线';
      }

      Alert.alert(healthPercentage >= 80 ? '检查成功' : '检查警告', message, [
        { text: '确定' },
      ]);
    } catch (error) {
      Alert.alert('错误', '快速检查失败');
    } finally {
      setLoading(false);
    }
  }, [services]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#27AE60';
      case 'offline':
        return '#E74C3C';
      case 'unknown':
        return '#95A5A6';
      default:
        return '#95A5A6';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'agent':
        return '#3498DB';
      case 'core':
        return '#9B59B6';
      case 'diagnosis':
        return '#E67E22';
      default:
        return '#95A5A6';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return '在线';
      case 'offline':
        return '离线';
      case 'unknown':
        return '未知';
      default:
        return '未知';
    }
  };

  const groupedServices = services.reduce(acc, service) => {
      if (!acc[service.category]) {
        acc[service.category] = [];
      }
      acc[service.category].push(service);
      return acc;
    },
    {} as Record<string, ServiceStatus[]>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>服务状态</Text>
        <TouchableOpacity onPress={runQuickCheck} disabled={loading}>
          <Text style={styles.quickCheckButton}>快速检查</Text>
        </TouchableOpacity>
      </View>

      <ScrollView;
        style={styles.content}
        refreshControl={
          <RefreshControl;
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#3498DB']}
            tintColor="#3498DB"
          />
        }
      >
        <View style={styles.statusHeader}>
          <Text style={styles.lastUpdateText}>
            最后更新: {lastUpdate.toLocaleTimeString()}
          </Text>
          <View style={styles.summaryStats}>
            <Text style={styles.statsText}>
              在线: {services.filter(s) => s.status === 'online').length}/
              {services.length}
            </Text>
          </View>
        </View>

        {loading && !refreshing ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#3498DB" />
            <Text style={styles.loadingText}>检查服务状态中...</Text>
          </View>
        ) : (
          <View style={styles.servicesContainer}>
            {Object.entries(groupedServices).map([category, categoryServices]) => (
                <View key={category} style={styles.categorySection}>
                  <Text style={styles.categoryTitle}>
                    {category === 'agent'
                      ? '智能体服务'
                      : category === 'core'
                        ? '核心服务'
                        : category === 'diagnosis'
                          ? '诊断服务'
                          : category}
                  </Text>
                  {categoryServices.map(service, index) => (
                    <View key={index} style={styles.serviceItem}>
                      <View style={styles.serviceHeader}>
                        <Text style={styles.serviceName}>{service.name}</Text>
                        <View style={styles.statusContainer}>
                          <View;
                            style={[
                              styles.statusIndicator,
                              {
                                backgroundColor: getStatusColor(service.status),
                              },
                            ]}
                          />
                          <Text;
                            style={[
                              styles.statusText,
                              { color: getStatusColor(service.status) },
                            ]}
                          >
                            {getStatusText(service.status)}
                          </Text>
                        </View>
                      </View>
                      <View style={styles.serviceDetails}>
                        <View;
                          style={[
                            styles.categoryBadge,
                            {
                              backgroundColor: getCategoryColor(
                                service.category;
                              ),
                            },
                          ]}
                        >
                          <Text style={styles.categoryBadgeText}>
                            {service.category.toUpperCase()}
                          </Text>
                        </View>
                        {service.responseTime && (
                          <Text style={styles.responseTime}>
                            响应时间: {service.responseTime}ms;
                          </Text>
                        )}
                        <Text style={styles.lastChecked}>
                          检查时间: {service.lastChecked.toLocaleTimeString()}
                        </Text>
                        <Text style={styles.endpoint}>
                          端点: {service.endpoint}
                        </Text>
                      </View>
                    </View>
                  ))}
                </View>
              )
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  backButton: {,
  fontSize: 24,
    color: '#2C3E50',
  },
  title: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  quickCheckButton: {,
  fontSize: 16,
    color: '#3498DB',
    fontWeight: '600',
  },
  content: {,
  flex: 1,
    padding: 20,
  },
  statusHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
  },
  lastUpdateText: {,
  fontSize: 14,
    color: '#7F8C8D',
  },
  summaryStats: {,
  alignItems: 'flex-end',
  },
  statsText: {,
  fontSize: 14,
    color: '#2C3E50',
    fontWeight: '600',
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {,
  marginTop: 16,
    fontSize: 16,
    color: '#7F8C8D',
  },
  servicesContainer: {,
  marginBottom: 20,
  },
  categorySection: {,
  marginBottom: 24,
  },
  categoryTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
  },
  serviceItem: {,
  backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  serviceHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceName: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  statusContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {,
  width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {,
  fontSize: 14,
    fontWeight: '600',
  },
  serviceDetails: {,
  gap: 8,
  },
  categoryBadge: {,
  paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  categoryBadgeText: {,
  color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  responseTime: {,
  fontSize: 14,
    color: '#7F8C8D',
  },
  lastChecked: {,
  fontSize: 14,
    color: '#7F8C8D',
  },
  endpoint: {,
  fontSize: 12,
    color: '#95A5A6',
    fontFamily: 'monospace',
  },
});

export default ServiceStatusScreen;
