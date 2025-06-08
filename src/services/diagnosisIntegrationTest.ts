import { FiveDiagnosisService, FiveDiagnosisInput } from './fiveDiagnosisService';
import { DiagnosisCacheManager } from './diagnosisCacheManager';
/**
* 诊断服务前端集成测试套件
* 测试五诊服务的API集成、错误处理、缓存机制等功能
*/
interface TestResult {
  testName: string;
  passed: boolean;
  duration: number;
  error?: string;
  details?: any;
}
interface IntegrationTestReport {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  totalDuration: number;
  results: TestResult[];
  coverage: {;
    apiIntegration: number;
  errorHandling: number;
    cacheManagement: number;
  dataValidation: number;
    performanceOptimization: number;
};
}
export class DiagnosisIntegrationTester {
  private fiveDiagnosisService: FiveDiagnosisService;
  private cacheManager: DiagnosisCacheManager;
  private testResults: TestResult[] = [];
  constructor() {
    this.fiveDiagnosisService = new FiveDiagnosisService();
    this.cacheManager = new DiagnosisCacheManager();
  }
  /**
  * 运行完整的集成测试套件
  */
  async runFullTestSuite(): Promise<IntegrationTestReport> {
    console.log('🚀 开始运行诊断服务前端集成测试套件...');
    const startTime = Date.now();
    this.testResults = [];
    // 初始化服务
    await this.fiveDiagnosisService.initialize();
    // API集成测试
    await this.runApiIntegrationTests();
    // 错误处理测试
    await this.runErrorHandlingTests();
    // 缓存管理测试
    await this.runCacheManagementTests();
    // 数据验证测试
    await this.runDataValidationTests();
    // 性能优化测试
    await this.runPerformanceTests();
    const totalDuration = Date.now() - startTime;
    const report = this.generateTestReport(totalDuration);
    console.log('✅ 测试套件运行完成');
    this.printTestReport(report);
    return report;
  }
  /**
  * API集成测试
  */
  private async runApiIntegrationTests(): Promise<void> {
    console.log('📡 运行API集成测试...');
    // 测试五诊综合分析
    await this.runTest('五诊综合分析API', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-001',
        sessionId: 'test-session-001',
        lookingData: {,
  tongueImage: 'data:image/jpeg;base64,test',
          faceImage: 'data:image/jpeg;base64,test'
        },
        listeningData: {,
  voiceRecording: 'data:audio/wav;base64,test'
        },
        inquiryData: {,
  symptoms: ["头痛", "失眠', '食欲不振'],
          medicalHistory: ['无'],
          lifestyle: {,
  sleep: '7小时',
            exercise: '偶尔',
            stress: '高'
          }
        },
        palpationData: {,
  pulseData: [72, 75, 70, 73, 74]
        },
        calculationData: {,
  birthDate: '1990-05-15',
          currentTime: new Date().toISOString();
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('诊断结果为空');
      }
      // 验证结果结构
      const requiredFields = ["sessionId",userId', 'timestamp'];
      for (const field of requiredFields) {
        if (!(field in result)) {
          throw new Error(`缺少${field}字段`);
        }
      }
      return { success: true, result };
    });
    // 测试望诊数据
    await this.runTest('望诊数据处理', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-002',
        lookingData: {,
  tongueImage: 'data:image/jpeg;base64,test',
          faceImage: 'data:image/jpeg;base64,test'
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('望诊结果不完整');
      }
      return { success: true, result };
    });
    // 测试闻诊数据
    await this.runTest('闻诊数据处理', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-003',
        listeningData: {,
  voiceRecording: 'data:audio/wav;base64,test'
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('闻诊结果不完整');
      }
      return { success: true, result };
    });
    // 测试问诊数据
    await this.runTest('问诊数据处理', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-004',
        inquiryData: {,
  symptoms: ['头痛'],
          medicalHistory: ['无'],
          lifestyle: { sleep: '8小时' }
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('问诊结果不完整');
      }
      return { success: true, result };
    });
    // 测试切诊数据
    await this.runTest('切诊数据处理', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-005',
        palpationData: {,
  pulseData: [72, 75, 70, 73, 74]
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('切诊结果不完整');
      }
      return { success: true, result };
    });
    // 测试算诊数据
    await this.runTest('算诊数据处理', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user-006',
        calculationData: {,
  birthDate: '1990-05-15',
          currentTime: new Date().toISOString();
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {
        throw new Error('算诊结果不完整');
      }
      return { success: true, result };
    });
  }
  /**
  * 错误处理测试
  */
  private async runErrorHandlingTests(): Promise<void> {
    console.log('🚨 运行错误处理测试...');
    // 测试无效数据处理
    await this.runTest('无效数据处理', async () => {
      try {
        const input: FiveDiagnosisInput = {,
  userId: 'test-user',
          inquiryData: {,
  symptoms: [], // 空症状数组
            medicalHistory: [],
            lifestyle: {}
          }
        };
        await this.fiveDiagnosisService.performDiagnosis(input);
        throw new Error('应该抛出数据验证错误');
      } catch (error: any) {
        if ()
          error.message.includes('验证') ||
          error.message.includes('无效') ||
          error.message.includes('症状');
        ) {
          return { success: true, errorHandled: true };
        }
        throw error;
      }
    });
    // 测试空用户ID处理
    await this.runTest('空用户ID处理', async () => {
      try {
        const input: FiveDiagnosisInput = {,
  userId: '', // 空用户ID;
          lookingData: {,
  tongueImage: 'test',
            faceImage: 'test'
          }
        };
        await this.fiveDiagnosisService.performDiagnosis(input);
        throw new Error('应该抛出用户ID错误');
      } catch (error: any) {
        if ()
          error.message.includes('用户') ||
          error.message.includes('ID') ||
          error.message.includes('空');
        ) {
          return { success: true, errorHandled: true };
        }
        throw error;
      }
    });
    // 测试无诊断数据处理
    await this.runTest('无诊断数据处理', async () => {
      try {
        const input: FiveDiagnosisInput = {,
  userId: 'test-user',
          // 没有任何诊断数据
        };
        await this.fiveDiagnosisService.performDiagnosis(input);
        throw new Error('应该抛出无数据错误');
      } catch (error: any) {
        if ()
          error.message.includes('数据') ||
          error.message.includes('诊断') ||
          error.message.includes('提供');
        ) {
          return { success: true, errorHandled: true };
        }
        throw error;
      }
    });
  }
  /**
  * 缓存管理测试
  */
  private async runCacheManagementTests(): Promise<void> {
    console.log('💾 运行缓存管理测试...');
    await this.runTest('缓存保存和读取', async () => {
      const testSession = {
      sessionId: "test-cache-session",
      userId: 'test-user',startTime: Date.now(),lastUpdateTime: Date.now(),currentStep: 'looking',collectedData: {
      userId: "test-user",
      sessionId: 'test-cache-session',lookingData: {
      tongueImage: "test",
      faceImage: 'test' };
        },isCompleted: false;
      };
      // 保存到缓存
      await this.cacheManager.saveSession(testSession);
      // 从缓存读取
      const cachedSession = await this.cacheManager.getSession('test-cache-session');
      if (!cachedSession || cachedSession.sessionId !== testSession.sessionId) {
        throw new Error('缓存保存或读取失败');
      }
      return { success: true, cached: true };
    });
    await this.runTest('缓存过期处理', async () => {
      const expiredSession = {
      sessionId: "expired-session",
      userId: 'test-user',startTime: Date.now() - 25 * 60 * 60 * 1000, // 25小时前;
        lastUpdateTime: Date.now() - 25 * 60 * 60 * 1000,currentStep: 'inquiry',collectedData: {},isCompleted: false;
      };
      await this.cacheManager.saveSession(expiredSession);
      // 尝试读取过期缓存
      const cachedSession = await this.cacheManager.getSession('expired-session');
      if (cachedSession !== null) {
        throw new Error('过期缓存应该被清理');
      }
      return { success: true, expiredHandled: true };
    });
    await this.runTest('缓存统计功能', async () => {
      const stats = this.cacheManager.getCacheStats();
      if (!stats || typeof stats.hits !== 'number') {
        throw new Error('缓存统计功能异常');
      }
      return { success: true, stats };
    });
  }
  /**
  * 数据验证测试
  */
  private async runDataValidationTests(): Promise<void> {
    console.log('🔍 运行数据验证测试...');
    await this.runTest('输入数据验证', async () => {
      const invalidInputs = [;
        {
      userId: "",
      sessionId: 'test' }, // 空用户ID;
        {
      userId: "test",
      sessionId: 'test' }, // 无诊断数据;
      ];
      for (const input of invalidInputs) {
        try {
          await this.fiveDiagnosisService.performDiagnosis(input as any);
          throw new Error(`无效输入应该被拒绝: ${JSON.stringify(input)}`);
        } catch (error: any) {
          if ()
            !error.message.includes('验证') &&
            !error.message.includes('无效') &&
            !error.message.includes('用户') &&
            !error.message.includes('数据');
          ) {
            throw new Error(`验证错误消息不正确: ${error.message}`);
          }
        }
      }
      return { success: true, validationWorking: true };
    });
    await this.runTest('输出数据完整性验证', async () => {
      const input: FiveDiagnosisInput = {,
  userId: 'test-user',
        sessionId: 'test-session',
        lookingData: {
      tongueImage: "test",
      faceImage: 'test' },
        listeningData: { voiceRecording: 'test' },
        inquiryData: { symptoms: ['头痛'], medicalHistory: ['无'], lifestyle: {} },
        palpationData: { pulseData: [72, 75, 70] },
        calculationData: {
      birthDate: "1990-05-15",
      currentTime: new Date().toISOString() }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      // 验证结果完整性
      const requiredFields = ["sessionId",userId', "timestamp",diagnosticResults'];
      for (const field of requiredFields) {
        if (!(field in result)) {
          throw new Error(`结果缺少必需字段: ${field}`);
        }
      }
      return { success: true, outputValid: true };
    });
  }
  /**
  * 性能优化测试
  */
  private async runPerformanceTests(): Promise<void> {
    console.log('⚡ 运行性能优化测试...');
    await this.runTest('响应时间测试', async () => {
      const startTime = Date.now();
      const input: FiveDiagnosisInput = {,
  userId: 'perf-test-user',
        sessionId: 'perf-test-session',
        lookingData: {
      tongueImage: "test",
      faceImage: 'test' }
      };
      await this.fiveDiagnosisService.performDiagnosis(input);
      const duration = Date.now() - startTime;
      if (duration > 10000) {
        // 10秒超时
        throw new Error(`响应时间过长: ${duration}ms`);
      }
      return { success: true, duration, performanceGood: duration < 5000 };
    });
    await this.runTest('并发处理测试', async () => {
      const concurrentRequests = 3;
      const promises = [];
      for (let i = 0; i < concurrentRequests; i++) {
        const input: FiveDiagnosisInput = {,
  userId: `concurrent-user-${i}`,
          inquiryData: {,
  symptoms: ['测试症状'],
            medicalHistory: ['无'],
            lifestyle: {}
          }
        };
        promises.push(this.fiveDiagnosisService.performDiagnosis(input));
      }
      const results = await Promise.all(promises);
      if (results.length !== concurrentRequests) {
        throw new Error('并发请求处理失败');
      }
      return { success: true, concurrentRequestsHandled: concurrentRequests };
    });
    await this.runTest('服务状态监控测试', async () => {
      const status = this.fiveDiagnosisService.getServiceStatus();
      if (!status || typeof status.isInitialized !== 'boolean') {
        throw new Error('服务状态监控异常');
      }
      return {success: true,status,isInitialized: status.isInitialized,performanceMetrics: status.performanceMetrics;
      };
    });
  }
  /**
  * 运行单个测试
  */
  private async runTest(testName: string, testFunction: () => Promise<any>): Promise<void> {
    const startTime = Date.now();
    try {
      console.log(`  🧪 运行测试: ${testName}`);
      const result = await testFunction();
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        passed: true,
        duration,
        details: result;
      });
      console.log(`  ✅ ${testName} - 通过 (${duration}ms)`);
    } catch (error: any) {
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        passed: false,
        duration,
        error: error.message;
      });
      console.log(`  ❌ ${testName} - 失败: ${error.message} (${duration}ms)`);
    }
  }
  /**
  * 生成测试报告
  */
  private generateTestReport(totalDuration: number): IntegrationTestReport {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    // 计算覆盖率
    const apiTests = this.testResults.filter(;)
      r => r.testName.includes('API') || r.testName.includes('数据处理');
    ).length;
    const errorTests = this.testResults.filter(;)
      r => r.testName.includes('错误') || r.testName.includes('处理');
    ).length;
    const cacheTests = this.testResults.filter(r => r.testName.includes('缓存')).length;
    const validationTests = this.testResults.filter(r => r.testName.includes('验证')).length;
    const performanceTests = this.testResults.filter(;)
      r =>;
        r.testName.includes('性能') ||;
        r.testName.includes('响应') ||;
        r.testName.includes('并发') ||;
        r.testName.includes('监控');
    ).length;
    return {totalTests,passedTests,failedTests,totalDuration,results: this.testResults,coverage: {apiIntegration: Math.min(100, (apiTests / 6) * 100), // 6个API测试;
        errorHandling: Math.min(100, (errorTests / 3) * 100), // 3个错误处理测试;
        cacheManagement: Math.min(100, (cacheTests / 3) * 100), // 3个缓存测试;
        dataValidation: Math.min(100, (validationTests / 2) * 100), // 2个验证测试;
        performanceOptimization: Math.min(100, (performanceTests / 3) * 100), // 3个性能测试;
      };
    };
  }
  /**
  * 打印测试报告
  */
  private printTestReport(report: IntegrationTestReport): void {
    console.log('\n📊 诊断服务前端集成测试报告');
    console.log('='.repeat(50));
    console.log(`总测试数: ${report.totalTests}`);
    console.log(`通过测试: ${report.passedTests}`);
    console.log(`失败测试: ${report.failedTests}`);
    console.log(`成功率: ${(report.passedTests / report.totalTests) * 100).toFixed(1)}%`);
    console.log(`总耗时: ${report.totalDuration}ms`);
    console.log('\n📈 功能覆盖率:');
    console.log(`API集成: ${report.coverage.apiIntegration.toFixed(1)}%`);
    console.log(`错误处理: ${report.coverage.errorHandling.toFixed(1)}%`);
    console.log(`缓存管理: ${report.coverage.cacheManagement.toFixed(1)}%`);
    console.log(`数据验证: ${report.coverage.dataValidation.toFixed(1)}%`);
    console.log(`性能优化: ${report.coverage.performanceOptimization.toFixed(1)}%`);
    if (report.failedTests > 0) {
      console.log('\n❌ 失败的测试:');
      report.results;
        .filter(r => !r.passed);
        .forEach(r => {
          console.log(`  - ${r.testName}: ${r.error}`);
        });
    }
    console.log('\n' + '='.repeat(50));
  }
}
// 导出测试实例
export const diagnosisIntegrationTester = new DiagnosisIntegrationTester();
// 如果直接运行此文件，执行测试
if (require.main === module) {
  diagnosisIntegrationTester;
    .runFullTestSuite();
    .then(report => {
      process.exit(report.failedTests > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('测试套件运行失败:', error);
      process.exit(1);
    });
}