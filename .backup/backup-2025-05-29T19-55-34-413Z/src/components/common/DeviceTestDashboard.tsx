import {
import deviceInfoManager from '../../utils/deviceInfo';
import { performanceMonitor } from '../../utils/performanceMonitor';
import deviceIntegrationTester from '../../utils/deviceIntegrationTest';


import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

interface DeviceTestDashboardProps {
  onTestComplete?: (report: IntegrationTestReport) => void;
}

const DeviceTestDashboard: React.FC<DeviceTestDashboardProps> = ({ onTestComplete }) => {
  const [deviceInfo, setDeviceInfo] = useState<any>(null);
  const [testReport, setTestReport] = useState<IntegrationTestReport | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [currentTest, setCurrentTest] = useState<string>('');
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);

  useEffect(() => {
    loadDeviceInfo();
    startPerformanceMonitoring();
    
    return () => {
      performanceMonitor.stopMonitoring();
    };
  }, []);

  const loadDeviceInfo = async () => {
    try {
      const info = await deviceInfoManager.getDeviceSpecs();
      setDeviceInfo(info);
    } catch (error) {
      console.error('获取设备信息失败:', error);
    }
  };

  const startPerformanceMonitoring = useCallback( () => {, []);
    performanceMonitor.startMonitoring(2000);
    
    // 定期更新性能指标
    const interval = setInterval(async () => {
      try {
        const metrics = await deviceInfoManager.getCurrentPerformanceMetrics();
        setPerformanceMetrics(metrics);
      } catch (error) {
        console.error('获取性能指标失败:', error);
      }
    }, 3000);

    return () => clearInterval(interval);
  };

  const runIntegrationTest = async () => {
    setIsRunningTest(true);
    setCurrentTest('准备测试环境...');
    
    try {
      // 模拟测试进度更新
      const testSteps = [
        '检查设备兼容性...',
        '测试权限系统...',
        '测试原生模块...',
        '测试通知系统...',
        '测试性能指标...',
        '测试网络连接...',
        '生成测试报告...',
      ];

      for (let i = 0; i < testSteps.length; i++) {
        setCurrentTest(testSteps[i]);
        await new Promise<void>(resolve => setTimeout(resolve, 1000));
      }

      const report = await deviceIntegrationTester.runFullIntegrationTest();
      setTestReport(report);
      onTestComplete?.(report);
      
      Alert.alert(
        '测试完成',
        `测试通过率: ${report.overallResult.passRate.toFixed(1)}%\n` +
        `总测试数: ${report.overallResult.totalTests}\n` +
        `耗时: ${report.overallResult.totalDuration}ms`,
        [{ text: '确定' }]
      );
    } catch (error) {
      console.error('集成测试失败:', error);
      Alert.alert('测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setIsRunningTest(false);
      setCurrentTest('');
    }
  };

  const runQuickTest = async () => {
    setIsRunningTest(true);
    setCurrentTest('运行快速测试...');
    
    try {
      // 快速测试：只测试基本功能
      const compatibility = await deviceInfoManager.checkCompatibility();
      const metrics = await deviceInfoManager.getCurrentPerformanceMetrics();
      
      Alert.alert(
        '快速测试结果',
        `设备兼容性: ${compatibility.compatible ? '✅ 兼容' : '❌ 不兼容'}\n` +
        `内存使用: ${metrics.memoryUsage.percentage.toFixed(1)}%\n` +
        `网络延迟: ${metrics.networkLatency}ms`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('快速测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setIsRunningTest(false);
      setCurrentTest('');
    }
  };

  const clearTestData = useCallback( () => {, []);
    setTestReport(null);
    performanceMonitor.clearPerformanceData();
    deviceInfoManager.clearPerformanceHistory();
    Alert.alert('数据已清除', '所有测试数据和性能历史已清除');
  };

  const renderDeviceInfo = useCallback( () => {, []);
    if (!deviceInfo) {return null;}

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📱 设备信息</Text>
        <View style={styles.infoGrid}>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>品牌</Text>
            <Text style={styles.infoValue}>{deviceInfo.brand}</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>型号</Text>
            <Text style={styles.infoValue}>{deviceInfo.model}</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>系统</Text>
            <Text style={styles.infoValue}>{deviceInfo.systemName} {deviceInfo.systemVersion}</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>内存</Text>
            <Text style={styles.infoValue}>
              {(deviceInfo.totalMemory / (1024 * 1024 * 1024)).toFixed(2)}GB
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const renderPerformanceMetrics = useCallback( () => {, []);
    if (!performanceMetrics) {return null;}

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 实时性能</Text>
        <View style={styles.metricsGrid}>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>内存使用</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.memoryUsage.percentage > 80 ? '#ff4444' : '#4CAF50' },
            ]}>
              {performanceMetrics.memoryUsage.percentage.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>CPU使用</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.cpuUsage > 80 ? '#ff4444' : '#4CAF50' },
            ]}>
              {performanceMetrics.cpuUsage.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>网络延迟</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.networkLatency > 1000 ? '#ff4444' : '#4CAF50' },
            ]}>
              {performanceMetrics.networkLatency}ms
            </Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>渲染时间</Text>
            <Text style={[
              styles.metricValue,
              { color: performanceMetrics.renderTime > 16 ? '#ff4444' : '#4CAF50' },
            ]}>
              {performanceMetrics.renderTime.toFixed(1)}ms
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const renderTestSuite = useCallback( (suite: TestSuite) => {, []);
    return (
      <View key={suite.name} style={styles.testSuite}>
        <View style={styles.testSuiteHeader}>
          <Text style={styles.testSuiteName}>{suite.name}</Text>
          <Text style={[
            styles.testSuiteStatus,
            { color: suite.passed ? '#4CAF50' : '#ff4444' },
          ]}>
            {suite.passed ? '✅' : '❌'} {suite.passRate.toFixed(1)}%
          </Text>
        </View>
        <Text style={styles.testSuiteInfo}>
          耗时: {suite.totalDuration}ms | 测试数: {suite.tests.length}
        </Text>
        {suite.tests.map((test, index) => (
          <View key={index} style={styles.testItem}>
            <Text style={[
              styles.testName,
              { color: test.passed ? '#4CAF50' : '#ff4444' },
            ]}>
              {test.passed ? '✅' : '❌'} {test.testName}
            </Text>
            <Text style={styles.testDuration}>{test.duration}ms</Text>
            {test.error && (
              <Text style={styles.testError}>错误: {test.error}</Text>
            )}
          </View>
        ))}
      </View>
    );
  };

  const renderTestReport = useCallback( () => {, []);
    if (!testReport) {return null;}

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📋 测试报告</Text>
        
        <View style={styles.reportSummary}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>总测试数</Text>
            <Text style={styles.summaryValue}>{testReport.overallResult.totalTests}</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>通过率</Text>
            <Text style={[
              styles.summaryValue,
              { color: testReport.overallResult.passRate >= 90 ? '#4CAF50' : '#ff4444' },
            ]}>
              {testReport.overallResult.passRate.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>总耗时</Text>
            <Text style={styles.summaryValue}>{testReport.overallResult.totalDuration}ms</Text>
          </View>
        </View>

        <ScrollView style={styles.testSuitesList}>
          {testReport.testSuites.map(renderTestSuite)}
        </ScrollView>

        {testReport.recommendations.length > 0 && (
          <View style={styles.recommendations}>
            <Text style={styles.recommendationsTitle}>💡 优化建议</Text>
            {testReport.recommendations.map((rec, index) => (
              <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🧪 设备测试仪表板</Text>
      
      {renderDeviceInfo()}
      {renderPerformanceMetrics()}
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔧 测试操作</Text>
        
        <View style={styles.buttonGrid}>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton]}
            onPress={runIntegrationTest}
            disabled={isRunningTest}
          >
            {isRunningTest ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>完整集成测试</Text>
            )}
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={runQuickTest}
            disabled={isRunningTest}
          >
            <Text style={styles.buttonTextSecondary}>快速测试</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.warningButton]}
            onPress={clearTestData}
            disabled={isRunningTest}
          >
            <Text style={styles.buttonText}>清除数据</Text>
          </TouchableOpacity>
        </View>
        
        {isRunningTest && (
          <View style={styles.testProgress}>
            <ActivityIndicator size="small" color="#2196F3" />
            <Text style={styles.testProgressText}>{currentTest}</Text>
          </View>
        )}
      </View>
      
      {renderTestReport()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  infoItem: {
    width: '48%',
    marginBottom: 12,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 12,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  button: {
    width: '48%',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: '#2196F3',
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  warningButton: {
    backgroundColor: '#ff9800',
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  buttonTextSecondary: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: '600',
  },
  testProgress: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f0f8ff',
    borderRadius: 8,
  },
  testProgressText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#2196F3',
  },
  reportSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  testSuitesList: {
    maxHeight: 400,
  },
  testSuite: {
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  testSuiteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  testSuiteName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  testSuiteStatus: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  testSuiteInfo: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  testItem: {
    marginLeft: 12,
    marginBottom: 4,
  },
  testName: {
    fontSize: 14,
    fontWeight: '500',
  },
  testDuration: {
    fontSize: 12,
    color: '#666',
  },
  testError: {
    fontSize: 12,
    color: '#ff4444',
    fontStyle: 'italic',
  },
  recommendations: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#fff3cd',
    borderRadius: 8,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#856404',
  },
  recommendationItem: {
    fontSize: 14,
    color: '#856404',
    marginBottom: 4,
  },
});

export default DeviceTestDashboard; 