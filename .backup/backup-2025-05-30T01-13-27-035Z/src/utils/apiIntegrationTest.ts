import { apiClient } from "../services/apiClient";
import { API_CONFIG, STORAGE_CONFIG } from "../constants/config";
import AsyncStorage from "@react-native-async-storage/async-storage";



/**
 * API集成测试工具
 * 用于测试前端与后端API的集成
 */

interface TestResult {
  service: string;
  endpoint: string;
  success: boolean;
  status?: number;
  responseTime: number;
  error?: string;
  data?: any;
}

interface TestReport {
  timestamp: string;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  results: TestResult[];
}

/**
 * API集成测试类
 */
class ApiIntegrationTest {
  private testResults: TestResult[] = [];

  /**
   * 测试认证服务
   */
  async testAuthService(): Promise<TestResult[]> {
    console.log("测试认证服务...");
    const results: TestResult[] = [];

    // 测试健康检查端点
    results.push(await this.testEndpoint("认证服务", "/auth/health", "GET"));

    return results;
  }

  /**
   * 测试用户服务
   */
  async testUserService(): Promise<TestResult[]> {
    console.log("测试用户服务...");
    const results: TestResult[] = [];

    // 测试健康检查端点
    results.push(await this.testEndpoint("用户服务", "/users/health", "GET"));

    return results;
  }

  /**
   * 测试健康数据服务
   */
  async testHealthDataService(): Promise<TestResult[]> {
    console.log("测试健康数据服务...");
    const results: TestResult[] = [];

    // 测试健康检查端点
    results.push(
      await this.testEndpoint("健康数据服务", "/health-data/health", "GET")
    );

    return results;
  }

  /**
   * 测试智能体服务
   */
  async testAgentServices(): Promise<TestResult[]> {
    console.log("测试智能体服务...");
    const results: TestResult[] = [];

    // 测试小艾服务
    const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOAI;
    results.push(
      await this.testExternalEndpoint(
        "小艾服务",
        xiaoaiBaseUrl,
        "/health",
        "GET"
      )
    );

    // 测试小克服务
    const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAOKE;
    results.push(
      await this.testExternalEndpoint(
        "小克服务",
        xiaokeBaseUrl,
        "/health",
        "GET"
      )
    );

    // 测试老克服务
    const laokeBaseUrl = API_CONFIG.AGENTS.LAOKE;
    results.push(
      await this.testExternalEndpoint(
        "老克服务",
        laokeBaseUrl,
        "/health",
        "GET"
      )
    );

    // 测试索儿服务
    const soerBaseUrl = API_CONFIG.AGENTS.SOER;
    results.push(
      await this.testExternalEndpoint("索儿服务", soerBaseUrl, "/health", "GET")
    );

    return results;
  }

  /**
   * 测试五诊服务
   */
  async testDiagnosisServices(): Promise<TestResult[]> {
    console.log("测试五诊服务...");
    const results: TestResult[] = [];

    // 测试望诊服务
    const lookBaseUrl = API_CONFIG.DIAGNOSIS.LOOK;
    results.push(
      await this.testExternalEndpoint("望诊服务", lookBaseUrl, "/health", "GET")
    );

    // 测试闻诊服务
    const listenBaseUrl = API_CONFIG.DIAGNOSIS.LISTEN;
    results.push(
      await this.testExternalEndpoint(
        "闻诊服务",
        listenBaseUrl,
        "/health",
        "GET"
      )
    );

    // 测试问诊服务
    const inquiryBaseUrl = API_CONFIG.DIAGNOSIS.INQUIRY;
    results.push(
      await this.testExternalEndpoint(
        "问诊服务",
        inquiryBaseUrl,
        "/health",
        "GET"
      )
    );

    // 测试切诊服务
    const palpationBaseUrl = API_CONFIG.DIAGNOSIS.PALPATION;
    results.push(
      await this.testExternalEndpoint(
        "切诊服务",
        palpationBaseUrl,
        "/health",
        "GET"
      )
    );

    return results;
  }

  /**
   * 测试单个API端点
   */
  private async testEndpoint(
    service: string,
    endpoint: string,
    method: "GET" | "POST" = "GET",
    data?: any
  ): Promise<TestResult> {
    console.log(`测试端点: ${endpoint}`);
    const startTime = Date.now();

    try {
      const response =
        method === "GET"
          ? await apiClient.get(endpoint)
          : await apiClient.post(endpoint, data);

      const responseTime = Date.now() - startTime;

      const result: TestResult = {
        service,
        endpoint,
        success: response.success,
        responseTime,
        data: response.data,
      };

      this.testResults.push(result);
      console.log(`✅ ${service} - ${endpoint}: ${responseTime}ms`);
      return result;
    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      const result: TestResult = {
        service,
        endpoint,
        success: false,
        responseTime,
        error: error.message || "未知错误",
      };

      this.testResults.push(result);
      console.log(`❌ ${service} - ${endpoint}: ${error.message}`);
      return result;
    }
  }

  /**
   * 测试外部服务端点
   */
  private async testExternalEndpoint(
    service: string,
    baseUrl: string,
    endpoint: string,
    method: "GET" | "POST" = "GET",
    data?: any
  ): Promise<TestResult> {
    console.log(`测试外部端点: ${baseUrl}${endpoint}`);
    const startTime = Date.now();

    try {
      const url = `${baseUrl}${endpoint}`;
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: method === "POST" ? JSON.stringify(data) : undefined,
      });

      const responseTime = Date.now() - startTime;
      const responseData = await response.json();

      const result: TestResult = {
        service,
        endpoint: url,
        success: response.ok,
        status: response.status,
        responseTime,
        data: responseData,
      };

      this.testResults.push(result);
      console.log(
        `${response.ok ? "✅" : "❌"} ${service} - ${url}: ${
          response.status
        }, ${responseTime}ms`
      );
      return result;
    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      const result: TestResult = {
        service,
        endpoint: `${baseUrl}${endpoint}`,
        success: false,
        responseTime,
        error: error.message || "未知错误",
      };

      this.testResults.push(result);
      console.log(`❌ ${service} - ${baseUrl}${endpoint}: ${error.message}`);
      return result;
    }
  }

  /**
   * 运行所有集成测试
   */
  async runAllTests(): Promise<TestReport> {
    console.log("开始API集成测试...");
    this.testResults = [];

    // 运行所有测试
    const authResults = await this.testAuthService();
    const userResults = await this.testUserService();
    const healthResults = await this.testHealthDataService();
    const agentResults = await this.testAgentServices();
    const diagnosisResults = await this.testDiagnosisServices();

    // 合并所有测试结果
    const allResults = [
      ...authResults,
      ...userResults,
      ...healthResults,
      ...agentResults,
      ...diagnosisResults,
    ];

    // 计算通过和失败的测试数量
    const passedTests = allResults.filter((r) => r.success).length;
    const failedTests = allResults.length - passedTests;

    // 创建测试报告
    const report: TestReport = {
      timestamp: new Date().toISOString(),
      totalTests: allResults.length,
      passedTests,
      failedTests,
      results: allResults,
    };

    // 保存测试报告
    await this.saveTestReport(report);

    console.log(
      `API集成测试完成: 总计 ${report.totalTests} 测试, ${report.passedTests} 通过, ${report.failedTests} 失败`
    );

    return report;
  }

  /**
   * 保存测试报告
   */
  private async saveTestReport(report: TestReport): Promise<void> {
    try {
      // 获取现有报告
      const reportsJson = await AsyncStorage.getItem("api_test_reports");
      const reports: TestReport[] = reportsJson ? JSON.parse(reportsJson) : [];

      // 添加新报告
      reports.push(report);

      // 只保留最近的10个报告
      const recentReports = reports.slice(-10);

      // 保存报告
      await AsyncStorage.setItem(
        "api_test_reports",
        JSON.stringify(recentReports)
      );
    } catch (error) {
      console.error("保存测试报告失败:", error);
    }
  }

  /**
   * 获取最近的测试报告
   */
  async getTestReports(): Promise<TestReport[]> {
    try {
      const reportsJson = await AsyncStorage.getItem("api_test_reports");
      return reportsJson ? JSON.parse(reportsJson) : [];
    } catch (error) {
      console.error("获取测试报告失败:", error);
      return [];
    }
  }

  /**
   * 快速健康检查
   */
  async quickHealthCheck(): Promise<{
    success: boolean;
    message: string;
    services: Record<string, boolean>;
  }> {
    try {
      // 检查主要服务
      const authHealth = await this.testEndpoint(
        "认证服务",
        "/auth/health",
        "GET"
      );
      const userHealth = await this.testEndpoint(
        "用户服务",
        "/users/health",
        "GET"
      );

      // 检查智能体服务
      const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOAI;
      const xiaoaiHealth = await this.testExternalEndpoint(
        "小艾服务",
        xiaoaiBaseUrl,
        "/health",
        "GET"
      );

      const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAOKE;
      const xiaokeHealth = await this.testExternalEndpoint(
        "小克服务",
        xiaokeBaseUrl,
        "/health",
        "GET"
      );

      // 结果
      const servicesStatus = {
        auth: authHealth.success,
        user: userHealth.success,
        xiaoai: xiaoaiHealth.success,
        xiaoke: xiaokeHealth.success,
      };

      const allServicesUp = Object.values(servicesStatus).every(
        (status) => status
      );

      return {
        success: allServicesUp,
        message: allServicesUp ? "所有核心服务正常运行" : "部分服务不可用",
        services: servicesStatus,
      };
    } catch (error: any) {
      return {
        success: false,
        message: `健康检查失败: ${error.message}`,
        services: {},
      };
    }
  }
}

// 导出API集成测试实例
export const apiIntegrationTest = new ApiIntegrationTest();
