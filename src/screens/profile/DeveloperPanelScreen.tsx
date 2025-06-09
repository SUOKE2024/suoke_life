import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Platform,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface DebugInfo {
  errorStats: {,
  total: number;
    recent: number;,
  bySeverity: Record<string, number>;
  };
  performanceStats: {,
  total: number;
    byType: Record<string, number>;
    averageDuration: Record<string, number>;
  };
  networkStats: {,
  totalRequests: number;
    averageResponseTime: number;,
  successRate: number;
  };
  systemInfo: {,
  platform: string;
    version: string;,
  isDebug: boolean;
    timestamp: string;
  };
}

export const DeveloperPanelScreen: React.FC = () => {
  const navigation = useNavigation();
  const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);
  const [performanceEnabled, setPerformanceEnabled] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect() => {
    loadDebugInfo();
  }, []);

  const loadDebugInfo = useCallback(async () => {
    try {
      // 模拟调试信息
      const mockDebugInfo: DebugInfo = {,
  errorStats: {
          total: 12,
          recent: 3,
          bySeverity: {,
  ERROR: 5,
            WARNING: 4,
            INFO: 3,
          },
        },
        performanceStats: {,
  total: 156,
          byType: {,
  render: 89,
            api: 34,
            navigation: 23,
            storage: 10,
          },
          averageDuration: {,
  render: 16.5,
            api: 245.8,
            navigation: 89.2,
            storage: 12.3,
          },
        },
        networkStats: {,
  totalRequests: 234,
          averageResponseTime: 187.5,
          successRate: 94.2,
        },
        systemInfo: {,
  platform: Platform.OS,
          version: Platform.Version.toString(),
          isDebug: __DEV__,
          timestamp: new Date().toISOString(),
        },
      };

      setDebugInfo(mockDebugInfo);
    } catch (error) {
      Alert.alert('错误', '加载调试信息失败');
    }
  }, []);

  const handleClearErrorLog = useCallback() => {
    Alert.alert('确认清除', '确定要清除所有错误日志吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        onPress: () => {
          // 模拟清除错误日志
          if (debugInfo) {
            setDebugInfo({
              ...debugInfo,
              errorStats: {,
  total: 0,
                recent: 0,
                bySeverity: {},
              },
            });
          }
          Alert.alert('成功', '错误日志已清除');
        },
      },
    ]);
  }, [debugInfo]);

  const handleClearPerformanceMetrics = useCallback() => {
    Alert.alert('确认清除', '确定要清除所有性能指标吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        onPress: () => {
          // 模拟清除性能指标
          if (debugInfo) {
            setDebugInfo({
              ...debugInfo,
              performanceStats: {,
  total: 0,
                byType: {},
                averageDuration: {},
              },
            });
          }
          Alert.alert('成功', '性能指标已清除');
        },
      },
    ]);
  }, [debugInfo]);

  const handleTogglePerformanceMonitoring = useCallback(enabled: boolean) => {
    setPerformanceEnabled(enabled);
    Alert.alert('设置已更新', `性能监控已${enabled ? '启用' : '禁用'}`);
  }, []);

  const handleRunQuickTest = useCallback(async () => {
    setLoading(true);
    try {
      // 模拟快速测试
      await new Promise(resolve) => setTimeout(resolve, 2000));
      const success = Math.random() > 0.3;
      Alert.alert(
        '快速测试结果',
        `状态: ${success ? '成功' : '失败'}\n${success ? '所有系统运行正常' : '发现部分问题'}`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('测试失败', '未知错误');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExportDebugData = useCallback() => {
    try {
      const exportData = {
        timestamp: new Date().toISOString(),
        debugInfo,
        appVersion: '1.0.0',
        buildNumber: '100',
      };

      Alert.alert(
        '导出成功',
        '调试数据已准备就绪\n(实际应用中会保存到文件或发送)',
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('导出失败', '无法导出调试数据');
    }
  }, [debugInfo]);

  const handleNavigateToApiDemo = useCallback() => {
    navigation.navigate('ApiIntegrationDemo' as never);
  }, [navigation]);

  const renderErrorStats = () => {
    if (!debugInfo?.errorStats) return null;

    const { total, bySeverity, recent } = debugInfo.errorStats;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>错误统计</Text>
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>总错误数</Text>
            <Text style={styles.statValue}>{total}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>最近1小时</Text>
            <Text style={styles.statValue}>{recent}</Text>
          </View>
        </View>

        <Text style={styles.subSectionTitle}>按严重程度分类</Text>
        {Object.entries(bySeverity).map([severity, count]) => (
          <View key={severity} style={styles.severityItem}>
            <Text style={styles.severityLabel}>{severity}</Text>
            <Text style={styles.severityCount}>{count}</Text>
          </View>
        ))}

        <TouchableOpacity;
          style={styles.actionButton}
          onPress={handleClearErrorLog}
        >
          <Text style={styles.actionButtonText}>清除错误日志</Text>
        </TouchableOpacity>
      </View>
    );
  };

  const renderPerformanceStats = () => {
    if (!debugInfo?.performanceStats) return null;

    const { total, byType, averageDuration } = debugInfo.performanceStats;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>性能统计</Text>
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>总指标数</Text>
            <Text style={styles.statValue}>{total}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>监控状态</Text>
            <Switch;
              value={performanceEnabled}
              onValueChange={handleTogglePerformanceMonitoring}
              trackColor={ false: '#E1E8ED', true: '#3498DB' }}
              thumbColor={performanceEnabled ? '#FFFFFF' : '#FFFFFF'}
            />
          </View>
        </View>

        <Text style={styles.subSectionTitle}>按类型分类</Text>
        {Object.entries(byType).map([type, count]) => (
          <View key={type} style={styles.typeItem}>
            <Text style={styles.typeLabel}>{type}</Text>
            <Text style={styles.typeCount}>{count}</Text>
            <Text style={styles.typeAverage}>
              {averageDuration[type]
                ? `${averageDuration[type].toFixed(2)}ms`
                : '-'}
            </Text>
          </View>
        ))}

        <TouchableOpacity;
          style={styles.actionButton}
          onPress={handleClearPerformanceMetrics}
        >
          <Text style={styles.actionButtonText}>清除性能指标</Text>
        </TouchableOpacity>
      </View>
    );
  };

  const renderNetworkStats = () => {
    if (!debugInfo?.networkStats) return null;

    const { totalRequests, averageResponseTime, successRate } =
      debugInfo.networkStats;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>网络统计</Text>
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>总请求数</Text>
            <Text style={styles.statValue}>{totalRequests}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>平均响应时间</Text>
            <Text style={styles.statValue}>
              {averageResponseTime.toFixed(2)}ms;
            </Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>成功率</Text>
            <Text;
              style={[
                styles.statValue,
                {
                  color:
                    successRate >= 90;
                      ? '#27AE60'
                      : successRate > 70;
                        ? '#F39C12'
                        : '#E74C3C',
                },
              ]}
            >
              {successRate.toFixed(1)}%
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const renderSystemInfo = () => {
    if (!debugInfo?.systemInfo) return null;

    const { platform, version, isDebug, timestamp } = debugInfo.systemInfo;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>系统信息</Text>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>平台</Text>
          <Text style={styles.infoValue}>{platform}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>版本</Text>
          <Text style={styles.infoValue}>{version}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>调试模式</Text>
          <Text style={styles.infoValue}>{isDebug ? '是' : '否'}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>更新时间</Text>
          <Text style={styles.infoValue}>
            {new Date(timestamp).toLocaleString()}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>开发者面板</Text>
        <TouchableOpacity onPress={loadDebugInfo}>
          <Text style={styles.refreshButton}>刷新</Text>
        </TouchableOpacity>
      </View>

      <ScrollView;
        style={styles.scrollView}
        refreshControl={
          <RefreshControl;
            refreshing={loading}
            onRefresh={loadDebugInfo}
            colors={['#3498DB']}
            tintColor="#3498DB"
          />
        }
      >
        <View style={styles.quickActions}>
          <TouchableOpacity;
            style={styles.quickActionButton}
            onPress={handleRunQuickTest}
            disabled={loading}
          >
            <Text style={styles.quickActionText}>
              {loading ? '测试中...' : '快速测试'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity;
            style={styles.quickActionButton}
            onPress={handleNavigateToApiDemo}
          >
            <Text style={styles.quickActionText}>API测试</Text>
          </TouchableOpacity>

          <TouchableOpacity;
            style={styles.quickActionButton}
            onPress={handleExportDebugData}
          >
            <Text style={styles.quickActionText}>导出数据</Text>
          </TouchableOpacity>
        </View>

        {renderSystemInfo()}
        {renderErrorStats()}
        {renderPerformanceStats()}
        {renderNetworkStats()}
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
  refreshButton: {,
  fontSize: 16,
    color: '#3498DB',
    fontWeight: '600',
  },
  scrollView: {,
  flex: 1,
    padding: 20,
  },
  quickActions: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    gap: 12,
  },
  quickActionButton: {,
  flex: 1,
    backgroundColor: '#3498DB',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  quickActionText: {,
  color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  section: {,
  backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 16,
  },
  subSectionTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginTop: 16,
    marginBottom: 12,
  },
  statsContainer: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statItem: {,
  alignItems: 'center',
  },
  statLabel: {,
  fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 4,
  },
  statValue: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  severityItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  severityLabel: {,
  fontSize: 14,
    color: '#2C3E50',
  },
  severityCount: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#E74C3C',
  },
  typeItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  typeLabel: {,
  flex: 1,
    fontSize: 14,
    color: '#2C3E50',
  },
  typeCount: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#3498DB',
    marginRight: 16,
  },
  typeAverage: {,
  fontSize: 14,
    color: '#7F8C8D',
  },
  infoItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  infoLabel: {,
  fontSize: 14,
    color: '#7F8C8D',
  },
  infoValue: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
  },
  actionButton: {,
  backgroundColor: '#E74C3C',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  actionButtonText: {,
  color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default DeveloperPanelScreen;
