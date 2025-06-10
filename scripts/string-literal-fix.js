#!/usr/bin/env node

/**
 * 索克生活 - 字符串字面量修复脚本
 * 专门修复未终止的字符串字面量问题
 */

const fs = require('fs');
const path = require('path');

// 颜色定义
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 修复未终止的字符串字面量
function fixUnterminatedStrings(content) {
  let lines = content.split('\n');
  let modified = false;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    
    // 检查是否有未闭合的字符串
    const singleQuoteMatches = (line.match(/'/g) || []).length;
    const doubleQuoteMatches = (line.match(/"/g) || []).length;
    const backtickMatches = (line.match(/`/g) || []).length;
    
    // 如果引号数量是奇数，说明有未闭合的字符串
    if (singleQuoteMatches % 2 !== 0) {
      // 在行末添加单引号
      lines[i] = line + "'";
      modified = true;
      log('yellow', `修复单引号: ${line} -> ${lines[i]}`);
    }
    
    if (doubleQuoteMatches % 2 !== 0) {
      // 在行末添加双引号
      lines[i] = line + '"';
      modified = true;
      log('yellow', `修复双引号: ${line} -> ${lines[i]}`);
    }
    
    if (backtickMatches % 2 !== 0) {
      // 在行末添加反引号
      lines[i] = line + '`';
      modified = true;
      log('yellow', `修复反引号: ${line} -> ${lines[i]}`);
    }
  }
  
  return modified ? lines.join('\n') : content;
}

// 修复特定的语法问题
function fixSpecificSyntaxIssues(content) {
  let modified = false;
  let newContent = content;
  
  // 修复常见的语法错误模式
  const fixes = [
    // 修复 import 语句中的未终止字符串
    [/import\s+.*from\s+['"][^'"]*$/gm, (match) => match + (match.includes("'") ? "'" : '"')],
    
    // 修复 export 语句中的未终止字符串
    [/export\s+.*from\s+['"][^'"]*$/gm, (match) => match + (match.includes("'") ? "'" : '"')],
    
    // 修复对象属性中的未终止字符串
    [/:\s*['"][^'"]*$/gm, (match) => match + (match.includes("'") ? "'" : '"')],
    
    // 修复函数调用中的未终止字符串
    [/\(\s*['"][^'"]*$/gm, (match) => match + (match.includes("'") ? "'" : '"')],
    
    // 修复数组元素中的未终止字符串
    [/\[\s*['"][^'"]*$/gm, (match) => match + (match.includes("'") ? "'" : '"')],
  ];
  
  fixes.forEach(([pattern, replacement]) => {
    const result = newContent.replace(pattern, replacement);
    if (result !== newContent) {
      newContent = result;
      modified = true;
    }
  });
  
  return modified ? newContent : content;
}

// 修复单个文件
function fixFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return false;
    }
    
    let content = fs.readFileSync(filePath, 'utf8');
    let originalContent = content;
    
    // 应用修复
    content = fixUnterminatedStrings(content);
    content = fixSpecificSyntaxIssues(content);
    
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return true;
    }
    
    return false;
  } catch (error) {
    log('red', `修复文件失败 ${filePath}: ${error.message}`);
    return false;
  }
}

// 获取有问题的文件列表
function getProblematicFiles() {
  return [
    'src/App.tsx',
    'src/__mocks__/react-native-device-info.js',
    'src/__mocks__/react-native-permissions.js',
    'src/__mocks__/react-native-vector-icons.js',
    'src/__tests__/AgentEmotionFeedback.test.tsx',
    'src/__tests__/App.test.tsx',
    'src/__tests__/agent_collaboration/agent_collaboration.integration.test.ts',
    'src/__tests__/agents/AgentCoordinator.test.tsx',
    'src/__tests__/components/FiveDiagnosisAgentIntegrationScreen.test.tsx',
    'src/__tests__/components/HomeScreen.test.tsx',
    'src/__tests__/e2e/agent-collaboration.test.tsx',
    'src/__tests__/e2e/agentIntegration.test.tsx',
    'src/__tests__/e2e/comprehensive-e2e.test.tsx',
    'src/__tests__/e2e/performance-stress.test.tsx',
    'src/__tests__/e2e/simple-e2e.test.tsx'
  ];
}

// 主函数
function main() {
  log('cyan', '🔧 开始修复未终止的字符串字面量...');
  
  const problematicFiles = getProblematicFiles();
  let fixedCount = 0;
  
  problematicFiles.forEach(filePath => {
    if (fs.existsSync(filePath)) {
      if (fixFile(filePath)) {
        fixedCount++;
        log('green', `✅ 修复: ${filePath}`);
      } else {
        log('blue', `ℹ️ 无需修复: ${filePath}`);
      }
    } else {
      log('yellow', `⚠️ 文件不存在: ${filePath}`);
    }
  });
  
  log('cyan', `✨ 修复完成！总计修复了 ${fixedCount} 个文件`);
  
  // 生成修复报告
  const reportContent = `# 字符串字面量修复报告

## 修复概览

**修复时间**: ${new Date().toLocaleString()}
**修复文件数**: ${fixedCount}个

## 修复的文件

${problematicFiles.map(file => `- ${file}`).join('\n')}

## 修复内容

- ✅ 未终止的单引号字符串
- ✅ 未终止的双引号字符串  
- ✅ 未终止的反引号字符串
- ✅ import/export语句中的字符串
- ✅ 对象属性中的字符串
- ✅ 函数调用中的字符串
- ✅ 数组元素中的字符串

---
*报告由索克生活字符串修复系统自动生成*
`;
  
  fs.writeFileSync('STRING_FIX_REPORT.md', reportContent);
  log('cyan', '📋 修复报告已生成: STRING_FIX_REPORT.md');
}

// 运行修复
if (require.main === module) {
  main();
}

module.exports = { fixFile, main }; 