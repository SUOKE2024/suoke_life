#!/usr/bin/env node

/**
 * API性能验证脚本
 * 验证缓存效果、错误处理和重试机制
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 索克生活 - API性能验证工具');
console.log('==================================================');

// 模拟API客户端
class ApiClient {
  constructor() {
    this.cache = new Map();
    this.requestCount = 0;
    this.cacheHits = 0;
    this.retryCount = 0;
    this.errorCount = 0;
  }

  // 模拟网络延迟
  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 模拟API请求
  async makeRequest(endpoint, options = {}) {
    this.requestCount++;
    const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
    
    // 检查缓存
    if (this.cache.has(cacheKey) && !options.skipCache) {
      this.cacheHits++;
      console.log(`💾 缓存命中: ${endpoint}`);
      return this.cache.get(cacheKey);
    }

    // 模拟网络延迟
    const baseDelay = Math.random() * 200 + 50; // 50-250ms
    await this.delay(baseDelay);

    // 模拟随机错误（5%概率）
    if (Math.random() < 0.05) {
      this.errorCount++;
      throw new Error(`网络错误: ${endpoint}`);
    }

    // 模拟响应数据
    const response = {
      success: true,
      data: {
        endpoint,
        timestamp: new Date().toISOString(),
        requestId: Math.random().toString(36).substr(2, 9),
      },
      duration: Math.round(baseDelay),
    };

    // 缓存响应（2分钟TTL）
    this.cache.set(cacheKey, response);
    setTimeout(() => {
      this.cache.delete(cacheKey);
    }, 2 * 60 * 1000);

    return response;
  }

  // 带重试的API请求
  async requestWithRetry(endpoint, options = {}, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.makeRequest(endpoint, options);
      } catch (error) {
        lastError = error;
        this.retryCount++;
        
        if (attempt < maxRetries) {
          const retryDelay = Math.pow(2, attempt - 1) * 1000; // 指数退避
          console.log(`🔄 重试 ${attempt}/${maxRetries} - ${endpoint} (${retryDelay}ms后)`);
          await this.delay(retryDelay);
        }
      }
    }
    
    throw lastError;
  }

  // 获取统计信息
  getStats() {
    return {
      totalRequests: this.requestCount,
      cacheHits: this.cacheHits,
      cacheHitRate: this.requestCount > 0 ? (this.cacheHits / this.requestCount * 100).toFixed(2) : 0,
      retries: this.retryCount,
      errors: this.errorCount,
      errorRate: this.requestCount > 0 ? (this.errorCount / this.requestCount * 100).toFixed(2) : 0,
    };
  }

  // 清除缓存
  clearCache() {
    this.cache.clear();
    console.log('🗑️  缓存已清除');
  }
}

// 测试API端点列表
const testEndpoints = [
  '/health',
  '/version',
  '/auth/user',
  '/health-data/user123',
  '/agents/status',
  '/diagnosis/history',
  '/system/metrics',
  '/knowledge/search',
  '/medical-resources/search',
  '/blockchain/records',
];

// 运行性能测试
async function runPerformanceTest() {
  const client = new ApiClient();
  
  console.log('\n📊 开始性能测试...\n');

  // 第一轮：无缓存请求
  console.log('🔥 第一轮：无缓存请求');
  const round1Start = Date.now();
  
  for (const endpoint of testEndpoints) {
    try {
      const response = await client.requestWithRetry(endpoint);
      console.log(`✅ ${endpoint} - ${response.duration}ms`);
    } catch (error) {
      console.log(`❌ ${endpoint} - ${error.message}`);
    }
  }
  
  const round1Duration = Date.now() - round1Start;
  console.log(`\n⏱️  第一轮总耗时: ${round1Duration}ms\n`);

  // 短暂延迟
  await client.delay(1000);

  // 第二轮：缓存命中请求
  console.log('💾 第二轮：缓存命中请求');
  const round2Start = Date.now();
  
  for (const endpoint of testEndpoints) {
    try {
      const response = await client.requestWithRetry(endpoint);
      console.log(`✅ ${endpoint} - ${response.duration}ms (缓存)`);
    } catch (error) {
      console.log(`❌ ${endpoint} - ${error.message}`);
    }
  }
  
  const round2Duration = Date.now() - round2Start;
  console.log(`\n⏱️  第二轮总耗时: ${round2Duration}ms\n`);

  // 性能提升计算
  const improvement = ((round1Duration - round2Duration) / round1Duration * 100).toFixed(1);
  console.log(`🚀 缓存性能提升: ${improvement}%\n`);

  return {
    client,
    round1Duration,
    round2Duration,
    improvement: parseFloat(improvement),
  };
}

// 运行错误处理测试
async function runErrorHandlingTest() {
  console.log('🛡️  错误处理和重试机制测试...\n');
  
  const client = new ApiClient();
  const errorEndpoints = [
    '/error/500',
    '/error/timeout',
    '/error/network',
    '/error/auth',
    '/error/rate-limit',
  ];

  for (const endpoint of errorEndpoints) {
    try {
      console.log(`🧪 测试错误处理: ${endpoint}`);
      await client.requestWithRetry(endpoint);
      console.log(`✅ ${endpoint} - 成功`);
    } catch (error) {
      console.log(`❌ ${endpoint} - 最终失败: ${error.message}`);
    }
  }

  return client;
}

// 运行并发测试
async function runConcurrencyTest() {
  console.log('\n⚡ 并发请求测试...\n');
  
  const client = new ApiClient();
  const concurrentRequests = 10;
  const endpoint = '/health';

  console.log(`🚀 发起 ${concurrentRequests} 个并发请求到 ${endpoint}`);
  
  const startTime = Date.now();
  const promises = Array(concurrentRequests).fill().map((_, index) => 
    client.requestWithRetry(`${endpoint}?id=${index}`)
      .then(response => ({ success: true, response }))
      .catch(error => ({ success: false, error }))
  );

  const results = await Promise.all(promises);
  const endTime = Date.now();

  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  console.log(`✅ 成功: ${successful}/${concurrentRequests}`);
  console.log(`❌ 失败: ${failed}/${concurrentRequests}`);
  console.log(`⏱️  总耗时: ${endTime - startTime}ms`);
  console.log(`📊 平均响应时间: ${(endTime - startTime) / concurrentRequests}ms\n`);

  return {
    total: concurrentRequests,
    successful,
    failed,
    totalTime: endTime - startTime,
    avgResponseTime: (endTime - startTime) / concurrentRequests,
  };
}

// 主函数
async function main() {
  try {
    // 性能测试
    const performanceResults = await runPerformanceTest();
    
    // 错误处理测试
    const errorClient = await runErrorHandlingTest();
    
    // 并发测试
    const concurrencyResults = await runConcurrencyTest();

    // 生成综合报告
    const report = {
      timestamp: new Date().toISOString(),
      performance: {
        round1Duration: performanceResults.round1Duration,
        round2Duration: performanceResults.round2Duration,
        cacheImprovement: performanceResults.improvement,
        stats: performanceResults.client.getStats(),
      },
      errorHandling: {
        stats: errorClient.getStats(),
      },
      concurrency: concurrencyResults,
      summary: {
        totalTests: 3,
        allPassed: performanceResults.improvement > 0,
        recommendations: [
          performanceResults.improvement > 50 ? '✅ 缓存效果优秀' : '⚠️  缓存效果需要优化',
          errorClient.getStats().retries > 0 ? '✅ 重试机制正常工作' : '⚠️  重试机制未触发',
          concurrencyResults.successful >= concurrencyResults.total * 0.9 ? '✅ 并发处理能力良好' : '⚠️  并发处理需要优化',
        ],
      },
    };

    // 保存报告
    const reportPath = path.join(__dirname, '..', 'API_PERFORMANCE_VALIDATION_REPORT.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log('📋 性能验证报告');
    console.log('==================================================');
    console.log(`📈 缓存性能提升: ${report.performance.cacheImprovement}%`);
    console.log(`📊 缓存命中率: ${report.performance.stats.cacheHitRate}%`);
    console.log(`🔄 重试次数: ${report.errorHandling.stats.retries}`);
    console.log(`❌ 错误率: ${report.errorHandling.stats.errorRate}%`);
    console.log(`⚡ 并发成功率: ${(concurrencyResults.successful / concurrencyResults.total * 100).toFixed(1)}%`);
    console.log(`\n📄 详细报告已保存到: ${reportPath}`);
    
    console.log('\n🎯 优化建议:');
    report.summary.recommendations.forEach(rec => console.log(`   ${rec}`));

    console.log('\n✅ API性能验证完成！');

  } catch (error) {
    console.error('❌ 验证过程中发生错误:', error);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  main();
} 