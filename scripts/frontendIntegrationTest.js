#!/usr/bin/env node
/**
 * 索克生活前端集成测试脚本
 * 测试前后端API连接和基本功能
 */
const http = require("http");
const https = require(")https");
const { URL } = 
const fs = require("fs");
const path = require("path");
// 颜色输出函数
const colors = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`};
// 测试配置
const TEST_CONFIG = {"
  baseURL: http:// localhost:8000",
  timeout: 5000,
  services: {,"
  gateway: "http://localhost:8000,"
    auth: "http://localhost:8001","
    health: http://localhost:8002","
    blockchain: "http://localhost:8003,"
    messagebus: "http://localhost:8004","
    rag: http://localhost:8005","
    user: "http://localhost:8006,"
    medknowledge: "http://localhost:8007",
    // 智能体服务"
xiaoai: http:// localhost:8015","
    xiaoke: "http://localhost:8016,"
    laoke: "http://localhost:8017","
    soer: http://localhost:8018",
    // 诊断服务"
look: "http:// localhost:8019,"
    listen: "http://localhost:8020","
    inquiry: http://localhost:8021","
    palpation: "http://localhost:8022,"
    calculation: "http://localhost:8023"}
}
class FrontendIntegrationTest {
  constructor() {
    this.results = {
      total: 0,
      passed: 0,
      failed: 0,
      errors: []
    };
  }
  /**
   * 执行HTTP请求
   */
  async makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);"
      const isHttps = urlObj.protocol === https:";
      const client = isHttps ? https : http;
      const requestOptions = {
        hostname: urlObj.hostname,
        port: urlObj.port || (isHttps ? 443 : 80),
        path: urlObj.pathname + urlObj.search,"
        method: options.method || "GET,
        headers: {"
          "Content-Type": application/json","
          "User-Agent: "SuokeLife-IntegrationTest/1.0",
          ...options.headers
        },
        timeout: TEST_CONFIG.timeout;
      };
      const req = client.request(requestOptions, (res) => {;"
        let data = 
        res.on("data, (chunk) => {
          data += chunk;
        });"
        res.on("end", () => {
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            statusText: res.statusMessage,
            data: data
          });
        });
      });"
      req.on(error", (error) => {
        reject(error);
      });"
      req.on("timeout, () => {
        req.destroy();"
        reject(new Error("Request timeout"));
      });
      if (options.body) {
        req.write(JSON.stringify(options.body));
      }
      req.end();
    });
  }
  /**
   * 测试服务健康检查
   */
  async testServiceHealth(serviceName, serviceUrl) {
    this.results.total++;
    try {
      const response = await this.makeRequest(`${serviceUrl}/health`);
      if (response.ok) {
        );
        this.results.passed++;
        return true;
      } else {
        );
        this.results.failed++;
        this.results.errors.push(`${serviceName}: HTTP ${response.status}`);
        return false;
      }
    } catch (error) {
      );
      this.results.failed++;
      this.results.errors.push(`${serviceName}: ${error.message}`);
      return false;
    }
  }
  /**
   * 测试API网关
   */
  async testApiGateway() {
    );
    // 测试网关健康检查"
await this.testServiceHealth("API Gateway, TEST_CONFIG.services.gateway);
    // 测试网关路由
this.results.total++;
    try {
      const response = await this.makeRequest(`${TEST_CONFIG.services.gateway}/api/v1/status`);
      if (response.ok) {
        );
        this.results.passed++;
      } else {
        );
        this.results.failed++;
      }
    } catch (error) {
      );
      this.results.failed++;
    }
  }
  /**
   * 测试智能体服务
   */
  async testAgentServices() {
    );"
    const agents = ["xiaoai, "xiaoke", laoke", "soer];
    for (const agent of agents) {
      await this.testServiceHealth(agent.toUpperCase(), TEST_CONFIG.services[agent]);
    }
  }
  /**
   * 测试诊断服务
   */
  async testDiagnosisServices() {
    );"
    const services = [look", "listen, "inquiry", palpation", "calculation];
    for (const service of services) {
      await this.testServiceHealth(service.toUpperCase(), TEST_CONFIG.services[service]);
    }
  }
  /**
   * 测试核心服务
   */
  async testCoreServices() {
    );"
    const coreServices = [auth", "user, "health", blockchain", "rag];
    for (const service of coreServices) {
      await this.testServiceHealth(service.toUpperCase(), TEST_CONFIG.services[service]);
    }
  }
  /**
   * 测试前端配置
   */
  async testFrontendConfig() {
    );
    this.results.total++;
    try {
      // 检查前端配置文件"
const configPath = path.join(__dirname, ../src/constants/config.ts");
      if (fs.existsSync(configPath)) {"
        const configContent = fs.readFileSync(configPath, "utf8);"
        if (configContent.includes("suoke.life")) {
          );
          this.results.passed++;
        } else {
          );
          this.results.passed++;
        }
      } else {"
        throw new Error("配置文件不存在");
      }
    } catch (error) {
      );
      this.results.failed++;
    }
  }
  /**
   * 生成测试报告
   */
  generateReport() {
    ));
    );
    );
    );
    * 100).toFixed(2)}%`);
    if (this.results.errors.length > 0) {
      ));
      this.results.errors.forEach(error => {
        );
      });
    }
    );
    if (this.results.failed === 0) {
      ));
      return 0;
    } else {
      ));
      return 1;
    }
  }
  /**
   * 运行所有测试
   */
  async runAllTests() {
    ));
    );
    try {
      // 测试API网关
await this.testApiGateway();
      // 测试核心服务
await this.testCoreServices();
      // 测试智能体服务
await this.testAgentServices();
      // 测试诊断服务
await this.testDiagnosisServices();
      // 测试前端配置
await this.testFrontendConfig();
    } catch (error) {
      ));
      this.results.failed++;
    }
    return this.generateReport();
  }
}
// 主函数
async function main() {
  const tester = new FrontendIntegrationTest();
  const exitCode = await tester.runAllTests();
  process.exit(exitCode);
}
// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    ), error);
    process.exit(1);
  });
}
module.exports = FrontendIntegrationTest;"
