#!/usr/bin/env node

/**
 * 高级语法错误修复脚本
 * 处理更复杂的语法错误，如未终止的字符串、注释、正则表达式等
 */

const fs = require("fs");
const path = require("path");
const glob = require("glob");

// 高级修复规则
const advancedFixRules = [
  // 修复未终止的字符串字面量
  {
    name: '未终止的字符串字面量',
    pattern: /import\s+([^"']+)\s+from\s+["']([^"']*?)$/gm,
    replacement: 'import $1 from "$2";'
  },
  // 修复未终止的正则表达式
  {
    name: '未终止的正则表达式',
    pattern: /\/([^\/\n]*?)$/gm,
    replacement: (match, content) => {
      if (content.includes('*') || content.includes('+') || content.includes('?')) {
        return `/${content}/`;
      }
      return `// ${content}`;
    }
  },
  // 修复未闭合的注释
  {
    name: '未闭合的注释',
    pattern: /\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*$/gm,
    replacement: (match) => match + ' */'
  },
  // 修复错误的标识符
  {
    name: '错误的标识符',
    pattern: /Unknown keyword or identifier\. Did you mean '([^']+)'\?/g,
    replacement: '$1'
  },
  // 修复缺少分号
  {
    name: '缺少分号',
    pattern: /(\w+)\s*$/gm,
    replacement: (match, word, offset, string) => {
      // 检查是否在行末且不是关键字
      const keywords = ['import', 'export', 'const', 'let', 'var', 'function', 'class', 'interface', 'type'];
      if (!keywords.includes(word)) {
        return word + ';';
      }
      return match;
    }
  },
  // 修复对象语法错误
  {
    name: '对象属性语法',
    pattern: /(\w+):\s*,/g,
    replacement: '$1: undefined,'
  },
  // 修复箭头函数语法
  {
    name: '箭头函数语法',
    pattern: /=>\s*$/gm,
    replacement: '=> {}'
  },
  // 修复枚举成员
  {
    name: '枚举成员',
    pattern: /enum\s+(\w+)\s*\{\s*,/g,
    replacement: 'enum $1 {'
  },
  // 修复泛型语法
  {
    name: '泛型语法',
    pattern: />\s*expected/g,
    replacement: '>'
  }
];

// 特殊文件修复规则
const specialFileRules = {
  // 修复import语句
  fixImports: (content) => {
    // 修复未闭合的import语句
    content = content.replace(/import\s+([^"']+)\s+from\s+["']([^"']*?)$/gm, 'import $1 from "$2";');
    // 修复重复的import
    content = content.replace(/import\s+([^"']+)\s+from\s+["']([^"']*?)["']\s*import/g, 'import $1 from "$2";\nimport');
    return content;
  },
  
  // 修复注释
  fixComments: (content) => {
    // 修复未闭合的块注释
    content = content.replace(/\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*$/gm, (match) => match + ' */');
    // 修复错误的注释语法
    content = content.replace(/\/;/g, '//');
    return content;
  },
  
  // 修复字符串
  fixStrings: (content) => {
    // 修复未闭合的字符串
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      // 检查是否有未闭合的字符串
      const singleQuoteCount = (line.match(/'/g) || []).length;
      const doubleQuoteCount = (line.match(/"/g) || []).length;
      
      if (singleQuoteCount % 2 !== 0) {
        lines[i] = line + "'";
      }
      if (doubleQuoteCount % 2 !== 0) {
        lines[i] = line + '"';
      }
    }
    return lines.join('\n');
  },
  
  // 修复正则表达式
  fixRegex: (content) => {
    // 修复未闭合的正则表达式
    content = content.replace(/\/([^\/\n]*?)$/gm, (match, regexContent) => {
      if (regexContent.includes('*') || regexContent.includes('+') || regexContent.includes('?')) {
        return `/${regexContent}/`;
      }
      return `// ${regexContent}`;
    });
    return content;
  },
  
  // 修复对象和数组语法
  fixObjectArray: (content) => {
    // 修复对象开始语法错误
    content = content.replace(/\{,/g, '{');
    // 修复对象结束语法错误
    content = content.replace(/,\s*\}/g, '}');
    // 修复数组语法错误
    content = content.replace(/\[,/g, '[');
    content = content.replace(/,\s*\]/g, ']');
    return content;
  },
  
  // 修复函数语法
  fixFunctions: (content) => {
    // 修复箭头函数
    content = content.replace(/=>\s*$/gm, '=> {}');
    // 修复函数调用
    content = content.replace(/(\w+)\s*\.\s*\(/g, '$1.(');
    return content;
  }
};

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
    
    // 应用特殊文件修复规则
    const beforeSpecialFix = content;
    content = specialFileRules.fixImports(content);
    content = specialFileRules.fixComments(content);
    content = specialFileRules.fixStrings(content);
    content = specialFileRules.fixRegex(content);
    content = specialFileRules.fixObjectArray(content);
    content = specialFileRules.fixFunctions(content);
    
    if (content !== beforeSpecialFix) {
      appliedRules.push('特殊语法修复');
      fixCount++;
    }
    
    // 应用高级修复规则
    advancedFixRules.forEach(rule => {
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
    
    // 最后清理
    content = content.replace(/;;+/g, ';'); // 移除重复分号
    content = content.replace(/\n\n\n+/g, '\n\n'); // 移除多余空行
    
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
  console.log("🔧 开始高级语法错误修复...\n");
  
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
    console.log("\n✨ 高级修复完成！建议运行 npm run lint 验证结果");
  } else {
    console.log("\n✅ 没有发现需要修复的高级语法错误");
  }
}

if (require.main === module) {
  main();
}

module.exports = { fixFile, getFilesToFix }; 