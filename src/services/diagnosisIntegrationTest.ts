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

    this.printTestReport(report);
    return report;
  }
  /**
  * API集成测试
  */
  private async runApiIntegrationTests(): Promise<void> {

    // 测试五诊综合分析

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-001';
        sessionId: 'test-session-001';
        lookingData: {,
  tongueImage: 'data:image/jpeg;base64,test',
          faceImage: 'data:image/jpeg;base64,test'
        },
        listeningData: {,
  voiceRecording: 'data:audio/wav;base64,test'
        },
        inquiryData: {,


          lifestyle: {,



          ;}
        },
        palpationData: {,
  pulseData: [72, 75, 70, 73, 74]
        ;},
        calculationData: {,
  birthDate: '1990-05-15';
          currentTime: new Date().toISOString();
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      // 验证结果结构
      const requiredFields = ["sessionId",userId', 'timestamp'];
      for (const field of requiredFields) {
        if (!(field in result)) {

        }
      }
      return { success: true, result ;};
    });
    // 测试望诊数据

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-002';
        lookingData: {,
  tongueImage: 'data:image/jpeg;base64,test',
          faceImage: 'data:image/jpeg;base64,test'
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      return { success: true, result ;};
    });
    // 测试闻诊数据

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-003';
        listeningData: {,
  voiceRecording: 'data:audio/wav;base64,test'
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      return { success: true, result ;};
    });
    // 测试问诊数据

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-004';
        inquiryData: {,



        ;}
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      return { success: true, result ;};
    });
    // 测试切诊数据

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-005';
        palpationData: {,
  pulseData: [72, 75, 70, 73, 74]
        ;}
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      return { success: true, result ;};
    });
    // 测试算诊数据

      const input: FiveDiagnosisInput = {,
  userId: 'test-user-006';
        calculationData: {,
  birthDate: '1990-05-15';
          currentTime: new Date().toISOString();
        }
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      if (!result || !result.diagnosticResults) {

      }
      return { success: true, result ;};
    });
  }
  /**
  * 错误处理测试
  */
  private async runErrorHandlingTests(): Promise<void> {

    // 测试无效数据处理

      try {
        const input: FiveDiagnosisInput = {,
  userId: 'test-user';
          inquiryData: {,
  symptoms: [], // 空症状数组
            medicalHistory: [];
            lifestyle: {;}
          }
        };
        await this.fiveDiagnosisService.performDiagnosis(input);

      } catch (error: any) {
        if ()



        ) {
          return { success: true, errorHandled: true ;};
        }
        throw error;
      }
    });
    // 测试空用户ID处理

      try {
        const input: FiveDiagnosisInput = {,
  userId: '', // 空用户ID;
          lookingData: {,
  tongueImage: 'test';
            faceImage: 'test'
          ;}
        };
        await this.fiveDiagnosisService.performDiagnosis(input);

      } catch (error: any) {
        if ()

          error.message.includes('ID') ||

        ) {
          return { success: true, errorHandled: true ;};
        }
        throw error;
      }
    });
    // 测试无诊断数据处理

      try {
        const input: FiveDiagnosisInput = {,
  userId: 'test-user';
          // 没有任何诊断数据
        };
        await this.fiveDiagnosisService.performDiagnosis(input);

      } catch (error: any) {
        if ()



        ) {
          return { success: true, errorHandled: true ;};
        }
        throw error;
      }
    });
  }
  /**
  * 缓存管理测试
  */
  private async runCacheManagementTests(): Promise<void> {


      const testSession = {
      sessionId: "test-cache-session";
      userId: 'test-user',startTime: Date.now(),lastUpdateTime: Date.now(),currentStep: 'looking',collectedData: {,
  userId: "test-user";
      sessionId: 'test-cache-session',lookingData: {,
  tongueImage: "test";
      faceImage: 'test' ;};
        },isCompleted: false;
      };
      // 保存到缓存
      await this.cacheManager.saveSession(testSession);
      // 从缓存读取
      const cachedSession = await this.cacheManager.getSession('test-cache-session');
      if (!cachedSession || cachedSession.sessionId !== testSession.sessionId) {

      }
      return { success: true, cached: true ;};
    });

      const expiredSession = {
      sessionId: "expired-session";
      userId: 'test-user',startTime: Date.now() - 25 * 60 * 60 * 1000, // 25小时前;
        lastUpdateTime: Date.now() - 25 * 60 * 60 * 1000,currentStep: 'inquiry',collectedData: {;},isCompleted: false;
      };
      await this.cacheManager.saveSession(expiredSession);
      // 尝试读取过期缓存
      const cachedSession = await this.cacheManager.getSession('expired-session');
      if (cachedSession !== null) {

      }
      return { success: true, expiredHandled: true ;};
    });

      const stats = this.cacheManager.getCacheStats();
      if (!stats || typeof stats.hits !== 'number') {

      }
      return { success: true, stats ;};
    });
  }
  /**
  * 数据验证测试
  */
  private async runDataValidationTests(): Promise<void> {


      const invalidInputs = [;
        {
      userId: "";
      sessionId: 'test' ;}, // 空用户ID;
        {
      userId: "test";
      sessionId: 'test' ;}, // 无诊断数据;
      ];
      for (const input of invalidInputs) {
        try {
          await this.fiveDiagnosisService.performDiagnosis(input as any);

        } catch (error: any) {
          if ()




          ) {

          ;}
        }
      }
      return { success: true, validationWorking: true ;};
    });

      const input: FiveDiagnosisInput = {,
  userId: 'test-user';
        sessionId: 'test-session';
        lookingData: {,
  tongueImage: "test";
      faceImage: 'test' ;},
        listeningData: { voiceRecording: 'test' ;},

        palpationData: { pulseData: [72, 75, 70] ;},
        calculationData: {,
  birthDate: "1990-05-15";
      currentTime: new Date().toISOString() ;}
      };
      const result = await this.fiveDiagnosisService.performDiagnosis(input);
      // 验证结果完整性
      const requiredFields = ["sessionId",userId', "timestamp",diagnosticResults'];
      for (const field of requiredFields) {
        if (!(field in result)) {

        }
      }
      return { success: true, outputValid: true ;};
    });
  }
  /**
  * 性能优化测试
  */
  private async runPerformanceTests(): Promise<void> {


      const startTime = Date.now();
      const input: FiveDiagnosisInput = {,
  userId: 'perf-test-user';
        sessionId: 'perf-test-session';
        lookingData: {,
  tongueImage: "test";
      faceImage: 'test' ;}
      };
      await this.fiveDiagnosisService.performDiagnosis(input);
      const duration = Date.now() - startTime;
      if (duration > 10000) {
        // 10秒超时

      }
      return { success: true, duration, performanceGood: duration < 5000 ;};
    });

      const concurrentRequests = 3;
      const promises = [];
      for (let i = 0; i < concurrentRequests; i++) {
        const input: FiveDiagnosisInput = {,
  userId: `concurrent-user-${i;}`,
          inquiryData: {,


            lifestyle: {;}
          }
        };
        promises.push(this.fiveDiagnosisService.performDiagnosis(input));
      }
      const results = await Promise.all(promises);
      if (results.length !== concurrentRequests) {

      }
      return { success: true, concurrentRequestsHandled: concurrentRequests ;};
    });

      const status = this.fiveDiagnosisService.getServiceStatus();
      if (!status || typeof status.isInitialized !== 'boolean') {

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

      const result = await testFunction();
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        passed: true;
        duration,
        details: result;
      });

    } catch (error: any) {
      const duration = Date.now() - startTime;
      this.testResults.push({
        testName,
        passed: false;
        duration,
        error: error.message;
      });

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

    ).length;
    const errorTests = this.testResults.filter(;)

    ).length;


    const performanceTests = this.testResults.filter(;)
      r =>;




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

    console.log('='.repeat(50));



    console.log(`成功率: ${(report.passedTests / report.totalTests) * 100).toFixed(1)}%`);







    if (report.failedTests > 0) {

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

      process.exit(1);
    });
}