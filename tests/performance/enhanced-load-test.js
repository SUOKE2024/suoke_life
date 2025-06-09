import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const agentResponseTime = new Trend('agent_response_time');
const collaborationTime = new Trend('collaboration_time');
const concurrentUsers = new Counter('concurrent_users');

// 测试配置
export const options = {
  stages: [
    { duration: '2m', target: 20 }, // 预热阶段
    { duration: '5m', target: 50 }, // 负载增加
    { duration: '10m', target: 100 }, // 稳定负载
    { duration: '5m', target: 200 }, // 峰值负载
    { duration: '3m', target: 300 }, // 压力测试
    { duration: '2m', target: 0 }, // 冷却阶段
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95%的请求响应时间小于3秒
    http_req_failed: ['rate<0.05'], // 错误率小于5%
    agent_response_time: ['p(95)<5000'], // 智能体响应时间小于5秒
    collaboration_time: ['p(95)<10000'], // 协作响应时间小于10秒
    errors: ['rate<0.05'],
  },
};

// 测试数据
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_TOKEN = __ENV.API_TOKEN || 'test-token';

// 测试用户池
const testUsers = [
  { username: 'test_user_1', password: 'password123', profile: { age: 25, gender: 'female' } },
  { username: 'test_user_2', password: 'password123', profile: { age: 35, gender: 'male' } },
  { username: 'test_user_3', password: 'password123', profile: { age: 45, gender: 'female' } },
  { username: 'test_user_4', password: 'password123', profile: { age: 55, gender: 'male' } },
  { username: 'test_user_5', password: 'password123', profile: { age: 65, gender: 'female' } },
];

// 健康咨询问题池
const healthQuestions = [
  '我最近总是感觉疲劳，睡眠质量也不好，该怎么办？',
  '我有高血压，平时饮食需要注意什么？',
  '我经常头痛，可能是什么原因？',
  '我想减肥，有什么好的建议吗？',
  '我的孩子经常感冒，如何提高免疫力？',
  '我有糖尿病，运动时需要注意什么？',
  '我经常失眠，有什么中医调理方法？',
  '我的血脂偏高，需要如何调理？',
  '我有胃病，饮食上有什么禁忌？',
  '我想了解如何预防心脏病',
];

// 中医症状池
const tcmSymptoms = [
  ['怕冷', '手脚冰凉', '精神不振', '食欲不振'],
  ['口干', '便秘', '心烦', '失眠'],
  ['头晕', '耳鸣', '腰膝酸软', '健忘'],
  ['胸闷', '气短', '乏力', '自汗'],
  ['腹胀', '便溏', '食少', '肢体困重'],
  ['潮热', '盗汗', '五心烦热', '口燥咽干'],
  ['情志抑郁', '胸胁胀痛', '善太息', '月经不调'],
  ['面色晦暗', '肌肤甲错', '胸痛', '舌质紫暗'],
  ['形体肥胖', '胸闷痰多', '头重如裹', '身重困倦'],
];

// 儿童健康问题池
const childHealthIssues = [
  { symptoms: ['咳嗽', '流鼻涕', '食欲不振'], age_months: 36 },
  { symptoms: ['发热', '精神萎靡', '拒食'], age_months: 24 },
  { symptoms: ['腹泻', '呕吐', '哭闹'], age_months: 12 },
  { symptoms: ['皮疹', '瘙痒', '睡眠不安'], age_months: 18 },
  { symptoms: ['便秘', '腹胀', '食欲差'], age_months: 30 },
];

// 获取认证令牌
function getAuthToken() {
  const user = testUsers[randomIntBetween(0, testUsers.length - 1)];
  const loginResponse = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: user.username,
    password: user.password
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginResponse.status === 200) {
    return loginResponse.json('access_token');
  }
  return API_TOKEN; // 回退到默认令牌
}

// 小艾智能体测试
function testXiaoAi(token) {
  group('小艾智能体测试', () => {
    const question = healthQuestions[randomIntBetween(0, healthQuestions.length - 1)];
    const user = testUsers[randomIntBetween(0, testUsers.length - 1)];
    
    const payload = JSON.stringify({
      message: question,
      user_context: user.profile
    });

    const response = http.post(`${BASE_URL}/api/agents/xiaoai/consult`, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const success = check(response, {
      '小艾响应状态正确': (r) => r.status === 200,
      '小艾响应包含建议': (r) => r.json('response') !== undefined,
      '小艾响应时间合理': (r) => r.timings.duration < 5000,
    });

    if (success) {
      agentResponseTime.add(response.timings.duration);
    } else {
      errorRate.add(1);
    }
  });
}

// 小克智能体测试
function testXiaoKe(token) {
  group('小克智能体测试', () => {
    const symptoms = tcmSymptoms[randomIntBetween(0, tcmSymptoms.length - 1)];
    
    const payload = JSON.stringify({
      symptoms: symptoms,
      tongue_image: 'base64_encoded_test_image',
      pulse_data: {
        rate: randomIntBetween(60, 100),
        rhythm: 'regular',
        strength: ['weak', 'normal', 'strong'][randomIntBetween(0, 2)]
      }
    });

    const response = http.post(`${BASE_URL}/api/agents/xiaoke/constitution-analysis`, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const success = check(response, {
      '小克响应状态正确': (r) => r.status === 200,
      '小克体质分析完整': (r) => r.json('constitution_type') !== undefined,
      '小克置信度合理': (r) => {
        const confidence = r.json('confidence_score');
        return confidence >= 0 && confidence <= 1;
      },
    });

    if (success) {
      agentResponseTime.add(response.timings.duration);
    } else {
      errorRate.add(1);
    }
  });
}

// 老克智能体测试
function testLaoKe(token) {
  group('老克智能体测试', () => {
    const payload = JSON.stringify({
      health_data: {
        vital_signs: {
          blood_pressure: `${randomIntBetween(110, 140)}/${randomIntBetween(70, 90)}`,
          heart_rate: randomIntBetween(60, 100),
          temperature: 36.5 + (Math.random() * 1.5)
        },
        lab_results: {
          blood_glucose: 4.0 + (Math.random() * 3.0),
          cholesterol: 3.0 + (Math.random() * 3.0),
          hemoglobin: randomIntBetween(120, 160)
        },
        symptoms_history: [
          { symptom: '头痛', frequency: 'weekly', duration: '6months' },
          { symptom: '失眠', frequency: 'daily', duration: '3months' }
        ]
      }
    });

    const response = http.post(`${BASE_URL}/api/agents/laoke/deep-analysis`, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const success = check(response, {
      '老克响应状态正确': (r) => r.status === 200,
      '老克分析报告完整': (r) => r.json('analysis_report') !== undefined,
      '老克风险评估存在': (r) => r.json('risk_factors') !== undefined,
    });

    if (success) {
      agentResponseTime.add(response.timings.duration);
    } else {
      errorRate.add(1);
    }
  });
}

// 索儿智能体测试
function testSoer(token) {
  group('索儿智能体测试', () => {
    const childIssue = childHealthIssues[randomIntBetween(0, childHealthIssues.length - 1)];
    
    const payload = JSON.stringify({
      child_info: {
        age_months: childIssue.age_months,
        gender: ['male', 'female'][randomIntBetween(0, 1)],
        weight_kg: 10 + (childIssue.age_months / 12) * 3,
        height_cm: 70 + (childIssue.age_months / 12) * 10
      },
      symptoms: childIssue.symptoms,
      duration_days: randomIntBetween(1, 7)
    });

    const response = http.post(`${BASE_URL}/api/agents/soer/child-assessment`, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const success = check(response, {
      '索儿响应状态正确': (r) => r.status === 200,
      '索儿评估完整': (r) => r.json('assessment') !== undefined,
      '索儿严重程度评估': (r) => r.json('severity_level') !== undefined,
    });

    if (success) {
      agentResponseTime.add(response.timings.duration);
    } else {
      errorRate.add(1);
    }
  });
}

// 智能体协作测试
function testAgentCollaboration(token) {
  group('智能体协作测试', () => {
    const payload = JSON.stringify({
      case_description: '45岁男性，慢性疲劳，睡眠质量差，血压偏高',
      participating_agents: ['xiaoai', 'xiaoke', 'laoke'],
      collaboration_type: 'comprehensive_analysis'
    });

    const response = http.post(`${BASE_URL}/api/agents/collaborate`, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const success = check(response, {
      '协作响应状态正确': (r) => r.status === 200,
      '协作ID存在': (r) => r.json('collaboration_id') !== undefined,
      '智能体贡献完整': (r) => {
        const contributions = r.json('agent_contributions');
        return contributions && contributions.xiaoai && contributions.xiaoke && contributions.laoke;
      },
      '共识诊断存在': (r) => r.json('consensus_diagnosis') !== undefined,
    });

    if (success) {
      collaborationTime.add(response.timings.duration);
    } else {
      errorRate.add(1);
    }
  });
}

// 系统健康检查
function healthCheck() {
  group('系统健康检查', () => {
    const response = http.get(`${BASE_URL}/api/health`);
    
    check(response, {
      '健康检查状态正确': (r) => r.status === 200,
      '所有服务运行正常': (r) => {
        const health = r.json();
        return health && health.status === 'healthy';
      },
    });
  });
}

// 数据库性能测试
function testDatabasePerformance(token) {
  group('数据库性能测试', () => {
    // 用户数据查询
    const userResponse = http.get(`${BASE_URL}/api/users/profile`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    // 健康数据查询
    const healthDataResponse = http.get(`${BASE_URL}/api/health-data/recent`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    // 诊断历史查询
    const diagnosisResponse = http.get(`${BASE_URL}/api/diagnosis/history`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    check(userResponse, {
      '用户数据查询成功': (r) => r.status === 200,
      '用户数据查询响应时间': (r) => r.timings.duration < 1000,
    });

    check(healthDataResponse, {
      '健康数据查询成功': (r) => r.status === 200,
      '健康数据查询响应时间': (r) => r.timings.duration < 2000,
    });

    check(diagnosisResponse, {
      '诊断历史查询成功': (r) => r.status === 200,
      '诊断历史查询响应时间': (r) => r.timings.duration < 1500,
    });
  });
}

// 并发用户模拟
function simulateConcurrentUsers(token) {
  concurrentUsers.add(1);
  
  // 随机选择测试场景
  const scenarios = [
    () => testXiaoAi(token),
    () => testXiaoKe(token),
    () => testLaoKe(token),
    () => testSoer(token),
    () => testDatabasePerformance(token),
  ];

  // 20%概率进行协作测试
  if (Math.random() < 0.2) {
    testAgentCollaboration(token);
  } else {
    const scenario = scenarios[randomIntBetween(0, scenarios.length - 1)];
    scenario();
  }
}

// 主测试函数
export default function () {
  // 每10个用户进行一次健康检查
  if (__VU % 10 === 1) {
    healthCheck();
  }

  // 获取认证令牌
  const token = getAuthToken();
  
  if (!token) {
    errorRate.add(1);
    return;
  }

  // 模拟并发用户行为
  simulateConcurrentUsers(token);

  // 用户思考时间
  sleep(randomIntBetween(1, 3));
}

// 测试结束后的清理
export function teardown(data) {
  console.log('性能测试完成');
  console.log(`总错误率: ${errorRate.rate * 100}%`);
  console.log(`平均智能体响应时间: ${agentResponseTime.avg}ms`);
  console.log(`平均协作响应时间: ${collaborationTime.avg}ms`);
} 