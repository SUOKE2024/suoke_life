import { check, sleep, group } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import * as config from './k6-config.js';

// 自定义指标
export const ragQueryDuration = new Trend('rag_query_duration');
export const ragErrorRate = new Rate('rag_errors');
export const ragQueries = new Counter('rag_queries');

// 测试数据
const SAMPLE_QUERIES = [
  '中医四诊法的主要内容是什么？',
  '肝火旺盛的症状有哪些？',
  '如何调理脾胃虚弱？',
  '舌苔发白是什么原因？',
  '针灸对失眠有效吗？',
  '艾灸的最佳时间是什么时候？',
  '中医如何看待高血压？',
  '食疗对改善体质有什么作用？',
  '节气养生有哪些注意事项？',
  '太极拳对健康有什么好处？'
];

// RAG服务API配置
const API_BASE_URL = __ENV.RAG_SERVICE_URL || 'http://localhost:8050';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

// 导出测试选项
export const options = {
  scenarios: config.scenarios,
  thresholds: {
    'rag_query_duration': [
      { threshold: 'p95<3000', abortOnFail: true }, // 95%的查询响应时间不超过3秒
      { threshold: 'p99<5000', abortOnFail: true }, // 99%的查询响应时间不超过5秒
    ],
    'rag_errors': [
      { threshold: 'rate<0.05', abortOnFail: true }, // 错误率不超过5%
    ],
    'http_req_duration': [
      { threshold: 'p95<3000', abortOnFail: true },
    ],
  },
};

// 设置函数 - 可以初始化测试数据或特定配置
export function setup() {
  console.log(`开始RAG服务负载测试，基础URL: ${API_BASE_URL}`);
  
  // 验证API可访问性
  const checkRes = http.get(`${API_BASE_URL}/health`);
  if (checkRes.status !== 200) {
    console.error(`RAG服务健康检查失败: ${checkRes.status}`);
  }
  
  return { startTime: new Date().toISOString() };
}

// 默认函数 - 主要测试逻辑
export default function() {
  // 随机选择一个查询
  const query = randomItem(SAMPLE_QUERIES);
  
  group('RAG查询测试', () => {
    // 准备请求头和请求体
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${AUTH_TOKEN}`,
    };
    
    const payload = JSON.stringify({
      query: query,
      max_results: 5,
      similarity_threshold: 0.7,
      include_sources: true,
    });
    
    // 记录查询次数
    ragQueries.add(1);
    
    // 发送查询请求
    const response = http.post(`${API_BASE_URL}/api/v1/query`, payload, {
      headers: headers,
    });
    
    // 记录查询时间
    ragQueryDuration.add(response.timings.duration);
    
    // 检查响应状态
    const success = check(response, {
      'RAG查询成功': (r) => r.status === 200,
      'RAG返回JSON': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
      '查询结果不为空': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.results && data.results.length > 0;
        } catch (e) {
          return false;
        }
      },
    });
    
    // 记录错误率
    if (!success) {
      ragErrorRate.add(1);
      console.error(`RAG查询失败: ${response.status}, 查询: "${query}"`);
    }
    
    // 模拟用户思考时间
    sleep(Math.random() * 3 + 1); // 1-4秒随机间隔
  });
  
  // 执行向量搜索测试
  group('向量搜索测试', () => {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${AUTH_TOKEN}`,
    };
    
    const payload = JSON.stringify({
      text: query,
      collection_name: 'suoke_knowledge',
      top_k: 3,
    });
    
    const response = http.post(`${API_BASE_URL}/api/v1/vector-search`, payload, {
      headers: headers,
    });
    
    check(response, {
      '向量搜索成功': (r) => r.status === 200,
      '向量结果有效': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.matches && data.matches.length > 0;
        } catch (e) {
          return false;
        }
      },
    });
    
    sleep(Math.random() * 2 + 0.5); // 0.5-2.5秒随机间隔
  });
}

// 清理函数 - 测试后清理
export function teardown(data) {
  console.log(`RAG服务负载测试完成，开始时间: ${data.startTime}, 结束时间: ${new Date().toISOString()}`);
  
  // 这里可以添加测试后的清理工作，例如删除测试数据
}