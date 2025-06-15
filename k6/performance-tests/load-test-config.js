/**
 * K6性能测试配置 - 索克生活健康管理平台
 * 测试各微服务的性能表现和系统整体负载能力
 */

import { randomIntBetween, randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';

// 自定义性能指标
export const errorRate = new Rate('errors');
export const responseTime = new Trend('response_time');
export const requestCount = new Counter('requests');

// 测试环境配置
const BASE_URL = __ENV.BASE_URL || 'https://api.suoke.life';
const TEST_USER_COUNT = parseInt(__ENV.TEST_USER_COUNT) || 100;
const TEST_DURATION = __ENV.TEST_DURATION || '5m';

// 性能测试选项配置
export const options = {
  // 测试场景配置
  scenarios: {
    // 1. 用户认证服务负载测试
    auth_load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 20 },   // 2分钟内增加到20个用户
        { duration: '5m', target: 20 },   // 保持20个用户5分钟
        { duration: '2m', target: 50 },   // 2分钟内增加到50个用户
        { duration: '5m', target: 50 },   // 保持50个用户5分钟
        { duration: '2m', target: 0 },    // 2分钟内降到0个用户
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'auth_load' },
    },

    // 2. 健康数据服务压力测试
    health_data_stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },  // 快速增加到100个用户
        { duration: '5m', target: 100 },  // 保持100个用户
        { duration: '2m', target: 200 },  // 增加到200个用户
        { duration: '5m', target: 200 },  // 保持200个用户
        { duration: '10m', target: 0 },   // 逐步降到0
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'health_data_stress' },
    },

    // 3. 智能体协同服务峰值测试
    agent_collaboration_spike_test: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '10s', target: 10 },  // 保持基线
        { duration: '1m', target: 300 },  // 快速增加到300个用户（峰值）
        { duration: '3m', target: 300 },  // 保持峰值
        { duration: '10s', target: 10 },  // 快速降回基线
        { duration: '3m', target: 10 },   // 保持基线
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'agent_spike' },
    },

    // 4. 中医诊断服务容量测试
    tcm_diagnosis_capacity_test: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      tags: { test_type: 'tcm_capacity' },
    },

    // 5. 系统整体稳定性测试
    system_stability_test: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '5m', target: 100 },  // 逐步增加
        { duration: '30m', target: 100 }, // 长时间稳定运行
        { duration: '5m', target: 0 },    // 逐步减少
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'stability' },
    },
  },

  // 性能阈值配置
  thresholds: {
    // HTTP请求失败率小于1%
    http_req_failed: ['rate<0.01'],
    
    // 95%的请求响应时间小于500ms
    http_req_duration: ['p(95)<500'],
    
    // 平均响应时间小于200ms
    'http_req_duration{expected_response:true}': ['avg<200'],
    
    // 各服务特定阈值
    'http_req_duration{test_type:auth_load}': ['p(95)<300'],
    'http_req_duration{test_type:health_data_stress}': ['p(95)<800'],
    'http_req_duration{test_type:agent_spike}': ['p(95)<1000'],
    'http_req_duration{test_type:tcm_capacity}': ['p(95)<600'],
    'http_req_duration{test_type:stability}': ['p(95)<400'],
    
    // 自定义指标阈值
    errors: ['rate<0.1'],
    response_time: ['p(95)<500'],
    requests: ['count>1000'],
  },

  // 其他配置
  userAgent: 'K6-SuokeLife-PerformanceTest/1.0',
  insecureSkipTLSVerify: false,
  noConnectionReuse: false,
  noVUConnectionReuse: false,
  minIterationDuration: '1s',
  maxRedirects: 4,
  batch: 15,
  batchPerHost: 5,
  httpDebug: 'none',
  
  // 输出配置
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)', 'p(99.99)', 'count'],
  summaryTimeUnit: 'ms',
};

// 测试数据生成器
export function generateTestData() {
  return {
    user: {
      username: `testuser_${randomString(8)}`,
      email: `test_${randomString(8)}@example.com`,
      password: 'TestPassword123!',
      phone: `138${randomString(8, '0123456789')}`,
    },
    healthData: {
      bloodPressure: {
        systolic: randomIntBetween(90, 180),
        diastolic: randomIntBetween(60, 120),
        timestamp: new Date().toISOString(),
      },
      heartRate: randomIntBetween(60, 120),
      temperature: (36 + Math.random() * 2).toFixed(1),
      weight: randomIntBetween(45, 120),
      height: randomIntBetween(150, 200),
    },
    tcmData: {
      symptoms: ['头痛', '失眠', '食欲不振', '疲劳'][randomIntBetween(0, 3)],
      constitution: ['平和质', '气虚质', '阳虚质', '阴虚质'][randomIntBetween(0, 3)],
      pulse: ['浮脉', '沉脉', '数脉', '迟脉'][randomIntBetween(0, 3)],
      tongue: {
        color: ['淡红', '红', '深红'][randomIntBetween(0, 2)],
        coating: ['薄白', '厚白', '黄腻'][randomIntBetween(0, 2)],
      },
    },
  };
}

// 认证相关测试函数
export function testAuthentication() {
  group('用户认证测试', () => {
    const testData = generateTestData();
    
    // 用户注册
    group('用户注册', () => {
      const registerResponse = http.post(`${BASE_URL}/api/auth/register`, JSON.stringify({
        username: testData.user.username,
        email: testData.user.email,
        password: testData.user.password,
        phone: testData.user.phone,
      }), {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'register' },
      });

      check(registerResponse, {
        '注册状态码为201': (r) => r.status === 201,
        '注册响应时间<500ms': (r) => r.timings.duration < 500,
        '返回用户ID': (r) => JSON.parse(r.body).user_id !== undefined,
      });

      errorRate.add(registerResponse.status !== 201);
      responseTime.add(registerResponse.timings.duration);
      requestCount.add(1);
    });

    // 用户登录
    group('用户登录', () => {
      const loginResponse = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
        username: testData.user.username,
        password: testData.user.password,
      }), {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'login' },
      });

      check(loginResponse, {
        '登录状态码为200': (r) => r.status === 200,
        '登录响应时间<300ms': (r) => r.timings.duration < 300,
        '返回访问令牌': (r) => JSON.parse(r.body).access_token !== undefined,
      });

      errorRate.add(loginResponse.status !== 200);
      responseTime.add(loginResponse.timings.duration);
      requestCount.add(1);

      return loginResponse.status === 200 ? JSON.parse(loginResponse.body).access_token : null;
    });
  });
}

// 健康数据相关测试函数
export function testHealthData(accessToken) {
  group('健康数据服务测试', () => {
    const testData = generateTestData();
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    };

    // 上传健康数据
    group('上传健康数据', () => {
      const uploadResponse = http.post(`${BASE_URL}/api/health-data/upload`, JSON.stringify({
        type: 'vital_signs',
        data: testData.healthData,
        timestamp: new Date().toISOString(),
      }), {
        headers,
        tags: { endpoint: 'health_data_upload' },
      });

      check(uploadResponse, {
        '上传状态码为201': (r) => r.status === 201,
        '上传响应时间<800ms': (r) => r.timings.duration < 800,
        '返回数据ID': (r) => JSON.parse(r.body).data_id !== undefined,
      });

      errorRate.add(uploadResponse.status !== 201);
      responseTime.add(uploadResponse.timings.duration);
      requestCount.add(1);
    });

    // 查询健康数据
    group('查询健康数据', () => {
      const queryResponse = http.get(`${BASE_URL}/api/health-data/query?type=vital_signs&limit=10`, {
        headers,
        tags: { endpoint: 'health_data_query' },
      });

      check(queryResponse, {
        '查询状态码为200': (r) => r.status === 200,
        '查询响应时间<400ms': (r) => r.timings.duration < 400,
        '返回数据列表': (r) => Array.isArray(JSON.parse(r.body).data),
      });

      errorRate.add(queryResponse.status !== 200);
      responseTime.add(queryResponse.timings.duration);
      requestCount.add(1);
    });
  });
}

// 智能体协同测试函数
export function testAgentCollaboration(accessToken) {
  group('智能体协同服务测试', () => {
    const testData = generateTestData();
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    };

    // 智能体协同诊断
    group('智能体协同诊断', () => {
      const diagnosisResponse = http.post(`${BASE_URL}/api/agents/collaborate/diagnosis`, JSON.stringify({
        patient_data: testData.healthData,
        tcm_data: testData.tcmData,
        agents: ['xiaoai', 'xiaoke', 'laoke', 'soer'],
      }), {
        headers,
        tags: { endpoint: 'agent_collaboration' },
        timeout: '30s',
      });

      check(diagnosisResponse, {
        '协同诊断状态码为200': (r) => r.status === 200,
        '协同诊断响应时间<1000ms': (r) => r.timings.duration < 1000,
        '返回诊断结果': (r) => JSON.parse(r.body).diagnosis !== undefined,
      });

      errorRate.add(diagnosisResponse.status !== 200);
      responseTime.add(diagnosisResponse.timings.duration);
      requestCount.add(1);
    });
  });
}

// 中医诊断测试函数
export function testTCMDiagnosis(accessToken) {
  group('中医诊断服务测试', () => {
    const testData = generateTestData();
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    };

    // 五诊合参诊断
    group('五诊合参诊断', () => {
      const diagnosisResponse = http.post(`${BASE_URL}/api/diagnosis/five-methods`, JSON.stringify({
        wangzhen: { face_color: '红润', spirit: '良好' },
        wenzhen: { voice: '洪亮', breath: '正常' },
        wenzhen_inquiry: { symptoms: testData.tcmData.symptoms },
        qiezhen: { pulse: testData.tcmData.pulse },
        suanzhen: { constitution: testData.tcmData.constitution },
      }), {
        headers,
        tags: { endpoint: 'tcm_diagnosis' },
        timeout: '20s',
      });

      check(diagnosisResponse, {
        '中医诊断状态码为200': (r) => r.status === 200,
        '中医诊断响应时间<600ms': (r) => r.timings.duration < 600,
        '返回辨证结果': (r) => JSON.parse(r.body).syndrome_differentiation !== undefined,
      });

      errorRate.add(diagnosisResponse.status !== 200);
      responseTime.add(diagnosisResponse.timings.duration);
      requestCount.add(1);
    });
  });
}

// 主测试函数
export default function () {
  // 获取当前测试场景
  const scenario = __ENV.K6_SCENARIO_NAME || 'default';
  
  // 根据不同场景执行不同的测试
  switch (scenario) {
    case 'auth_load_test':
      testAuthentication();
      break;
      
    case 'health_data_stress_test':
      const token1 = testAuthentication();
      if (token1) {
        testHealthData(token1);
      }
      break;
      
    case 'agent_collaboration_spike_test':
      const token2 = testAuthentication();
      if (token2) {
        testAgentCollaboration(token2);
      }
      break;
      
    case 'tcm_diagnosis_capacity_test':
      const token3 = testAuthentication();
      if (token3) {
        testTCMDiagnosis(token3);
      }
      break;
      
    case 'system_stability_test':
    default:
      // 综合测试所有功能
      const token4 = testAuthentication();
      if (token4) {
        testHealthData(token4);
        testAgentCollaboration(token4);
        testTCMDiagnosis(token4);
      }
      break;
  }

  // 随机等待时间，模拟真实用户行为
  sleep(randomIntBetween(1, 3));
}

// 测试完成后的处理函数
export function handleSummary(data) {
  return {
    'performance-test-results.json': JSON.stringify(data, null, 2),
    'performance-test-summary.html': generateHTMLReport(data),
    stdout: generateConsoleReport(data),
  };
}

// 生成HTML报告
function generateHTMLReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>索克生活性能测试报告</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f8ff; padding: 20px; border-radius: 5px; }
        .metrics { display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }
        .metric-card { background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 200px; }
        .metric-title { font-weight: bold; color: #333; }
        .metric-value { font-size: 24px; color: #007acc; }
        .pass { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <div class="header">
        <h1>索克生活健康管理平台 - 性能测试报告</h1>
        <p>测试时间: ${new Date().toLocaleString('zh-CN')}</p>
        <p>测试持续时间: ${data.state.testRunDurationMs / 1000}秒</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-title">总请求数</div>
            <div class="metric-value">${data.metrics.http_reqs.count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">平均响应时间</div>
            <div class="metric-value">${data.metrics.http_req_duration.avg.toFixed(2)}ms</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">95%响应时间</div>
            <div class="metric-value">${data.metrics.http_req_duration['p(95)'].toFixed(2)}ms</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">错误率</div>
            <div class="metric-value ${data.metrics.http_req_failed.rate < 0.01 ? 'pass' : 'fail'}">
                ${(data.metrics.http_req_failed.rate * 100).toFixed(2)}%
            </div>
        </div>
    </div>
    
    <h2>阈值检查结果</h2>
    <ul>
        ${Object.entries(data.thresholds).map(([key, value]) => 
          `<li class="${value.ok ? 'pass' : 'fail'}">${key}: ${value.ok ? '通过' : '失败'}</li>`
        ).join('')}
    </ul>
</body>
</html>`;
}

// 生成控制台报告
function generateConsoleReport(data) {
  return `
========================================
索克生活性能测试报告
========================================
测试时间: ${new Date().toLocaleString('zh-CN')}
测试持续时间: ${data.state.testRunDurationMs / 1000}秒
虚拟用户数: ${data.state.vusMax}

核心指标:
- 总请求数: ${data.metrics.http_reqs.count}
- 平均响应时间: ${data.metrics.http_req_duration.avg.toFixed(2)}ms
- 95%响应时间: ${data.metrics.http_req_duration['p(95)'].toFixed(2)}ms
- 错误率: ${(data.metrics.http_req_failed.rate * 100).toFixed(2)}%

阈值检查: ${Object.values(data.thresholds).every(t => t.ok) ? '全部通过' : '存在失败项'}
========================================
`;
}