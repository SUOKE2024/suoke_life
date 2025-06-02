#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🎯 开始高精度语法修复...\n');

// 高精度修复规则
const precisionFixRules = [
  // 规则1: 修复对象属性后缺少逗号（最精确的匹配）
  {
    name: '对象属性缺少逗号',
    pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*\n\s*)(\w+):/gm,
    replacement: (match, indent1, prop1, value1, newline, prop2) => {
      const trimmedValue = value1.trim();
      // 检查是否已经有逗号或分号
      if (!trimmedValue.endsWith(',') && !trimmedValue.endsWith(';') && 
          !trimmedValue.endsWith('{') && !trimmedValue.endsWith('[')) {
        return `${indent1}${prop1}: ${trimmedValue},${newline}${prop2}:`;
      }
      return match;
    }
  },

  // 规则2: 修复字符串值后缺少逗号
  {
    name: '字符串值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(['"`][^'"`\n]*['"`])(\s*\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 规则3: 修复数字值后缺少逗号
  {
    name: '数字值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(\d+(?:\.\d+)?)(\s*\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 规则4: 修复布尔值后缺少逗号
  {
    name: '布尔值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(true|false)(\s*\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 规则5: 修复undefined/null值后缺少逗号
  {
    name: 'undefined/null值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(undefined|null)(\s*\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 规则6: 修复导入语句缺少分号
  {
    name: '导入语句缺少分号',
    pattern: /(import\s+[^;\n]+)(\n)/g,
    replacement: (match, importStatement, newline) => {
      if (!importStatement.trim().endsWith(';')) {
        return importStatement + ';' + newline;
      }
      return match;
    }
  },

  // 规则7: 修复导出语句缺少分号
  {
    name: '导出语句缺少分号',
    pattern: /(export\s+[^;\n{]+)(\n)/g,
    replacement: (match, exportStatement, newline) => {
      if (!exportStatement.trim().endsWith(';') && 
          !exportStatement.includes('{') && 
          !exportStatement.includes('function') && 
          !exportStatement.includes('class')) {
        return exportStatement + ';' + newline;
      }
      return match;
    }
  }
];

// 特殊文件的精确修复规则
const specialFileFixRules = {
  'src/agents/xiaoai/config/XiaoaiConfigManager.tsx': (content) => {
    // 修复特殊的导入语句错误
    content = content.replace(/import { ;/g, 'import {');
    content = content.replace(/} from/g, '} from');
    
    // 修复注释和代码混合的问题
    content = content.replace(/\/\/ import { EventEmitter } from 'events';/g, 
      "// import { EventEmitter } from 'events';");
    
    // 修复配置对象的语法错误
    content = content.replace(/enabled: true,\s*debugMode: false,/g, 
      'enabled: true,\n  debugMode: false,');
    
    return content;
  },

  'src/navigation/MainNavigator.tsx': (content) => {
    // 修复类型定义中的语法错误
    content = content.replace(/export type MainTabParamList = \{/g, 
      'export type MainTabParamList = {');
    content = content.replace(/export type MainStackParamList = \{/g, 
      'export type MainStackParamList = {');
    
    // 修复函数参数定义
    content = content.replace(/const getTabBarIcon = \(\{/g, 
      'const getTabBarIcon = ({');
    
    return content;
  }
};

// 深度对象属性修复函数
function deepFixObjectProperties(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  let inObject = false;
  let objectDepth = 0;
  let braceStack = [];

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const nextLine = lines[i + 1];
    const trimmedLine = line.trim();

    // 跟踪大括号
    const openBraces = (line.match(/\{/g) || []).length;
    const closeBraces = (line.match(/\}/g) || []).length;
    objectDepth += openBraces - closeBraces;

    // 检测对象开始
    if (openBraces > 0 && (
      trimmedLine.includes('StyleSheet.create') ||
      trimmedLine.includes('= {') ||
      trimmedLine.includes(': {') ||
      trimmedLine.match(/^\s*\w+:\s*\{/) ||
      trimmedLine.includes('interface') ||
      trimmedLine.includes('type')
    )) {
      inObject = true;
    }

    // 检测对象结束
    if (objectDepth <= 0) {
      inObject = false;
    }

    // 在对象内部修复属性定义
    if (inObject && nextLine && objectDepth > 0) {
      const currentIndent = line.match(/^(\s*)/)[1];
      const nextIndent = nextLine.match(/^(\s*)/)[1];
      const nextTrimmed = nextLine.trim();
      
      // 检查当前行是否是属性定义
      const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\n;]+)$/);
      const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
      const nextCloseBrace = nextTrimmed === '}' || nextTrimmed === '});' || nextTrimmed === '},';

      if (propertyMatch && (nextPropertyMatch || nextCloseBrace)) {
        // 同一缩进层级的属性或对象结束
        if ((nextPropertyMatch && currentIndent.length === nextIndent.length) || 
            (nextCloseBrace && currentIndent.length >= nextIndent.length)) {
          const value = propertyMatch[3].trim();
          // 如果值不以逗号结尾且不是对象或数组的开始，且下一行不是对象结束
          if (!value.endsWith(',') && 
              !value.endsWith('{') && 
              !value.endsWith('[') && 
              !value.endsWith(';') &&
              !nextCloseBrace) {
            line = propertyMatch[1] + propertyMatch[2] + ': ' + value + ',';
          }
        }
      }
    }

    fixedLines.push(line);
  }

  return fixedLines.join('\n');
}

// 清理多余符号
function cleanupSyntax(content) {
  // 清理多余的逗号
  content = content.replace(/,(\s*[}\]])/g, '$1');
  content = content.replace(/,(\s*\))/g, '$1');
  
  // 清理多余的分号
  content = content.replace(/;;+/g, ';');
  
  // 清理错误的字符组合
  content = content.replace(/;,/g, ',');
  content = content.replace(/,;/g, ',');
  
  // 清理行尾空格
  content = content.replace(/\s+$/gm, '');
  
  return content;
}

// 获取所有需要修复的文件
const files = glob.sync('src/**/*.{ts,tsx,js,jsx}', {
  ignore: ['**/node_modules/**', '**/dist/**', '**/.git/**']
});

let totalFixCount = 0;
let fixedFileCount = 0;

console.log(`📁 发现 ${files.length} 个文件需要检查\n`);

files.forEach(file => {
  try {
    let content = fs.readFileSync(file, 'utf8');
    let originalContent = content;
    let fileFixCount = 0;

    // 应用特殊文件修复规则
    if (specialFileFixRules[file]) {
      const beforeContent = content;
      content = specialFileFixRules[file](content);
      if (content !== beforeContent) {
        fileFixCount += 1;
      }
    }

    // 应用高精度修复规则
    precisionFixRules.forEach(rule => {
      if (typeof rule.replacement === 'function') {
        const beforeContent = content;
        content = content.replace(rule.pattern, rule.replacement);
        if (content !== beforeContent) {
          fileFixCount += 1;
        }
      } else {
        const beforeMatches = content.match(rule.pattern);
        if (beforeMatches) {
          content = content.replace(rule.pattern, rule.replacement);
          const afterMatches = content.match(rule.pattern);
          const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
          if (fixedCount > 0) {
            fileFixCount += fixedCount;
          }
        }
      }
    });

    // 应用深度对象属性修复
    const beforeDeepFix = content;
    content = deepFixObjectProperties(content);
    if (content !== beforeDeepFix) {
      fileFixCount += 1;
    }

    // 清理语法
    const beforeCleanup = content;
    content = cleanupSyntax(content);
    if (content !== beforeCleanup) {
      fileFixCount += 1;
    }

    // 如果内容有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(file, content, 'utf8');
      console.log(`✅ ${file} (修复 ${fileFixCount} 处)`);
      totalFixCount += fileFixCount;
      fixedFileCount++;
    }

  } catch (error) {
    console.error(`❌ ${file}: ${error.message}`);
  }
});

console.log(`\n📊 高精度语法修复报告`);
console.log(`==================================================`);
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((totalFixCount / files.length) * 100).toFixed(1)}%`);
console.log(`🎯 高精度语法修复完成！建议运行代码质量检查验证结果。`); 