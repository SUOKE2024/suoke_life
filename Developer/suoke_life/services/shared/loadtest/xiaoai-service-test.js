import { check, sleep, group } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import * as config from './k6-config.js';

// 自定义指标
export const aiResponseTime = new Trend('ai_response_time');
export const aiErrorRate = new Rate('ai_errors');
export const aiRequests = new Counter('ai_requests');
export const aiTokenUsage = new Trend('ai_token_usage');

// 测试数据 - 模拟用户不同类型的问题
const SAMPLE_QUERIES = [
  { type: '健康咨询', text: '我最近睡眠质量不好，该怎么调理？' },
  { type: '体质辨识', text: '我经常手脚冰凉，容易疲劳，可能是什么体质？' },
  { type: '饮食指导', text: '春季养生应该吃什么食物？' },
  { type: '穴位按摩', text: '有哪些穴位按摩可以缓解头痛？' },
  { type: '运动推荐', text: '哪些运动适合脾胃虚弱的人？' },
  { type: '节气养生', text: '立夏时节如何养生？' },
  { type: '心理健康', text: '工作压力大导致焦虑，有什么中医调理方法？' },
  { type: '中药咨询', text: '枸杞子有什么功效和作用？' },
  { type: '生活习惯', text: '中医角度看，早上几点起床最健康？' },
  { type: '亚健康', text: '我总是容易疲劳，注意力不集中，是什么原因？' }
];

// 服务配置
const API_BASE_URL = __ENV.XIAOAI_SERVICE_URL || 'http://localhost:8040';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

// 导出测试选项
export const options = {
  scenarios: config.scenarios,
  thresholds: {
    'ai_response_time': [
      { threshold: 'p90<5000', abortOnFail: true }, // 90%的响应不超过5秒
      { threshold: 'p95<8000', abortOnFail: true }, // 95%的响应不超过8秒
    ],
    'ai_errors': [
      { threshold: 'rate<0.03', abortOnFail: true }, // 错误率不超过3%
    ],
    'http_req_duration': [
      { threshold: 'p95<10000', abortOnFail: true }, // 考虑到AI生成可能需要更长时间
    ],
  },
};

export function setup() {
  console.log(`开始小艾服务负载测试，基础URL: ${API_BASE_URL}`);
  
  // 验证API可访问性
  const checkRes = http.get(`${API_BASE_URL}/health`);
  if (checkRes.status !== 200) {
    console.error(`小艾服务健康检查失败: ${checkRes.status}`);
  }
  
  return { startTime: new Date().toISOString() };
}

export default function() {
  const queryData = randomItem(SAMPLE_QUERIES);
  
  group(`小艾AI对话测试 - ${queryData.type}`, () => {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${AUTH_TOKEN}`,
    };
    
    const conversationId = `test-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    const payload = JSON.stringify({
      message: queryData.text,
      conversation_id: conversationId,
      user_id: 'load-test-user',
      session_data: {
        context: '用户健康咨询',
        query_type: queryData.type
      }
    });
    
    // 记录请求数
    aiRequests.add(1);
    
    // 发送AI对话请求
    const startTime = new Date().getTime();
    const response = http.post(`${API_BASE_URL}/api/v1/chat`, payload, {
      headers: headers,
      timeout: '60s' // 考虑到AI生成可能需要更长时间
    });
    const endTime = new Date().getTime();
    
    // 记录响应时间
    aiResponseTime.add(endTime - startTime);
    
    // 检查响应状态和内容
    const success = check(response, {
      'AI响应成功': (r) => r.status === 200,
      'AI返回JSON': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
      'AI回复不为空': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.response && data.response.length > 0;
        } catch (e) {
          return false;
        }
      },
    });
    
    // 记录错误率
    if (!success) {
      aiErrorRate.add(1);
      console.error(`AI响应失败: ${response.status}, 查询: "${queryData.text}"`);
    } else {
      // 记录token使用情况（如果API返回了这一数据）
      try {
        const data = JSON.parse(response.body);
        if (data.token_usage) {
          aiTokenUsage.add(data.token_usage.total);
        }
      } catch (e) {
        // 忽略解析错误
      }
    }
    
    // 模拟用户阅读回复的时间
    sleep(Math.random() * 10 + 5); // 5-15秒随机间隔，模拟真实用户阅读AI回复的时间
  });
  
  // 测试健康养生推荐API
  group('健康养生推荐测试', () => {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${AUTH_TOKEN}`,
    };
    
    const payload = JSON.stringify({
      user_id: 'load-test-user',
      health_concerns: ['睡眠', '压力', '消化'],
      constitution_type: '气虚质'
    });
    
    const response = http.post(`${API_BASE_URL}/api/v1/health-recommendations`, payload, {
      headers: headers
    });
    
    check(response, {
      '推荐响应成功': (r) => r.status === 200,
      '推荐内容有效': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.recommendations && data.recommendations.length > 0;
        } catch (e) {
          return false;
        }
      },
    });
    
    sleep(Math.random() * 3 + 2); // 2-5秒随机间隔
  });
}

export function teardown(data) {
  console.log(`小艾服务负载测试完成，开始时间: ${data.startTime}, 结束时间: ${new Date().toISOString()}`);
}