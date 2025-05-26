#!/usr/bin/env node

/**
 * 索克生活扩展前端集成测试脚本
 * 测试所有微服务的完整集成验证
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
    password: 'test123',
    id: 'user_001'
  }
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
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

function logHeader(message) {
  log(`\n🔍 ${message}`, 'cyan');
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

// 扩展测试用例
class ExtendedIntegrationTests {
  constructor() {
    this.results = [];
    this.authToken = null;
    this.testData = {};
  }

  async runTest(name, testFunction) {
    logInfo(`Running: ${name}`);
    
    try {
      const startTime = Date.now();
      const result = await testFunction();
      const duration = Date.now() - startTime;
      
      if (result.success) {
        logSuccess(`${name} (${duration}ms)`);
        this.results.push({ name, status: 'PASS', duration, details: result.details });
      } else {
        logError(`${name}: ${result.message || 'Unknown error'}`);
        this.results.push({ name, status: 'FAIL', duration, error: result.message });
      }
    } catch (error) {
      logError(`${name}: ${error.message}`);
      this.results.push({ name, status: 'ERROR', error: error.message });
    }
  }

  // 1. 无障碍服务测试
  async testAccessibilityService() {
    // 获取无障碍配置
    const getConfigResponse = await makeRequest('GET', `/api/accessibility/config?user_id=${TEST_CONFIG.testUser.id}`);
    
    if (!getConfigResponse.success || !getConfigResponse.data.success) {
      return { success: false, message: 'Failed to get accessibility config' };
    }

    // 更新无障碍配置
    const updateConfigResponse = await makeRequest('POST', '/api/accessibility/config', {
      user_id: TEST_CONFIG.testUser.id,
      config: {
        font_size: 'extra_large',
        contrast_mode: 'high',
        voice_speed: 'slow'
      }
    });

    if (!updateConfigResponse.success || !updateConfigResponse.data.success) {
      return { success: false, message: 'Failed to update accessibility config' };
    }

    return { 
      success: true, 
      details: {
        features: getConfigResponse.data.features,
        updated_config: updateConfigResponse.data.updated_config
      }
    };
  }

  // 2. 区块链服务测试
  async testBlockchainService() {
    // 存储健康数据到区块链
    const healthData = {
      blood_pressure: { systolic: 120, diastolic: 80 },
      heart_rate: 72,
      timestamp: new Date().toISOString()
    };

    const storeResponse = await makeRequest('POST', '/api/blockchain/store', {
      user_id: TEST_CONFIG.testUser.id,
      data: healthData
    });

    if (!storeResponse.success || !storeResponse.data.success) {
      return { success: false, message: 'Failed to store data to blockchain' };
    }

    const blockId = storeResponse.data.block_id;
    this.testData.blockId = blockId;

    // 验证数据完整性
    const verifyResponse = await makeRequest('GET', `/api/blockchain/verify/${blockId}`);

    if (!verifyResponse.success || !verifyResponse.data.success) {
      return { success: false, message: 'Failed to verify blockchain data' };
    }

    return { 
      success: true, 
      details: {
        block_id: blockId,
        data_hash: storeResponse.data.data_hash,
        verified: verifyResponse.data.verified
      }
    };
  }

  // 3. 健康数据服务测试
  async testHealthDataService() {
    // 存储健康记录
    const healthRecord = {
      vital_signs: {
        temperature: 36.5,
        blood_pressure: { systolic: 120, diastolic: 80 },
        heart_rate: 72
      },
      symptoms: ['headache', 'fatigue'],
      notes: 'Regular checkup'
    };

    const storeResponse = await makeRequest('POST', '/api/health-data/records', {
      user_id: TEST_CONFIG.testUser.id,
      record_type: 'vital_signs',
      data: healthRecord
    });

    if (!storeResponse.success || !storeResponse.data.success) {
      return { success: false, message: 'Failed to store health record' };
    }

    // 获取健康记录
    const getResponse = await makeRequest('GET', `/api/health-data/records?user_id=${TEST_CONFIG.testUser.id}&record_type=vital_signs`);

    if (!getResponse.success || !getResponse.data.success) {
      return { success: false, message: 'Failed to get health records' };
    }

    return { 
      success: true, 
      details: {
        record_id: storeResponse.data.record_id,
        records_count: getResponse.data.count,
        records: getResponse.data.records
      }
    };
  }

  // 4. 医学知识服务测试
  async testMedKnowledgeService() {
    // 查询症状分析
    const queryResponse = await makeRequest('POST', '/api/med-knowledge/query', {
      query_type: 'symptom_analysis',
      query_data: {
        symptom: 'headache'
      }
    });

    if (!queryResponse.success || !queryResponse.data.success) {
      return { success: false, message: 'Failed to query medical knowledge' };
    }

    const knowledge = queryResponse.data.knowledge;
    if (!knowledge.causes || !knowledge.treatments) {
      return { success: false, message: 'Incomplete medical knowledge response' };
    }

    return { 
      success: true, 
      details: {
        symptom: queryResponse.data.symptom,
        knowledge: knowledge,
        confidence: queryResponse.data.confidence
      }
    };
  }

  // 5. 医疗资源服务测试
  async testMedicalResourceService() {
    // 查找附近医院
    const hospitalResponse = await makeRequest('POST', '/api/medical-resource/find', {
      resource_type: 'hospitals',
      location: { lat: 39.9042, lng: 116.4074 }, // 北京坐标
      radius: 10
    });

    if (!hospitalResponse.success || !hospitalResponse.data.success) {
      return { success: false, message: 'Failed to find hospitals' };
    }

    // 查找附近医生
    const doctorResponse = await makeRequest('POST', '/api/medical-resource/find', {
      resource_type: 'doctors',
      location: { lat: 39.9042, lng: 116.4074 },
      radius: 10
    });

    if (!doctorResponse.success || !doctorResponse.data.success) {
      return { success: false, message: 'Failed to find doctors' };
    }

    return { 
      success: true, 
      details: {
        hospitals: hospitalResponse.data.resources,
        doctors: doctorResponse.data.resources,
        total_resources: hospitalResponse.data.count + doctorResponse.data.count
      }
    };
  }

  // 6. 消息总线服务测试
  async testMessageBusService() {
    // 订阅主题
    const subscribeResponse = await makeRequest('POST', '/api/message-bus/subscribe', {
      topic: 'health_alerts',
      subscriber_id: TEST_CONFIG.testUser.id
    });

    if (!subscribeResponse.success || !subscribeResponse.data.success) {
      return { success: false, message: 'Failed to subscribe to topic' };
    }

    // 发布消息
    const publishResponse = await makeRequest('POST', '/api/message-bus/publish', {
      topic: 'health_alerts',
      message: {
        type: 'vital_sign_alert',
        user_id: TEST_CONFIG.testUser.id,
        alert: 'High blood pressure detected',
        timestamp: new Date().toISOString()
      }
    });

    if (!publishResponse.success || !publishResponse.data.success) {
      return { success: false, message: 'Failed to publish message' };
    }

    return { 
      success: true, 
      details: {
        topic: 'health_alerts',
        message_id: publishResponse.data.message_id,
        subscriber_status: subscribeResponse.data.status
      }
    };
  }

  // 7. RAG服务测试
  async testRAGService() {
    const ragResponse = await makeRequest('POST', '/api/rag/generate', {
      query: '高血压的预防方法有哪些？',
      context: {
        user_profile: {
          age: 30,
          gender: 'male',
          medical_history: ['hypertension_family_history']
        }
      }
    });

    if (!ragResponse.success || !ragResponse.data.success) {
      return { success: false, message: 'Failed to generate RAG response' };
    }

    const response = ragResponse.data;
    if (!response.response || response.confidence < 0.5) {
      return { success: false, message: 'Low quality RAG response' };
    }

    return { 
      success: true, 
      details: {
        query: response.query,
        response: response.response,
        retrieved_docs: response.retrieved_docs,
        confidence: response.confidence
      }
    };
  }

  // 8. 基准测试服务测试
  async testSuokeBenchService() {
    const benchmarkResponse = await makeRequest('POST', '/api/suoke-bench/run', {
      benchmark_type: 'api_performance',
      config: {
        duration: 10,
        concurrent_users: 5,
        target_endpoints: ['/health', '/api/auth/login']
      }
    });

    if (!benchmarkResponse.success || !benchmarkResponse.data.success) {
      return { success: false, message: 'Failed to run benchmark' };
    }

    const results = benchmarkResponse.data.results;
    if (!results.results || results.results.performance_score < 50) {
      return { success: false, message: 'Poor benchmark performance' };
    }

    return { 
      success: true, 
      details: {
        benchmark_id: results.benchmark_id,
        performance_score: results.results.performance_score,
        accuracy: results.results.accuracy,
        response_time: results.results.response_time
      }
    };
  }

  // 9. 玉米迷宫服务测试
  async testCornMazeService() {
    // 开始游戏会话
    const startResponse = await makeRequest('POST', '/api/corn-maze/start', {
      user_id: TEST_CONFIG.testUser.id,
      difficulty: 'medium'
    });

    if (!startResponse.success || !startResponse.data.success) {
      return { success: false, message: 'Failed to start game session' };
    }

    const sessionId = startResponse.data.session_id;

    // 更新游戏进度
    const updateResponse = await makeRequest('POST', '/api/corn-maze/update', {
      session_id: sessionId,
      action: 'move_forward',
      position: { x: 1, y: 1 }
    });

    if (!updateResponse.success || !updateResponse.data.success) {
      return { success: false, message: 'Failed to update game progress' };
    }

    return { 
      success: true, 
      details: {
        session_id: sessionId,
        difficulty: startResponse.data.difficulty,
        maze_config: startResponse.data.maze_config,
        score: updateResponse.data.score
      }
    };
  }

  // 10. 综合服务协作测试
  async testServiceIntegration() {
    // 模拟完整的健康管理流程
    const integrationSteps = [];

    try {
      // 1. 存储健康数据
      const healthData = {
        blood_pressure: { systolic: 140, diastolic: 90 },
        heart_rate: 85,
        timestamp: new Date().toISOString()
      };

      const storeResponse = await makeRequest('POST', '/api/health-data/records', {
        user_id: TEST_CONFIG.testUser.id,
        record_type: 'vital_signs',
        data: healthData
      });
      integrationSteps.push({ step: 'store_health_data', success: storeResponse.success });

      // 2. 区块链验证
      const blockchainResponse = await makeRequest('POST', '/api/blockchain/store', {
        user_id: TEST_CONFIG.testUser.id,
        data: healthData
      });
      integrationSteps.push({ step: 'blockchain_store', success: blockchainResponse.success });

      // 3. 医学知识查询
      const knowledgeResponse = await makeRequest('POST', '/api/med-knowledge/query', {
        query_type: 'symptom_analysis',
        query_data: { symptom: 'high_blood_pressure' }
      });
      integrationSteps.push({ step: 'knowledge_query', success: knowledgeResponse.success });

      // 4. 发送健康警报
      const alertResponse = await makeRequest('POST', '/api/message-bus/publish', {
        topic: 'health_alerts',
        message: {
          type: 'high_bp_alert',
          user_id: TEST_CONFIG.testUser.id,
          data: healthData
        }
      });
      integrationSteps.push({ step: 'send_alert', success: alertResponse.success });

      // 5. RAG生成建议
      const ragResponse = await makeRequest('POST', '/api/rag/generate', {
        query: '血压偏高应该如何调理？',
        context: { health_data: healthData }
      });
      integrationSteps.push({ step: 'rag_advice', success: ragResponse.success });

      const successfulSteps = integrationSteps.filter(step => step.success).length;
      const totalSteps = integrationSteps.length;

      if (successfulSteps < totalSteps * 0.8) {
        return { 
          success: false, 
          message: `Integration test failed: ${successfulSteps}/${totalSteps} steps successful` 
        };
      }

      return { 
        success: true, 
        details: {
          total_steps: totalSteps,
          successful_steps: successfulSteps,
          success_rate: (successfulSteps / totalSteps * 100).toFixed(1) + '%',
          steps: integrationSteps
        }
      };

    } catch (error) {
      return { success: false, message: `Integration test error: ${error.message}` };
    }
  }

  // 运行所有扩展测试
  async runAllExtendedTests() {
    logHeader('🚀 Starting Extended Suoke Life Integration Tests');

    // 基础服务测试
    logHeader('📋 Basic Services');
    await this.runTest('Health Check', () => this.testHealthCheck());
    await this.runTest('User Authentication', () => this.testUserAuthentication());

    // 新增的9个服务测试
    logHeader('🆕 Extended Services (9 New Services)');
    await this.runTest('Accessibility Service', () => this.testAccessibilityService());
    await this.runTest('Blockchain Service', () => this.testBlockchainService());
    await this.runTest('Health Data Service', () => this.testHealthDataService());
    await this.runTest('Medical Knowledge Service', () => this.testMedKnowledgeService());
    await this.runTest('Medical Resource Service', () => this.testMedicalResourceService());
    await this.runTest('Message Bus Service', () => this.testMessageBusService());
    await this.runTest('RAG Service', () => this.testRAGService());
    await this.runTest('Suoke Bench Service', () => this.testSuokeBenchService());
    await this.runTest('Corn Maze Service', () => this.testCornMazeService());

    // 综合集成测试
    logHeader('🔗 Service Integration');
    await this.runTest('Service Integration Flow', () => this.testServiceIntegration());
  }

  // 基础测试方法（从原测试脚本复制）
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

    return { 
      success: true, 
      details: {
        total_services: data.total_services,
        healthy_services: data.services.length
      }
    };
  }

  async testUserAuthentication() {
    const response = await makeRequest('POST', '/api/auth/login', TEST_CONFIG.testUser);
    
    if (!response.success) {
      return { success: false, message: 'Login request failed' };
    }

    const { data } = response;
    if (!data.success || !data.token) {
      return { success: false, message: 'Login failed or no token received' };
    }

    this.authToken = data.token;
    
    return { success: true, details: { token_received: true } };
  }

  // 生成扩展测试报告
  generateExtendedReport() {
    logHeader('📊 Extended Test Results Summary');
    log('='.repeat(60), 'cyan');

    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    const errors = this.results.filter(r => r.status === 'ERROR').length;
    const total = this.results.length;

    // 按类别分组显示结果
    const basicTests = this.results.filter(r => 
      r.name.includes('Health Check') || r.name.includes('Authentication')
    );
    const extendedTests = this.results.filter(r => 
      !r.name.includes('Health Check') && 
      !r.name.includes('Authentication') && 
      !r.name.includes('Integration')
    );
    const integrationTests = this.results.filter(r => 
      r.name.includes('Integration')
    );

    // 显示基础测试结果
    if (basicTests.length > 0) {
      log('\n📋 Basic Services:', 'blue');
      basicTests.forEach(result => {
        const icon = result.status === 'PASS' ? '✓' : '✗';
        const color = result.status === 'PASS' ? 'green' : 'red';
        const duration = result.duration ? ` (${result.duration}ms)` : '';
        log(`  ${icon} ${result.name}: ${result.status}${duration}`, color);
      });
    }

    // 显示扩展服务测试结果
    if (extendedTests.length > 0) {
      log('\n🆕 Extended Services (9 New Services):', 'magenta');
      extendedTests.forEach(result => {
        const icon = result.status === 'PASS' ? '✓' : '✗';
        const color = result.status === 'PASS' ? 'green' : 'red';
        const duration = result.duration ? ` (${result.duration}ms)` : '';
        log(`  ${icon} ${result.name}: ${result.status}${duration}`, color);
        
        if (result.error) {
          log(`    Error: ${result.error}`, 'red');
        }
      });
    }

    // 显示集成测试结果
    if (integrationTests.length > 0) {
      log('\n🔗 Service Integration:', 'cyan');
      integrationTests.forEach(result => {
        const icon = result.status === 'PASS' ? '✓' : '✗';
        const color = result.status === 'PASS' ? 'green' : 'red';
        const duration = result.duration ? ` (${result.duration}ms)` : '';
        log(`  ${icon} ${result.name}: ${result.status}${duration}`, color);
        
        if (result.details && result.details.success_rate) {
          log(`    Success Rate: ${result.details.success_rate}`, 'blue');
        }
      });
    }

    log('\n📈 Overall Summary:', 'cyan');
    log(`Total Tests: ${total}`, 'blue');
    log(`Passed: ${passed}`, 'green');
    log(`Failed: ${failed}`, failed > 0 ? 'red' : 'blue');
    log(`Errors: ${errors}`, errors > 0 ? 'red' : 'blue');
    log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`, passed === total ? 'green' : 'yellow');

    // 新增服务统计
    const newServicesPassed = extendedTests.filter(r => r.status === 'PASS').length;
    const newServicesTotal = extendedTests.length;
    log(`New Services Integration: ${newServicesPassed}/${newServicesTotal} (${((newServicesPassed / newServicesTotal) * 100).toFixed(1)}%)`, 
        newServicesPassed === newServicesTotal ? 'green' : 'yellow');

    // 保存扩展测试报告
    const report = {
      timestamp: new Date().toISOString(),
      summary: { 
        total, 
        passed, 
        failed, 
        errors,
        new_services_passed: newServicesPassed,
        new_services_total: newServicesTotal
      },
      categories: {
        basic_services: basicTests,
        extended_services: extendedTests,
        integration_tests: integrationTests
      },
      results: this.results
    };

    const reportPath = path.join(__dirname, '..', 'test-results', 'extended-integration-test-report.json');
    const reportDir = path.dirname(reportPath);
    
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    log(`\n📄 Extended test report saved to: ${reportPath}`, 'blue');

    return passed === total;
  }
}

// 主函数
async function main() {
  try {
    // 检查扩展后端服务是否运行
    logInfo('Checking extended backend service availability...');
    const healthResponse = await makeRequest('GET', '/health');
    
    if (!healthResponse.success) {
      logError('Extended backend service is not available. Please start the extended mock service first.');
      logInfo('Run: python3 scripts/extendedIntegrationTest.py');
      process.exit(1);
    }

    const serviceCount = healthResponse.data.total_services || 0;
    logSuccess(`Extended backend service is available with ${serviceCount} services`);

    if (serviceCount < 19) {
      logWarning(`Expected 19 services, but found ${serviceCount}. Some services may be missing.`);
    }

    // 运行扩展集成测试
    const tests = new ExtendedIntegrationTests();
    await tests.runAllExtendedTests();
    const allPassed = tests.generateExtendedReport();

    if (allPassed) {
      log('\n🎉 All extended tests passed! Complete microservices integration is working correctly.', 'green');
      log('✅ All 9 new services have been successfully integrated!', 'green');
      process.exit(0);
    } else {
      log('\n❌ Some extended tests failed. Please check the results above.', 'red');
      process.exit(1);
    }

  } catch (error) {
    logError(`Extended test execution failed: ${error.message}`);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  main();
}

module.exports = { ExtendedIntegrationTests, makeRequest }; 