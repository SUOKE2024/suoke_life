/**
 * 知识图谱服务性能测试脚本
 * 
 * 本脚本用于测试知识图谱服务在不同查询负载下的性能表现
 * 包括节点检索、关系查询和路径分析等常见图谱操作
 */

const neo4j = require('neo4j-driver');
const fs = require('fs');

// 连接配置
const uri = process.env.NEO4J_URI || 'bolt://localhost:7687';
const user = process.env.NEO4J_USER || 'neo4j';
const password = process.env.NEO4J_PASSWORD || 'password';

// 测试配置
const ITERATIONS = 10;            // 每个查询重复次数
const WARM_UP_ITERATIONS = 2;     // 预热迭代次数
const CONCURRENT_QUERIES = 5;     // 并发查询数

// 创建Neo4j驱动实例
const driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {
  maxConnectionPoolSize: 50,
  connectionAcquisitionTimeout: 30000
});

// 测试查询集合
const queries = [
  {
    name: "节点检索-按类型",
    cypher: "MATCH (n:TCMConcept) RETURN n LIMIT 100"
  },
  {
    name: "节点检索-按属性",
    cypher: "MATCH (n:TCMConcept) WHERE n.name CONTAINS '脾' RETURN n LIMIT 50"
  },
  {
    name: "关系查询-直接关系",
    cypher: "MATCH (a:TCMSymptom)-[r:HAS_TREATMENT]->(b:TCMHerb) RETURN a, r, b LIMIT 100"
  },
  {
    name: "关系查询-多层关系",
    cypher: "MATCH (a:TCMDisease)-[:HAS_SYMPTOM]->(b:TCMSymptom)-[:HAS_TREATMENT]->(c:TCMHerb) RETURN a, b, c LIMIT 50"
  },
  {
    name: "路径分析-最短路径",
    cypher: "MATCH p=shortestPath((a:TCMConcept {name: '肝'})-[*..5]-(b:TCMConcept {name: '心'})) RETURN p"
  },
  {
    name: "高级查询-社区检测",
    cypher: "MATCH (n:TCMDisease)-[:HAS_SYMPTOM]->(s:TCMSymptom) WITH n, count(s) AS symptom_count WHERE symptom_count > 3 RETURN n, symptom_count ORDER BY symptom_count DESC LIMIT 10"
  },
  {
    name: "高级查询-相似度计算",
    cypher: "MATCH (a:TCMHerb)-[:HAS_PROPERTY]->(p:TCMProperty)<-[:HAS_PROPERTY]-(b:TCMHerb) WHERE a.name = '人参' AND a <> b WITH b, count(p) AS common_properties RETURN b.name, common_properties ORDER BY common_properties DESC LIMIT 10"
  },
  {
    name: "统计查询-关系分布",
    cypher: "MATCH ()-[r]->() RETURN type(r) AS relation_type, count(r) AS count ORDER BY count DESC"
  },
  {
    name: "复杂查询-递归关系",
    cypher: "MATCH path = (herb:TCMHerb {name: '人参'})-[:TREATS*1..3]->(disease:TCMDisease) RETURN path LIMIT 10"
  },
  {
    name: "读写查询-临时节点",
    cypher: "CREATE (n:TestNode {name: 'test', created: timestamp()}) SET n.processed = true RETURN n"
  }
];

// 清理函数
async function cleanup() {
  const session = driver.session();
  try {
    await session.run("MATCH (n:TestNode) DETACH DELETE n");
  } finally {
    await session.close();
  }
}

// 运行单个查询测试
async function runQueryTest(query, iteration) {
  const session = driver.session();
  const startTime = process.hrtime();
  
  try {
    const result = await session.run(query.cypher);
    const endTime = process.hrtime(startTime);
    const duration = endTime[0] * 1000 + endTime[1] / 1000000; // 转换为毫秒
    
    return {
      query: query.name,
      iteration: iteration,
      duration: duration,
      records: result.records.length,
      success: true
    };
  } catch (error) {
    const endTime = process.hrtime(startTime);
    const duration = endTime[0] * 1000 + endTime[1] / 1000000;
    
    return {
      query: query.name,
      iteration: iteration,
      duration: duration,
      error: error.message,
      success: false
    };
  } finally {
    await session.close();
  }
}

// 运行并发查询测试
async function runConcurrentTest(query) {
  const promises = [];
  for (let i = 0; i < CONCURRENT_QUERIES; i++) {
    promises.push(runQueryTest(query, i));
  }
  return Promise.all(promises);
}

// 主测试函数
async function runPerformanceTests() {
  console.log("开始知识图谱性能测试...");
  
  const results = [];
  const summaries = {};
  
  // 预热阶段
  console.log("执行预热查询...");
  for (const query of queries) {
    for (let i = 0; i < WARM_UP_ITERATIONS; i++) {
      await runQueryTest(query, -i-1); // 使用负数表示预热迭代
    }
  }
  
  // 顺序测试阶段
  console.log("执行顺序查询测试...");
  for (const query of queries) {
    console.log(`测试查询: ${query.name}`);
    
    const queryResults = [];
    for (let i = 0; i < ITERATIONS; i++) {
      const result = await runQueryTest(query, i);
      queryResults.push(result);
      process.stdout.write(".");
    }
    process.stdout.write("\n");
    
    results.push(...queryResults);
    
    // 计算统计数据
    const durations = queryResults.filter(r => r.success).map(r => r.duration);
    const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const successRate = (queryResults.filter(r => r.success).length / queryResults.length) * 100;
    
    summaries[query.name] = {
      averageDuration: avgDuration,
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      p95Duration: calculatePercentile(durations, 95),
      successRate: successRate
    };
  }
  
  // 并发测试阶段
  console.log("执行并发查询测试...");
  for (const query of queries) {
    console.log(`并发测试查询: ${query.name}`);
    const concurrentResults = await runConcurrentTest(query);
    
    results.push(...concurrentResults);
    
    // 计算并发统计数据
    const durations = concurrentResults.filter(r => r.success).map(r => r.duration);
    const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const successRate = (concurrentResults.filter(r => r.success).length / concurrentResults.length) * 100;
    
    summaries[query.name + " (并发)"] = {
      averageDuration: avgDuration,
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      p95Duration: calculatePercentile(durations, 95),
      successRate: successRate
    };
  }
  
  // 清理测试数据
  await cleanup();
  
  // 保存结果
  const timestamp = new Date().toISOString().replace(/:/g, '-');
  fs.writeFileSync(`kg-performance-results-${timestamp}.json`, JSON.stringify(results, null, 2));
  fs.writeFileSync(`kg-performance-summary-${timestamp}.json`, JSON.stringify(summaries, null, 2));
  
  console.log("性能测试完成，结果已保存");
  
  // 输出汇总报告
  console.log("\n性能测试汇总:");
  console.log("---------------------------------------");
  for (const [queryName, summary] of Object.entries(summaries)) {
    console.log(`查询: ${queryName}`);
    console.log(`  平均响应时间: ${summary.averageDuration.toFixed(2)} ms`);
    console.log(`  最小响应时间: ${summary.minDuration.toFixed(2)} ms`);
    console.log(`  最大响应时间: ${summary.maxDuration.toFixed(2)} ms`);
    console.log(`  P95响应时间: ${summary.p95Duration.toFixed(2)} ms`);
    console.log(`  成功率: ${summary.successRate.toFixed(2)}%`);
    console.log("---------------------------------------");
  }
  
  // 关闭驱动
  await driver.close();
}

// 辅助函数：计算百分位数
function calculatePercentile(values, percentile) {
  if (values.length === 0) return 0;
  values.sort((a, b) => a - b);
  const index = Math.ceil(percentile / 100 * values.length) - 1;
  return values[index];
}

// 执行测试
runPerformanceTests()
  .catch(error => {
    console.error("测试执行失败:", error);
    process.exit(1);
  });