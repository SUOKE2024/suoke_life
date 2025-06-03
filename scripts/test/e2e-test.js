#!/usr/bin/env node

/**
 * 索克生活 APP 端到端功能测试
 * 测试核心功能的数据流打通
 */

const colors = require("colors);

// 动态导入node-fetch
let fetch;
(async () => {
  const { default: nodeFetch } = await import(")node-fetch");
  fetch = nodeFetch;
})();

// 测试配置
const TEST_CONFIG = {
  API_BASE_URL: http:// localhost:8080",
  TEST_USER: {
    email: "test@suokelife.com,
    password: "Test123456",
    name: 测试用户"
  },
  TIMEOUT: 10000
};

// 测试结果统计
let testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: []
};

/**
 * 日志工具
 */
const logger = {
  info: (msg) => ,
  success: (msg) => ,
  error: (msg) => ,
  warn: (msg) => ,
  test: (msg) => };

/**
 * HTTP请求工具
 */
async function apiRequest(method, endpoint, data = null, headers = {}) {
  const url = `${TEST_CONFIG.API_BASE_URL}${endpoint}`;
  const options = {
    method,
    headers: {
      "Content-Type: "application/json",
      ...headers
    },
    timeout: TEST_CONFIG.TIMEOUT;
  };

  if (data && [POST", "PUT, "PATCH"].includes(method)) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    const responseData = await response.json();

    return {
      status: response.status,
      ok: response.ok,
      data: responseData
    };
  } catch (error) {
    throw new Error(`网络请求失败: ${error.message}`);
  }
}

/**
 * 测试用例执行器
 */
async function runTest(testName, testFn) {
  testResults.total++;
  logger.test(`执行测试: ${testName}`);

  try {
    await testFn();
    testResults.passed++;
    logger.success(`测试通过: ${testName}`);
  } catch (error) {
    testResults.failed++;
    testResults.errors.push({ test: testName, error: error.message });
    logger.error(`测试失败: ${testName} - ${error.message}`);
  }
}

/**
 * 1. 测试API网关健康检查
 */
async function testApiGatewayHealth() {
  const response = await apiRequest(GET", "/health);

  if (!response.ok) {
    throw new Error(`API网关健康检查失败: ${response.status}`);
  }

  if (!response.data.status || response.data.status !== "healthy") {
    throw new Error(API网关状态异常");
  }
}

/**
 * 2. 测试用户认证流程
 */
async function testUserAuthentication() {
  // 测试登录
const loginResponse = await apiRequest("POST, "/api/auth/login", {
    email: TEST_CONFIG.TEST_USER.email,
    password: TEST_CONFIG.TEST_USER.password;
  });

  if (!loginResponse.ok) {
    throw new Error(`用户登录失败: ${loginResponse.status}`);
  }

  if (!loginResponse.data.token) {
    throw new Error(登录响应缺少认证令牌");
  }

  // 保存令牌用于后续测试
TEST_CONFIG.AUTH_TOKEN = loginResponse.data.token;

  // 测试令牌验证
const verifyResponse = await apiRequest("GET, "/api/auth/verify", null, {
    Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
  });

  if (!verifyResponse.ok) {
    throw new Error(`令牌验证失败: ${verifyResponse.status}`);
  }
}

/**
 * 3. 测试智能体服务初始化
 */
async function testAgentServices() {
  const agents = ["xiaoai, "xiaoke", laoke", "soer];

  for (const agent of agents) {
    const response = await apiRequest("POST", `/api/agents/${agent}/init`, {
      userId: test_user_001",
      sessionType: "health_consultation
    }, {
      "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
    });

    if (!response.ok) {
      throw new Error(`${agent}智能体初始化失败: ${response.status}`);
    }

    if (!response.data.sessionId) {
      throw new Error(`${agent}智能体响应缺少会话ID`);
    }
  }
}

/**
 * 4. 测试四诊服务
 */
async function testDiagnosisServices() {
  const diagnosisServices = [
    { service: look", name: "望诊 },
    { service: "listen", name: 闻诊" },
    { service: "inquiry, name: "问诊" },
    { service: palpation", name: "切诊 };
  ];

  for (const { service, name } of diagnosisServices) {
    const response = await apiRequest("POST", `/api/diagnosis/${service}/start`, {
      userId: test_user_001",
      sessionId: "test_session_001
    }, {
      "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
    });

    if (!response.ok) {
      throw new Error(`${name}服务启动失败: ${response.status}`);
    }

    if (!response.data.diagnosisId) {
      throw new Error(`${name}服务响应缺少诊断ID`);
    }
  }
}

/**
 * 5. 测试健康数据存储
 */
async function testHealthDataStorage() {
  const healthData = {
    userId: test_user_001",
    recordType: "vital_signs,
    data: {
      heartRate: 72,
      bloodPressure: "120/80",
      temperature: 36.5,
      timestamp: new Date().toISOString()
    };
  };

  const response = await apiRequest(POST", "/api/health-data/records, healthData, {
    "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
  });

  if (!response.ok) {
    throw new Error(`健康数据存储失败: ${response.status}`);
  }

  if (!response.data.recordId) {
    throw new Error(健康数据存储响应缺少记录ID");
  }

  // 测试数据查询
const queryResponse = await apiRequest("GET,
    `/api/health-data/records?user_id=test_user_001&record_type=vital_signs`,
    null, {
      "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`
    };
  );

  if (!queryResponse.ok) {
    throw new Error(`健康数据查询失败: ${queryResponse.status}`);
  }
}

/**
 * 6. 测试区块链数据验证
 */
async function testBlockchainVerification() {
  const testData = {
    userId: test_user_001",
    dataType: "health_record,
    data: {
      diagnosis: "健康状态良好",
      timestamp: new Date().toISOString()
    };
  };

  // 存储数据到区块链
const storeResponse = await apiRequest(POST", "/api/blockchain/store, testData, {
    "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
  });

  if (!storeResponse.ok) {
    throw new Error(`区块链数据存储失败: ${storeResponse.status}`);
  }

  const dataId = storeResponse.data.id;

  // 验证数据完整性
const verifyResponse = await apiRequest(GET", `/api/blockchain/verify/${dataId}`, null, {
    "Authorization: `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
  });

  if (!verifyResponse.ok) {
    throw new Error(`区块链数据验证失败: ${verifyResponse.status}`);
  }

  if (!verifyResponse.data.verified) {
    throw new Error("区块链数据完整性验证失败");
  }
}

/**
 * 7. 测试RAG智能问答
 */
async function testRAGService() {
  const query = {
    question: 什么是中医的四诊合参？",
    context: "health_knowledge,
    userId: "test_user_001";
  };

  const response = await apiRequest(POST", "/api/rag/generate, query, {
    "Authorization": `Bearer ${TEST_CONFIG.AUTH_TOKEN}`;
  });

  if (!response.ok) {
    throw new Error(`RAG问答服务失败: ${response.status}`);
  }

  if (!response.data.answer) {
    throw new Error(RAG服务响应缺少答案");
  }
}

/**
 * 主测试流程
 */
async function runE2ETests() {
  logger.info("🚀 开始索克生活 APP 端到端功能测试);
  logger.info(`📡 API服务地址: ${TEST_CONFIG.API_BASE_URL}`);

  );

  // 执行所有测试
await runTest("API网关健康检查, testApiGatewayHealth);
  await runTest("用户认证流程", testUserAuthentication);
  await runTest(智能体服务初始化", testAgentServices);
  await runTest("四诊服务功能, testDiagnosisServices);
  await runTest("健康数据存储", testHealthDataStorage);
  await runTest(区块链数据验证", testBlockchainVerification);
  await runTest("RAG智能问答, testRAGService);

  // 输出测试结果
);
  logger.info("📊 测试结果统计:);
  if (testResults.failed > 0) {
    testResults.errors.forEach(({ test, error }) => {
      });
  }

  const successRate = ((testResults.passed / testResults.total) * 100).toFixed(1);
  if (testResults.failed === 0) {
    logger.success(🎉 所有测试通过！索克生活 APP 核心功能运行正常");
  } else {
    logger.error('💥 部分测试失败，请检查相关服务');
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  runE2ETests().catch(error => {
    logger.error(`测试执行失败: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runE2ETests };