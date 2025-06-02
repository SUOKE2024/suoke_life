#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🚀 开始超精确语法修复...\n');

// 超精确修复规则
const ultraPreciseRules = [
  // 注释格式错误修复 - 更精确的模式
  {
    name: '单行注释格式错误',
    pattern: /\/\*\s*([^*\n]+?)\s*\*\//g,
    replacement: '// $1'
  },
  {
    name: '多行注释转单行',
    pattern: /\/\*\*\s*([^*\n]+?)\s*\*\//g,
    replacement: '// $1'
  },
  // 对象属性定义错误修复
  {
    name: '对象属性缺少逗号',
    pattern: /(\w+:\s*[^,}\n]+)(\n\s*)(\w+:)/g,
    replacement: '$1,$2$3'
  },
  {
    name: '对象属性值后缺少逗号',
    pattern: /(\w+:\s*['"`][^'"`]*['"`])(\n\s*)(\w+:)/g,
    replacement: '$1,$2$3'
  },
  {
    name: '对象属性数字值后缺少逗号',
    pattern: /(\w+:\s*\d+)(\n\s*)(\w+:)/g,
    replacement: '$1,$2$3'
  },
  {
    name: '对象属性布尔值后缺少逗号',
    pattern: /(\w+:\s*(?:true|false))(\n\s*)(\w+:)/g,
    replacement: '$1,$2$3'
  },
  // 导入语句缺少分号
  {
    name: '导入语句缺少分号',
    pattern: /(import\s+.*from\s+['"][^'"]+['"])(?!\s*;)/g,
    replacement: '$1;'
  },
  {
    name: '导出语句缺少分号',
    pattern: /(export\s+.*from\s+['"][^'"]+['"])(?!\s*;)/g,
    replacement: '$1;'
  },
  // 行尾多余空格
  {
    name: '行尾多余空格',
    pattern: /\s+$/gm,
    replacement: ''
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

    // 应用超精确修复规则
    ultraPreciseRules.forEach(rule => {
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

    // 特殊处理：修复StyleSheet对象定义
    content = content.replace(
      /(StyleSheet\.create\(\{[\s\S]*?)(\w+:\s*\{[^}]*\})(\n\s*)(\w+:\s*\{)/g,
      '$1$2,$3$4'
    );

    // 特殊处理：修复接口定义中的属性
    content = content.replace(
      /(interface\s+\w+\s*\{[\s\S]*?)(\w+:\s*[^,}\n]+)(\n\s*)(\w+:)/g,
      '$1$2,$3$4'
    );

    // 特殊处理：修复类型定义中的属性
    content = content.replace(
      /(type\s+\w+\s*=\s*\{[\s\S]*?)(\w+:\s*[^,}\n]+)(\n\s*)(\w+:)/g,
      '$1$2,$3$4'
    );

    // 如果内容有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${filePath} (修复 ${fileFixCount} 处)`);
      totalFixed += fileFixCount;
      filesFixed++;
    } else {
      console.log(`⚪ ${filePath} (无需修复)`);
    }

  } catch (error) {
    console.log(`❌ ${filePath} (修复失败: ${error.message})`);
  }
});

console.log('\n📊 超精确语法修复报告');
console.log('==================================================');
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${filesFixed}`);
console.log(`✨ 总修复数: ${totalFixed}`);
console.log(`📈 修复率: ${Math.round((totalFixed / files.length) * 100)}%`);
console.log('🎉 超精确语法修复完成！建议运行代码质量检查验证结果。'); 