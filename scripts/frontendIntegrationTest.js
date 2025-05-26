#!/usr/bin/env node

/**
 * 索克生活前端集成测试脚本
 * 测试前后端通信、API客户端功能、智能体协作等
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

// 测试配置
const TEST_CONFIG = {
  baseUrl: 'http://localhost:8080',
  timeout: 5000,
  testUser: {
    email: 'test@suoke.life',
    password: 'test123'
  }
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✓ ${message}`, 'green');
}

function logError(message) {
  log(`✗ ${message}`, 'red');
}

function logInfo(message) {
  log(`ℹ ${message}`, 'blue');
}

function logWarning(message) {
  log(`⚠ ${message}`, 'yellow');
}

// HTTP请求工具
async function makeRequest(method, endpoint, data = null, headers = {}) {
  const url = `${TEST_CONFIG.baseUrl}${endpoint}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    timeout: TEST_CONFIG.timeout
  };

  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    const responseData = await response.json();
    
    return {
      success: response.ok,
      status: response.status,
      data: responseData,
      headers: response.headers
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// 测试用例
class IntegrationTests {
  constructor() {
    this.results = [];
    this.authToken = null;
  }

  async runTest(name, testFunction) {
    logInfo(`Running: ${name}`);
    
    try {
      const startTime = Date.now();
      const result = await testFunction();
      const duration = Date.now() - startTime;
      
      if (result.success) {
        logSuccess(`${name} (${duration}ms)`);
        this.results.push({ name, status: 'PASS', duration });
      } else {
        logError(`${name}: ${result.message || 'Unknown error'}`);
        this.results.push({ name, status: 'FAIL', duration, error: result.message });
      }
    } catch (error) {
      logError(`${name}: ${error.message}`);
      this.results.push({ name, status: 'ERROR', error: error.message });
    }
  }

  // 1. 健康检查测试
  async testHealthCheck() {
    const response = await makeRequest('GET', '/health');
    
    if (!response.success) {
      return { success: false, message: 'Health check failed' };
    }

    const { data } = response;
    if (data.status !== 'ok' || !Array.isArray(data.services)) {
      return { success: false, message: 'Invalid health check response' };
    }

    // 验证所有服务都是健康的
    const unhealthyServices = data.services.filter(service => service.status !== 'healthy');
    if (unhealthyServices.length > 0) {
      return { 
        success: false, 
        message: `Unhealthy services: ${unhealthyServices.map(s => s.service).join(', ')}` 
      };
    }

    return { success: true };
  }

  // 2. 用户认证测试
  async testUserAuthentication() {
    const response = await makeRequest('POST', '/api/auth/login', TEST_CONFIG.testUser);
    
    if (!response.success) {
      return { success: false, message: 'Login request failed' };
    }

    const { data } = response;
    if (!data.success || !data.token) {
      return { success: false, message: 'Login failed or no token received' };
    }

    // 保存token用于后续测试
    this.authToken = data.token;
    
    // 验证token
    const verifyResponse = await makeRequest('POST', '/api/auth/verify', { token: data.token });
    if (!verifyResponse.success || !verifyResponse.data.valid) {
      return { success: false, message: 'Token verification failed' };
    }

    return { success: true };
  }

  // 3. 用户数据获取测试
  async testUserDataRetrieval() {
    if (!this.authToken) {
      return { success: false, message: 'No auth token available' };
    }

    const response = await makeRequest('GET', '/api/user/user_001', null, {
      'Authorization': `Bearer ${this.authToken}`
    });

    if (!response.success) {
      return { success: false, message: 'User data request failed' };
    }

    const { data } = response;
    if (!data.success || !data.data) {
      return { success: false, message: 'Invalid user data response' };
    }

    // 验证用户数据结构
    const userData = data.data;
    const requiredFields = ['id', 'email', 'name', 'health_profile'];
    const missingFields = requiredFields.filter(field => !userData[field]);
    
    if (missingFields.length > 0) {
      return { 
        success: false, 
        message: `Missing user data fields: ${missingFields.join(', ')}` 
      };
    }

    return { success: true };
  }

  // 4. 智能体服务测试
  async testAgentServices() {
    const agents = ['xiaoai', 'xiaoke', 'laoke', 'soer'];
    const results = [];

    for (const agent of agents) {
      const response = await makeRequest('POST', `/api/agent/${agent}`, {
        type: 'health_analysis',
        data: {
          symptoms: ['fatigue', 'headache'],
          patient_id: 'user_001'
        }
      });

      if (!response.success || !response.data.success) {
        results.push({ agent, success: false });
      } else {
        const agentData = response.data;
        if (agentData.agent === agent && Array.isArray(agentData.capabilities)) {
          results.push({ agent, success: true });
        } else {
          results.push({ agent, success: false });
        }
      }
    }

    const failedAgents = results.filter(r => !r.success);
    if (failedAgents.length > 0) {
      return { 
        success: false, 
        message: `Failed agents: ${failedAgents.map(r => r.agent).join(', ')}` 
      };
    }

    return { success: true };
  }

  // 5. 四诊服务测试
  async testDiagnosisServices() {
    const diagnosisTypes = ['look', 'listen', 'inquiry', 'palpation'];
    const results = [];

    for (const type of diagnosisTypes) {
      const response = await makeRequest('POST', `/api/diagnosis/${type}`, {
        patient_id: 'user_001',
        data: {
          image_data: 'base64_encoded_data',
          metadata: { timestamp: new Date().toISOString() }
        }
      });

      if (!response.success || !response.data.success) {
        results.push({ type, success: false });
      } else {
        const diagnosisData = response.data;
        if (diagnosisData.diagnosis_type === type && diagnosisData.confidence > 0) {
          results.push({ type, success: true });
        } else {
          results.push({ type, success: false });
        }
      }
    }

    const failedDiagnosis = results.filter(r => !r.success);
    if (failedDiagnosis.length > 0) {
      return { 
        success: false, 
        message: `Failed diagnosis: ${failedDiagnosis.map(r => r.type).join(', ')}` 
      };
    }

    return { success: true };
  }

  // 6. API响应时间测试
  async testApiPerformance() {
    const endpoints = [
      { method: 'GET', path: '/health' },
      { method: 'POST', path: '/api/auth/login', data: TEST_CONFIG.testUser },
      { method: 'GET', path: '/api/user/user_001' }
    ];

    const performanceResults = [];

    for (const endpoint of endpoints) {
      const startTime = Date.now();
      const response = await makeRequest(endpoint.method, endpoint.path, endpoint.data);
      const responseTime = Date.now() - startTime;

      performanceResults.push({
        endpoint: `${endpoint.method} ${endpoint.path}`,
        responseTime,
        success: response.success
      });
    }

    // 检查是否有响应时间超过阈值的请求
    const slowRequests = performanceResults.filter(r => r.responseTime > 1000); // 1秒阈值
    if (slowRequests.length > 0) {
      return { 
        success: false, 
        message: `Slow requests detected: ${slowRequests.map(r => `${r.endpoint} (${r.responseTime}ms)`).join(', ')}` 
      };
    }

    const avgResponseTime = performanceResults.reduce((sum, r) => sum + r.responseTime, 0) / performanceResults.length;
    logInfo(`Average response time: ${avgResponseTime.toFixed(2)}ms`);

    return { success: true };
  }

  // 7. 错误处理测试
  async testErrorHandling() {
    const errorTests = [
      {
        name: 'Invalid endpoint',
        request: () => makeRequest('GET', '/api/invalid/endpoint')
      },
      {
        name: 'Invalid login credentials',
        request: () => makeRequest('POST', '/api/auth/login', { email: 'invalid@test.com', password: 'wrong' })
      },
      {
        name: 'Invalid user ID',
        request: () => makeRequest('GET', '/api/user/invalid_user_id')
      }
    ];

    for (const test of errorTests) {
      const response = await test.request();
      
      // 对于错误测试，我们期望得到适当的错误响应
      if (response.success && response.data.success) {
        return { 
          success: false, 
          message: `${test.name} should have failed but succeeded` 
        };
      }
    }

    return { success: true };
  }

  // 运行所有测试
  async runAllTests() {
    log('\n🚀 Starting Suoke Life Frontend Integration Tests\n', 'cyan');

    await this.runTest('Health Check', () => this.testHealthCheck());
    await this.runTest('User Authentication', () => this.testUserAuthentication());
    await this.runTest('User Data Retrieval', () => this.testUserDataRetrieval());
    await this.runTest('Agent Services', () => this.testAgentServices());
    await this.runTest('Diagnosis Services', () => this.testDiagnosisServices());
    await this.runTest('API Performance', () => this.testApiPerformance());
    await this.runTest('Error Handling', () => this.testErrorHandling());
  }

  // 生成测试报告
  generateReport() {
    log('\n📊 Test Results Summary\n', 'cyan');
    log('='.repeat(50), 'cyan');

    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    const errors = this.results.filter(r => r.status === 'ERROR').length;
    const total = this.results.length;

    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✓' : '✗';
      const color = result.status === 'PASS' ? 'green' : 'red';
      const duration = result.duration ? ` (${result.duration}ms)` : '';
      log(`${icon} ${result.name}: ${result.status}${duration}`, color);
      
      if (result.error) {
        log(`  Error: ${result.error}`, 'red');
      }
    });

    log('\n📈 Summary:', 'cyan');
    log(`Total Tests: ${total}`, 'blue');
    log(`Passed: ${passed}`, 'green');
    log(`Failed: ${failed}`, failed > 0 ? 'red' : 'blue');
    log(`Errors: ${errors}`, errors > 0 ? 'red' : 'blue');
    log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`, passed === total ? 'green' : 'yellow');

    // 保存测试报告
    const report = {
      timestamp: new Date().toISOString(),
      summary: { total, passed, failed, errors },
      results: this.results
    };

    const reportPath = path.join(__dirname, '..', 'test-results', 'integration-test-report.json');
    const reportDir = path.dirname(reportPath);
    
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    log(`\n📄 Test report saved to: ${reportPath}`, 'blue');

    return passed === total;
  }
}

// 主函数
async function main() {
  try {
    // 检查后端服务是否运行
    logInfo('Checking backend service availability...');
    const healthResponse = await makeRequest('GET', '/health');
    
    if (!healthResponse.success) {
      logError('Backend service is not available. Please start the mock service first.');
      logInfo('Run: python3 scripts/localTest.py');
      process.exit(1);
    }

    logSuccess('Backend service is available');

    // 运行集成测试
    const tests = new IntegrationTests();
    await tests.runAllTests();
    const allPassed = tests.generateReport();

    if (allPassed) {
      log('\n🎉 All tests passed! Frontend-Backend integration is working correctly.', 'green');
      process.exit(0);
    } else {
      log('\n❌ Some tests failed. Please check the results above.', 'red');
      process.exit(1);
    }

  } catch (error) {
    logError(`Test execution failed: ${error.message}`);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  main();
}

module.exports = { IntegrationTests, makeRequest }; 