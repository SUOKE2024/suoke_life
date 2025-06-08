import React from "react;";
import { apiClient } from "../../placeholder";../services/apiClient";/import { API_CONFIG, STORAGE_CONFIG } from "../constants/config";/import AsyncStorage from "@react-native-async-storage/    async-storage;
interface ApiResponse<T = any /> { data: T;/     , success: boolean;
  message?: string;
code?: number}
API集成测试工具   用于测试前端与后端API的集成
interface TestResult {
  service: string;
  endpoint: string;
  success: boolean;
  status?: number;
  responseTime: number;
  error?: string;
  data?: unknown
}
interface TestReport {
  timestamp: string;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  results: TestResult[];
}
// API集成测试类class ApiIntegrationTest {
  private testResults: TestResult[] = []
  ///    > {
    const results: TestResult[] = [];
    results.push(await this.testEndpoint("认证服务", / auth * health", "GET");); /     return result;s;
  }
  ///    > {
    const results: TestResult[] = [];
    results.push(await this.testEndpoint("用户服务", / users * health", "GET");); /     return result;s;
  }
  ///    > {
    const results: TestResult[] = [];
    results.push()
      await this.testEndpoint("健康数据服务",/health-data/health", "GET");/        );
    return resul;t;s;
  }
  ///    > {
    const results: TestResult[] = [];
    const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOA;I;
    results.push()
      await this.testExternalEndpoint()
        "小艾服务",
        xiaoaiBaseUrl,
        "/health",/            "GET"
      ;);
    );
    const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAOK;E;
    results.push()
      await this.testExternalEndpoint()
        "小克服务",
        xiaokeBaseUrl,
        "/health",/            "GET"
      ;);
    );
    const laokeBaseUrl = API_CONFIG.AGENTS.LAOK;E;
    results.push()
      await this.testExternalEndpoint()
        "老克服务",
        laokeBaseUrl,
        "/health",/            "GET"
      ;);
    );
    const soerBaseUrl = API_CONFIG.AGENTS.SOE;R;
    results.push()
      await this.testExternalEndpoint("索儿服务", soerBaseUrl, "/health",GET";);/        );
    return resul;t;s;
  }
  ///    > {
    const results: TestResult[] = [];
    const lookBaseUrl = API_CONFIG.DIAGNOSIS.LOO;K;
    results.push()
      await this.testExternalEndpoint("望诊服务", lookBaseUrl, "/health",GET";);/        );
    const listenBaseUrl = API_CONFIG.DIAGNOSIS.LISTE;N;
    results.push()
      await this.testExternalEndpoint()
        "闻诊服务",
        listenBaseUrl,
        "/health",/            "GET"
      ;);
    );
    const inquiryBaseUrl = API_CONFIG.DIAGNOSIS.INQUIR;Y;
    results.push()
      await this.testExternalEndpoint()
        "问诊服务",
        inquiryBaseUrl,
        "/health",/            "GET"
      ;);
    );
    const palpationBaseUrl = API_CONFIG.DIAGNOSIS.PALPATIO;N;
    results.push()
      await this.testExternalEndpoint()
        "切诊服务",
        palpationBaseUrl,
        "/health",/            "GET"
      ;);
    );
    return resul;t;s;
  }
  // 测试单个API端点  private async testEndpoint(service: string,)
    endpoint: string,
    method: "GET" | "POST" = "GET",
    data?: unknown;
  ): Promise<TestResult /    >  {
    const startTime = Date.now;(;);
    try {
      const response =;
        method === "GET";
          ? await apiClient.get(endpo;i;n;t;);: await apiClient.post(endpoint, dat;a;);
      const responseTime = Date.now - startTime;
      const result: TestResult =  {service,
        endpoint,
        success: response.success,
        responseTime,
        data: response.data;
      };
      this.testResults.push(result);
      return result;
    } catch (error: unknown) {
      const responseTime = Date.now - startTime;
const result: TestResult = {service,
        endpoint,
        success: false,
        responseTime,
        error: error.message || "未知错误"
      };
      this.testResults.push(result);
      return resu;l;t;
    }
  }
  // 测试外部服务端点  private async testExternalEndpoint(service: string,)
    baseUrl: string,
    endpoint: string,
    method: "GET" | "POST" = "GET",
    data?: unknown;
  ): Promise<TestResult /    >  {
    const startTime = Date.now;(;);
    try {
      const url = `${baseUrl}${endpoint;};`;
      const response = await fetch(url, {method,)
        headers: {
          "Content-Type": "application/json",/          Accept: "application/json",/            },body: method === "POST" ? JSON.stringify(d;a;t;a;);: undefined;
      });
      const responseTime = Date.now - startTime;
      const responseData = await response.js;o;n;
      const result: TestResult =  {service,
        endpoint: url,
        success: response.ok,
        status: response.status,
        responseTime,
        data: responseData;
      };
      this.testResults.push(result);
      return result;
    } catch (error: unknown) {
      const responseTime = Date.now - startTime;
const result: TestResult = {service,
        endpoint: `${baseUrl}${endpoint}`,
        success: false,
        responseTime,
        error: error.message || "未知错误"
      };
      this.testResults.push(result);
      return result;
    }
  }
  ///    > {
    this.testResults = [];
    const authResults = await this.testAuthServic;e;
    const userResults = await this.testUserServi;c;e;
    const healthResults = await this.testHealthDataServi;c;e;
    const agentResults = await this.testAgentServic;e;s;
    const diagnosisResults = await this.testDiagnosisServic;e;s;
    const allResults = [;
      ...authResults,...userResults,...healthResults,...agentResults,...diagnosisResults];
    const passedTests = allResults.filter(r) => r.success).length;
    const failedTests = allResults.length - passedTes;t;s;
    const report: TestReport = {,
  timestamp: new Date().toISOString(),
      totalTests: allResults.length,
      passedTests,
      failedTests,
      results: allResults;
    }
    await this.saveTestReport(report;);
    return repo;r;t;
  }
  // 保存测试报告  private async saveTestReport(report: TestReport): Promise<void>  {
    try {
      const reportsJson = await AsyncStorage.getItem("api_test_report;s;";);
      const reports: TestReport[] = reportsJson ? JSON.parse(reportsJson);: [];
      reports.push(report);
      const recentReports = reports.slice(-10;);
      await AsyncStorage.setItem()
        "api_test_reports",
        JSON.stringify(recentReports;);
      )
    } catch (error)  {
      }
  }
  ///    > {
    try {
      const reportsJson = await AsyncStorage.getItem("api_test_report;s;";);
      return reportsJson ? JSON.parse(reportsJso;n;);: []
    } catch (error)  {
      return [;];
    }
  }
  // 快速健康检查  async quickHealthCheck(): Promise<{
    success: boolean,
    message: string,
    services: Record<string, boolean>;
  }> {
    try {
      const authHealth = await this.testEndpoint(;)
        "认证服务",/auth/health",/            "G;E;T"
      ;);
      const userHealth = await this.testEndpoint(;)
        "用户服务",/users/health",/            "G;E;T"
      ;);
      const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOA;I;
      const xiaoaiHealth = await this.testExternalEndpoint(;)
        "小艾服务",
        xiaoaiBaseUrl,"/health",/            "G;E;T"
      ;);
      const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAO;K;E;
      const xiaokeHealth = await this.testExternalEndpoint(;)
        "小克服务",
        xiaokeBaseUrl,"/health",/            "G;E;T"
      ;);
      const servicesStatus = {auth: authHealth.success,user: userHealth.success,xiaoai: xiaoaiHealth.success,xiaoke: xiaokeHealth.succes;s;};
      const allServicesUp = Object.values(servicesStatus).every(;)
        (statu;s;); => status;
      );
      return {success: allServicesUp,message: allServicesUp ? "所有核心服务正常运行" : "部分服务不可用",services: servicesStatu;s;}
    } catch (error: unknown) {
      return {success: false,message: `健康检查失败: ${error.message}`,services: {}
      ;};
    }
  }
}
//   ;