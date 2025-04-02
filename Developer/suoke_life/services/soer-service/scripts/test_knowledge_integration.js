'use strict';

/**
 * 知识集成服务测试脚本
 * 
 * 使用方法：
 * 1. 确保服务已经启动
 * 2. 运行: node scripts/test_knowledge_integration.js
 */

const axios = require('axios');
const dotenv = require('dotenv');

// 加载环境变量
dotenv.config();

// 服务器URL
const SERVER_URL = `http://${process.env.HOST || 'localhost'}:${process.env.PORT || 3006}`;
// API端点
const KNOWLEDGE_API = `${SERVER_URL}/api/v1/knowledge`;

// 测试查询
const TEST_QUERIES = [
  '中医体质调理',
  '春季养生',
  '心脏健康',
  '睡眠改善方法',
  '情绪与健康关系'
];

/**
 * 运行一个测试查询
 * @param {string} query 查询文本
 */
async function runTest(query) {
  console.log(`\n======= 测试查询: "${query}" =======`);
  
  try {
    // 执行知识搜索
    const searchResponse = await axios.post(`${KNOWLEDGE_API}/search`, {
      query,
      limit: 3,
      filters: {
        domains: ['health', 'tcm', 'nutrition']
      }
    });
    
    console.log('✅ 知识搜索成功');
    console.log(`找到 ${searchResponse.data.combined.length} 条结果`);
    
    // 显示结果概要
    if (searchResponse.data.combined.length > 0) {
      console.log('\n--- 搜索结果概要 ---');
      searchResponse.data.combined.forEach((item, index) => {
        console.log(`[${index + 1}] ${item.title} (${item.source}, 相关性: ${item.relevance.toFixed(2)})`);
      });
    }
    
    // 如果有知识图谱结果，尝试获取可视化数据
    const hasGraphResults = searchResponse.data.combined.some(item => item.source === 'knowledge_graph');
    
    if (hasGraphResults) {
      try {
        // 选择第一个知识图谱节点作为中心节点
        const graphNode = searchResponse.data.combined.find(item => item.source === 'knowledge_graph');
        
        if (graphNode) {
          // 获取可视化数据
          const visResponse = await axios.get(`${KNOWLEDGE_API}/visualization`, {
            params: {
              centralNode: graphNode.id,
              depth: 2,
              limit: 20
            }
          });
          
          console.log('\n✅ 知识图谱可视化数据获取成功');
          console.log(`包含 ${visResponse.data.nodes.length} 个节点和 ${visResponse.data.edges.length} 个关系`);
        }
      } catch (error) {
        console.error(`❌ 知识图谱可视化数据获取失败: ${error.message}`);
      }
    }
    
  } catch (error) {
    console.error(`❌ 测试失败: ${error.message}`);
    
    if (error.response) {
      console.error(`状态码: ${error.response.status}`);
      console.error(`错误信息: ${JSON.stringify(error.response.data)}`);
    }
  }
}

/**
 * 运行所有测试
 */
async function runAllTests() {
  console.log('开始测试知识集成服务...');
  console.log(`服务URL: ${SERVER_URL}`);
  
  // 首先检查服务健康状态
  try {
    const healthResponse = await axios.get(`${SERVER_URL}/health`);
    console.log(`服务健康状态: ${healthResponse.data.status}`);
    console.log(`版本: ${healthResponse.data.version}`);
  } catch (error) {
    console.error(`❌ 服务健康检查失败: ${error.message}`);
    console.error('请确保服务已启动，然后再次尝试。');
    process.exit(1);
  }
  
  // 按顺序执行每个测试查询
  for (const query of TEST_QUERIES) {
    await runTest(query);
  }
  
  console.log('\n======= 测试完成 =======');
}

// 执行测试
runAllTests().catch(error => {
  console.error(`测试执行过程中发生错误: ${error.message}`);
  process.exit(1);
});