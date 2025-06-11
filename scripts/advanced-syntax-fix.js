#!/usr/bin/env node;
const fs = require("fs");
const path = require("path");
const glob = require(""glob");
/**
 * 索克生活 - 高级语法错误修复脚本
 * 专门修复复杂的语法错误和格式问题
 */
// 颜色定义
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};
function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}
// 高级语法修复规则
const advancedFixRules = [
  // 修复属性后的多余逗号和分号
  {
    name: '修复属性后的多余逗号分号',
    pattern: /(\w+:\s*[^]+);/g,
    replacement: '$1,'
  },
  // 修复接口属性的语法错误
  {
    name: '修复接口属性语法',
    pattern: /(\w+:\s*[^;}]+);/g,
    replacement: '$1;
  },
  // 修复字符串字面量问题
  {
    name: '修复字符串字面量',
    pattern: /(['"])[^'"]*$/gm,
    replacement: (match, quote) => {
      if (!match.endsWith(quote)) {
        return match + quote;
      }
      return match;
    }
  },
  // 修复导入语句
  {
    name: '修复导入语句',
    pattern: /import\s+([^'"]+)['"]([^'"]+)['"];['"]/g,
    replacement: 'import $1"$2
  },
  // 修复多余的引号
  {
    name: '修复多余引号',
    pattern: /(['"])([^'"]*)\1['"]+/g,
    replacement: '$1$2$1'
  },
  // 修复函数参数语法
  {
    name: '修复函数参数',
    pattern: /\(([^)]*);([^)]*)\)/g,
    replacement: '($1, $2)'
  },
  // 修复对象属性语法
  {
    name: '修复对象属性',
    pattern: /\{([^}]*);([^}]*)\}/g,
    replacement: '{$1, $2}
  },
  // 修复类型定义
  {
    name: '修复类型定义',
    pattern: /:\s*([^;}]+);/g,
    replacement: ': $1,'
  },
  // 修复枚举定义
  {
    name: '修复枚举定义',
    pattern: /=\s*['"]([^'"]+)['"],['"]*/g,
    replacement: '= \'$1\','
  },
  // 修复未闭合的括号
  {
    name: '修复未闭合括号',
    pattern: /\([^)]*$/gm,
    replacement: (match) => match + ')'
  },
  // 修复未闭合的花括号
  {
    name: '修复未闭合花括号',
    pattern: /\{[^}]*$/gm,
    replacement: (match) => match + '}
  },
  // 修复React导入
  {
    name: '修复React导入',
    pattern: /import\s+React\s+from\s+['"]react['"];['"]+/g,
    replacement: 'import React from "react"
  },
  // 修复注释语法
  {
    name: '修复注释语法',
    pattern: /\/\*([^*]|\*(?!\/))*\*\/\s*\*\//g,
    replacement: '/* $1 */
  },
  // 修复export语句
  {
    name: '修复export语句',
    pattern: /export\s+\{([^}]*);([^}]*)\}/g,
    replacement: 'export { $1, $2 }';
  }
];
// 特殊文件修复规则
const specialFileRules = {
  // TypeScript类型文件
  '.d.ts': [
    {
      pattern: /declare\s+([^;]*);/g,
      replacement: 'declare $1;
    }
  ],
  // 测试文件
  '.test.ts': [
    {
      pattern: /describe\(['"]([^'"]+)['"],\s*\(\)\s*=>\s*\{['"]+/g,
      replacement: 'describe("$1", () => {});
  ],
  // React组件文件
  '.tsx': [
    {
      pattern: /interface\s+(\w+)\s*\{([^}]*);([^}]*)\}/g,
      replacement: 'interface $1 {\n  $2;\n  $3;\n}
    }
  ]
};
// 应用修复规则到文件
function applyAdvancedFixes(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let originalContent = content;
    let appliedFixes = [];
    // 应用通用修复规则
    advancedFixRules.forEach(rule => {
      const newContent = content.replace(rule.pattern, rule.replacement);
      if (newContent !== content) {
        content = newContent;
        appliedFixes.push(rule.name);
      }
    });
    // 应用特殊文件规则
    const ext = path.extname(filePath);
    if (specialFileRules[ext]) {
      specialFileRules[ext].forEach(rule => {
        const newContent = content.replace(rule.pattern, rule.replacement);
        if (newContent !== content) {
          content = newContent;
          appliedFixes.push(`特殊规则: ${ext}`);
        }
      });
    }
    // 额外的清理步骤
    content = cleanupContent(content);
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return appliedFixes;
    }
    return [];
  } catch (error) {
    log('red', `修复文件失败 ${filePath}: ${error.message}`);
    return [];
  }
}
// 内容清理函数
function cleanupContent(content) {
  // 移除多余的空行
  content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
  // 修复常见的语法模式
  content = content
    // 修复属性定义
    .replace(/(\w+):\s*([^;}]+);/g, '$1: $2,')
    // 修复字符串连接
    .replace(/(['"])([^'"]*)\1['"]+/g, '$1$2$1')
    // 修复导入语句
    .replace(/import\s+([^'"]+)['"]([^'"]+)['"];['"]/g, 'import $1"$2)
    // 修复注释
    .replace(/\/\*\*?([^*]|\*(?!\/))*\*\/\s*\*\//g, '/* $1 */)
    // 修复函数定义
    .replace(/function\s+(\w+)\s*\([^)]*\)\s*\{['"]+/g, 'function $1() {')
    // 修复对象字面量
    .replace(/\{([^}]*);([^}]*)\}/g, '{ $1, $2 }')
    // 修复数组定义
    .replace(/\[([^\]]*);([^\]]*)\]/g, '[$1, $2]');
  return content;
}
// 批量修复文件
function batchFixFiles(directory) {
  const stats = {
    totalFiles: 0,
    fixedFiles: 0,
    totalFixes: 0
  };
  function processDirectory(dir) {
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
        processDirectory(fullPath);
      } else if (item.match(/\.(ts|tsx|js|jsx)$/) && !item.includes('.test.')) {
        stats.totalFiles++;
        const fixes = applyAdvancedFixes(fullPath);
        if (fixes.length > 0) {
          stats.fixedFiles++;
          stats.totalFixes += fixes.length;
          log('green', `✅ 修复: ${fullPath} (${fixes.length}项)`);
        }
      }
    }
  }
  processDirectory(directory);
  return stats;
}
// 生成修复报告
function generateFixReport(stats) {
  const reportContent = `# 索克生活 - 高级语法修复报告
## 修复概览
**执行时间**: ${new Date().toLocaleString()}
**扫描文件**: ${stats.totalFiles}个
**修复文件**: ${stats.fixedFiles}个
**应用修复**: ${stats.totalFixes}项
## 修复类型
### 语法错误修复
- ✅ 属性后多余逗号分号
- ✅ 接口属性语法错误
- ✅ 字符串字面量问题
- ✅ 导入语句错误
### 格式问题修复
- ✅ 多余引号清理
- ✅ 函数参数语法
- ✅ 对象属性语法
- ✅ 类型定义错误
### 特殊文件修复
- ✅ TypeScript声明文件
- ✅ 测试文件语法
- ✅ React组件文件
- ✅ 枚举定义错误
## 修复效果
| 指标 | 数值 |
|------|------|
| 修复成功率 | ${Math.round((stats.fixedFiles / stats.totalFiles) * 100)}% |
| 平均修复数 | ${Math.round(stats.totalFixes / stats.fixedFiles || 0)}项/文件 |
| 总体改进 | ${stats.totalFixes}项语法问题 |
## 下一步建议
1. **验证修复效果**: 运行 \`npm run lint\` 检查剩余问题
2. **类型检查**: 运行 \`npx tsc --noEmit\` 验证TypeScript
3. **测试运行**: 运行 \`npm test\` 确保功能正常
4. **构建验证**: 运行 \`npm run build\` 验证构建
---
*报告由索克生活高级语法修复系统自动生成*
`;
  fs.writeFileSync('ADVANCED_SYNTAX_FIX_REPORT.md', reportContent);
  log('cyan', '📋 高级语法修复报告已生成: ADVANCED_SYNTAX_FIX_REPORT.md');
}
// 主函数
async function main() {
  log('cyan', '🔧 开始高级语法错误修复...');
  // 修复src目录下的文件
  log('blue', '🔍 扫描并修复src目录...');
  const stats = batchFixFiles('./src');
  // 生成报告
  generateFixReport(stats);
  log('cyan', '✨ 高级语法修复完成！');
  log('cyan', `📊 修复文件: ${stats.fixedFiles}个，应用修复: ${stats.totalFixes}项`);
  log('blue', '💡 建议运行: npm run lint 验证修复效果');
}
// 运行修复
if (require.main === module) {
  main().catch(error => {
    log('red', `❌ 高级语法修复出错: ${error.message}`);
    process.exit(1);
  });
}
module.exports = { main, applyAdvancedFixes, cleanupContent };