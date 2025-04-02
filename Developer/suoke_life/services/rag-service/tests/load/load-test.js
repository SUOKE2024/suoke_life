import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// 定义测试指标
const errors = new Counter('errors');
const ragQueryDuration = new Trend('rag_query_duration', true);
const ragSuccessRate = new Rate('rag_success_rate');

// 测试配置
export const options = {
  scenarios: {
    // 常规负载测试
    average_load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 20 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '30s',
    },
    // 峰值负载测试
    peak_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 30 },
        { duration: '1m', target: 30 },
        { duration: '10s', target: 0 },
      ],
      gracefulRampDown: '30s',
      startTime: '3m',
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<1000'], // 95%的请求必须在1秒内完成
    'http_req_failed': ['rate<0.05'],    // 错误率必须低于5%
    'rag_query_duration': ['p(95)<2000'], // 95%的RAG查询必须在2秒内完成
    'rag_success_rate': ['rate>0.95'],   // RAG查询成功率必须高于95%
  },
};

// 测试数据 - 中医相关查询示例
const testQueries = [
  { query: "什么是阴阳五行理论？", context: "中医基础理论" },
  { query: "请介绍一下望闻问切四诊法", context: "中医诊断方法" },
  { query: "太阳体质的主要特征是什么？", context: "中医体质分类" },
  { query: "白术有什么功效？", context: "中药学" },
  { query: "针灸如何治疗头痛？", context: "针灸治疗" },
  { query: "中医如何调理失眠？", context: "中医治疗" },
  { query: "春季养生应注意什么？", context: "季节养生" },
  { query: "湿热体质应该如何饮食？", context: "体质养生" },
  { query: "足三里穴位的作用和位置", context: "经络穴位" },
  { query: "如何辨别舌苔的健康状况？", context: "舌诊" }
];

// 测试执行主函数
export default function() {
  // 随机选择一个查询
  const testCase = randomItem(testQueries);
  
  // 准备请求数据
  const payload = JSON.stringify({
    query: testCase.query,
    context: testCase.context,
    max_tokens: 1000,
    temperature: 0.7
  });
  
  // 设置请求头
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-api-key'
    },
  };
  
  // 发送请求到RAG服务
  const response = http.post('https://staging.api.suoke.life/rag/query', payload, params);
  
  // 记录查询耗时
  ragQueryDuration.add(response.timings.duration);
  
  // 检查响应结果
  const success = check(response, {
    'Status is 200': (r) => r.status === 200,
    'Response has answer': (r) => r.json().hasOwnProperty('answer'),
    'Response has sources': (r) => r.json().hasOwnProperty('sources'),
    'Response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  // 记录成功率
  ragSuccessRate.add(success);
  
  // 如果失败，增加错误计数
  if (!success) {
    errors.add(1);
    console.log(`查询失败: ${testCase.query} - 状态码: ${response.status} - 响应: ${response.body}`);
  }
  
  // 请求间隔，模拟真实用户行为
  sleep(1);
}