/**
 * 最简单的智能体测试
 * 验证智能体系统的基本结构
 */

console.log('🚀 开始验证索克生活四智能体系统结构...\n');

// 测试智能体文件是否存在
const fs = require('fs');
const path = require('path');

const agentPaths = [
  'src/agents/xiaoai/XiaoaiAgentImpl.ts',
  'src/agents/xiaoke/XiaokeAgentImpl.ts', 
  'src/agents/laoke/LaokeAgentImpl.ts',
  'src/agents/soer/SoerAgentImpl.ts'
];

const agentNames = ['小艾', '小克', '老克', '索儿'];

console.log('📁 检查智能体文件...');
agentPaths.forEach((agentPath, index) => {
  const fullPath = path.join(process.cwd(), agentPath);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    const sizeKB = Math.round(stats.size / 1024);
    console.log(`✅ ${agentNames[index]} 智能体文件存在 (${sizeKB}KB)`);
  } else {
    console.log(`❌ ${agentNames[index]} 智能体文件不存在`);
  }
});

// 检查主要配置文件
console.log('\n📋 检查系统配置文件...');
const configFiles = [
  'src/agents/index.ts',
  'src/agents/AgentCoordinator.ts',
  'src/agents/AgentManager.ts',
  'src/agents/types.ts'
];

const configNames = ['主入口文件', '智能体协调器', '智能体管理器', '类型定义'];

configFiles.forEach((configFile, index) => {
  const fullPath = path.join(process.cwd(), configFile);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    const sizeKB = Math.round(stats.size / 1024);
    console.log(`✅ ${configNames[index]}存在 (${sizeKB}KB)`);
  } else {
    console.log(`❌ ${configNames[index]}不存在`);
  }
});

// 检查文档
console.log('\n📚 检查文档文件...');
const docFiles = [
  'src/agents/README.md',
  'src/agents/test-agents.ts'
];

const docNames = ['使用文档', '测试套件'];

docFiles.forEach((docFile, index) => {
  const fullPath = path.join(process.cwd(), docFile);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    const sizeKB = Math.round(stats.size / 1024);
    console.log(`✅ ${docNames[index]}存在 (${sizeKB}KB)`);
  } else {
    console.log(`❌ ${docNames[index]}不存在`);
  }
});

console.log('\n🎯 系统架构总结:');
console.log('├── 🤖 小艾 (XiaoaiAgent) - 健康助手 & 首页聊天频道版主');
console.log('├── 🛒 小克 (XiaokeAgent) - SUOKE频道版主，商业化服务');
console.log('├── 📚 老克 (LaokeAgent) - 探索频道版主，知识教育');
console.log('└── 💝 索儿 (SoerAgent) - LIFE频道版主，生活陪伴');

console.log('\n✨ 核心特性:');
console.log('• 中医"辨证论治未病"理念与现代预防医学结合');
console.log('• 四智能体分布式自主协作架构');
console.log('• 多模态传感技术与生物标志物分析');
console.log('• 区块链健康数据管理');
console.log('• "检测-辨证-调理-养生"健康管理闭环');

console.log('\n🎉 索克生活四智能体系统结构验证完成！');
console.log('💡 提示: 使用 npm run test 或相关脚本来运行完整的功能测试'); 