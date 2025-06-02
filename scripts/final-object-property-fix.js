#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🎯 开始最终对象属性修复...\n');

// 精确的对象属性修复函数
function fixObjectPropertiesExact(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  let inStyleSheet = false;
  let inObject = false;
  let objectDepth = 0;
  let braceDepth = 0;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const nextLine = lines[i + 1];
    const trimmedLine = line.trim();

    // 跟踪大括号深度
    const openBraces = (line.match(/\{/g) || []).length;
    const closeBraces = (line.match(/\}/g) || []).length;
    braceDepth += openBraces - closeBraces;

    // 检测StyleSheet.create开始
    if (trimmedLine.includes('StyleSheet.create')) {
      inStyleSheet = true;
      inObject = true;
      objectDepth = braceDepth;
    }

    // 检测其他对象开始
    if (!inStyleSheet && (
      trimmedLine.match(/^\s*\w+:\s*\{/) ||
      trimmedLine.includes('= {') ||
      (trimmedLine.includes('{') && (
        trimmedLine.includes('interface') ||
        trimmedLine.includes('type') ||
        trimmedLine.includes('const') ||
        trimmedLine.includes('let') ||
        trimmedLine.includes('var')
      ))
    )) {
      inObject = true;
      objectDepth = braceDepth;
    }

    // 检测对象结束
    if (inObject && braceDepth <= objectDepth - 1) {
      inObject = false;
      inStyleSheet = false;
    }

    // 在对象内部修复属性定义
    if (inObject && nextLine) {
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
              !nextCloseBrace) {
            line = propertyMatch[1] + propertyMatch[2] + ': ' + value + ',';
          }
        }
      }

      // 特殊处理：数字、字符串、布尔值
      const simpleValueMatch = line.match(/^(\s*)(\w+):\s*([\d'"true|false][^,{}\n]*)$/);
      if (simpleValueMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        const value = simpleValueMatch[3].trim();
        if (!value.endsWith(',')) {
          line = simpleValueMatch[1] + simpleValueMatch[2] + ': ' + value + ',';
        }
      }

      // 特殊处理：函数值
      const functionMatch = line.match(/^(\s*)(\w+):\s*(\([^)]*\)\s*=>\s*[^,{}\n]+)$/);
      if (functionMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        const value = functionMatch[3].trim();
        if (!value.endsWith(',')) {
          line = functionMatch[1] + functionMatch[2] + ': ' + value + ',';
        }
      }

      // 特殊处理：对象值
      const objectValueMatch = line.match(/^(\s*)(\w+):\s*(\{[^}]*\})$/);
      if (objectValueMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        const value = objectValueMatch[3].trim();
        if (!value.endsWith(',')) {
          line = objectValueMatch[1] + objectValueMatch[2] + ': ' + value + ',';
        }
      }

      // 特殊处理：数组值
      const arrayValueMatch = line.match(/^(\s*)(\w+):\s*(\[[^\]]*\])$/);
      if (arrayValueMatch && nextPropertyMatch && currentIndent.length === nextIndent.length) {
        const value = arrayValueMatch[3].trim();
        if (!value.endsWith(',')) {
          line = arrayValueMatch[1] + arrayValueMatch[2] + ': ' + value + ',';
        }
      }
    }

    fixedLines.push(line);
  }

  return fixedLines.join('\n');
}

// 特殊文件修复规则
const specialFileRules = {
  'src/agents/xiaoai/config/XiaoaiConfigManager.tsx': (content) => {
    // 修复特殊的语法错误
    content = content.replace(/import AsyncStorage from '@react-native-async-storage\/async-storage'/g, 
      "import AsyncStorage from '@react-native-async-storage/async-storage';");
    content = content.replace(/\/\/ 配置键前缀\s*const CONFIG_KEY_PREFIX = 'xiaoai_config_';/g,
      "// 配置键前缀\nconst CONFIG_KEY_PREFIX = 'xiaoai_config_';");
    content = content.replace(/\/\/ 配置版本\s*const CONFIG_VERSION = '1\.0\.0';/g,
      "// 配置版本\nconst CONFIG_VERSION = '1.0.0';");
    return content;
  },
  
  'src/utils/fhir.ts': (content) => {
    // 修复FHIR文件的特殊错误
    content = content.replace(/^export interface Patient \{$/gm, 'export interface Patient {');
    return content;
  }
};

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

    // 应用特殊文件修复规则
    if (specialFileRules[filePath]) {
      const beforeContent = content;
      content = specialFileRules[filePath](content);
      if (content !== beforeContent) {
        fileFixCount += 1;
      }
    }

    // 应用精确对象属性修复
    const beforeObjectFix = content;
    content = fixObjectPropertiesExact(content);
    if (content !== beforeObjectFix) {
      fileFixCount += 1;
    }

    // 额外的清理工作
    // 清理多余的逗号
    content = content.replace(/,(\s*[}\]])/g, '$1');
    content = content.replace(/,(\s*\))/g, '$1');
    
    // 清理多余的分号
    content = content.replace(/;;+/g, ';');
    
    // 修复导入语句缺少分号
    content = content.replace(/(import\s+[^;\n]+)(\n)/g, (match, p1, p2) => {
      if (!p1.trim().endsWith(';')) {
        return p1 + ';' + p2;
      }
      return match;
    });

    // 修复导出语句缺少分号
    content = content.replace(/(export\s+[^;\n{]+)(\n)/g, (match, p1, p2) => {
      if (!p1.trim().endsWith(';') && !p1.includes('{') && !p1.includes('function') && !p1.includes('class')) {
        return p1 + ';' + p2;
      }
      return match;
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

console.log('\n📊 最终对象属性修复报告');
console.log('==================================================');
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${filesFixed}`);
console.log(`✨ 总修复数: ${totalFixed}`);
console.log(`📈 修复率: ${Math.round((totalFixed / files.length) * 100)}%`);
console.log('🎯 最终对象属性修复完成！建议运行代码质量检查验证结果。'); 