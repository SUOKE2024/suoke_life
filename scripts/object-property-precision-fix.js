#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🔧 开始对象属性精确修复...\n');

// 对象属性精确修复函数
function fixObjectPropertiesPrecision(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  let inObject = false;
  let objectDepth = 0;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const nextLine = lines[i + 1];
    const trimmedLine = line.trim();
    
    // 检测对象开始
    if (trimmedLine.includes('{') && (
      trimmedLine.includes('StyleSheet.create') ||
      trimmedLine.includes('styles =') ||
      trimmedLine.includes(': {') ||
      trimmedLine.match(/^\s*\w+:\s*\{/)
    )) {
      inObject = true;
      objectDepth = (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
    }
    
    // 更新对象深度
    if (inObject) {
      objectDepth += (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
      if (objectDepth <= 0) {
        inObject = false;
      }
    }
    
    // 在对象内部修复属性定义
    if (inObject && nextLine) {
      const currentIndent = line.match(/^(\s*)/)[1];
      const nextIndent = nextLine.match(/^(\s*)/)[1];
      
      // 检查当前行是否是属性定义
      const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\n]+)$/);
      const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
      
      if (propertyMatch && nextPropertyMatch) {
        // 同一缩进层级的属性
        if (currentIndent.length === nextIndent.length) {
          const value = propertyMatch[3].trim();
          // 如果值不以逗号结尾且不是对象或数组的开始
          if (!value.endsWith(',') && !value.endsWith('{') && !value.endsWith('[')) {
            line = propertyMatch[1] + propertyMatch[2] + ': ' + value + ',';
          }
        }
      }
      
      // 特殊处理数字、字符串、布尔值
      const valueMatch = line.match(/^(\s*)(\w+):\s*([\d'"true|false][^,{}\n]*)$/);
      if (valueMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        if (!valueMatch[3].endsWith(',')) {
          line = valueMatch[1] + valueMatch[2] + ': ' + valueMatch[3] + ',';
        }
      }
      
      // 特殊处理函数值
      const functionMatch = line.match(/^(\s*)(\w+):\s*(\([^)]*\)\s*=>\s*[^,{}\n]+)$/);
      if (functionMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        if (!functionMatch[3].endsWith(',')) {
          line = functionMatch[1] + functionMatch[2] + ': ' + functionMatch[3] + ',';
        }
      }
    }
    
    fixedLines.push(line);
  }
  
  return fixedLines.join('\n');
}

// 特殊修复规则
function applySpecialFixes(content) {
  // 修复常见的对象属性错误模式
  
  // 修复 StyleSheet 对象
  content = content.replace(/(\w+):\s*\{([^}]+)\}(\n\s*)(\w+):/g, (match, prop1, styles, newline, prop2) => {
    if (!styles.trim().endsWith(',') && !match.includes(',')) {
      return `${prop1}: {${styles}},${newline}${prop2}:`;
    }
    return match;
  });
  
  // 修复简单属性值
  content = content.replace(/^(\s*)(\w+):\s*(['"`]?[^,{}\n]+['"`]?)(\n\s*)(\w+):/gm, (match, indent1, prop1, value, newline, prop2) => {
    if (!value.endsWith(',') && !value.includes('{') && !value.includes('[')) {
      return `${indent1}${prop1}: ${value},${newline}${prop2}:`;
    }
    return match;
  });
  
  // 修复数字属性值
  content = content.replace(/^(\s*)(\w+):\s*(\d+)(\n\s*)(\w+):/gm, (match, indent1, prop1, value, newline, prop2) => {
    return `${indent1}${prop1}: ${value},${newline}${prop2}:`;
  });
  
  // 修复布尔属性值
  content = content.replace(/^(\s*)(\w+):\s*(true|false)(\n\s*)(\w+):/gm, (match, indent1, prop1, value, newline, prop2) => {
    return `${indent1}${prop1}: ${value},${newline}${prop2}:`;
  });
  
  return content;
}

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

    // 应用精确对象属性修复
    const beforePrecisionFix = content;
    content = fixObjectPropertiesPrecision(content);
    if (content !== beforePrecisionFix) {
      fileFixCount += 1;
    }

    // 应用特殊修复规则
    const beforeSpecialFix = content;
    content = applySpecialFixes(content);
    if (content !== beforeSpecialFix) {
      fileFixCount += 1;
    }

    // 清理多余的逗号
    content = content.replace(/,(\s*[}\]])/g, '$1');
    content = content.replace(/,(\s*\))/g, '$1');

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

console.log('\n📊 对象属性精确修复报告');
console.log('==================================================');
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${filesFixed}`);
console.log(`✨ 总修复数: ${totalFixed}`);
console.log(`📈 修复率: ${Math.round((totalFixed / files.length) * 100)}%`);
console.log('🔧 对象属性精确修复完成！建议运行代码质量检查验证结果。'); 