#!/usr/bin/env node

/**
 * 语法错误修复脚本
 * 修复优化过程中引入的重复import语句等语法错误
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const glob = require("glob");

// 修复规则
const fixRules = [
  // 修复未闭合的字符串引号 - 更精确的匹配
  {
    name: '未闭合的import字符串',
    pattern: /import\s+([^"']+)\s+from\s+"([^"]*);/g,
    replacement: 'import $1 from "$2";'
  },
  {
    name: '未闭合的import字符串(单引号)',
    pattern: /import\s+([^"']+)\s+from\s+'([^']*);/g,
    replacement: 'import $1 from \'$2\';'
  },
  // 修复正则表达式错误
  {
    name: '错误的正则表达式',
    pattern: /\/;/g,
    replacement: '//'
  },
  // 修复对象语法错误
  {
    name: '对象开始语法错误',
    pattern: /\{,/g,
    replacement: '{'
  },
  {
    name: '对象结束语法错误',
    pattern: /,\s*\}/g,
    replacement: '}'
  },
  // 修复分号问题
  {
    name: '重复分号',
    pattern: /;;+/g,
    replacement: ';'
  },
  // 修复分号逗号混用
  {
    name: '分号逗号混用',
    pattern: /;,/g,
    replacement: ','
  },
  // 修复链式调用语法
  {
    name: '链式调用语法',
    pattern: /(\w+)\s*\.\s*\(/g,
    replacement: '$1.('
  },
  // 修复箭头函数语法
  {
    name: '箭头函数语法',
    pattern: /=>\s*\{([^}]*?)$/gm,
    replacement: (match, content) => `=> {${content.trim()}}`
  },
  // 修复函数调用语法
  {
    name: '函数调用语法',
    pattern: /(\w+)\s*\(\s*\)/g,
    replacement: '$1()'
  }
];

// 获取所有需要修复的文件
function getFilesToFix() {
  const patterns = [
    'src/**/*.ts',
    'src/**/*.tsx',
    'src/**/*.js',
    'src/**/*.jsx'
  ];
  
  let files = [];
  patterns.forEach(pattern => {
    const matched = glob.sync(pattern, { 
      ignore: ['**/node_modules/**', '**/*.test.*', '**/*.spec.*'] 
    });
    files = files.concat(matched);
  });
  
  return [...new Set(files)]; // 去重
}

// 修复单个文件
function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, "utf8");
    let originalContent = content;
    let fixCount = 0;
    let appliedRules = [];
    
    // 应用所有修复规则
    fixRules.forEach(rule => {
      const beforeContent = content;
      content = content.replace(rule.pattern, rule.replacement);
      
      if (content !== beforeContent) {
        const matches = beforeContent.match(rule.pattern);
        if (matches) {
          fixCount += matches.length;
          appliedRules.push(`${rule.name}: ${matches.length}个`);
        }
      }
    });
    
    // 如果有修改，写回文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, "utf8");
      console.log(`✅ 修复 ${filePath}:`);
      appliedRules.forEach(rule => console.log(`   - ${rule}`));
      return fixCount;
    }
    
    return 0;
  } catch (error) {
    console.error(`❌ 修复 ${filePath} 失败:`, error.message);
    return 0;
  }
}

// 主函数
function main() {
  console.log("🔧 开始修复前端语法错误...\n");
  
  const files = getFilesToFix();
  console.log(`📁 找到 ${files.length} 个文件需要检查\n`);
  
  let totalFixes = 0;
  let fixedFiles = 0;
  
  files.forEach(file => {
    const fixes = fixFile(file);
    if (fixes > 0) {
      totalFixes += fixes;
      fixedFiles++;
    }
  });
  
  console.log("\n📊 修复统计:");
  console.log(`- 检查文件: ${files.length}`);
  console.log(`- 修复文件: ${fixedFiles}`);
  console.log(`- 修复问题: ${totalFixes}`);
  
  if (totalFixes > 0) {
    console.log("\n✨ 修复完成！建议运行 npm run lint 验证结果");
  } else {
    console.log("\n✅ 没有发现需要修复的语法错误");
  }
}

// 检查是否安装了glob
try {
  require("glob");
} catch (error) {
  console.error("❌ 缺少依赖: glob");
  console.log("请运行: npm install glob");
  process.exit(1);
}

if (require.main === module) {
  main();
}

module.exports = { fixFile, getFilesToFix };