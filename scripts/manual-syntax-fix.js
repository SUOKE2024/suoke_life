#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🔧 开始手动语法修复...\n');

// 手动修复规则
const manualFixRules = [
  // 修复分号和逗号混合的错误
  {
    name: '修复分号逗号混合错误',
    pattern: /;(\s*;)+/g,
    replacement: ';'
  },
  
  // 修复多余的分号
  {
    name: '修复多余分号',
    pattern: /(\w+)\s*;\s*;/g,
    replacement: '$1'
  },
  
  // 修复对象属性值中的错误分号
  {
    name: '修复对象属性值错误分号',
    pattern: /:\s*([^,{}\[\]\n;]+?)\s*;\s*([;}])/g,
    replacement: ': $1$2'
  },
  
  // 修复字符串中的错误分号
  {
    name: '修复字符串错误分号',
    pattern: /(['"`][^'"`]*);([^'"`]*['"`])/g,
    replacement: '$1$2'
  },
  
  // 修复数组中的错误分号
  {
    name: '修复数组错误分号',
    pattern: /\[\s*;([^;\]]*)\s*;\s*\]/g,
    replacement: '[$1]'
  },
  
  // 修复函数参数中的错误分号
  {
    name: '修复函数参数错误分号',
    pattern: /\(\s*;([^;)]*)\s*;\s*\)/g,
    replacement: '($1)'
  },
  
  // 修复对象属性定义中的错误分号
  {
    name: '修复对象属性定义错误分号',
    pattern: /(\w+):\s*([^,{}\[\]\n;]+?)\s*;\s*([,}])/g,
    replacement: '$1: $2$3'
  },
  
  // 修复注释中的错误语法
  {
    name: '修复注释错误语法',
    pattern: /\/\*\s*\*\s*([^*]+)\s*\*\s*\*\//g,
    replacement: '// $1'
  },
  
  // 修复导入语句缺少分号
  {
    name: '修复导入语句缺少分号',
    pattern: /(import\s+[^;\n]+)(\n)/g,
    replacement: (match, importStatement, newline) => {
      if (!importStatement.trim().endsWith(';')) {
        return importStatement + ';' + newline;
      }
      return match;
    }
  }
];

// 特殊文件的手动修复
const specialFileFixRules = {
  'src/agents/AgentCoordinator.tsx': (content) => {
    // 修复特殊的语法错误
    content = content.replace(/conflict\.vote;s;/g, 'conflict.votes');
    content = content.replace(/\(a, ;b;\)/g, '(a, b)');
    content = content.replace(/capabilities: \[;/g, 'capabilities: [');
    content = content.replace(/return \{ response: `([^`]+)`, contex;t ;\}/g, 'return { response: `$1`, context }');
    content = content.replace(/confidence: 0\.;(\d+);/g, 'confidence: 0.$1');
    content = content.replace(/recommendations: ;\[;\]/g, 'recommendations: []');
    content = content.replace(/recordId: "([^"]+);";/g, 'recordId: "$1"');
    content = content.replace(/total;: ;(\d+)/g, 'total: $1');
    content = content.replace(/generated: tr;u;e/g, 'generated: true');
    content = content.replace(/version: "([^"]+);"/g, 'version: "$1"');
    
    return content;
  },
  
  'src/agents/xiaoai/XiaoaiAgentImpl.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },
  
  'src/services/enhancedI18nService.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },
  
  'src/services/mlTrainingService.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },
  
  'src/utils/codeSplitting.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },
  
  'src/utils/lazyLoader.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  }
};

// 深度修复对象属性
function deepFixObjectProperties(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const nextLine = lines[i + 1];
    
    // 修复对象属性后缺少逗号的情况
    if (nextLine) {
      const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\[\]\n;]+)$/);
      const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
      const nextCloseBrace = nextLine.trim().match(/^[}\]]/);
      
      if (propertyMatch && (nextPropertyMatch || nextCloseBrace)) {
        const [, indent, prop, value] = propertyMatch;
        const trimmedValue = value.trim();
        
        // 如果下一行是同级属性且当前行没有逗号
        if (nextPropertyMatch && !trimmedValue.endsWith(',') && !trimmedValue.endsWith(';')) {
          line = `${indent}${prop}: ${trimmedValue},`;
        }
      }
    }
    
    fixedLines.push(line);
  }
  
  return fixedLines.join('\n');
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

    // 应用手动修复规则
    manualFixRules.forEach(rule => {
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

    // 最终清理
    content = content.replace(/\s+$/gm, ''); // 清理行尾空格
    content = content.replace(/;;+/g, ';'); // 清理多余分号
    content = content.replace(/,,+/g, ','); // 清理多余逗号

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

console.log(`\n📊 手动语法修复报告`);
console.log(`==================================================`);
console.log(`📁 总文件数: ${files.length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((totalFixCount / files.length) * 100).toFixed(1)}%`);
console.log(`🔧 手动语法修复完成！建议运行代码质量检查验证结果。`); 