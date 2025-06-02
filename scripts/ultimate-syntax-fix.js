#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🚀 开始终极语法修复...\n');

// 终极修复规则
const ultimateFixRules = [
  // 修复导入语句缺少分号
  {
    name: '导入语句缺少分号',
    pattern: /(import\s+[^;\n]+)(\n)/g,
    replacement: (match, p1, p2) => {
      if (!p1.trim().endsWith(';')) {
        return p1 + ';' + p2;
      }
      return match;
    }
  },
  
  // 修复导出语句缺少分号
  {
    name: '导出语句缺少分号',
    pattern: /(export\s+[^;\n{]+)(\n)/g,
    replacement: (match, p1, p2) => {
      if (!p1.trim().endsWith(';') && !p1.includes('{') && !p1.includes('function') && !p1.includes('class')) {
        return p1 + ';' + p2;
      }
      return match;
    }
  },

  // 修复对象属性定义错误
  {
    name: '对象属性缺少逗号',
    pattern: /^(\s*)(\w+):\s*([^,{}\n;]+)(\n\s*)(\w+):/gm,
    replacement: (match, indent1, prop1, value, newline, prop2) => {
      const trimmedValue = value.trim();
      if (!trimmedValue.endsWith(',') && !trimmedValue.endsWith(';') && !trimmedValue.endsWith('{') && !trimmedValue.endsWith('[')) {
        return `${indent1}${prop1}: ${trimmedValue},${newline}${prop2}:`;
      }
      return match;
    }
  },

  // 修复数字属性值
  {
    name: '数字属性值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(\d+(?:\.\d+)?)(\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 修复布尔属性值
  {
    name: '布尔属性值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(true|false)(\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  },

  // 修复字符串属性值
  {
    name: '字符串属性值缺少逗号',
    pattern: /^(\s*)(\w+):\s*(['"`][^'"`]*['"`])(\n\s*)(\w+):/gm,
    replacement: '$1$2: $3,$4$5:'
  }
];

// 特殊文件修复规则
const specialFileRules = {
  'src/agents/xiaoai/config/XiaoaiConfigManager.tsx': (content) => {
    // 修复复杂的语法错误
    content = content.replace(/importAsyncStorage/g, 'import AsyncStorage');
    content = content.replace(/\/import/g, '// import');
    content = content.replace(/\/;/g, ';');
    content = content.replace(/\*\s*\*\//g, '*/');
    content = content.replace(/;\s*\*\s*\*\/\//g, ';');
    content = content.replace(/\*\s*([^*]+)\s*\*\//g, '// $1');
    content = content.replace(/const CONFIG_KEY_PREFIX = 'xiaoai_config;_;';/g, "const CONFIG_KEY_PREFIX = 'xiaoai_config_';");
    content = content.replace(/const CONFIG_VERSION = '1\.0\.;0;';/g, "const CONFIG_VERSION = '1.0.0';");
    return content;
  },
  
  'src/agents/AgentCoordinator.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/agents/xiaoai/XiaoaiAgentImpl.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  }
};

// 复杂对象属性修复函数
function fixComplexObjectProperties(content) {
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
      trimmedLine.match(/^\s*\w+:\s*\{/)
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
      
      // 检查当前行是否是属性定义
      const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\n]+)$/);
      const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
      const nextCloseBrace = nextLine.trim() === '}';

      if (propertyMatch && (nextPropertyMatch || nextCloseBrace)) {
        // 同一缩进层级的属性或对象结束
        if (currentIndent.length === nextIndent.length || nextCloseBrace) {
          const value = propertyMatch[3].trim();
          // 如果值不以逗号结尾且不是对象或数组的开始
          if (!value.endsWith(',') && !value.endsWith('{') && !value.endsWith('[') && !nextCloseBrace) {
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
  
  // 清理错误的注释格式
  content = content.replace(/\/\*\s*\*\//g, '//');
  content = content.replace(/\/\*\s*([^*]+)\s*\*\//g, '// $1');
  
  // 清理错误的字符
  content = content.replace(/;,/g, ',');
  content = content.replace(/,;/g, ',');
  
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

    // 应用特殊文件修复规则
    if (specialFileRules[filePath]) {
      const beforeContent = content;
      content = specialFileRules[filePath](content);
      if (content !== beforeContent) {
        fileFixCount += 1;
      }
    }

    // 应用终极修复规则
    ultimateFixRules.forEach(rule => {
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

    // 应用复杂对象属性修复
    const beforeComplexFix = content;
    content = fixComplexObjectProperties(content);
    if (content !== beforeComplexFix) {
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
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${filePath} (修复 ${fileFixCount} 处)`);
      totalFixed += fileFixCount;
      filesFixed++;
    }

  } catch (error) {
    console.log(`❌ ${filePath} (修复失败: ${error.message})`);
  }
});

console.log('\n📊 终极语法修复报告');
console.log('==================================================');
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${filesFixed}`);
console.log(`✨ 总修复数: ${totalFixed}`);
console.log(`📈 修复率: ${Math.round((totalFixed / files.length) * 100)}%`);
console.log('🚀 终极语法修复完成！建议运行代码质量检查验证结果。'); 