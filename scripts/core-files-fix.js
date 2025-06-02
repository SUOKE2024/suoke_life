#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 开始核心文件修复...\n');

// 核心文件修复规则
const coreFileRules = [
  // 修复对象定义中的错误分号
  {
    name: '修复对象定义错误分号',
    pattern: /export const (\w+) = ;{;/g,
    replacement: 'export const $1 = {'
  },
  
  // 修复对象属性缺少逗号
  {
    name: '修复对象属性缺少逗号',
    pattern: /^(\s*)(\w+):\s*([^,{};\n]+?)([,;]?)(\s*\n\s*)(\w+|}):/gm,
    replacement: (match, indent, prop, value, ending, newline, next) => {
      const trimmedValue = value.trim();
      if (next === '}') {
        return `${indent}${prop}: ${trimmedValue}${newline}${next}:`;
      }
      if (!ending || ending === ';') {
        return `${indent}${prop}: ${trimmedValue},${newline}${next}:`;
      }
      return match;
    }
  },
  
  // 修复函数调用中的错误分号
  {
    name: '修复函数调用错误分号',
    pattern: /(\w+)\s*;(\(;?\);?)/g,
    replacement: '$1$2'
  },
  
  // 修复导入语句格式
  {
    name: '修复导入语句格式',
    pattern: /import\s+{([^}]+)}\s+from\s+"([^"]+)"\/([^;]*)/g,
    replacement: 'import { $1 } from "$2";'
  },
  
  // 修复JSX标签错误
  {
    name: '修复JSX标签错误',
    pattern: /<\/(\w+);>/g,
    replacement: '</$1>'
  },
  
  // 修复对象展开语法
  {
    name: '修复对象展开语法',
    pattern: /(\s*)\.\.\.(\w+)([,;]?)/g,
    replacement: '$1...$2,'
  },
  
  // 修复字符串结尾错误分号
  {
    name: '修复字符串结尾错误分号',
    pattern: /"([^"]*);"/g,
    replacement: '"$1"'
  },
  
  // 修复数组定义错误
  {
    name: '修复数组定义错误',
    pattern: /\[([^\]]*);?\]/g,
    replacement: (match, content) => {
      const cleanContent = content.replace(/;+/g, '');
      return `[${cleanContent}]`;
    }
  },
  
  // 修复类型定义错误
  {
    name: '修复类型定义错误',
    pattern: /:\s*([^,;{}]+);([,}])/g,
    replacement: ': $1$2'
  },
  
  // 修复函数参数错误
  {
    name: '修复函数参数错误',
    pattern: /\(([^)]*);([^)]*)\)/g,
    replacement: (match, param1, param2) => {
      const cleanParam1 = param1.replace(/;+/g, '');
      const cleanParam2 = param2.replace(/;+/g, '');
      return `(${cleanParam1}${cleanParam2})`;
    }
  }
];

// 核心文件列表
const coreFiles = [
  'src/App.tsx',
  'src/constants/theme.ts',
  'src/navigation/AppNavigator.tsx',
  'src/navigation/AuthNavigator.tsx',
  'src/navigation/LazyRoutes.tsx',
  'src/navigation/MainNavigator.tsx',
  'src/screens/main/HomeScreen.tsx',
  'src/screens/main/IntegratedExperienceScreen.tsx',
  'src/hooks/usePerformanceMonitor.ts',
  'src/services/Logger.ts',
  'src/store/index.ts',
  'src/store/index.tsx'
];

// 修复单个文件
function fixCoreFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚪ ${filePath} (文件不存在)`);
    return 0;
  }

  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let fixCount = 0;
    const originalContent = content;
    
    // 应用所有修复规则
    coreFileRules.forEach(rule => {
      const before = content;
      if (typeof rule.replacement === 'function') {
        content = content.replace(rule.pattern, rule.replacement);
      } else {
        content = content.replace(rule.pattern, rule.replacement);
      }
      
      if (before !== content) {
        fixCount++;
      }
    });
    
    // 特殊处理：修复连续的分号
    content = content.replace(/;+;/g, ';');
    
    // 特殊处理：修复对象结尾
    content = content.replace(/(\w+):\s*([^,{};\n]+?)\s*\n\s*}/g, '$1: $2\n}');
    
    // 特殊处理：修复导入语句连接
    content = content.replace(/import\s+{([^}]+)}\s+from\s+"([^"]+)"\/import/g, 'import { $1 } from "$2";\nimport');
    
    // 如果有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${filePath} (应用 ${fixCount} 个规则)`);
      return fixCount;
    } else {
      console.log(`⚪ ${filePath} (无需修复)`);
      return 0;
    }
  } catch (error) {
    console.error(`❌ ${filePath}: ${error.message}`);
    return 0;
  }
}

// 执行修复
let totalFixCount = 0;
let fixedFileCount = 0;

console.log(`📁 发现 ${coreFiles.length} 个核心文件需要修复\n`);

coreFiles.forEach(file => {
  const fixCount = fixCoreFile(file);
  if (fixCount > 0) {
    totalFixCount += fixCount;
    fixedFileCount++;
  }
});

console.log(`\n📊 核心文件修复报告`);
console.log(`==================================================`);
console.log(`📁 处理文件数: ${coreFiles.length}`);
console.log(`🔧 修复文件数: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((fixedFileCount / coreFiles.length) * 100).toFixed(1)}%`);
console.log(`🔧 核心文件修复完成！建议运行TypeScript检查验证结果。`); 