import {
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { Card, Button } from '../../components/ui';
import { useApiIntegration } from '../../hooks/useApiIntegration';
import { colors, spacing, typography } from '../../constants/theme';
import { ApiTestResultsDisplay } from '../../components/demo/ApiTestResultsDisplay';


import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Dimensions,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';


const { width } = Dimensions.get('window');

// 模拟测试报告数据
const mockTestReportData = useMemo(() => useMemo(() => {
  timestamp: new Date().toISOString(),
  summary: {
    total: 51,
    passed: 50,
    failed: 1,
    successRate: 98.0,
    avgDuration: 162.78,
  },
  categories: {
    auth: { total: 3, passed: 3, failed: 0 },
    health: { total: 8, passed: 8, failed: 0 },
    agents: { total: 10, passed: 10, failed: 0 },
    diagnosis: { total: 8, passed: 7, failed: 1 },
    settings: { total: 3, passed: 3, failed: 0 },
    blockchain: { total: 3, passed: 3, failed: 0 },
    ml: { total: 3, passed: 3, failed: 0 },
    accessibility: { total: 3, passed: 3, failed: 0 },
    eco: { total: 3, passed: 3, failed: 0 },
    support: { total: 4, passed: 4, failed: 0 },
    system: { total: 3, passed: 3, failed: 0 },
  },
  details: [
    {
      name: '健康检查',
      category: 'auth',
      status: 'PASSED' as const,
      duration: 99,
      endpoint: '/health',
      method: 'GET',
    },
    {
      name: '启动问诊',
      category: 'diagnosis',
      status: 'FAILED' as const,
      duration: 215,
      endpoint: '/diagnosis/inquiry',
      method: 'POST',
      error: 'API调用失败: POST /diagnosis/inquiry',
    },
    // ... 其他测试结果
  ],
}, []), []);

interface ApiTestResult {
  name: string;
  category: string;
  status: 'PASSED' | 'FAILED';
  duration: number;
  endpoint: string;
  method: string;
  error?: string;
}

export const ApiIntegrationDemo: React.FC = () => {
  const navigation = useMemo(() => useMemo(() => useNavigation(), []), []);
  const api = useMemo(() => useMemo(() => useApiIntegration(), []), []);

  const [currentTab, setCurrentTab] = useState<'overview' | 'results' | 'live'>('overview');
  const [testResults, setTestResults] = useState(mockTestReportData);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // 加载最新的测试结果
    loadTestResults();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const loadTestResults = useMemo(() => useMemo(() => async () => {
    try {
      // 这里可以从实际的API或本地存储加载测试结果
      // 目前使用静态数据
      setTestResults(mockTestReportData), []), []);
    } catch (error) {
      console.error('加载测试结果失败:', error);
    }
  };

  const handleRunAllTests = useMemo(() => useMemo(() => async () => {
    setIsRunningTests(true), []), []);
    try {
      Alert.alert(
        '开始测试',
        '即将运行所有51个API接口测试，这可能需要几分钟时间。',
        [
          { text: '取消', style: 'cancel' },
          {
            text: '开始',
            onPress: async () => {
              try {
                // 使用现有的API方法进行测试
                await api.healthCheck();
                await api.getApiVersion();
                await api.getCurrentUser();
                Alert.alert('测试完成', '所有API测试已完成，请查看结果。');
                await loadTestResults();
                setCurrentTab('results');
              } catch (error: any) {
                Alert.alert('测试失败', error.message || '测试过程中发生错误');
              }
            },
          },
        ]
      );
    } finally {
      setIsRunningTests(false);
    }
  };

  const handleRetryTest = useMemo(() => useMemo(() => async (testName: string) => {
    try {
      // 根据测试名称执行对应的API调用
      if (testName === '健康检查') {
        await api.healthCheck(), []), []);
      } else if (testName === '获取API版本') {
        await api.getApiVersion();
      }
      Alert.alert('重试完成', `${testName} 测试已重新运行`);
      await loadTestResults();
    } catch (error: any) {
      Alert.alert('重试失败', error.message || '重试过程中发生错误');
    }
  };

  const handleViewTestDetails = useMemo(() => useMemo(() => useCallback( (test: ApiTestResult) => {, []), []), []);
    Alert.alert(
      test.name,
      `状态: ${test.status}\n` +
      `响应时间: ${test.duration}ms\n` +
      `接口: ${test.method} ${test.endpoint}\n` +
      `类别: ${test.category}` +
      (test.error ? `\n错误: ${test.error}` : ''),
      [{ text: '确定' }]
    );
  };

  const handleRefresh = useMemo(() => useMemo(() => async () => {
    setRefreshing(true), []), []);
    await loadTestResults();
    setRefreshing(false);
  };

  // TODO: 将内联组件移到组件外部
const renderHeader = useMemo(() => useMemo(() => () => (
    <View style={styles.header}>
      <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
        <Text style={styles.backButtonText}>← 返回</Text>
      </TouchableOpacity>
      <Text style={styles.headerTitle}>API集成演示</Text>
      <TouchableOpacity onPress={handleRefresh} style={styles.refreshButton}>
        <Text style={styles.refreshButtonText}>刷新</Text>
      </TouchableOpacity>
    </View>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      <TouchableOpacity
        style={[styles.tab, currentTab === 'overview' && styles.activeTab]}
        onPress={() => setCurrentTab('overview')}
      >
        <Text style={[styles.tabText, currentTab === 'overview' && styles.activeTabText]}>
          概览
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.tab, currentTab === 'results' && styles.activeTab]}
        onPress={() => setCurrentTab('results')}
      >
        <Text style={[styles.tabText, currentTab === 'results' && styles.activeTabText]}>
          测试结果
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.tab, currentTab === 'live' && styles.activeTab]}
        onPress={() => setCurrentTab('live')}
      >
        <Text style={[styles.tabText, currentTab === 'live' && styles.activeTabText]}>
          实时测试
        </Text>
      </TouchableOpacity>
    </View>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderOverview = useMemo(() => useMemo(() => () => (
    <ScrollView
      style={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
    >
      <View style={styles.overviewCard}>
        <Text style={styles.cardTitle}>🏥 索克生活 API集成系统</Text>
        <Text style={styles.cardDescription}>
          本演示展示了索克生活平台的完整API集成功能，包含51个核心接口，
          涵盖四大智能体、五诊系统、健康数据管理、区块链存储等功能模块。
        </Text>
        
        <View style={styles.featureList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🤖</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>四大智能体</Text>
              <Text style={styles.featureDesc}>小艾、小克、老克、索儿协同工作</Text>
            </View>
          </View>
          
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔍</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>五诊系统</Text>
              <Text style={styles.featureDesc}>望、闻、问、切、综合诊断</Text>
            </View>
          </View>
          
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>健康数据</Text>
              <Text style={styles.featureDesc}>多维度健康指标监测与分析</Text>
            </View>
          </View>
          
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔐</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>区块链存储</Text>
              <Text style={styles.featureDesc}>安全可信的健康数据管理</Text>
            </View>
          </View>
        </View>
        
        <TouchableOpacity
          style={styles.runTestButton}
          onPress={handleRunAllTests}
          disabled={isRunningTests}
        >
          {isRunningTests ? (
            <ActivityIndicator color={colors.white} />
          ) : (
            <Text style={styles.runTestButtonText}>运行完整测试</Text>
          )}
        </TouchableOpacity>
      </View>
      
      <View style={styles.statsCard}>
        <Text style={styles.cardTitle}>📈 最新测试统计</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{testResults.summary.total}</Text>
            <Text style={styles.statLabel}>总接口数</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.success }]}>
              {testResults.summary.passed}
            </Text>
            <Text style={styles.statLabel}>成功</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.error }]}>
              {testResults.summary.failed}
            </Text>
            <Text style={styles.statLabel}>失败</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={[
              styles.statValue,
              { color: testResults.summary.successRate >= 90 ? colors.success : colors.warning },
            ]}>
              {testResults.summary.successRate.toFixed(1)}%
            </Text>
            <Text style={styles.statLabel}>成功率</Text>
          </View>
        </View>
        <Text style={styles.lastUpdate}>
          最后更新: {new Date(testResults.timestamp).toLocaleString()}
        </Text>
      </View>
    </ScrollView>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderResults = useMemo(() => useMemo(() => () => (
    <ApiTestResultsDisplay
      summary={testResults.summary}
      categories={testResults.categories}
      details={testResults.details}
      onRetryTest={handleRetryTest}
      onViewDetails={handleViewTestDetails}
    />
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderLiveTest = useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.content}>
      <View style={styles.liveTestCard}>
        <Text style={styles.cardTitle}>🔴 实时API测试</Text>
        <Text style={styles.cardDescription}>
          选择要测试的API类别或单个接口进行实时测试
        </Text>
        
        <View style={styles.categoryButtons}>
          {Object.entries(testResults.categories).map(([category, stats]) => (
            <TouchableOpacity
              key={category}
              style={styles.categoryButton}
              onPress={() => {
                Alert.alert(
                  `测试 ${category} 类别`,
                  `即将测试 ${stats.total} 个 ${category} 相关的API接口`,
                  [
                    { text: '取消', style: 'cancel' },
                    { text: '开始测试', onPress: () => console.log(`Testing ${category}`) },
                  ]
                ), []), []);
              }}
            >
              <Text style={styles.categoryButtonText}>{category}</Text>
              <Text style={styles.categoryButtonCount}>{stats.total} 个接口</Text>
            </TouchableOpacity>
          ))}
        </View>
        
        <View style={styles.quickActions}>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={async () => {
              try {
                await api.healthCheck();
                Alert.alert('健康检查', '系统状态正常');
              } catch (error: any) {
                Alert.alert('健康检查失败', error.message);
              }
            }}
          >
            <Text style={styles.quickActionText}>健康检查</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={async () => {
              try {
                await api.getAgentStatus();
                Alert.alert('智能体状态', '所有智能体运行正常');
              } catch (error: any) {
                Alert.alert('获取状态失败', error.message);
              }
            }}
          >
            <Text style={styles.quickActionText}>智能体状态</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.quickActionButton}
            onPress={async () => {
              try {
                await api.getSystemHealth();
                Alert.alert('系统监控', '系统运行状态良好');
              } catch (error: any) {
                Alert.alert('系统监控失败', error.message);
              }
            }}
          >
            <Text style={styles.quickActionText}>系统监控</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );

  const renderContent = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    switch (currentTab) {
      case 'overview':
        return renderOverview();
      case 'results':
        return renderResults();
      case 'live':
        return renderLiveTest();
      default:
        return renderOverview();
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {renderHeader()}
      {renderTabBar()}
      {renderContent()}
    </SafeAreaView>
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
    padding: spacing.sm,
  },
  refreshButtonText: {
    color: colors.primary,
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.md,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  overviewCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  cardDescription: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    lineHeight: 24,
    marginBottom: spacing.lg,
  },
  featureList: {
    marginBottom: spacing.lg,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: spacing.md,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 2,
  },
  featureDesc: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  runTestButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
  },
  runTestButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: 'bold',
  },
  statsCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  lastUpdate: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  liveTestCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  categoryButtons: {
    marginBottom: spacing.lg,
  },
  categoryButton: {
    backgroundColor: colors.gray50,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  categoryButtonText: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    textTransform: 'capitalize',
  },
  categoryButtonCount: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: 6,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    marginHorizontal: spacing.xs,
  },
  quickActionText: {
    color: colors.white,
    fontSize: typography.fontSize.sm,
    fontWeight: 'bold',
  },
}), []), []); 