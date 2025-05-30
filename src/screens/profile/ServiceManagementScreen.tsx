import { useNavigation } from '@react-navigation/native';
import { colors, spacing, fonts } from '../../constants/theme';
import { API_CONFIG } from '../../constants/config';





import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Switch,
  Platform,
} from 'react-native';

interface ServiceInfo {
  id: string;
  name: string;
  description: string;
  type: 'agent' | 'core' | 'diagnosis';
  isRunning: boolean;
  baseUrl: string;
  status: 'starting' | 'running' | 'stopping' | 'stopped' | 'error';
  lastAction?: string;
}

export const ServiceManagementScreen: React.FC = () => {
  const navigation = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useNavigation(), []), []), []), []), []), []);
  const [loading, setLoading] = useState(false);
  const [services, setServices] = useState<ServiceInfo[]>([]);
  const [autoStart, setAutoStart] = useState(false);

  useEffect(() => {
    // 初始化服务列表
    initializeServices();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  const initializeServices = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []), []), []), []);
    // 创建服务列表
    const servicesList: ServiceInfo[] = [
      // 智能体服务
      {
        id: 'xiaoai',
        name: '小艾服务',
        description: '中医诊断智能体',
        type: 'agent',
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.XIAOAI,
        status: 'stopped',
      },
      {
        id: 'xiaoke',
        name: '小克服务',
        description: '服务管理智能体',
        type: 'agent',
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.XIAOKE,
        status: 'stopped',
      },
      {
        id: 'laoke',
        name: '老克服务',
        description: '教育智能体',
        type: 'agent',
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.LAOKE,
        status: 'stopped',
      },
      {
        id: 'soer',
        name: '索儿服务',
        description: '生活智能体',
        type: 'agent',
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.SOER,
        status: 'stopped',
      },

      // 核心服务
      {
        id: 'auth',
        name: '认证服务',
        description: '用户认证和授权',
        type: 'core',
        isRunning: false,
        baseUrl: API_CONFIG.SERVICES.AUTH,
        status: 'stopped',
      },
      {
        id: 'user',
        name: '用户服务',
        description: '用户资料和数据管理',
        type: 'core',
        isRunning: false,
        baseUrl: API_CONFIG.SERVICES.USER,
        status: 'stopped',
      },
      {
        id: 'health',
        name: '健康数据服务',
        description: '健康数据收集和分析',
        type: 'core',
        isRunning: false,
        baseUrl: API_CONFIG.SERVICES.HEALTH,
        status: 'stopped',
      },

      // 五诊服务
      {
        id: 'look',
        name: '望诊服务',
        description: '图像分析和识别',
        type: 'diagnosis',
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.LOOK,
        status: 'stopped',
      },
      {
        id: 'listen',
        name: '闻诊服务',
        description: '音频分析和处理',
        type: 'diagnosis',
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.LISTEN,
        status: 'stopped',
      },
      {
        id: 'inquiry',
        name: '问诊服务',
        description: '智能问答系统',
        type: 'diagnosis',
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.INQUIRY,
        status: 'stopped',
      },
      {
        id: 'palpation',
        name: '切诊服务',
        description: '脉象检测和分析',
        type: 'diagnosis',
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.PALPATION,
        status: 'stopped',
      },
    ];

    setServices(servicesList);
    checkServicesStatus(servicesList);
  };

  // 检查服务状态
  const checkServicesStatus = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async (servicesList: ServiceInfo[]) => {
    setLoading(true), []), []), []), []), []), []);
    
    try {
      const updatedServices = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => [...(servicesList || services)], []), []), []), []), []), []);
      
      // 使用AbortController实现超时功能
      const controller = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => new AbortController(), []), []), []), []), []), []);
      const timeoutId = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => setTimeout(() => controller.abort(), 3000), []), []), []), []), []), []);
      
      // 并行检查所有服务
      const checkPromises = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => updatedServices.map(async (service) => {
        try {
          const response = await fetch(`${service.baseUrl}/health`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            },
            signal: controller.signal,
          }), []), []), []), []), []), []);
          
          return {
            id: service.id,
            isRunning: response.ok,
            status: response.ok ? 'running' : 'stopped' as 'running' | 'stopped',
          };
        } catch (error) {
          return {
            id: service.id,
            isRunning: false,
            status: 'stopped' as 'stopped',
          };
        }
      });
      
      // 等待所有检查完成
      const results = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => await Promise.all(checkPromises), []), []), []), []), []), []);
      clearTimeout(timeoutId);
      
      // 更新服务状态
      results.forEach(result => {
        const index = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => updatedServices.findIndex(s => s.id === result.id), []), []), []), []), []), []);
        if (index !== -1) {
          updatedServices[index] = {
            ...updatedServices[index],
            isRunning: result.isRunning,
            status: result.status,
          };
        }
      });
      
      setServices(updatedServices);
    } catch (error) {
      console.error('检查服务状态失败:', error);
      Alert.alert('错误', '检查服务状态失败，请稍后重试。');
    } finally {
      setLoading(false);
    }
  };

  // 启动服务
  const startService = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async (serviceId: string) => {
    // 更新服务状态为启动中
    setServices(prev => prev.map(s => 
      s.id === serviceId 
        ? { ...s, status: 'starting', lastAction: '正在启动...' } 
        : s
    )), []), []), []), []), []), []);
    
    try {
      // 通常这里会调用后端API启动服务，这里模拟一下
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve();
        }, 2000);
      });
      
      // 更新服务状态为运行中
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, isRunning: true, status: 'running', lastAction: '启动成功' } 
          : s
      ));
      
      Alert.alert('成功', `服务 ${serviceId} 已成功启动`);
    } catch (error) {
      console.error(`启动服务 ${serviceId} 失败:`, error);
      
      // 更新服务状态为错误
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, status: 'error', lastAction: '启动失败' } 
          : s
      ));
      
      Alert.alert('错误', `启动服务 ${serviceId} 失败，请稍后重试。`);
    }
  };

  // 停止服务
  const stopService = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async (serviceId: string) => {
    // 更新服务状态为停止中
    setServices(prev => prev.map(s => 
      s.id === serviceId 
        ? { ...s, status: 'stopping', lastAction: '正在停止...' } 
        : s
    )), []), []), []), []), []), []);
    
    try {
      // 通常这里会调用后端API停止服务，这里模拟一下
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve();
        }, 1500);
      });
      
      // 更新服务状态为已停止
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, isRunning: false, status: 'stopped', lastAction: '停止成功' } 
          : s
      ));
      
      Alert.alert('成功', `服务 ${serviceId} 已成功停止`);
    } catch (error) {
      console.error(`停止服务 ${serviceId} 失败:`, error);
      
      // 更新服务状态为错误
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, status: 'error', lastAction: '停止失败' } 
          : s
      ));
      
      Alert.alert('错误', `停止服务 ${serviceId} 失败，请稍后重试。`);
    }
  };

  // 重启服务
  const restartService = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async (serviceId: string) => {
    // 更新服务状态为停止中
    setServices(prev => prev.map(s => 
      s.id === serviceId 
        ? { ...s, status: 'stopping', lastAction: '正在重启...' } 
        : s
    )), []), []), []), []), []), []);
    
    try {
      // 通常这里会调用后端API重启服务，这里模拟一下
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve();
        }, 3000);
      });
      
      // 更新服务状态为运行中
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, isRunning: true, status: 'running', lastAction: '重启成功' } 
          : s
      ));
      
      Alert.alert('成功', `服务 ${serviceId} 已成功重启`);
    } catch (error) {
      console.error(`重启服务 ${serviceId} 失败:`, error);
      
      // 更新服务状态为错误
      setServices(prev => prev.map(s => 
        s.id === serviceId 
          ? { ...s, status: 'error', lastAction: '重启失败' } 
          : s
      ));
      
      Alert.alert('错误', `重启服务 ${serviceId} 失败，请稍后重试。`);
    }
  };

  // 启动所有服务
  const startAllServices = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async () => {
    if (loading) {return, []), []), []), []), []), []);}
    
    setLoading(true);
    Alert.alert('确认', '确定要启动所有服务吗？这可能需要一些时间。', [
      {
        text: '取消',
        style: 'cancel',
        onPress: () => setLoading(false),
      },
      {
        text: '确定',
        onPress: async () => {
          try {
            // 更新所有服务状态为启动中
            setServices(prev => prev.map(s => 
              s.status !== 'running' 
                ? { ...s, status: 'starting', lastAction: '正在启动...' } 
                : s
            ));
            
            // 通常这里会调用后端API启动所有服务，这里模拟一下
            await new Promise<void>((resolve) => {
              setTimeout(() => {
                resolve();
              }, 5000);
            });
            
            // 更新所有服务状态为运行中
            setServices(prev => prev.map(s => 
              s.status !== 'running'
                ? { ...s, isRunning: true, status: 'running', lastAction: '启动成功' } 
                : s
            ));
            
            Alert.alert('成功', '所有服务已成功启动');
          } catch (error) {
            console.error('启动所有服务失败:', error);
            Alert.alert('错误', '启动所有服务失败，请稍后重试。');
          } finally {
            setLoading(false);
          }
        },
      },
    ]);
  };

  // 停止所有服务
  const stopAllServices = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => async () => {
    if (loading) {return, []), []), []), []), []), []);}
    
    setLoading(true);
    Alert.alert('确认', '确定要停止所有服务吗？这将中断所有正在进行的操作。', [
      {
        text: '取消',
        style: 'cancel',
        onPress: () => setLoading(false),
      },
      {
        text: '确定',
        onPress: async () => {
          try {
            // 更新所有服务状态为停止中
            setServices(prev => prev.map(s => 
              s.status === 'running' 
                ? { ...s, status: 'stopping', lastAction: '正在停止...' } 
                : s
            ));
            
            // 通常这里会调用后端API停止所有服务，这里模拟一下
            await new Promise<void>((resolve) => {
              setTimeout(() => {
                resolve();
              }, 3000);
            });
            
            // 更新所有服务状态为已停止
            setServices(prev => prev.map(s => 
              s.status === 'running' || s.status === 'stopping'
                ? { ...s, isRunning: false, status: 'stopped', lastAction: '停止成功' } 
                : s
            ));
            
            Alert.alert('成功', '所有服务已成功停止');
          } catch (error) {
            console.error('停止所有服务失败:', error);
            Alert.alert('错误', '停止所有服务失败，请稍后重试。');
          } finally {
            setLoading(false);
          }
        },
      },
    ]);
  };

  // 刷新服务状态
  const refreshServicesStatus = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []), []), []), []);
    checkServicesStatus(services);
  };

  // 返回处理
  const handleBack = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []), []), []), []);
    navigation.goBack();
  };

  // 获取服务状态样式
  const getStatusStyle = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (status: string) => {, []), []), []), []), []), []), []);
    switch (status) {
      case 'running':
        return styles.statusRunning;
      case 'starting':
        return styles.statusStarting;
      case 'stopping':
        return styles.statusStopping;
      case 'error':
        return styles.statusError;
      default:
        return styles.statusStopped;
    }
  };

  // 获取服务状态文本
  const getStatusText = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (status: string) => {, []), []), []), []), []), []), []);
    switch (status) {
      case 'running':
        return '运行中';
      case 'starting':
        return '启动中';
      case 'stopping':
        return '停止中';
      case 'error':
        return '错误';
      default:
        return '已停止';
    }
  };

  // 渲染服务项
  const renderServiceItem = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (service: ServiceInfo) => {, []), []), []), []), []), []), []);
    const isDisabled = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => service.status === 'starting' || service.status === 'stopping', []), []), []), []), []), []);
    
    return (
      <View key={service.id} style={styles.serviceItem}>
        <View style={styles.serviceHeader}>
          <Text style={styles.serviceName}>{service.name}</Text>
          <View style={[styles.statusIndicator, getStatusStyle(service.status)]} />
        </View>
        
        <Text style={styles.serviceDescription}>{service.description}</Text>
        
        <View style={styles.serviceStatusRow}>
          <Text style={styles.serviceStatusText}>
            状态: {getStatusText(service.status)}
          </Text>
          {service.lastAction && (
            <Text style={styles.serviceActionText}>
              最后操作: {service.lastAction}
            </Text>
          )}
        </View>
        
        <View style={styles.serviceActions}>
          {service.status === 'running' ? (
            <>
              <TouchableOpacity
                style={[styles.actionButton, styles.stopButton, isDisabled && styles.disabledButton]}
                onPress={() => stopService(service.id)}
                disabled={isDisabled}
              >
                <Text style={styles.actionButtonText}>停止</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.actionButton, styles.restartButton, isDisabled && styles.disabledButton]}
                onPress={() => restartService(service.id)}
                disabled={isDisabled}
              >
                <Text style={styles.actionButtonText}>重启</Text>
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity
              style={[styles.actionButton, styles.startButton, isDisabled && styles.disabledButton]}
              onPress={() => startService(service.id)}
              disabled={isDisabled}
            >
              <Text style={styles.actionButtonText}>启动</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>返回</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>服务管理</Text>
        <TouchableOpacity onPress={refreshServicesStatus} disabled={loading}>
          <Text style={[styles.refreshButton, loading && styles.disabledText]}>
            刷新
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.globalControls}>
        <View style={styles.autoStartContainer}>
          <Text style={styles.autoStartText}>启动时自动启动服务</Text>
          <Switch
            value={autoStart}
            onValueChange={setAutoStart}
            trackColor={{ false: colors.disabled, true: colors.primary }}
            thumbColor={Platform.OS === 'android' ? colors.white : ''}
          />
        </View>
        
        <View style={styles.globalButtons}>
          <TouchableOpacity
            style={[styles.globalButton, styles.startAllButton]}
            onPress={startAllServices}
            disabled={loading}
          >
            <Text style={styles.globalButtonText}>启动所有服务</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.globalButton, styles.stopAllButton]}
            onPress={stopAllServices}
            disabled={loading}
          >
            <Text style={styles.globalButtonText}>停止所有服务</Text>
          </TouchableOpacity>
        </View>
      </View>

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>正在处理...</Text>
        </View>
      )}

      <ScrollView style={styles.content}>
        <View style={styles.serviceSection}>
          <Text style={styles.sectionTitle}>智能体服务</Text>
          {services
            .filter(service => service.type === 'agent')
            .map(renderServiceItem)}
        </View>
        
        <View style={styles.serviceSection}>
          <Text style={styles.sectionTitle}>核心服务</Text>
          {services
            .filter(service => service.type === 'core')
            .map(renderServiceItem)}
        </View>
        
        <View style={styles.serviceSection}>
          <Text style={styles.sectionTitle}>五诊服务</Text>
          {services
            .filter(service => service.type === 'diagnosis')
            .map(renderServiceItem)}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
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
    zIndex: 10,
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
  refreshButton: {
    color: colors.primary,
    fontSize: fonts.size.md,
    fontWeight: 'bold',
    padding: spacing.sm,
  },
  globalControls: {
    backgroundColor: colors.white,
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    zIndex: 5,
  },
  autoStartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  autoStartText: {
    fontSize: fonts.size.md,
    color: colors.text,
  },
  globalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  globalButton: {
    flex: 1,
    padding: spacing.md,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: spacing.sm,
  },
  startAllButton: {
    backgroundColor: colors.primary,
  },
  stopAllButton: {
    backgroundColor: colors.error,
  },
  globalButtonText: {
    color: colors.white,
    fontSize: fonts.size.md,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  serviceSection: {
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: fonts.size.md,
    fontWeight: 'bold',
    color: colors.textSecondary,
    marginBottom: spacing.md,
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
  statusRunning: {
    backgroundColor: colors.success,
  },
  statusStarting: {
    backgroundColor: colors.warning,
  },
  statusStopping: {
    backgroundColor: colors.info,
  },
  statusStopped: {
    backgroundColor: colors.disabled,
  },
  statusError: {
    backgroundColor: colors.error,
  },
  serviceDescription: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  serviceStatusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  serviceStatusText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  serviceActionText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  serviceActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  actionButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 4,
    marginLeft: spacing.sm,
  },
  startButton: {
    backgroundColor: colors.primary,
  },
  stopButton: {
    backgroundColor: colors.error,
  },
  restartButton: {
    backgroundColor: colors.warning,
  },
  actionButtonText: {
    color: colors.white,
    fontSize: fonts.size.sm,
    fontWeight: 'bold',
  },
  disabledButton: {
    opacity: 0.5,
  },
  disabledText: {
    opacity: 0.5,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
  loadingText: {
    color: colors.white,
    fontSize: fonts.size.md,
    marginTop: spacing.md,
  },
}), []), []), []), []), []), []); 