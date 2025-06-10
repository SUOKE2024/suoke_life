import { check, sleep } from 'k6';
import http from 'k6/http';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

// 测试配置
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // 预热阶段：2分钟内逐渐增加到10个用户
    { duration: '5m', target: 10 },   // 稳定阶段：保持10个用户5分钟
    { duration: '2m', target: 20 },   // 增压阶段：2分钟内增加到20个用户
    { duration: '5m', target: 20 },   // 高负载阶段：保持20个用户5分钟
    { duration: '2m', target: 50 },   // 峰值阶段：2分钟内增加到50个用户
    { duration: '3m', target: 50 },   // 峰值保持：保持50个用户3分钟
    { duration: '2m', target: 0 },    // 降压阶段：2分钟内降到0个用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%的请求响应时间小于500ms
    http_req_failed: ['rate<0.1'],    // 错误率小于10%
    errors: ['rate<0.1'],             // 自定义错误率小于10%
  },
};

// 测试环境配置
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

// 测试数据
const testUsers = [
  { username: 'test_user_1', password: 'test_password_1' },
  { username: 'test_user_2', password: 'test_password_2' },
  { username: 'test_user_3', password: 'test_password_3' },
];

const healthQuestions = [
  '我最近感觉头痛，可能是什么原因？',
  '我的睡眠质量不好，有什么建议吗？',
  '我想了解一下中医体质调理',
  '最近食欲不振，应该怎么办？',
  '我想咨询一下养生保健的方法',
];

// 获取随机测试用户
function getRandomUser() {
  return testUsers[Math.floor(Math.random() * testUsers.length)];
}

// 获取随机健康问题
function getRandomQuestion() {
  return healthQuestions[Math.floor(Math.random() * healthQuestions.length)];
}

// 用户认证
function authenticate() {
  const user = getRandomUser();
  const loginPayload = JSON.stringify({
    username: user.username,
    password: user.password,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(`${BASE_URL}/api/${API_VERSION}/auth/login`, loginPayload, params);
  
  const success = check(response, {
    '登录状态码为200': (r) => r.status === 200,
    '登录响应包含token': (r) => r.json('access_token') !== undefined,
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);

  if (success) {
    return response.json('access_token');
  }
  return null;
}

// 健康检查测试
function testHealthCheck() {
  const response = http.get(`${BASE_URL}/health`);
  
  const success = check(response, {
    '健康检查状态码为200': (r) => r.status === 200,
    '健康检查响应时间<100ms': (r) => r.timings.duration < 100,
    '健康检查返回正确状态': (r) => r.json('status') === 'healthy',
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

// API网关测试
function testApiGateway(token) {
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const response = http.get(`${BASE_URL}/api/${API_VERSION}/gateway/status`, params);
  
  const success = check(response, {
    'API网关状态码为200': (r) => r.status === 200,
    'API网关响应时间<200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

// 用户服务测试
function testUserService(token) {
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const response = http.get(`${BASE_URL}/api/${API_VERSION}/users/profile`, params);
  
  const success = check(response, {
    '用户服务状态码为200': (r) => r.status === 200,
    '用户服务响应时间<300ms': (r) => r.timings.duration < 300,
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

// AI诊断服务测试
function testAiDiagnosis(token) {
  const question = getRandomQuestion();
  const payload = JSON.stringify({
    question: question,
    user_context: {
      age: 30,
      gender: 'male',
      symptoms: ['头痛', '失眠'],
    },
  });

  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(`${BASE_URL}/api/${API_VERSION}/ai/diagnosis`, payload, params);
  
  const success = check(response, {
    'AI诊断状态码为200': (r) => r.status === 200,
    'AI诊断响应时间<2000ms': (r) => r.timings.duration < 2000,
    'AI诊断返回建议': (r) => r.json('suggestions') !== undefined,
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

// 健康数据服务测试
function testHealthDataService(token) {
  const healthData = JSON.stringify({
    blood_pressure: {
      systolic: 120,
      diastolic: 80,
    },
    heart_rate: 72,
    temperature: 36.5,
    weight: 70.5,
    recorded_at: new Date().toISOString(),
  });

  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  // 创建健康数据
  const createResponse = http.post(`${BASE_URL}/api/${API_VERSION}/health/data`, healthData, params);
  
  const createSuccess = check(createResponse, {
    '创建健康数据状态码为201': (r) => r.status === 201,
    '创建健康数据响应时间<500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(!createSuccess);
  responseTime.add(createResponse.timings.duration);

  // 获取健康数据
  const getResponse = http.get(`${BASE_URL}/api/${API_VERSION}/health/data`, params);
  
  const getSuccess = check(getResponse, {
    '获取健康数据状态码为200': (r) => r.status === 200,
    '获取健康数据响应时间<300ms': (r) => r.timings.duration < 300,
  });

  errorRate.add(!getSuccess);
  responseTime.add(getResponse.timings.duration);
}

// 区块链服务测试
function testBlockchainService(token) {
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const response = http.get(`${BASE_URL}/api/${API_VERSION}/blockchain/health`, params);
  
  const success = check(response, {
    '区块链服务状态码为200': (r) => r.status === 200,
    '区块链服务响应时间<1000ms': (r) => r.timings.duration < 1000,
  });

  errorRate.add(!success);
  responseTime.add(response.timings.duration);
}

// 主测试函数
export default function () {
  // 1. 健康检查（无需认证）
  testHealthCheck();
  
  // 2. 用户认证
  const token = authenticate();
  if (!token) {
    console.error('认证失败，跳过后续测试');
    return;
  }

  // 3. API网关测试
  testApiGateway(token);
  sleep(0.5);

  // 4. 用户服务测试
  testUserService(token);
  sleep(0.5);

  // 5. AI诊断服务测试
  testAiDiagnosis(token);
  sleep(1);

  // 6. 健康数据服务测试
  testHealthDataService(token);
  sleep(0.5);

  // 7. 区块链服务测试
  testBlockchainService(token);
  sleep(0.5);

  // 随机等待时间，模拟真实用户行为
  sleep(Math.random() * 2 + 1);
}

// 测试完成后的清理函数
export function teardown(data) {
  console.log('性能测试完成');
  console.log(`总请求数: ${data.http_reqs}`);
  console.log(`平均响应时间: ${data.http_req_duration.avg}ms`);
  console.log(`95%响应时间: ${data.http_req_duration['p(95)']}ms`);
  console.log(`错误率: ${data.http_req_failed.rate * 100}%`);
} 