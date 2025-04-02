// K6 负载测试配置模板

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// 自定义指标
const errorRate = new Rate('error_rate');
const apiCallDuration = new Trend('api_call_duration');
const apiCalls = new Counter('api_calls');

// 基本选项配置
export const options = {
  // 基本场景配置
  scenarios: {
    // 冒烟测试
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '1m',
      tags: { test_type: 'smoke' },
    },
    // 负载测试
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 50 },   // 逐渐增加到50个虚拟用户
        { duration: '10m', target: 50 },  // 保持50个虚拟用户10分钟
        { duration: '5m', target: 0 },    // 逐渐减少到0个虚拟用户
      ],
      tags: { test_type: 'load' },
    },
    // 压力测试
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },   // 逐渐增加到100个虚拟用户
        { duration: '5m', target: 100 },   // 保持100个虚拟用户5分钟
        { duration: '2m', target: 200 },   // 增加到200个虚拟用户
        { duration: '5m', target: 200 },   // 保持200个虚拟用户5分钟
        { duration: '2m', target: 0 },     // 逐渐减少到0个虚拟用户
      ],
      tags: { test_type: 'stress' },
    },
    // 高峰测试
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 500 },   // 快速增加到500个虚拟用户
        { duration: '1m', target: 500 },    // 保持500个虚拟用户1分钟
        { duration: '10s', target: 0 },     // 快速减少到0个虚拟用户
      ],
      tags: { test_type: 'spike' },
    },
    // 耐久测试
    soak: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },     // 逐渐增加到50个虚拟用户
        { duration: '3h', target: 50 },     // 保持50个虚拟用户3小时
        { duration: '2m', target: 0 },      // 逐渐减少到0个虚拟用户
      ],
      tags: { test_type: 'soak' },
    },
  },
  // 一般设置
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1500'],  // 95%的请求响应时间小于500ms，99%小于1500ms
    http_req_failed: ['rate<0.01'],                 // 请求失败率低于1%
    'error_rate': ['rate<0.05'],                   // 业务错误率低于5%
    'api_call_duration': ['p(95)<1000'],           // API调用95%响应时间小于1000ms
  },
  // 每个VU完成测试后，确保清理资源
  teardownTimeout: '10s',
};

// 设置基本URL（可根据环境修改）
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// VU初始化
export function setup() {
  console.log(`开始负载测试: ${BASE_URL}`);
  // 在此处可以进行测试前的准备工作，如创建测试帐户，获取身份验证令牌等
  
  // 返回对象在VU中可用
  return {
    token: 'dummy-token', // 这里可以是实际获取的认证令牌
    testData: {
      userId: `user_${randomString(8)}`,
      timestamp: Date.now(),
    }
  };
}

// 主要测试函数
export default function(data) {
  // 添加统一的请求头
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
    'X-Request-ID': `load-test-${randomString(8)}`
  };
  
  // 健康检查API调用示例
  const healthCheckStartTime = Date.now();
  const healthResponse = http.get(`${BASE_URL}/health`, { headers });
  apiCallDuration.add(Date.now() - healthCheckStartTime);
  apiCalls.add(1);
  
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response has healthy': (r) => r.json().status === 'healthy',
  }) || errorRate.add(1);
  
  // 在实际测试中，可以添加更多API调用
  // 例如：创建资源、查询、更新、删除等操作
  // 模拟用户行为的场景
  
  // 每次API调用之间添加一些思考时间，更真实地模拟用户行为
  sleep(Math.random() * 3 + 1); // 1-4秒随机延迟
}

// 清理工作
export function teardown(data) {
  console.log(`完成负载测试：${Date.now() - data.testData.timestamp}ms`);
  // 在此处可以进行测试后的清理工作，如删除测试帐户等
}

// -----------------------------------------------
// 用法说明:
// 1. 基础运行: k6 run k6-config.js
// 2. 指定场景: k6 run --env SCENARIO=load k6-config.js
// 3. 指定API基础URL: k6 run --env BASE_URL=http://staging-api.example.com k6-config.js
// 4. 输出结果到文件: k6 run --out json=results.json k6-config.js
// 5. 将结果发送到时序数据库: k6 run --out influxdb=http://localhost:8086/k6 k6-config.js
// -----------------------------------------------