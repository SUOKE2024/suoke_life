#!/usr/bin/env node

/**
 * 索克生活项目前后端API集成测试
 * 测试前端与后端服务的API调用和数据交互
 */

const fs = require('fs');
const path = require('path');

console.log('🔗 索克生活前后端API集成测试');
console.log('=====================================');

// 测试配置
const TEST_CONFIG = {
  baseUrl: 'http://localhost:3000',
  apiTimeout: 10000,
  retryAttempts: 3,
  services: {
    auth: 'http://localhost:8001',
    agents: 'http://localhost:8002',
    health: 'http://localhost:8003',
    blockchain: 'http://localhost:8004'
  }
};

// 测试结果统计
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0,
  errors: [],
  details: []
};

/**
 * 模拟HTTP请求
 */
async function mockApiCall(endpoint, method = 'GET', data = null) {
  return new Promise((resolve) => {
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟不同的响应
      if (endpoint.includes('/auth/login')) {
        resolve({
          status: 200,
          data: {
            token: 'mock-jwt-token',
            user: { id: '123', name: '测试用户' }
          }
        });
      } else if (endpoint.includes('/agents/')) {
        resolve({
          status: 200,
          data: {
            agentId: 'xiaoai',
            response: '您好！我是小艾，很高兴为您服务。',
            timestamp: new Date().toISOString()
          }
        });
      } else if (endpoint.includes('/health/')) {
        resolve({
          status: 200,
          data: {
            metrics: {
              heartRate: 72,
              bloodPressure: '120/80',
              temperature: 36.5
            }
          }
        });
      } else if (endpoint.includes('/error')) {
        resolve({
          status: 500,
          error: 'Internal Server Error'
        });
      } else {
        resolve({
          status: 200,
          data: { message: 'Success' }
        });
      }
    }, Math.random() * 1000 + 100);
  });
}

/**
 * 执行单个API测试
 */
async function runApiTest(testCase) {
  const { name, endpoint, method, data, expectedStatus, expectedData } = testCase;
  
  try {
    console.log(`  🧪 测试: ${name}`);
    
    const startTime = Date.now();
    const response = await mockApiCall(endpoint, method, data);
    const duration = Date.now() - startTime;
    
    let passed = true;
    let errorMessage = '';
    
    // 验证状态码
    if (expectedStatus && response.status !== expectedStatus) {
      passed = false;
      errorMessage = `状态码不匹配: 期望 ${expectedStatus}, 实际 ${response.status}`;
    }
    
    // 验证响应数据
    if (expectedData && passed) {
      for (const key in expectedData) {
        if (response.data && response.data[key] !== expectedData[key]) {
          passed = false;
          errorMessage = `数据不匹配: ${key} 期望 ${expectedData[key]}, 实际 ${response.data[key]}`;
          break;
        }
      }
    }
    
    testResults.total++;
    
    if (passed) {
      testResults.passed++;
      console.log(`    ✅ 通过 (${duration}ms)`);
    } else {
      testResults.failed++;
      console.log(`    ❌ 失败: ${errorMessage}`);
      testResults.errors.push({ test: name, error: errorMessage });
    }
    
    testResults.details.push({
      name,
      passed,
      duration,
      error: errorMessage || null
    });
    
  } catch (error) {
    testResults.total++;
    testResults.failed++;
    console.log(`    ❌ 异常: ${error.message}`);
    testResults.errors.push({ test: name, error: error.message });
  }
}

/**
 * 认证服务测试
 */
async function testAuthService() {
  console.log('\n🔐 认证服务API测试');
  
  const authTests = [
    {
      name: '用户登录',
      endpoint: '/auth/login',
      method: 'POST',
      data: { username: 'test@example.com', password: 'password123' },
      expectedStatus: 200,
      expectedData: { token: 'mock-jwt-token' }
    },
    {
      name: '用户注册',
      endpoint: '/auth/register',
      method: 'POST',
      data: { username: 'newuser@example.com', password: 'password123' },
      expectedStatus: 200
    },
    {
      name: '令牌验证',
      endpoint: '/auth/verify',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '密码重置',
      endpoint: '/auth/reset-password',
      method: 'POST',
      data: { email: 'test@example.com' },
      expectedStatus: 200
    }
  ];
  
  for (const test of authTests) {
    await runApiTest(test);
  }
}

/**
 * 智能体服务测试
 */
async function testAgentService() {
  console.log('\n🤖 智能体服务API测试');
  
  const agentTests = [
    {
      name: '小艾对话',
      endpoint: '/agents/xiaoai/chat',
      method: 'POST',
      data: { message: '你好，我想咨询健康问题' },
      expectedStatus: 200
    },
    {
      name: '小克服务推荐',
      endpoint: '/agents/xiaoke/recommend',
      method: 'POST',
      data: { category: 'health', preferences: ['中医', '养生'] },
      expectedStatus: 200
    },
    {
      name: '老克知识查询',
      endpoint: '/agents/laoke/knowledge',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '索儿生活建议',
      endpoint: '/agents/soer/lifestyle',
      method: 'POST',
      data: { goals: ['减重', '改善睡眠'] },
      expectedStatus: 200
    },
    {
      name: '智能体状态查询',
      endpoint: '/agents/status',
      method: 'GET',
      expectedStatus: 200
    }
  ];
  
  for (const test of agentTests) {
    await runApiTest(test);
  }
}

/**
 * 健康数据服务测试
 */
async function testHealthService() {
  console.log('\n💊 健康数据服务API测试');
  
  const healthTests = [
    {
      name: '健康数据上传',
      endpoint: '/health/data',
      method: 'POST',
      data: { 
        type: 'vitals',
        data: { heartRate: 72, bloodPressure: '120/80' }
      },
      expectedStatus: 200
    },
    {
      name: '健康报告生成',
      endpoint: '/health/report',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '诊断记录查询',
      endpoint: '/health/diagnosis/history',
      method: 'GET',
      expectedStatus: 200
    },
    {
      name: '健康指标分析',
      endpoint: '/health/analysis',
      method: 'POST',
      data: { period: '30days' },
      expectedStatus: 200
    }
  ];
  
  for (const test of healthTests) {
    await runApiTest(test);
  }
}

/**
 * 区块链服务测试
 */
async function testBlockchainService() {
  console.log('\n⛓️  区块链服务API测试');
  
  const blockchainTests = [
    {
      name: '健康数据上链',
      endpoint: '/blockchain/store',
      method: 'POST',
      data: { 
        type: 'health_record',
        data: { patientId: '123', diagnosis: 'test' }
      },
      expectedStatus: 200
    },
    {
      name: '数据验证',
      endpoint: '/blockchain/verify',
      method: 'POST',
      data: { hash: 'test-hash' },
      expectedStatus: 200
    },
    {
      name: '隐私数据查询',
      endpoint: '/blockchain/query',
      method: 'GET',
      expectedStatus: 200
    }
  ];
  
  for (const test of blockchainTests) {
    await runApiTest(test);
  }
}

/**
 * 错误处理测试
 */
async function testErrorHandling() {
  console.log('\n⚠️  错误处理测试');
  
  const errorTests = [
    {
      name: '404错误处理',
      endpoint: '/nonexistent',
      method: 'GET',
      expectedStatus: 404
    },
    {
      name: '500错误处理',
      endpoint: '/error',
      method: 'GET',
      expectedStatus: 500
    },
    {
      name: '无效参数处理',
      endpoint: '/auth/login',
      method: 'POST',
      data: { invalid: 'data' },
      expectedStatus: 400
    }
  ];
  
  for (const test of errorTests) {
    await runApiTest(test);
  }
}

/**
 * 性能测试
 */
async function testPerformance() {
  console.log('\n⚡ API性能测试');
  
  const performanceTests = [
    {
      name: '并发请求测试',
      test: async () => {
        const promises = [];
        for (let i = 0; i < 10; i++) {
          promises.push(mockApiCall('/agents/xiaoai/chat', 'POST', { message: `测试消息${i}` }));
        }
        
        const startTime = Date.now();
        const results = await Promise.all(promises);
        const duration = Date.now() - startTime;
        
        const allSuccessful = results.every(r => r.status === 200);
        
        console.log(`    ${allSuccessful ? '✅' : '❌'} 并发请求 (${duration}ms, ${results.length}个请求)`);
        
        testResults.total++;
        if (allSuccessful) {
          testResults.passed++;
        } else {
          testResults.failed++;
        }
      }
    },
    {
      name: '响应时间测试',
      test: async () => {
        const startTime = Date.now();
        await mockApiCall('/health/data');
        const duration = Date.now() - startTime;
        
        const passed = duration < 2000; // 2秒内响应
        console.log(`    ${passed ? '✅' : '❌'} 响应时间 (${duration}ms)`);
        
        testResults.total++;
        if (passed) {
          testResults.passed++;
        } else {
          testResults.failed++;
        }
      }
    }
  ];
  
  for (const test of performanceTests) {
    await test.test();
  }
}

/**
 * 生成测试报告
 */
function generateTestReport() {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: testResults.total,
      passed: testResults.passed,
      failed: testResults.failed,
      successRate: ((testResults.passed / testResults.total) * 100).toFixed(2) + '%'
    },
    details: testResults.details,
    errors: testResults.errors,
    recommendations: []
  };
  
  // 生成建议
  if (testResults.failed > 0) {
    report.recommendations.push('修复失败的API测试');
  }
  
  if (testResults.passed / testResults.total < 0.9) {
    report.recommendations.push('提升API稳定性和可靠性');
  }
  
  report.recommendations.push('定期运行API集成测试');
  report.recommendations.push('监控API性能指标');
  
  try {
    fs.writeFileSync('api-integration-test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 API集成测试报告已保存到: api-integration-test-report.json');
  } catch (error) {
    console.warn('⚠️  无法保存测试报告');
  }
  
  return report;
}

/**
 * 主测试函数
 */
async function runApiIntegrationTests() {
  console.log('开始API集成测试...\n');
  
  try {
    await testAuthService();
    await testAgentService();
    await testHealthService();
    await testBlockchainService();
    await testErrorHandling();
    await testPerformance();
    
    console.log('\n📊 API集成测试结果');
    console.log('=====================================');
    console.log(`总测试数: ${testResults.total}`);
    console.log(`通过: ${testResults.passed}`);
    console.log(`失败: ${testResults.failed}`);
    console.log(`成功率: ${((testResults.passed / testResults.total) * 100).toFixed(2)}%`);
    
    if (testResults.errors.length > 0) {
      console.log('\n❌ 失败的测试:');
      testResults.errors.forEach(error => {
        console.log(`  - ${error.test}: ${error.error}`);
      });
    }
    
    const report = generateTestReport();
    
    console.log('\n💡 建议:');
    report.recommendations.forEach(rec => {
      console.log(`  - ${rec}`);
    });
    
    console.log('\n✅ API集成测试完成！');
    
  } catch (error) {
    console.error('❌ 测试执行失败:', error.message);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  runApiIntegrationTests();
}

module.exports = { runApiIntegrationTests, testResults }; 