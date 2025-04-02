/**
 * 生物识别API负载测试
 * 
 * 要运行此测试，请执行:
 * NODE_ENV=test node src/tests/load-tests/biometric-api.test.js
 */
const autocannon = require('autocannon');
const { promisify } = require('util');
const { generateTestJWT } = require('../utils.test');

const autocannonAsync = promisify(autocannon);

// 测试配置
const BASE_URL = process.env.TEST_API_URL || 'http://localhost:3001';
const TEST_DURATION = process.env.TEST_DURATION || 30; // 秒
const CONNECTIONS = process.env.TEST_CONNECTIONS || 100;
const PIPELINING = process.env.TEST_PIPELINING || 10;

// 测试用户信息
const TEST_USER = {
  id: 'load-test-user',
  email: 'load-test@suoke.life',
  username: 'loadTestUser',
  isAdmin: false
};

// 测试设备信息
const TEST_DEVICE = {
  deviceId: 'load-test-device',
  biometricType: 'fingerprint',
  publicKey: 'load-test-public-key',
  deviceInfo: {
    os: 'iOS',
    model: 'iPhone Load Test',
    osVersion: '16.0'
  }
};

// 运行挑战值生成API负载测试
async function runChallengeLoadTest(token) {
  console.log('开始挑战值生成API负载测试...');
  
  const result = await autocannonAsync({
    url: `${BASE_URL}/api/auth/biometric/challenge`,
    connections: CONNECTIONS,
    duration: TEST_DURATION,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    method: 'POST',
    body: JSON.stringify({
      userId: TEST_USER.id,
      deviceId: TEST_DEVICE.deviceId
    }),
    pipelining: PIPELINING
  });
  
  printResults('挑战值生成API', result);
  return result;
}

// 运行凭据列表API负载测试
async function runCredentialsListLoadTest(token) {
  console.log('开始凭据列表API负载测试...');
  
  const result = await autocannonAsync({
    url: `${BASE_URL}/api/auth/biometric/credentials?userId=${TEST_USER.id}`,
    connections: CONNECTIONS,
    duration: TEST_DURATION,
    headers: {
      'Authorization': `Bearer ${token}`
    },
    method: 'GET',
    pipelining: PIPELINING
  });
  
  printResults('凭据列表API', result);
  return result;
}

// 运行注册API负载测试
async function runRegisterLoadTest(token) {
  console.log('开始注册API负载测试...');
  
  const result = await autocannonAsync({
    url: `${BASE_URL}/api/auth/biometric/register`,
    connections: CONNECTIONS,
    duration: TEST_DURATION,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    method: 'POST',
    body: JSON.stringify({
      userId: TEST_USER.id,
      deviceId: TEST_DEVICE.deviceId,
      biometricType: TEST_DEVICE.biometricType,
      publicKey: TEST_DEVICE.publicKey,
      deviceInfo: TEST_DEVICE.deviceInfo,
      attestation: {
        attestationData: 'load-test-attestation-data'
      }
    }),
    pipelining: PIPELINING
  });
  
  printResults('注册API', result);
  return result;
}

// 运行验证API负载测试
async function runVerifyLoadTest(token, challenge) {
  console.log('开始验证API负载测试...');
  
  const result = await autocannonAsync({
    url: `${BASE_URL}/api/auth/biometric/verify`,
    connections: CONNECTIONS,
    duration: TEST_DURATION,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    method: 'POST',
    body: JSON.stringify({
      userId: TEST_USER.id,
      deviceId: TEST_DEVICE.deviceId,
      biometricType: TEST_DEVICE.biometricType,
      signature: 'load-test-signature',
      challenge: challenge || 'load-test-challenge'
    }),
    pipelining: PIPELINING
  });
  
  printResults('验证API', result);
  return result;
}

// 打印测试结果
function printResults(name, results) {
  console.log(`\n${name}负载测试结果:`);
  console.log(`  请求数: ${results.requests.total}`);
  console.log(`  吞吐量: ${results.requests.average} req/sec`);
  console.log(`  延迟:   平均 ${results.latency.average}ms`);
  console.log(`          最小 ${results.latency.min}ms`);
  console.log(`          最大 ${results.latency.max}ms`);
  console.log(`          p99 ${results.latency.p99}ms`);
  console.log(`  错误数: ${results.errors}`);
  console.log(`  2xx响应: ${results['2xx']}`);
  console.log(`  非2xx响应: ${results.non2xx}`);
}

// 运行所有负载测试
async function runAllTests() {
  try {
    console.log('生成测试JWT令牌...');
    const token = await generateTestJWT(TEST_USER);
    
    console.log('准备开始负载测试...');
    console.log(`基础URL: ${BASE_URL}`);
    console.log(`测试时长: ${TEST_DURATION}秒`);
    console.log(`并发连接: ${CONNECTIONS}`);
    console.log(`管道请求: ${PIPELINING}`);
    
    // 记录开始时间
    const startTime = new Date();
    console.log(`\n测试开始时间: ${startTime.toISOString()}`);
    
    // 运行所有测试
    await runRegisterLoadTest(token);
    await runChallengeLoadTest(token);
    await runCredentialsListLoadTest(token);
    await runVerifyLoadTest(token);
    
    // 记录结束时间
    const endTime = new Date();
    console.log(`\n测试结束时间: ${endTime.toISOString()}`);
    console.log(`总测试时间: ${(endTime - startTime) / 1000}秒`);
    
    console.log('\n所有负载测试完成');
  } catch (error) {
    console.error('负载测试中发生错误:', error);
    process.exit(1);
  }
}

// 启动测试
runAllTests(); 