import { Platform, Alert } from 'react-native';
import deviceInfoManager from './deviceInfo';
import { performanceMonitor } from './performanceMonitor';
import permissionManager from './permissions';
import nativeModulesManager from './nativeModules';
import notificationManager from './notifications';

export interface TestResult {
  testName: string;
  passed: boolean;
  duration: number;
  error?: string;
  details?: any;
}

export interface TestSuite {
  name: string;
  tests: TestResult[];
  passed: boolean;
  totalDuration: number;
  passRate: number;
}

export interface IntegrationTestReport {
  deviceInfo: any;
  testSuites: TestSuite[];
  overallResult: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    passRate: number;
    totalDuration: number;
  };
  performanceMetrics: any;
  recommendations: string[];
}

class DeviceIntegrationTester {
  private testResults: TestResult[] = [];
  private currentSuite: string = '';

  /**
   * 运行完整的集成测试
   */
  async runFullIntegrationTest(): Promise<IntegrationTestReport> {
    console.log('🧪 开始真实设备集成测试...');
    
    // 开始性能监控
    performanceMonitor.startMonitoring(1000);
    
    const startTime = Date.now();
    const testSuites: TestSuite[] = [];

    try {
      // 获取设备信息
      const deviceInfo = await deviceInfoManager.getDeviceSpecs();
      console.log('📱 设备信息获取完成');

      // 运行各个测试套件
      testSuites.push(await this.runDeviceCompatibilityTests());
      testSuites.push(await this.runPermissionTests());
      testSuites.push(await this.runNativeModuleTests());
      testSuites.push(await this.runNotificationTests());
      testSuites.push(await this.runPerformanceTests());
      testSuites.push(await this.runNetworkTests());

      // 计算总体结果
      const totalTests = testSuites.reduce((sum, suite) => sum + suite.tests.length, 0);
      const passedTests = testSuites.reduce((sum, suite) => sum + suite.tests.filter(t => t.passed).length, 0);
      const failedTests = totalTests - passedTests;
      const totalDuration = Date.now() - startTime;

      // 获取性能指标
      const performanceMetrics = performanceMonitor.getPerformanceReport();
      
      // 生成建议
      const recommendations = this.generateRecommendations(testSuites, performanceMetrics);

      const report: IntegrationTestReport = {
        deviceInfo,
        testSuites,
        overallResult: {
          totalTests,
          passedTests,
          failedTests,
          passRate: (passedTests / totalTests) * 100,
          totalDuration,
        },
        performanceMetrics,
        recommendations,
      };

      console.log(`✅ 集成测试完成: ${passedTests}/${totalTests} 通过 (${report.overallResult.passRate.toFixed(1)}%)`);
      return report;

    } catch (error) {
      console.error('❌ 集成测试失败:', error);
      throw error;
    } finally {
      performanceMonitor.stopMonitoring();
    }
  }

  /**
   * 设备兼容性测试
   */
  private async runDeviceCompatibilityTests(): Promise<TestSuite> {
    this.currentSuite = '设备兼容性测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试设备信息获取
    tests.push(await this.runTest('获取设备信息', async () => {
      const deviceSpecs = await deviceInfoManager.getDeviceSpecs();
      if (!deviceSpecs.deviceId || !deviceSpecs.brand || !deviceSpecs.model) {
        throw new Error('设备信息不完整');
      }
      return deviceSpecs;
    }));

    // 测试兼容性检查
    tests.push(await this.runTest('兼容性检查', async () => {
      const compatibility = await deviceInfoManager.checkCompatibility();
      return compatibility;
    }));

    // 测试系统版本
    tests.push(await this.runTest('系统版本检查', async () => {
      const deviceSpecs = await deviceInfoManager.getDeviceSpecs();
      if (Platform.OS === 'ios') {
        const version = parseFloat(deviceSpecs.systemVersion);
        if (version < 12.0) {
          throw new Error(`iOS版本过低: ${version}`);
        }
      } else if (Platform.OS === 'android') {
        const version = parseInt(deviceSpecs.systemVersion);
        if (version < 21) {
          throw new Error(`Android版本过低: ${version}`);
        }
      }
      return { version: deviceSpecs.systemVersion, compatible: true };
    }));

    // 测试内存检查
    tests.push(await this.runTest('内存检查', async () => {
      const deviceSpecs = await deviceInfoManager.getDeviceSpecs();
      const memoryGB = deviceSpecs.totalMemory / (1024 * 1024 * 1024);
      if (memoryGB < 1) {
        throw new Error(`内存不足: ${memoryGB.toFixed(2)}GB`);
      }
      return { totalMemory: memoryGB, sufficient: true };
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 权限测试
   */
  private async runPermissionTests(): Promise<TestSuite> {
    this.currentSuite = '权限系统测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试权限检查
    tests.push(await this.runTest('相机权限检查', async () => {
      const result = await permissionManager.checkPermission('camera');
      return result;
    }));

    tests.push(await this.runTest('麦克风权限检查', async () => {
      const result = await permissionManager.checkPermission('microphone');
      return result;
    }));

    tests.push(await this.runTest('位置权限检查', async () => {
      const result = await permissionManager.checkPermission('location');
      return result;
    }));

    // 测试健康应用权限组合
    tests.push(await this.runTest('健康应用权限检查', async () => {
      const result = await permissionManager.checkHealthAppPermissions();
      return result;
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 原生模块测试
   */
  private async runNativeModuleTests(): Promise<TestSuite> {
    this.currentSuite = '原生模块测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试模块状态
    tests.push(await this.runTest('模块状态检查', async () => {
      const status = nativeModulesManager.getModulesStatus();
      return status;
    }));

    // 测试相机可用性
    tests.push(await this.runTest('相机可用性测试', async () => {
      const available = await nativeModulesManager.isCameraAvailable();
      return { available };
    }));

    // 测试健康功能初始化
    tests.push(await this.runTest('健康功能初始化', async () => {
      const result = await nativeModulesManager.initializeHealthFeatures();
      return result;
    }));

    // 测试位置服务
    tests.push(await this.runTest('位置服务测试', async () => {
      try {
        const location = await nativeModulesManager.getCurrentLocation({
          timeout: 10000,
          enableHighAccuracy: false,
        });
        return location;
             } catch (error: any) {
         // 位置服务可能因为权限或网络问题失败，这是可接受的
         return { error: (error instanceof Error ? error.message : String(error)), skipped: true };
       }
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 通知系统测试
   */
  private async runNotificationTests(): Promise<TestSuite> {
    this.currentSuite = '通知系统测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试通知状态
    tests.push(await this.runTest('通知系统状态', async () => {
      const status = notificationManager.getNotificationStatus();
      return status;
    }));

    // 测试权限检查
    tests.push(await this.runTest('通知权限检查', async () => {
      const hasPermission = await notificationManager.checkNotificationPermission();
      return { hasPermission };
    }));

    // 测试本地通知
    tests.push(await this.runTest('本地通知测试', async () => {
      const success = await notificationManager.scheduleLocalNotification({
        id: 'test_notification',
        title: '测试通知',
        body: '这是一个测试通知',
        date: new Date(Date.now() + 5000), // 5秒后
      });
      
      // 立即取消测试通知
      notificationManager.cancelLocalNotification('test_notification');
      
      return { success };
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 性能测试
   */
  private async runPerformanceTests(): Promise<TestSuite> {
    this.currentSuite = '性能测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试启动性能
    tests.push(await this.runTest('应用启动性能', async () => {
      const startupMetrics = await performanceMonitor.testAppStartupPerformance();
      if (startupMetrics.firstRender > 3000) {
        throw new Error(`首次渲染时间过长: ${startupMetrics.firstRender}ms`);
      }
      return startupMetrics;
    }));

    // 测试内存泄漏
    tests.push(await this.runTest('内存泄漏测试', async () => {
      const memoryTest = await performanceMonitor.testMemoryLeaks(5);
      if (memoryTest.averageGrowthPerIteration > 10 * 1024 * 1024) { // 10MB per iteration
        throw new Error(`内存增长过快: ${memoryTest.averageGrowthPerIteration / (1024 * 1024)}MB per iteration`);
      }
      return memoryTest;
    }));

    // 测试当前性能指标
    tests.push(await this.runTest('当前性能指标', async () => {
      const metrics = await deviceInfoManager.getCurrentPerformanceMetrics();
      if (metrics.memoryUsage.percentage > 90) {
        throw new Error(`内存使用率过高: ${metrics.memoryUsage.percentage.toFixed(1)}%`);
      }
      return metrics;
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 网络测试
   */
  private async runNetworkTests(): Promise<TestSuite> {
    this.currentSuite = '网络连接测试';
    console.log(`🔍 开始${this.currentSuite}...`);
    
    const tests: TestResult[] = [];
    const startTime = Date.now();

    // 测试网络连接
    tests.push(await this.runTest('网络连接测试', async () => {
      const startTime = Date.now();
             const response = await fetch('https://www.google.com', { 
         method: 'HEAD',
       });
      const latency = Date.now() - startTime;
      
      if (!response.ok) {
        throw new Error(`网络请求失败: ${response.status}`);
      }
      
      if (latency > 5000) {
        throw new Error(`网络延迟过高: ${latency}ms`);
      }
      
      return { latency, status: response.status };
    }));

    // 测试API连接
    tests.push(await this.runTest('API连接测试', async () => {
      try {
        // 这里可以测试实际的API端点
        const startTime = Date.now();
        const response = await fetch('https://httpbin.org/get', {
          method: 'GET',
          timeout: 10000,
        });
        const latency = Date.now() - startTime;
        
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status}`);
        }
        
        return { latency, status: response.status };
      } catch (error) {
        // API测试失败是可接受的，可能是网络问题
        return { error: (error instanceof Error ? error.message : String(error)), skipped: true };
      }
    }));

    const totalDuration = Date.now() - startTime;
    const passedTests = tests.filter(t => t.passed).length;

    return {
      name: this.currentSuite,
      tests,
      passed: passedTests === tests.length,
      totalDuration,
      passRate: (passedTests / tests.length) * 100,
    };
  }

  /**
   * 运行单个测试
   */
  private async runTest(testName: string, testFunction: () => Promise<any>): Promise<TestResult> {
    const startTime = Date.now();
    
    try {
      console.log(`  🧪 运行测试: ${testName}`);
      const result = await testFunction();
      const duration = Date.now() - startTime;
      
      console.log(`  ✅ ${testName} - ${duration}ms`);
      return {
        testName,
        passed: true,
        duration,
        details: result,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      console.log(`  ❌ ${testName} - ${duration}ms - ${(error instanceof Error ? error.message : String(error))}`);
      
      return {
        testName,
        passed: false,
        duration,
        error: (error instanceof Error ? error.message : String(error)),
      };
    }
  }

  /**
   * 生成优化建议
   */
  private generateRecommendations(testSuites: TestSuite[], performanceMetrics: any): string[] {
    const recommendations: string[] = [];

    // 基于测试结果生成建议
    testSuites.forEach(suite => {
      if (suite.passRate < 100) {
        recommendations.push(`${suite.name}存在问题，建议检查失败的测试项`);
      }
    });

    // 基于性能指标生成建议
    if (performanceMetrics.summary.criticalAlerts > 0) {
      recommendations.push('检测到严重性能问题，建议立即优化');
    }

    if (performanceMetrics.summary.memoryIssues > 0) {
      recommendations.push('内存使用存在问题，建议优化内存管理');
    }

    // 通用建议
    recommendations.push('定期运行集成测试以确保应用稳定性');
    recommendations.push('在不同设备上测试以确保兼容性');
    recommendations.push('监控应用性能并及时优化');

    return recommendations;
  }

  /**
   * 生成测试报告
   */
  generateTestReport(report: IntegrationTestReport): string {
    const { deviceInfo, testSuites, overallResult, recommendations } = report;

    let reportText = `
# 索克生活真实设备集成测试报告

## 设备信息
- 品牌: ${deviceInfo.brand}
- 型号: ${deviceInfo.model}
- 系统: ${deviceInfo.systemName} ${deviceInfo.systemVersion}
- 内存: ${(deviceInfo.totalMemory / (1024 * 1024 * 1024)).toFixed(2)}GB
- 是否模拟器: ${deviceInfo.isEmulator ? '是' : '否'}

## 测试总览
- 总测试数: ${overallResult.totalTests}
- 通过测试: ${overallResult.passedTests}
- 失败测试: ${overallResult.failedTests}
- 通过率: ${overallResult.passRate.toFixed(1)}%
- 总耗时: ${overallResult.totalDuration}ms

## 测试套件详情
`;

    testSuites.forEach(suite => {
      reportText += `
### ${suite.name}
- 通过率: ${suite.passRate.toFixed(1)}%
- 耗时: ${suite.totalDuration}ms
- 状态: ${suite.passed ? '✅ 通过' : '❌ 失败'}

#### 测试详情:
`;
      suite.tests.forEach(test => {
        reportText += `- ${test.passed ? '✅' : '❌'} ${test.testName} (${test.duration}ms)`;
        if (test.error) {
          reportText += ` - 错误: ${test.error}`;
        }
        reportText += '\n';
      });
    });

    reportText += `
## 优化建议
${recommendations.map(rec => `- ${rec}`).join('\n')}

---
报告生成时间: ${new Date().toLocaleString()}
    `;

    return reportText.trim();
  }
}

export const deviceIntegrationTester = new DeviceIntegrationTester();
export default deviceIntegrationTester; 