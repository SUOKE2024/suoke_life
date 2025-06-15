/**
 * 认证服务负载测试 - 索克生活健康管理平台
 * 专门测试用户认证相关API的性能表现
 */

import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
export const authErrorRate = new Rate('auth_errors');
export const authResponseTime = new Trend('auth_response_time');

// 测试配置
const BASE_URL = __ENV.BASE_URL || 'https://api.suoke.life';

export const options = {
  scenarios: {
    auth_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 10 },   // 预热
        { duration: '3m', target: 50 },   // 增加负载
        { duration: '5m', target: 100 },  // 高负载
        { duration: '3m', target: 50 },   // 降低负载
        { duration: '1m', target: 0 },    // 结束
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
    auth_errors: ['rate<0.05'],
    auth_response_time: ['p(95)<250'],
  },
};

// 生成测试用户数据
function generateUserData() {
  const userId = randomString(8);
  return {
    username: `testuser_${userId}`,
    email: `test_${userId}@suoke.life`,
    password: 'TestPassword123!',
    phone: `138${randomString(8, '0123456789')}`,
    profile: {
      name: `测试用户${userId}`,
      age: Math.floor(Math.random() * 50) + 20,
      gender: Math.random() > 0.5 ? 'male' : 'female',
    },
  };
}

export default function () {
  const userData = generateUserData();
  let accessToken = null;

  group('用户注册流程', () => {
    const registerPayload = {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      phone: userData.phone,
      profile: userData.profile,
    };

    const registerResponse = http.post(
      `${BASE_URL}/api/auth/register`,
      JSON.stringify(registerPayload),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'register' },
      }
    );

    const registerSuccess = check(registerResponse, {
      '注册状态码为201': (r) => r.status === 201,
      '注册响应时间<500ms': (r) => r.timings.duration < 500,
      '返回用户信息': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.user_id && body.username;
        } catch (e) {
          return false;
        }
      },
      '包含激活链接': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.activation_required === true;
        } catch (e) {
          return false;
        }
      },
    });

    authErrorRate.add(!registerSuccess);
    authResponseTime.add(registerResponse.timings.duration);

    if (registerSuccess) {
      // 模拟邮箱激活（在测试环境中直接激活）
      const activationResponse = http.post(
        `${BASE_URL}/api/auth/activate`,
        JSON.stringify({
          username: userData.username,
          activation_code: 'TEST_ACTIVATION_CODE',
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          tags: { endpoint: 'activate' },
        }
      );

      check(activationResponse, {
        '激活状态码为200': (r) => r.status === 200,
        '激活响应时间<300ms': (r) => r.timings.duration < 300,
      });
    }
  });

  sleep(1);

  group('用户登录流程', () => {
    const loginPayload = {
      username: userData.username,
      password: userData.password,
    };

    const loginResponse = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify(loginPayload),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'login' },
      }
    );

    const loginSuccess = check(loginResponse, {
      '登录状态码为200': (r) => r.status === 200,
      '登录响应时间<300ms': (r) => r.timings.duration < 300,
      '返回访问令牌': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.access_token && body.token_type === 'Bearer';
        } catch (e) {
          return false;
        }
      },
      '返回刷新令牌': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.refresh_token !== undefined;
        } catch (e) {
          return false;
        }
      },
    });

    authErrorRate.add(!loginSuccess);
    authResponseTime.add(loginResponse.timings.duration);

    if (loginSuccess) {
      try {
        const loginData = JSON.parse(loginResponse.body);
        accessToken = loginData.access_token;
      } catch (e) {
        console.error('解析登录响应失败:', e);
      }
    }
  });

  if (accessToken) {
    sleep(1);

    group('令牌验证和用户信息获取', () => {
      const profileResponse = http.get(`${BASE_URL}/api/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        tags: { endpoint: 'profile' },
      });

      check(profileResponse, {
        '获取用户信息状态码为200': (r) => r.status === 200,
        '获取用户信息响应时间<200ms': (r) => r.timings.duration < 200,
        '返回完整用户信息': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.username && body.email && body.profile;
          } catch (e) {
            return false;
          }
        },
      });

      authResponseTime.add(profileResponse.timings.duration);
    });

    sleep(1);

    group('令牌刷新流程', () => {
      // 模拟令牌即将过期的情况
      const refreshResponse = http.post(
        `${BASE_URL}/api/auth/refresh`,
        JSON.stringify({
          refresh_token: 'mock_refresh_token',
        }),
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          tags: { endpoint: 'refresh' },
        }
      );

      check(refreshResponse, {
        '刷新令牌状态码为200': (r) => r.status === 200,
        '刷新令牌响应时间<400ms': (r) => r.timings.duration < 400,
        '返回新的访问令牌': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.access_token !== undefined;
          } catch (e) {
            return false;
          }
        },
      });

      authResponseTime.add(refreshResponse.timings.duration);
    });

    sleep(1);

    group('用户登出流程', () => {
      const logoutResponse = http.post(
        `${BASE_URL}/api/auth/logout`,
        null,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          tags: { endpoint: 'logout' },
        }
      );

      check(logoutResponse, {
        '登出状态码为200': (r) => r.status === 200,
        '登出响应时间<200ms': (r) => r.timings.duration < 200,
        '确认登出成功': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.message === 'Logged out successfully';
          } catch (e) {
            return false;
          }
        },
      });

      authResponseTime.add(logoutResponse.timings.duration);
    });
  }

  // 模拟用户思考时间
  sleep(Math.random() * 2 + 1);
}

// 测试完成后的处理
export function handleSummary(data) {
  const authMetrics = {
    total_requests: data.metrics.http_reqs.count,
    avg_response_time: data.metrics.http_req_duration.avg,
    p95_response_time: data.metrics.http_req_duration['p(95)'],
    error_rate: data.metrics.http_req_failed.rate,
    auth_error_rate: data.metrics.auth_errors ? data.metrics.auth_errors.rate : 0,
    auth_avg_response_time: data.metrics.auth_response_time ? data.metrics.auth_response_time.avg : 0,
  };

  return {
    'auth-load-test-results.json': JSON.stringify({
      summary: authMetrics,
      detailed: data,
      timestamp: new Date().toISOString(),
    }, null, 2),
    stdout: `
========================================
认证服务负载测试结果
========================================
总请求数: ${authMetrics.total_requests}
平均响应时间: ${authMetrics.avg_response_time.toFixed(2)}ms
95%响应时间: ${authMetrics.p95_response_time.toFixed(2)}ms
HTTP错误率: ${(authMetrics.error_rate * 100).toFixed(2)}%
认证错误率: ${(authMetrics.auth_error_rate * 100).toFixed(2)}%
认证平均响应时间: ${authMetrics.auth_avg_response_time.toFixed(2)}ms

阈值检查结果:
${Object.entries(data.thresholds).map(([key, value]) => 
  `- ${key}: ${value.ok ? '✓ 通过' : '✗ 失败'}`
).join('\n')}
========================================
`,
  };
} 