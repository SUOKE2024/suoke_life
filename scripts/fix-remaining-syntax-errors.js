#!/usr/bin/env node;
const fs = require("fs");
const path = require("path");
const glob = require("glob");

/**
 * 剩余语法错误修复脚本
 * 处理特定的语法错误模式
 */

// 特定错误修复规则
const specificFixRules = [
  // 修复未终止的字符串字面量 - 测试文件
  {
    name: '测试文件未终止字符串',
    pattern: /describe\(['"]([^'"]*?)$/gm,
    replacement: 'describe("$1", () => {'
  },
  {
    name: '测试文件未终止字符串2',
    pattern: /it\(['"]([^'"]*?)$/gm,
    replacement: 'it("$1", () => {'
  },
  // 修复import语句错误
  {
    name: 'import语句缺少分号',
    pattern: /import\s+([^"']+)\s+from\s+["']([^"']+)["'](?!;)/g,
    replacement: 'import $1 from "$2";'
  },
  // 修复export语句错误
  {
    name: 'export语句缺少分号',
    pattern: /export\s+([^;]+)(?!;)$/gm,
    replacement: 'export $1;'
  },
  // 修复对象属性错误
  {
    name: '对象属性逗号错误',
    pattern: /(\w+):\s*,\s*(\w+):/g,
    replacement: '$1: undefined,\n  $2:'
  },
  // 修复箭头函数错误
  {
    name: '箭头函数期望错误',
    pattern: /(\w+)\s*expected/g,
    replacement: '$1'
  },
  // 修复标识符错误
  {
    name: '标识符期望错误',
    pattern: /Unknown keyword or identifier\. Did you mean '([^']+)'\?/g,
    replacement: '$1'
  },
  // 修复声明语句错误
  {
    name: '声明语句期望',
    pattern: /Declaration or statement expected/g,
    replacement: ''
  },
  // 修复表达式期望错误
  {
    name: '表达式期望',
    pattern: /Expression expected/g,
    replacement: ''
  }
];

// 文件特定修复函数
const fileSpecificFixes = {
  // 修复测试文件
  fixTestFiles: (content, filePath) => {
    if (filePath.includes('test') || filePath.includes('spec')) {
      // 修复测试文件的import语句
      content = content.replace(/import\s+([^"']+)\s+from\s+["']([^"']*?)$/gm, 'import $1 from "$2";');
      // 修复describe和it语句
      content = content.replace(/describe\(['"]([^'"]*?)$/gm, 'describe("$1", () => {');
      content = content.replace(/it\(['"]([^'"]*?)$/gm, 'it("$1", () => {');
      // 添加缺少的结束括号
      const openBraces = (content.match(/\{/g) || []).length;
      const closeBraces = (content.match(/\}/g) || []).length;
      if (openBraces > closeBraces) {
        content += '\n' + '});'.repeat(openBraces - closeBraces);
      }
    }
    return content;
  },

  // 修复import/export文件
  fixImportExport: (content) => {
    // 修复import语句
    content = content.replace(/import\s+([^"']+)\s+from\s+["']([^"']+)["'](?!;)/g, 'import $1 from "$2";');
    // 修复export语句
    content = content.replace(/export\s+([^;{]+)(?!;)$/gm, 'export $1;');
    // 修复export default
    content = content.replace(/export\s+default\s+([^;]+)(?!;)$/gm, 'export default $1;');
    return content;
  },

  // 修复类型定义文件
  fixTypeFiles: (content, filePath) => {
    if (filePath.endsWith('.d.ts') || filePath.includes('types/')) {
      // 修复接口定义
      content = content.replace(/interface\s+(\w+)\s*\{([^}]*?)$/gm, 'interface $1 {\n$2\n}');
      // 修复类型定义
      content = content.replace(/type\s+(\w+)\s*=\s*([^;]+)(?!;)$/gm, 'type $1 = $2;');
      // 修复枚举定义
      content = content.replace(/enum\s+(\w+)\s*\{([^}]*?)$/gm, 'enum $1 {\n$2\n}');
    }
    return content;
  },

  // 修复React组件文件
  fixReactFiles: (content, filePath) => {
    if (filePath.endsWith('.tsx') || filePath.endsWith('.jsx')) {
      // 修复React import
      if (!content.includes('import React') && content.includes('React.')) {
        content = 'import React from "react";\n' + content;
      }
      // 修复组件导出
      content = content.replace(/export\s+default\s+(\w+)(?!;)$/gm, 'export default $1;');
      // 修复JSX语法
      content = content.replace(/<([A-Z]\w*)\s+([^>]*?)(?<!\/)\s*$/gm, '<$1 $2 />');
    }
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
      ignore: ['**/node_modules/**'] 
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
    
    // 应用文件特定修复
    const beforeSpecialFix = content;
    content = fileSpecificFixes.fixTestFiles(content, filePath);
    content = fileSpecificFixes.fixImportExport(content);
    content = fileSpecificFixes.fixTypeFiles(content, filePath);
    content = fileSpecificFixes.fixReactFiles(content, filePath);
    
    if (content !== beforeSpecialFix) {
      appliedRules.push('文件特定修复');
      fixCount++;
    }
    
    // 应用特定修复规则
    specificFixRules.forEach(rule => {
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
    
    // 通用清理
    content = content.replace(/;;+/g, ';'); // 移除重复分号
    content = content.replace(/\n\n\n+/g, '\n\n'); // 移除多余空行
    content = content.replace(/\s+$/gm, ''); // 移除行尾空格
    
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
  console.log("🔧 开始修复剩余语法错误...\n");
  
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
    console.log("\n✨ 剩余错误修复完成！建议运行 npm run lint 验证结果");
  } else {
    console.log("\n✅ 没有发现需要修复的剩余语法错误");
  }
}

if (require.main === module) {
  main();
}

module.exports = { fixFile, getFilesToFix }; 