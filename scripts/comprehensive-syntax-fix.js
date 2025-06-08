#!/usr/bin/env node;
const fs = require("fs");
const path = require("path");
const glob = require("glob");

console.log('🔧 开始综合语法修复...');

// 修复规则
const fixRules = [
  // 修复 describe 函数调用语法错误
  {
    pattern: /describe\(([^"]+)"\s*,\s*\(\)\s*=>\s*\{"/g,
    replacement: 'describe("$1", () => {'
  },
  
  // 修复 import 语句中的引号问题
  {
    pattern: /import\s+\{([^}]+)\}\s+from\s+@([^"]+)"\s*;\s*"/g,
    replacement: 'import { $1 } from "@$2";'
  },
  
  // 修复对象字面量语法
  {
    pattern: /\{\s*;\s*/g,
    replacement: '{'
  },
  
  // 修复多余的分号
  {
    pattern: /,\s*;\s*/g,
    replacement: ','
  },
  
  // 修复类型定义语法
  {
    pattern: /export\s+type\s+([^=]+)=\s*;\s*/g,
    replacement: 'export type $1 = '
  },
  
  // 修复接口定义语法
  {
    pattern: /export\s+interface\s+([^{]+)\{\s*;\s*/g,
    replacement: 'export interface $1 {'
  },
  
  // 修复函数参数语法
  {
    pattern: /\(\s*([^)]+),\s*;\s*\)/g,
    replacement: '($1)'
  },
  
  // 修复字符串连接问题
  {
    pattern: /"\s*;\s*"/g,
    replacement: ''
  },
  
  // 修复注释语法
  {
    pattern: /\/\/\/\/\/\/\s*/g,
    replacement: '// '
  },
  
  // 修复多行注释
  {
    pattern: /\/\*\*\/\/\/\/\s*/g,
    replacement: '/**\n * '
  },
  
  // 修复 return 语句
  {
    pattern: /return\s*;\s*"/g,
    replacement: 'return "'
  },
  
  // 修复模板字符串
  {
    pattern: /`([^`]*)\$\{([^}]*)\}([^`]*)`/g,
    replacement: '`$1\${$2}$3`'
  },
  
  // 修复箭头函数语法
  {
    pattern: /\(\s*\(\)\s*=>\s*\{\s*\}/g,
    replacement: '(() => {'
  },
  
  // 修复对象属性语法
  {
    pattern: /:\s*([^,}]+),\s*;\s*/g,
    replacement: ': $1,'
  },
  
  // 修复数组语法
  {
    pattern: /[\s*([^]]+),\s*;\s*\]/g,
    replacement: '[$1]'
  },
  
  // 修复条件语句
  {
    pattern: /if\s*\(\s*([^)]+)\s*;\s*\)\s*\{/g,
    replacement: 'if ($1) {'
  },
  
  // 修复 try-catch 语句
  {
    pattern: /try\s*\{\s*;\s*/g,
    replacement: 'try {'
  },
  
  // 修复 export 语句
  {
    pattern: /export\s*\{\s*([^}]+),\s*;\s*\}/g,
    replacement: 'export { $1 }'
  },
  
  // 修复类定义
  {
    pattern: /class\s+([^{]+)\{\s*;\s*/g,
    replacement: 'class $1 {'
  },
  
  // 修复方法定义
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(\s*([^)]*)\s*\)\s*:\s*([^{]+)\{\s*;\s*/g,
    replacement: '$1($2): $3 {'
  },
  
  // 修复变量声明
  {
    pattern: /(const|let|var)\s+([^=]+)=\s*\{\s*;\s*/g,
    replacement: '$1 $2 = {'
  },
  
  // 修复联合类型
  {
    pattern: /\|\s*"([^"]+);\s*;\s*"/g,
    replacement: '| "$1"'
  },
  
  // 修复泛型语法
  {
    pattern: /<([^>]+),\s*;\s*>/g,
    replacement: '<$1>'
  },
  
  // 修复解构赋值
  {
    pattern: /\{\s*([^}]+),\s*;\s*\}/g,
    replacement: '{ $1 }'
  },
  
  // 修复 JSX 属性
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\{\s*([^}]+),\s*;\s*\}/g,
    replacement: '$1={$2}'
  },
  
  // 修复字符串模板
  {
    pattern: /"\s*\+\s*"/g,
    replacement: ''
  },
  
  // 修复多余的逗号和分号组合
  {
    pattern: /,\s*;\s*,/g,
    replacement: ','
  },
  
  // 修复函数调用
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(\s*([^)]*),\s*;\s*\)/g,
    replacement: '$1($2)'
  },
  
  // 修复对象方法
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*\(\s*([^)]*)\s*\)\s*=>\s*\{\s*;\s*/g,
    replacement: '$1: ($2) => {'
  },
  
  // 修复 async/await 语法
  {
    pattern: /async\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(\s*([^)]*)\s*\)\s*:\s*([^{]+)\{\s*;\s*/g,
    replacement: 'async $1($2): $3 {'
  },
  
  // 修复 Promise 类型
  {
    pattern: /Promise<([^>]+),\s*;\s*>/g,
    replacement: 'Promise<$1>'
  },
  
  // 修复数组类型
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)[\s*],\s*;\s*/g,
    replacement: '$1[],'
  },
  
  // 修复可选属性
  {
    pattern: /([a-zA-Z_$][a-zA-Z0-9_$]*)\?\s*:\s*([^,}]+),\s*;\s*/g,
    replacement: '$1?: $2,'
  },
  
  // 修复 import 路径
  {
    pattern: /import\s+([^"]+)"\s*;\s*([^"]*)";\s*"/g,
    replacement: 'import $1"$2";'
  },
  
  // 修复多行字符串
  {
    pattern: /"\s*\n\s*"/g,
    replacement: ''
  },
  
  // 修复注释中的语法错误
  {
    pattern: /\/\*\s*([^*]+)\s*\*\s*([^/]+)\s*\*\//g,
    replacement: '/* $1 $2 */'
  },
  
  // 修复 switch 语句
  {
    pattern: /switch\s*\(\s*([^)]+)\s*\)\s*\{\s*;\s*/g,
    replacement: 'switch ($1) {'
  },
  
  // 修复 case 语句
  {
    pattern: /case\s+([^:]+):\s*;\s*/g,
    replacement: 'case $1:'
  },
  
  // 修复 break 语句
  {
    pattern: /break\s*;\s*;\s*/g,
    replacement: 'break;'
  },
  
  // 修复 continue 语句
  {
    pattern: /continue\s*;\s*;\s*/g,
    replacement: 'continue;'
  },
  
  // 修复 throw 语句
  {
    pattern: /throw\s+([^;]+);\s*;\s*/g,
    replacement: 'throw $1;'
  },
  
  // 修复 new 表达式
  {
    pattern: /new\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(\s*([^)]*),\s*;\s*\)/g,
    replacement: 'new $1($2)'
  },
  
  // 修复正则表达式
  {
    pattern: /\/([^/]+)\/([gimuy]*),\s*;\s*/g,
    replacement: '/$1/$2,'
  },
  
  // 修复三元运算符
  {
    pattern: /([^?]+)\?\s*([^:]+):\s*([^,}]+),\s*;\s*/g,
    replacement: '$1 ? $2 : $3,'
  },
  
  // 修复逻辑运算符
  {
    pattern: /([^&]+)&&\s*([^,}]+),\s*;\s*/g,
    replacement: '$1 && $2,'
  },
  
  // 修复或运算符
  {
    pattern: /([^|]+)\|\|\s*([^,}]+),\s*;\s*/g,
    replacement: '$1 || $2,'
  }
];

function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let fixCount = 0;
    
    // 应用所有修复规则
    fixRules.forEach(rule => {
      const matches = content.match(rule.pattern);
      if (matches) {
        content = content.replace(rule.pattern, rule.replacement);
        fixCount += matches.length;
      }
    });
    
    // 额外的清理规则
    // 移除多余的空行
    content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    // 修复缩进
    content = content.replace(/^[ \t]+$/gm, '');
    
    // 确保文件以换行符结尾
    if (!content.endsWith('\n')) {
      content += '\n';
    }
    
    if (fixCount > 0) {
      fs.writeFileSync(filePath, content);
      console.log(`📝 修复文件: ${filePath} (${fixCount} 处修复)`);
    }
    
    return fixCount;
  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath}`, error.message);
    return 0;
  }
}

// 获取所有需要修复的文件
const patterns = [
  'src/**/*.ts',
  'src/**/*.tsx',
  'src/**/*.js',
  'src/**/*.jsx'
];

let totalFixes = 0;
let fixedFiles = 0;

patterns.forEach(pattern => {
  const files = glob.sync(pattern, { ignore: ['**/node_modules/**', '**/dist/**', '**/build/**'] });
  
  files.forEach(file => {
    const fixes = fixFile(file);
    if (fixes > 0) {
      fixedFiles++;
      totalFixes += fixes;
    }
  });
});

console.log(`\n📊 综合修复报告:`);
console.log(`✅ 修复的文件数: ${fixedFiles}`);
console.log(`🔧 总修复数: ${totalFixes}`);
console.log(`✅ 综合语法修复完成！`);
