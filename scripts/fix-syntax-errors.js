#!/usr/bin/env node

/**
 * 语法错误修复脚本
 * 修复优化过程中引入的重复import语句等语法错误
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const glob = require("glob");

// 常见语法错误修复规则
const fixRules = [
  // 修复缺少分号
  {
    pattern: /(\w+)\s*$/gm,
    replacement: '$1;',
    description: '添加缺少的分号'
  },
  
  // 修复缺少逗号的对象属性
  {
    pattern: /(\w+:\s*[^,}\n]+)\s*\n\s*(\w+:)/g,
    replacement: '$1,\n  $2',
    description: '添加缺少的逗号'
  },
  
  // 修复字符串引号问题
  {
    pattern: /([^"'])"([^"']*)"([^"'])/g,
    replacement: '$1"$2"$3',
    description: '修复字符串引号'
  },
  
  // 修复导入语句
  {
    pattern: /import\s*{\s*([^}]+)\s*}\s*from\s*["']([^"']+)["']\s*["']([^"']+)["']/g,
    replacement: 'import { $1 } from "$2";',
    description: '修复导入语句'
  },
  
  // 修复多余的分号
  {
    pattern: /;;+/g,
    replacement: ';',
    description: '移除多余的分号'
  },
  
  // 修复括号问题
  {
    pattern: /\(\s*\(\s*/g,
    replacement: '(',
    description: '修复多余的括号'
  },
  
  // 修复花括号问题
  {
    pattern: /{\s*{/g,
    replacement: '{',
    description: '修复多余的花括号'
  }
];

// 获取所有TypeScript文件
function getTypeScriptFiles() {
  return glob.sync('src/**/*.{ts,tsx}', {
    ignore: ['src/**/*.test.{ts,tsx}', 'src/**/__tests__/**/*']
  });
}

// 应用修复规则
function applyFixes(content, filePath) {
  let fixedContent = content;
  let appliedFixes = [];
  
  fixRules.forEach(rule => {
    const beforeLength = fixedContent.length;
    fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
    const afterLength = fixedContent.length;
    
    if (beforeLength !== afterLength) {
      appliedFixes.push(rule.description);
    }
  });
  
  return { content: fixedContent, fixes: appliedFixes };
}

// 备份文件
function backupFile(filePath) {
  const backupPath = filePath + '.backup';
  fs.copyFileSync(filePath, backupPath);
  return backupPath;
}

// 主修复函数
function fixFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const { content: fixedContent, fixes } = applyFixes(content, filePath);
    
    if (fixes.length > 0) {
      // 备份原文件
      backupFile(filePath);
      
      // 写入修复后的内容
      fs.writeFileSync(filePath, fixedContent, 'utf8');
      
      console.log(`✅ 修复文件: ${filePath}`);
      fixes.forEach(fix => console.log(`   - ${fix}`));
      
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath}`, error.message);
    return false;
  }
}

// 主函数
function main() {
  console.log('🔧 开始自动修复语法错误...\n');
  
  const files = getTypeScriptFiles();
  let fixedCount = 0;
  let totalFiles = files.length;
  
  console.log(`📁 找到 ${totalFiles} 个TypeScript文件\n`);
  
  files.forEach(filePath => {
    if (fixFile(filePath)) {
      fixedCount++;
    }
  });
  
  console.log(`\n📊 修复完成:`);
  console.log(`   - 总文件数: ${totalFiles}`);
  console.log(`   - 修复文件数: ${fixedCount}`);
  console.log(`   - 修复率: ${((fixedCount / totalFiles) * 100).toFixed(1)}%`);
  
  if (fixedCount > 0) {
    console.log(`\n💡 提示: 原文件已备份为 .backup 后缀`);
    console.log(`   如需恢复，请运行: find src -name "*.backup" -exec bash -c 'mv "$1" "\${1%.backup}"' _ {} \\;`);
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = { fixFile, applyFixes };