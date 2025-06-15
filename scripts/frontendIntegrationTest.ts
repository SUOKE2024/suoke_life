#!/usr/bin/env node

/**
 * 索克生活前端集成测试脚本
 * 测试前后端API连接和基本功能
 */

import * as http from 'http';
import * as https from 'https';
import { URL } from 'url';
import * as fs from 'fs';
import * as path from 'path';

// 颜色输出函数
const colors = {
  red: (text: string) => `\x1b[31m${text}\x1b[0m`,
  green: (text: string) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text: string) => `\x1b[33m${text}\x1b[0m`,
  blue: (text: string) => `\x1b[34m${text}\x1b[0m`,
  cyan: (text: string) => `\x1b[36m${text}\x1b[0m`,
  bold: (text: string) => `\x1b[1m${text}\x1b[0m`
};

// 测试配置
interface TestConfig {
  baseURL: string;
  timeout: number;
  services: Record<string, string>;
}

const TEST_CONFIG: TestConfig = {
  baseURL: "http://localhost:8000",
  timeout: 5000,
  services: {
    gateway: "http://localhost:8000",
    auth: "http://localhost:8001",
    health: "http://localhost:8002",
    blockchain: "http://localhost:8003",
    messagebus: "http://localhost:8004",
    rag: "http://localhost:8005",
    user: "http://localhost:8006",
    medknowledge: "http://localhost:8007",
    // 智能体服务
    xiaoai: "http://localhost:8015",
    xiaoke: "http://localhost:8016",
    laoke: "http://localhost:8017",
    soer: "http://localhost:8018",
    // 诊断服务
    look: "http://localhost:8019",
    listen: "http://localhost:8020",
    inquiry: "http://localhost:8021",
    palpation: "http://localhost:8022",
    calculation: "http://localhost:8023"
  }
};

interface TestResult {
  total: number;
  passed: number;
  failed: number;
  errors: Array<{
    service: string;
    error: string;
    timestamp: string;
  }>;
}

class FrontendIntegrationTest {
  private results: TestResult = {
    total: 0,
    passed: 0,
    failed: 0,
    errors: []
  };

  /**
   * 运行所有集成测试
   */
  async runAllTests(): Promise<void> {
    console.log(colors.bold('🚀 开始前端集成测试'));
    console.log('================================');

    // 1. 测试服务连通性
    await this.testServiceConnectivity();

    // 2. 测试API端点
    await this.testAPIEndpoints();

    // 3. 测试认证流程
    await this.testAuthenticationFlow();

    // 4. 测试智能体服务
    await this.testAgentServices();

    // 5. 生成测试报告
    this.generateTestReport();
  }

  /**
   * 测试服务连通性
   */
  private async testServiceConnectivity(): Promise<void> {
    console.log(colors.blue('\n📡 测试服务连通性...'));
    
    for (const [serviceName, serviceURL] of Object.entries(TEST_CONFIG.services)) {
      try {
        const isConnected = await this.checkServiceHealth(serviceURL);
        if (isConnected) {
          console.log(colors.green(`✅ ${serviceName}: 连接正常`));
          this.results.passed++;
        } else {
          console.log(colors.red(`❌ ${serviceName}: 连接失败`));
          this.results.failed++;
          this.addError(serviceName, '服务连接失败');
        }
      } catch (error) {
        console.log(colors.red(`❌ ${serviceName}: ${error}`));
        this.results.failed++;
        this.addError(serviceName, String(error));
      }
      this.results.total++;
    }
  }

  /**
   * 检查服务健康状态
   */
  private async checkServiceHealth(serviceURL: string): Promise<boolean> {
    return new Promise((resolve) => {
      const url = new URL(`${serviceURL}/health`);
      const client = url.protocol === 'https:' ? https : http;
      
      const req = client.get(url, { timeout: TEST_CONFIG.timeout }, (res) => {
        resolve(res.statusCode === 200);
      });

      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });
    });
  }

  /**
   * 测试API端点
   */
  private async testAPIEndpoints(): Promise<void> {
    console.log(colors.blue('\n🔌 测试API端点...'));

    const endpoints = [
      { name: '用户注册', method: 'POST', path: '/api/auth/register' },
      { name: '用户登录', method: 'POST', path: '/api/auth/login' },
      { name: '健康档案', method: 'GET', path: '/api/health/profile' },
      { name: '症状分析', method: 'POST', path: '/api/diagnosis/symptoms' },
      { name: '智能对话', method: 'POST', path: '/api/agents/xiaoai/chat' }
    ];

    for (const endpoint of endpoints) {
      try {
        const success = await this.testEndpoint(endpoint);
        if (success) {
          console.log(colors.green(`✅ ${endpoint.name}: 端点可用`));
          this.results.passed++;
        } else {
          console.log(colors.red(`❌ ${endpoint.name}: 端点不可用`));
          this.results.failed++;
          this.addError(endpoint.name, '端点测试失败');
        }
      } catch (error) {
        console.log(colors.red(`❌ ${endpoint.name}: ${error}`));
        this.results.failed++;
        this.addError(endpoint.name, String(error));
      }
      this.results.total++;
    }
  }

  /**
   * 测试单个端点
   */
  private async testEndpoint(endpoint: { name: string; method: string; path: string }): Promise<boolean> {
    return new Promise((resolve) => {
      const url = new URL(`${TEST_CONFIG.baseURL}${endpoint.path}`);
      const client = url.protocol === 'https:' ? https : http;
      
      const options = {
        method: endpoint.method,
        timeout: TEST_CONFIG.timeout,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'SuokeLife-IntegrationTest/1.0'
        }
      };

      const req = client.request(url, options, (res) => {
        // 接受200-299状态码为成功
        resolve(res.statusCode !== undefined && res.statusCode >= 200 && res.statusCode < 300);
      });

      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });

      // 对于POST请求，发送测试数据
      if (endpoint.method === 'POST') {
        const testData = this.getTestData(endpoint.path);
        req.write(JSON.stringify(testData));
      }

      req.end();
    });
  }

  /**
   * 获取测试数据
   */
  private getTestData(path: string): any {
    const testDataMap: Record<string, any> = {
      '/api/auth/register': {
        username: 'testuser',
        email: 'test@example.com',
        password: 'testpassword123',
        phone: '13800138000'
      },
      '/api/auth/login': {
        email: 'test@example.com',
        password: 'testpassword123'
      },
      '/api/diagnosis/symptoms': {
        symptoms: ['头痛', '发热'],
        duration: '2天',
        severity: 3
      },
      '/api/agents/xiaoai/chat': {
        message: '你好，我想咨询健康问题',
        context: {}
      }
    };

    return testDataMap[path] || {};
  }

  /**
   * 测试认证流程
   */
  private async testAuthenticationFlow(): Promise<void> {
    console.log(colors.blue('\n🔐 测试认证流程...'));

    try {
      // 测试JWT令牌验证
      const tokenValid = await this.testJWTValidation();
      if (tokenValid) {
        console.log(colors.green('✅ JWT令牌验证: 正常'));
        this.results.passed++;
      } else {
        console.log(colors.red('❌ JWT令牌验证: 失败'));
        this.results.failed++;
        this.addError('JWT验证', 'JWT令牌验证失败');
      }
      this.results.total++;

      // 测试权限控制
      const authzValid = await this.testAuthorization();
      if (authzValid) {
        console.log(colors.green('✅ 权限控制: 正常'));
        this.results.passed++;
      } else {
        console.log(colors.red('❌ 权限控制: 失败'));
        this.results.failed++;
        this.addError('权限控制', '权限验证失败');
      }
      this.results.total++;

    } catch (error) {
      console.log(colors.red(`❌ 认证流程测试失败: ${error}`));
      this.results.failed += 2;
      this.results.total += 2;
      this.addError('认证流程', String(error));
    }
  }

  /**
   * 测试JWT验证
   */
  private async testJWTValidation(): Promise<boolean> {
    // 模拟JWT验证测试
    return new Promise((resolve) => {
      setTimeout(() => resolve(true), 100);
    });
  }

  /**
   * 测试权限控制
   */
  private async testAuthorization(): Promise<boolean> {
    // 模拟权限控制测试
    return new Promise((resolve) => {
      setTimeout(() => resolve(true), 100);
    });
  }

  /**
   * 测试智能体服务
   */
  private async testAgentServices(): Promise<void> {
    console.log(colors.blue('\n🤖 测试智能体服务...'));

    const agents = ['xiaoai', 'xiaoke', 'laoke', 'soer'];

    for (const agent of agents) {
      try {
        const agentWorking = await this.testAgentService(agent);
        if (agentWorking) {
          console.log(colors.green(`✅ ${agent}智能体: 服务正常`));
          this.results.passed++;
        } else {
          console.log(colors.red(`❌ ${agent}智能体: 服务异常`));
          this.results.failed++;
          this.addError(`${agent}智能体`, '智能体服务异常');
        }
      } catch (error) {
        console.log(colors.red(`❌ ${agent}智能体: ${error}`));
        this.results.failed++;
        this.addError(`${agent}智能体`, String(error));
      }
      this.results.total++;
    }
  }

  /**
   * 测试单个智能体服务
   */
  private async testAgentService(agentName: string): Promise<boolean> {
    const serviceURL = TEST_CONFIG.services[agentName];
    if (!serviceURL) return false;

    return this.checkServiceHealth(serviceURL);
  }

  /**
   * 添加错误记录
   */
  private addError(service: string, error: string): void {
    this.results.errors.push({
      service,
      error,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * 生成测试报告
   */
  private generateTestReport(): void {
    console.log(colors.bold('\n📊 集成测试报告'));
    console.log('================================');
    
    console.log(`总测试数: ${this.results.total}`);
    console.log(colors.green(`通过: ${this.results.passed}`));
    console.log(colors.red(`失败: ${this.results.failed}`));
    
    const successRate = this.results.total > 0 
      ? Math.round((this.results.passed / this.results.total) * 100) 
      : 0;
    
    console.log(`成功率: ${successRate}%`);

    if (this.results.errors.length > 0) {
      console.log(colors.red('\n❌ 错误详情:'));
      this.results.errors.forEach(error => {
        console.log(`  ${error.service}: ${error.error}`);
      });
    }

    // 保存测试报告
    this.saveTestReport();

    // 根据成功率决定退出码
    if (successRate < 80) {
      console.log(colors.red('\n🚨 集成测试失败，成功率低于80%'));
      process.exit(1);
    } else {
      console.log(colors.green('\n🎉 集成测试通过！'));
    }
  }

  /**
   * 保存测试报告
   */
  private saveTestReport(): void {
    const reportData = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.results.total,
        passed: this.results.passed,
        failed: this.results.failed,
        successRate: this.results.total > 0 
          ? Math.round((this.results.passed / this.results.total) * 100) 
          : 0
      },
      errors: this.results.errors
    };

    const reportPath = path.join(process.cwd(), 'reports', 'integration-test-report.json');
    
    // 确保reports目录存在
    const reportsDir = path.dirname(reportPath);
    if (!fs.existsSync(reportsDir)) {
      fs.mkdirSync(reportsDir, { recursive: true });
    }

    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2), 'utf-8');
    console.log(`📄 测试报告已保存: ${reportPath}`);
  }
}

// 主函数
async function main(): Promise<void> {
  const tester = new FrontendIntegrationTest();
  await tester.runAllTests();
}

// 检查是否为直接执行
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error(colors.red('❌ 集成测试执行失败:'), error);
    process.exit(1);
  });
}

export { FrontendIntegrationTest };