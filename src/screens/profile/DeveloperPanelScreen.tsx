import { useNavigation } from '@react-navigation/native';
import { colors, spacing, typography } from '../../constants/theme';
import { apiIntegrationTest } from '../../utils/apiIntegrationTest';
import { ApiIntegrationDemo } from '../demo/ApiIntegrationDemo';





import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
  Platform,
  SafeAreaView,
  RefreshControl,
} from 'react-native';
  errorHandler,
  getErrorStats,
  clearErrorLog,
  performanceMonitor,
  getPerformanceStats,
  getNetworkPerformanceStats,
  clearPerformanceMetrics,
} from '../../utils';

// 导入ApiIntegrationDemo

interface DebugInfo {
  errorStats: ReturnType<typeof getErrorStats>;
  performanceStats: ReturnType<typeof getPerformanceStats>;
  networkStats: ReturnType<typeof getNetworkPerformanceStats>;
  systemInfo: {
    platform: string;
    version: string;
    isDebug: boolean;
    timestamp: string;
  };
}

export const DeveloperPanelScreen: React.FC = () => {
  const navigation = useNavigation();
  const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);
  const [performanceEnabled, setPerformanceEnabled] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDebugInfo();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  const loadDebugInfo = useCallback( () => {, []);
    try {
      const errorStats = getErrorStats();
      const performanceStats = getPerformanceStats();
      const networkStats = getNetworkPerformanceStats();
      
      const systemInfo = {
        platform: Platform.OS,
        version: Platform.Version.toString(),
        isDebug: __DEV__,
        timestamp: new Date().toISOString(),
      };

      setDebugInfo({
        errorStats,
        performanceStats,
        networkStats,
        systemInfo,
      });
    } catch (error) {
      console.error('Failed to load debug info:', error);
      Alert.alert('错误', '加载调试信息失败');
    }
  };

  const handleBack = useCallback( () => {, []);
    navigation.goBack();
  };

  const handleClearErrorLog = useCallback( () => {, []);
    Alert.alert(
      '确认清除',
      '确定要清除所有错误日志吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            clearErrorLog();
            loadDebugInfo();
            Alert.alert('成功', '错误日志已清除');
          },
        },
      ]
    );
  };

  const handleClearPerformanceMetrics = useCallback( () => {, []);
    Alert.alert(
      '确认清除',
      '确定要清除所有性能指标吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            clearPerformanceMetrics();
            loadDebugInfo();
            Alert.alert('成功', '性能指标已清除');
          },
        },
      ]
    );
  };

  const handleTogglePerformanceMonitoring = useCallback( (enabled: boolean) => {, []);
    setPerformanceEnabled(enabled);
    performanceMonitor.setEnabled(enabled);
    Alert.alert('设置已更新', `性能监控已${enabled ? '启用' : '禁用'}`);
  };

  const handleRunQuickTest = async () => {
    setLoading(true);
    try {
      const result = await apiIntegrationTest.quickHealthCheck();
      Alert.alert(
        '快速测试结果',
        `状态: ${result.success ? '成功' : '失败'}\n${result.message}`,
        [{ text: '确定' }]
      );
    } catch (error: any) {
      Alert.alert('测试失败', error.message || '未知错误');
    } finally {
      setLoading(false);
    }
  };

  const handleExportDebugData = useCallback( () => {, []);
    try {
      const exportData = {
        timestamp: new Date().toISOString(),
        errorLog: errorHandler.getErrorLog(),
        performanceData: performanceMonitor.exportData(),
        systemInfo: debugInfo?.systemInfo,
      };

      // 在实际应用中，这里可以实现数据导出功能
      // 比如保存到文件、发送邮件或上传到服务器
      console.log('Debug data exported:', exportData);
      Alert.alert('导出成功', '调试数据已导出到控制台');
    } catch (error) {
      console.error('Failed to export debug data:', error);
      Alert.alert('导出失败', '无法导出调试数据');
    }
  };

  const handleNavigateToApiDemo = useCallback( () => {, []);
    // 导航到ApiIntegrationDemo
    navigation.navigate('ApiIntegrationDemo' as never);
  };

  const renderErrorStats = useCallback( () => {, []);
    if (!debugInfo?.errorStats) {return null;}

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
        {Object.entries(bySeverity).map(([severity, count]) => (
          <View key={severity} style={styles.severityItem}>
            <Text style={styles.severityLabel}>{severity}</Text>
            <Text style={styles.severityCount}>{count}</Text>
          </View>
        ))}
        
        <TouchableOpacity style={styles.actionButton} onPress={handleClearErrorLog}>
          <Text style={styles.actionButtonText}>清除错误日志</Text>
        </TouchableOpacity>
      </View>
    );
  };

  const renderPerformanceStats = useCallback( () => {, []);
    if (!debugInfo?.performanceStats) {return null;}

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
            <Switch
              value={performanceEnabled}
              onValueChange={handleTogglePerformanceMonitoring}
              trackColor={{ false: colors.gray400, true: colors.primary }}
              thumbColor={Platform.OS === 'android' ? colors.white : ''}
            />
          </View>
        </View>
        
        <Text style={styles.subSectionTitle}>按类型分类</Text>
        {Object.entries(byType).map(([type, count]) => (
          <View key={type} style={styles.typeItem}>
            <Text style={styles.typeLabel}>{type}</Text>
            <Text style={styles.typeCount}>{count}</Text>
            <Text style={styles.typeAverage}>
              {averageDuration[type] ? `${averageDuration[type].toFixed(2)}ms` : '-'}
            </Text>
          </View>
        ))}
        
        <TouchableOpacity style={styles.actionButton} onPress={handleClearPerformanceMetrics}>
          <Text style={styles.actionButtonText}>清除性能指标</Text>
        </TouchableOpacity>
      </View>
    );
  };

  const renderNetworkStats = useCallback( () => {, []);
    if (!debugInfo?.networkStats) {return null;}

    const { totalRequests, averageResponseTime, successRate } = debugInfo.networkStats;

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
            <Text style={styles.statValue}>{averageResponseTime.toFixed(2)}ms</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>成功率</Text>
            <Text style={[
              styles.statValue,
              { color: successRate > 90 ? colors.success : successRate > 70 ? colors.warning : colors.error },
            ]}>
              {successRate.toFixed(1)}%
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const renderSystemInfo = useCallback( () => {, []);
    if (!debugInfo?.systemInfo) {return null;}

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
          <Text style={styles.infoValue}>{new Date(timestamp).toLocaleString()}</Text>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={loadDebugInfo} />
        }
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBack}>
            <Text style={styles.backButtonText}>← 返回</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>开发者面板</Text>
          <TouchableOpacity onPress={loadDebugInfo}>
            <Text style={styles.refreshButton}>刷新</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.actionsSection}>
          <TouchableOpacity
            style={[styles.quickActionButton, styles.testButton]}
            onPress={handleRunQuickTest}
            disabled={loading}
          >
            <Text style={styles.quickActionButtonText}>
              {loading ? '测试中...' : '快速健康检查'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.quickActionButton, styles.exportButton]}
            onPress={handleExportDebugData}
          >
            <Text style={styles.quickActionButtonText}>导出调试数据</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.demoSection}>
          <TouchableOpacity
            style={[styles.quickActionButton, styles.demoButton]}
            onPress={handleNavigateToApiDemo}
          >
            <Text style={styles.quickActionButtonText}>API集成演示</Text>
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
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: 'bold',
    color: colors.textPrimary,
  },
  refreshButton: {
    color: colors.primary,
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
    padding: spacing.sm,
  },
  disabledText: {
    opacity: 0.5,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  actionsSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  quickActionButton: {
    flex: 1,
    padding: spacing.md,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: spacing.sm,
  },
  testButton: {
    backgroundColor: colors.primary,
  },
  exportButton: {
    backgroundColor: colors.info,
  },
  quickActionButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
  },
  section: {
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
  sectionTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  subSectionTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: '600',
    color: colors.textSecondary,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: spacing.md,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  statValue: {
    fontSize: typography.fontSize.lg,
    fontWeight: 'bold',
    color: colors.textPrimary,
  },
  severityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  severityLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
  },
  severityCount: {
    fontSize: typography.fontSize.sm,
    fontWeight: 'bold',
    color: colors.primary,
  },
  typeItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  typeLabel: {
    flex: 1,
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
  },
  typeCount: {
    fontSize: typography.fontSize.sm,
    fontWeight: 'bold',
    color: colors.primary,
    marginRight: spacing.md,
  },
  typeAverage: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  infoLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  infoValue: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  actionButton: {
    backgroundColor: colors.error,
    padding: spacing.sm,
    borderRadius: 4,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  actionButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.sm,
    fontWeight: 'bold',
  },
  demoSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  demoButton: {
    backgroundColor: colors.primary,
  },
  scrollView: {
    flex: 1,
  },
}); 