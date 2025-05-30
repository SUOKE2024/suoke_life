import {
import { useNavigation } from '@react-navigation/native';
import { colors, spacing, fonts } from '../../constants/theme';
import { apiIntegrationTest } from '../../utils/apiIntegrationTest';



import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';

interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'unknown';
  responseTime?: number;
  lastChecked: Date;
}

export const ServiceStatusScreen: React.FC = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // 初始化服务列表
  useEffect(() => {
    const initialServices: ServiceStatus[] = [
      { name: '认证服务', status: 'unknown', lastChecked: new Date() },
      { name: '用户服务', status: 'unknown', lastChecked: new Date() },
      { name: '健康数据服务', status: 'unknown', lastChecked: new Date() },
      { name: '小艾服务', status: 'unknown', lastChecked: new Date() },
      { name: '小克服务', status: 'unknown', lastChecked: new Date() },
      { name: '老克服务', status: 'unknown', lastChecked: new Date() },
      { name: '索儿服务', status: 'unknown', lastChecked: new Date() },
      { name: '望诊服务', status: 'unknown', lastChecked: new Date() },
      { name: '闻诊服务', status: 'unknown', lastChecked: new Date() },
      { name: '问诊服务', status: 'unknown', lastChecked: new Date() },
      { name: '切诊服务', status: 'unknown', lastChecked: new Date() },
    ];
    
    setServices(initialServices);
    checkServicesStatus();
  }, []);

  // 检查服务状态
  const checkServicesStatus = async () => {
    setLoading(true);
    
    try {
      // 运行测试
      const report = await apiIntegrationTest.runAllTests();
      
      // 更新服务状态
      setServices(prevServices => {
        return prevServices.map(service => {
          // 查找对应的测试结果
          const result = report.results.find(r => r.service === service.name);
          
          if (result) {
            return {
              ...service,
              status: result.success ? 'online' : 'offline',
              responseTime: result.responseTime,
              lastChecked: new Date(),
            };
          }
          
          return service;
        });
      });
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('服务检查失败:', error);
      Alert.alert('错误', '服务状态检查失败，请稍后重试。');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 刷新处理
  const handleRefresh = useCallback( () => {, []);
    setRefreshing(true);
    checkServicesStatus();
  };

  // 返回处理
  const handleBack = useCallback( () => {, []);
    navigation.goBack();
  };

  // 运行快速检查
  const runQuickCheck = async () => {
    setLoading(true);
    
    try {
      const result = await apiIntegrationTest.quickHealthCheck();
      
      Alert.alert(
        result.success ? '检查成功' : '检查警告',
        result.message,
        [{ text: '确定', onPress: () => console.log('确定') }]
      );
    } catch (error: any) {
      Alert.alert('错误', `快速检查失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>返回</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>服务状态</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
      >
        <View style={styles.statusHeader}>
          <Text style={styles.lastUpdateText}>
            最后更新: {lastUpdate.toLocaleTimeString()}
          </Text>
          <TouchableOpacity 
            style={styles.quickCheckButton}
            onPress={runQuickCheck}
            disabled={loading}
          >
            <Text style={styles.quickCheckButtonText}>快速检查</Text>
          </TouchableOpacity>
        </View>

        {loading && !refreshing ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>检查服务状态中...</Text>
          </View>
        ) : (
          <View style={styles.servicesContainer}>
            {services.map((service, index) => (
              <View key={index} style={styles.serviceItem}>
                <View style={styles.serviceHeader}>
                  <Text style={styles.serviceName}>{service.name}</Text>
                  <View style={[
                    styles.statusIndicator,
                    service.status === 'online' ? styles.statusOnline :
                    service.status === 'offline' ? styles.statusOffline :
                    styles.statusUnknown,
                  ]} />
                </View>
                
                <View style={styles.serviceDetails}>
                  <Text style={styles.serviceStatus}>
                    状态: {
                      service.status === 'online' ? '在线' :
                      service.status === 'offline' ? '离线' :
                      '未知'
                    }
                  </Text>
                  {service.responseTime && (
                    <Text style={styles.serviceResponseTime}>
                      响应时间: {service.responseTime}ms
                    </Text>
                  )}
                  <Text style={styles.serviceLastChecked}>
                    检查时间: {service.lastChecked.toLocaleTimeString()}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    padding: spacing.sm,
  },
  backButtonText: {
    color: colors.primary,
    fontSize: fonts.size.md,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    color: colors.text,
  },
  placeholder: {
    width: 50,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fonts.size.md,
    color: colors.textSecondary,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  lastUpdateText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  quickCheckButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 4,
  },
  quickCheckButtonText: {
    color: colors.white,
    fontSize: fonts.size.sm,
    fontWeight: 'bold',
  },
  servicesContainer: {
    marginBottom: spacing.xl,
  },
  serviceItem: {
    backgroundColor: colors.white,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
    ...StyleSheet.flatten({
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    }),
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  serviceName: {
    fontSize: fonts.size.md,
    fontWeight: 'bold',
    color: colors.text,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  statusOnline: {
    backgroundColor: colors.success,
  },
  statusOffline: {
    backgroundColor: colors.error,
  },
  statusUnknown: {
    backgroundColor: colors.disabled,
  },
  serviceDetails: {
    marginTop: spacing.sm,
  },
  serviceStatus: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  serviceResponseTime: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  serviceLastChecked: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
}); 