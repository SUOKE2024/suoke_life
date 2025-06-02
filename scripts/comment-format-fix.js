#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🚀 开始注释格式修复...\n');

// 注释格式修复规则
const commentFixRules = [
  // 修复多行注释格式错误
  {
    name: '多行注释转单行',
    pattern: /\/\*\*([^*]|\*(?!\/))*\*\//g,
    replacement: (match) => {
      // 提取注释内容
      const content = match
        .replace(/\/\*\*|\*\//g, '')
        .replace(/\*/g, '')
        .replace(/\n/g, ' ')
        .trim();
      if (content) {
        return `// ${content}`;
      }
      return '//';
    }
  },
  // 修复单行注释格式错误
  {
    name: '单行注释格式错误',
    pattern: /\/\*([^*]|\*(?!\/))*\*\//g,
    replacement: (match) => {
      // 提取注释内容
      const content = match
        .replace(/\/\*|\*\//g, '')
        .replace(/\*/g, '')
        .trim();
      if (content) {
        return `// ${content}`;
      }
      return '//';
    }
  },
  // 修复空注释
  {
    name: '空注释修复',
    pattern: /\/\*\s*\*\//g,
    replacement: '//'
  }
];

// 获取所有需要修复的文件
const files = glob.sync('src/**/*.{ts,tsx,js,jsx}', {
  ignore: ['**/node_modules/**', '**/dist/**', '**/*.d.ts']
});

let totalFixed = 0;
let filesFixed = 0;

files.forEach(filePath => {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let originalContent = content;
    let fileFixCount = 0;

    // 应用注释修复规则
    commentFixRules.forEach(rule => {
      const beforeMatches = content.match(rule.pattern);
      if (beforeMatches) {
        content = content.replace(rule.pattern, rule.replacement);
        const afterMatches = content.match(rule.pattern);
        const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
        if (fixedCount > 0) {
          fileFixCount += fixedCount;
        }
      }
    });

    // 如果内容有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${filePath} (修复 ${fileFixCount} 处)`);
      totalFixed += fileFixCount;
      filesFixed++;
    }

  } catch (error) {
    console.log(`❌ ${filePath} (修复失败: ${error.message})`);
  }
});

console.log('\n📊 注释格式修复报告');
console.log('==================================================');
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${filesFixed}`);
console.log(`✨ 总修复数: ${totalFixed}`);
console.log('🎉 注释格式修复完成！'); 