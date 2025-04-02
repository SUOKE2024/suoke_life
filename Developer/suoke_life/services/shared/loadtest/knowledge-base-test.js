import { check, sleep, group } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import * as config from './k6-config.js';

// 自定义指标
export const documentFetchDuration = new Trend('document_fetch_duration');
export const searchDuration = new Trend('search_duration');
export const errorRate = new Rate('kb_errors');
export const documentRequests = new Counter('document_requests');
export const searchRequests = new Counter('search_requests');

// 测试数据 - 模拟各种中医文档ID
const SAMPLE_DOCUMENT_IDS = [
  'tcm-herbology-001',
  'tcm-diagnosis-002',
  'tcm-acupuncture-003',
  'tcm-massage-004',
  'tcm-qigong-005',
  'tcm-diet-therapy-006',
  'tcm-classic-texts-007',
  'tcm-case-studies-008',
  'tcm-meridians-009',
  'tcm-constitution-types-010'
];

// 测试搜索关键词
const SEARCH_TERMS = [
  '肝火旺',
  '补气血',
  '艾灸穴位',
  '中医养生',
  '脾胃虚弱',
  '经络不通',
  '太极养生',
  '春季养生',
  '舌诊特点',
  '望闻问切'
];

// 服务配置
const API_BASE_URL = __ENV.KB_SERVICE_URL || 'http://localhost:8010';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token';

// 导出测试选项
export const options = {
  scenarios: config.scenarios,
  thresholds: {
    'document_fetch_duration': [
      { threshold: 'p95<1000', abortOnFail: true }, // 95%的文档获取响应时间不超过1秒
      { threshold: 'p99<2000', abortOnFail: true }, // 99%的文档获取响应时间不超过2秒
    ],
    'search_duration': [
      { threshold: 'p95<2000', abortOnFail: true }, // 95%的搜索响应时间不超过2秒
      { threshold: 'p99<4000', abortOnFail: true }, // 99%的搜索响应时间不超过4秒
    ],
    'kb_errors': [
      { threshold: 'rate<0.05', abortOnFail: true }, // 错误率不超过5%
    ],
    'http_req_duration': [
      { threshold: 'p95<2000', abortOnFail: true },
    ],
  },
};

export function setup() {
  console.log(`开始知识库服务负载测试，基础URL: ${API_BASE_URL}`);
  
  // 验证API可访问性
  const checkRes = http.get(`${API_BASE_URL}/health`);
  if (checkRes.status !== 200) {
    console.error(`知识库服务健康检查失败: ${checkRes.status}`);
  }
  
  return { startTime: new Date().toISOString() };
}

export default function() {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AUTH_TOKEN}`,
  };
  
  // 随机选择测试场景：60%搜索请求，40%文档获取
  const scenario = Math.random() < 0.6 ? 'search' : 'document';
  
  if (scenario === 'search') {
    // 搜索场景
    group('知识库搜索测试', () => {
      const searchTerm = randomItem(SEARCH_TERMS);
      
      const payload = JSON.stringify({
        query: searchTerm,
        limit: 10,
        offset: 0,
        filters: {
          categories: ['中医理论', '中医诊断', '养生保健'],
          date_range: {
            start: null,
            end: null
          }
        }
      });
      
      // 记录搜索请求数
      searchRequests.add(1);
      
      const response = http.post(`${API_BASE_URL}/api/v1/search`, payload, {
        headers: headers,
      });
      
      // 记录搜索时间
      searchDuration.add(response.timings.duration);
      
      // 检查响应状态
      const success = check(response, {
        '搜索请求成功': (r) => r.status === 200,
        '返回JSON格式': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
        '搜索结果有效': (r) => {
          try {
            const data = JSON.parse(r.body);
            return data.results && Array.isArray(data.results);
          } catch (e) {
            return false;
          }
        },
        '结果分页信息存在': (r) => {
          try {
            const data = JSON.parse(r.body);
            return data.pagination && typeof data.pagination.total_count === 'number';
          } catch (e) {
            return false;
          }
        }
      });
      
      if (!success) {
        errorRate.add(1);
        console.error(`知识库搜索失败: ${response.status}, 搜索词: "${searchTerm}"`);
      }
      
      // 模拟用户浏览搜索结果时间
      sleep(Math.random() * 3 + 2); // 2-5秒随机间隔
    });
  } else {
    // 文档获取场景
    group('知识库文档获取测试', () => {
      const documentId = randomItem(SAMPLE_DOCUMENT_IDS);
      
      // 记录文档请求数
      documentRequests.add(1);
      
      const response = http.get(`${API_BASE_URL}/api/v1/documents/${documentId}`, {
        headers: headers,
      });
      
      // 记录文档获取时间
      documentFetchDuration.add(response.timings.duration);
      
      // 检查响应状态
      const success = check(response, {
        '文档获取成功': (r) => r.status === 200,
        '返回JSON格式': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
        '文档内容存在': (r) => {
          try {
            const data = JSON.parse(r.body);
            return data.document && data.document.content && data.document.title;
          } catch (e) {
            return false;
          }
        }
      });
      
      if (!success) {
        errorRate.add(1);
        console.error(`文档获取失败: ${response.status}, 文档ID: "${documentId}"`);
      }
      
      // 模拟用户阅读文档时间
      sleep(Math.random() * 15 + 10); // 10-25秒随机间隔，模拟用户阅读文档
    });
  }
  
  // 模拟批量操作场景
  if (Math.random() < 0.1) { // 10%概率执行批量操作测试
    group('批量文档操作测试', () => {
      const batchSize = Math.floor(Math.random() * 3) + 3; // 3-5个文档
      const documentIds = [];
      
      for (let i = 0; i < batchSize; i++) {
        documentIds.push(randomItem(SAMPLE_DOCUMENT_IDS));
      }
      
      const payload = JSON.stringify({
        document_ids: documentIds
      });
      
      const response = http.post(`${API_BASE_URL}/api/v1/documents/batch`, payload, {
        headers: headers,
      });
      
      check(response, {
        '批量操作成功': (r) => r.status === 200,
        '批量结果有效': (r) => {
          try {
            const data = JSON.parse(r.body);
            return data.results && data.results.length === documentIds.length;
          } catch (e) {
            return false;
          }
        }
      });
      
      sleep(Math.random() * 2 + 1); // 1-3秒随机间隔
    });
  }
}

export function teardown(data) {
  console.log(`知识库服务负载测试完成，开始时间: ${data.startTime}, 结束时间: ${new Date().toISOString()}`);
}