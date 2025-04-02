#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { program } from 'commander';
import Table from 'cli-table';
import { performance } from 'perf_hooks';

// 默认配置
const DEFAULT_CONFIG = {
  apiBaseUrl: 'http://localhost:4000/api',
  iterations: 10,
  concurrency: 5,
  endpoints: [
    {
      name: 'Knowledge Search',
      method: 'GET',
      path: '/knowledge/search?query=维生素',
      payload: null
    },
    {
      name: 'Agent Query',
      method: 'POST',
      path: '/agents/default/query',
      payload: {
        query: '中医如何看待维生素D与骨骼健康的关系？',
        userId: 'benchmark-user'
      }
    },
    {
      name: 'Analyze Query',
      method: 'POST',
      path: '/coordination/analyze',
      payload: {
        query: '维生素D的作用是什么？',
        userId: 'benchmark-user',
        sessionId: 'benchmark-session'
      }
    }
  ],
  outputDir: path.resolve(process.cwd(), 'benchmark-results'),
  threshold: {
    p50: 500,  // 毫秒
    p90: 800,  // 毫秒
    p95: 1000  // 毫秒
  }
};

// 性能测试结果接口
interface EndpointResult {
  name: string;
  method: string;
  path: string;
  iterations: number;
  success: number;
  failed: number;
  min: number;
  max: number;
  mean: number;
  median: number;
  p90: number;
  p95: number;
  p99: number;
  timestamp: string;
}

// 计算百分位数
function percentile(values: number[], p: number) {
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * p;
  const base = Math.floor(pos);
  const rest = pos - base;
  
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  } else {
    return sorted[base];
  }
}

// 测试单个端点
async function testEndpoint(config: any, endpoint: any, authToken?: string): Promise<EndpointResult> {
  console.log(`测试端点: ${endpoint.name} (${endpoint.method} ${endpoint.path})`);
  
  const responseTimes: number[] = [];
  const axiosConfig: any = {
    method: endpoint.method,
    url: `${config.apiBaseUrl}${endpoint.path}`,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  // 如果提供了认证令牌，添加到请求头
  if (authToken) {
    axiosConfig.headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  // 添加请求负载（如果有）
  if (endpoint.payload && endpoint.method !== 'GET') {
    axiosConfig.data = endpoint.payload;
  }
  
  let successCount = 0;
  let failureCount = 0;
  
  // 控制并发
  const batchSize = config.concurrency;
  const iterations = config.iterations;
  
  for (let i = 0; i < iterations; i += batchSize) {
    const batch = Math.min(batchSize, iterations - i);
    const requests = Array(batch).fill(0).map(() => {
      return (async () => {
        try {
          const start = performance.now();
          const response = await axios(axiosConfig);
          const end = performance.now();
          const duration = end - start;
          
          responseTimes.push(duration);
          successCount++;
          
          return { success: true, duration };
        } catch (error) {
          failureCount++;
          return { success: false, error };
        }
      })();
    });
    
    await Promise.all(requests);
    
    // 进度显示
    const progress = Math.min(100, Math.round(((i + batch) / iterations) * 100));
    process.stdout.write(`\r进度: ${progress}% (${i + batch}/${iterations})`);
  }
  
  console.log('\n');
  
  // 如果没有成功的请求，返回错误结果
  if (responseTimes.length === 0) {
    return {
      name: endpoint.name,
      method: endpoint.method,
      path: endpoint.path,
      iterations: config.iterations,
      success: successCount,
      failed: failureCount,
      min: 0,
      max: 0,
      mean: 0,
      median: 0,
      p90: 0,
      p95: 0,
      p99: 0,
      timestamp: new Date().toISOString()
    };
  }
  
  // 计算统计数据
  const min = Math.min(...responseTimes);
  const max = Math.max(...responseTimes);
  const mean = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
  const median = percentile(responseTimes, 0.5);
  const p90 = percentile(responseTimes, 0.9);
  const p95 = percentile(responseTimes, 0.95);
  const p99 = percentile(responseTimes, 0.99);
  
  return {
    name: endpoint.name,
    method: endpoint.method,
    path: endpoint.path,
    iterations: config.iterations,
    success: successCount,
    failed: failureCount,
    min,
    max,
    mean,
    median,
    p90,
    p95,
    p99,
    timestamp: new Date().toISOString()
  };
}

// 格式化持续时间
function formatDuration(ms: number): string {
  return ms.toFixed(2) + 'ms';
}

// 显示结果表格
function displayResults(results: EndpointResult[]): void {
  const table = new Table({
    head: ['端点', '成功/总计', '最小', '最大', '平均', '中值', 'p90', 'p95', 'p99'],
    colWidths: [20, 15, 10, 10, 10, 10, 10, 10, 10]
  });
  
  results.forEach(result => {
    table.push([
      result.name,
      `${result.success}/${result.iterations}`,
      formatDuration(result.min),
      formatDuration(result.max),
      formatDuration(result.mean),
      formatDuration(result.median),
      formatDuration(result.p90),
      formatDuration(result.p95),
      formatDuration(result.p99)
    ]);
  });
  
  console.log(table.toString());
}

// 保存结果到JSON文件
function saveResults(results: EndpointResult[], outputDir: string): string {
  // 确保输出目录存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(outputDir, `benchmark-${timestamp}.json`);
  
  fs.writeFileSync(outputFile, JSON.stringify({
    results,
    timestamp,
    totalEndpoints: results.length,
    totalSuccess: results.reduce((sum, r) => sum + r.success, 0),
    totalFailures: results.reduce((sum, r) => sum + r.failed, 0)
  }, null, 2));
  
  return outputFile;
}

// 比较当前结果与基准
function compareWithBaseline(results: EndpointResult[], baselineFile: string): void {
  if (!fs.existsSync(baselineFile)) {
    console.log(`基准文件不存在: ${baselineFile}`);
    return;
  }
  
  try {
    const baseline = JSON.parse(fs.readFileSync(baselineFile, 'utf8'));
    
    console.log('\n==== 性能与基准比较 ====');
    const table = new Table({
      head: ['端点', '指标', '当前', '基准', '差异', '变化%'],
      colWidths: [20, 8, 12, 12, 12, 12]
    });
    
    results.forEach(result => {
      const baselineResult = baseline.results.find((b: any) => b.name === result.name);
      if (!baselineResult) {
        console.log(`基准中没有端点: ${result.name}`);
        return;
      }
      
      // 比较关键指标
      const metrics = [
        { name: 'p50', current: result.median, baseline: baselineResult.median },
        { name: 'p90', current: result.p90, baseline: baselineResult.p90 },
        { name: 'p95', current: result.p95, baseline: baselineResult.p95 }
      ];
      
      metrics.forEach(metric => {
        const diff = metric.current - metric.baseline;
        const pctChange = (metric.baseline === 0)
          ? 'N/A'
          : ((diff / metric.baseline) * 100).toFixed(2) + '%';
        
        // 为性能下降添加颜色标记
        const changeColor = (diff > 0) ? '\x1b[31m' : '\x1b[32m';
        const resetColor = '\x1b[0m';
        
        table.push([
          metric === metrics[0] ? result.name : '',
          metric.name,
          formatDuration(metric.current),
          formatDuration(metric.baseline),
          `${changeColor}${diff > 0 ? '+' : ''}${formatDuration(diff)}${resetColor}`,
          `${changeColor}${diff > 0 ? '+' : ''}${pctChange}${resetColor}`
        ]);
      });
    });
    
    console.log(table.toString());
  } catch (error) {
    console.error(`读取或解析基准文件时出错: ${error}`);
  }
}

// 创建或更新基准文件
function updateBaseline(results: EndpointResult[], baselineFile: string): void {
  const baselineData = {
    results,
    timestamp: new Date().toISOString(),
    updatedBy: process.env.USER || 'benchmark-tool'
  };
  
  const baselineDir = path.dirname(baselineFile);
  if (!fs.existsSync(baselineDir)) {
    fs.mkdirSync(baselineDir, { recursive: true });
  }
  
  fs.writeFileSync(baselineFile, JSON.stringify(baselineData, null, 2));
  console.log(`基准已更新: ${baselineFile}`);
}

// 检查性能是否符合阈值
function checkPerformanceThresholds(results: EndpointResult[], thresholds: any): boolean {
  let allPassed = true;
  
  console.log('\n==== 性能阈值检查 ====');
  const table = new Table({
    head: ['端点', '指标', '当前值', '阈值', '结果'],
    colWidths: [20, 8, 12, 12, 10]
  });
  
  results.forEach(result => {
    // 检查关键指标
    const checks = [
      { name: 'p50', value: result.median, threshold: thresholds.p50 },
      { name: 'p90', value: result.p90, threshold: thresholds.p90 },
      { name: 'p95', value: result.p95, threshold: thresholds.p95 }
    ];
    
    checks.forEach(check => {
      const passed = check.value <= check.threshold;
      allPassed = allPassed && passed;
      
      const resultColor = passed ? '\x1b[32m' : '\x1b[31m';
      const resetColor = '\x1b[0m';
      
      table.push([
        check === checks[0] ? result.name : '',
        check.name,
        formatDuration(check.value),
        formatDuration(check.threshold),
        `${resultColor}${passed ? '通过' : '失败'}${resetColor}`
      ]);
    });
  });
  
  console.log(table.toString());
  return allPassed;
}

// 主函数
async function main() {
  // 配置命令行参数
  program
    .description('API性能基准测试工具')
    .option('-c, --config <path>', '配置文件路径')
    .option('-u, --url <url>', 'API基础URL')
    .option('-i, --iterations <number>', '每个端点的迭代次数', parseInt)
    .option('-n, --concurrency <number>', '并发请求数', parseInt)
    .option('-o, --output <dir>', '结果输出目录')
    .option('-b, --baseline <path>', '基准文件路径')
    .option('-s, --set-baseline', '将当前结果设置为新基准')
    .option('-t, --token <token>', 'API认证令牌')
    .parse(process.argv);
  
  const options = program.opts();
  
  // 读取配置文件（如果指定）
  let config = { ...DEFAULT_CONFIG };
  if (options.config) {
    try {
      const configFile = path.resolve(process.cwd(), options.config);
      const fileConfig = JSON.parse(fs.readFileSync(configFile, 'utf8'));
      config = { ...config, ...fileConfig };
    } catch (error) {
      console.error(`读取配置文件失败: ${error}`);
      process.exit(1);
    }
  }
  
  // 应用命令行选项覆盖配置
  if (options.url) config.apiBaseUrl = options.url;
  if (options.iterations) config.iterations = options.iterations;
  if (options.concurrency) config.concurrency = options.concurrency;
  if (options.output) config.outputDir = options.output;
  
  // 确定基准文件路径
  const baselineFile = options.baseline || path.join(config.outputDir, 'baseline.json');
  
  console.log(`开始性能基准测试 - ${config.apiBaseUrl}`);
  console.log(`每个端点 ${config.iterations} 次请求，并发 ${config.concurrency}`);
  
  // 运行所有端点的测试
  const results: EndpointResult[] = [];
  for (const endpoint of config.endpoints) {
    const result = await testEndpoint(config, endpoint, options.token);
    results.push(result);
  }
  
  // 显示结果
  console.log('\n==== 性能测试结果 ====');
  displayResults(results);
  
  // 保存结果
  const outputFile = saveResults(results, config.outputDir);
  console.log(`\n结果已保存到: ${outputFile}`);
  
  // 与基准比较
  compareWithBaseline(results, baselineFile);
  
  // 检查性能阈值
  const thresholdsPassed = checkPerformanceThresholds(results, config.threshold);
  
  // 可选：设置当前结果为新基准
  if (options.setBaseline) {
    updateBaseline(results, baselineFile);
  }
  
  // 返回适当的退出代码
  process.exit(thresholdsPassed ? 0 : 1);
}

// 执行主函数
main().catch(error => {
  console.error('基准测试失败:', error);
  process.exit(1);
}); 