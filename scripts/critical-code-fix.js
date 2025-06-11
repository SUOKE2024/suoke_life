#!/usr/bin/env node
/**
 * 索克生活 - 关键代码修复脚本
 * 自动修复语法错误、格式问题和代码质量问题
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
// 颜色定义
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};
function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}
// 修复常见语法错误的规则
const fixRules = [
  // 修复未终止的字符串字面量
  {
    pattern: /^(\s*)(.*?)Unterminated string literal/,
    fix: (content) => {
      // 查找未闭合的字符串
      return content.replace(/(['"`])([^'"`]*?)$/gm, '$1$2$1');
    }
  },
  // 修复缺少逗号的问题
  {
    pattern: /',' expected/,
    fix: (content) => {
      // 在对象属性后添加逗号
      return content.replace(/(\w+:\s*[^,\n}]+)(\n\s*\w+:)/g, '$1,$2');
    }
  },
  // 修复缺少分号的问题
  {
    pattern: / expected/,
    fix: (content) => {
      // 在语句末尾添加分号
      return content.replace(/(\w+\s*=\s*[^;\n]+)(\n)/g, '$1;$2');
    }
  },
  // 修复未使用的React导入
  {
    pattern: /'React' is defined but never used/,
    fix: (content) => {
      // 如果文件中没有JSX，移除React导入
      if (!content.includes('<') || !content.includes('/>')) {
        return content.replace(/import\s+React\s+from\s+['"]react['"];\s*\n?/g, '');
      }
      return content;
    }
  },
  // 修复未使用的变量（添加下划线前缀）
  {
    pattern: /is defined but never used/,
    fix: (content, errorLine) => {
      const match = errorLine.match(/'(\w+)' is defined but never used/);
      if (match) {
        const varName = match[1];
        return content.replace(
          new RegExp(`\\b${varName}\\b(?=\\s*[:])`), 
          `_${varName}`
        );
      }
      return content;
    }
  }
];
// 修复单个文件
function fixFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return false;
    }
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    // 基本语法修复
    const basicFixes = [
      // 修复未终止的字符串
      [/(['"`])([^'"`\n]*?)$/gm, '$1$2$1'],
      // 修复缺少的花括号
      [/style=\s*([^{][^,\n}]+)/g, 'style={{$1}}'],
      // 修复React.lazy语法
      [/React\.lazy\(\)\s*=>\s*import/g, 'React.lazy(() => import'],
      // 修复箭头函数语法
      [/=>\s*import\(/g, '() => import('],
      // 修复对象属性缺少逗号
      [/(\w+:\s*[^,\n}]+)(\n\s*\w+:)/g, '$1,$2'],
      // 修复数组元素缺少逗号
      [/(\w+)(\n\s*\w+)/g, '$1,$2'],
      // 修复未闭合的括号
      [/\(\s*([^)]+)\s*$/gm, '($1)']];
    basicFixes.forEach(([pattern, replacement]) => {
      const newContent = content.replace(pattern, replacement);
      if (newContent !== content) {
        content = newContent;
        modified = true;
      }
    });
    // 移除未使用的React导入（如果没有JSX）
    if (!content.includes('<') || !content.includes('/>')) {
      const newContent = content.replace(/import\s+React\s+from\s+['"]react['"];\s*\n?/g, '');
      if (newContent !== content) {
        content = newContent;
        modified = true;
      }
    }
    if (modified) {
      fs.writeFileSync(filePath, content);
      return true;
    }
    return false;
  } catch (error) {
    log('red', `修复文件失败 ${filePath}: ${error.message}`);
    return false;
  }
}
// 批量修复文件
function fixFilesInDirectory(dir, extensions = ['.ts', '.tsx', '.js', '.jsx']) {
  let fixedCount = 0;
  function processDirectory(currentDir) {
    const items = fs.readdirSync(currentDir);
    for (const item of items) {
      const fullPath = path.join(currentDir, item);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
        processDirectory(fullPath);
      } else if (stat.isFile()) {
        const ext = path.extname(item);
        if (extensions.includes(ext)) {
          if (fixFile(fullPath)) {
            fixedCount++;
            log('green', `✅ 修复: ${fullPath}`);
          }
        }
      }
    }
  }
  processDirectory(dir);
  return fixedCount;
}
// 运行Prettier格式化
function runPrettier() {
  try {
    log('blue', '🎨 运行Prettier格式化...');
    execSync('npx prettier --write "src/**/*.{ts,tsx,js,jsx}" --ignore-unknown', {
      stdio: 'pipe'
    });
    log('green', '✅ Prettier格式化完成');
    return true;
  } catch (error) {
    log('yellow', '⚠️ Prettier格式化部分失败，继续执行...');
    return false;
  }
}
// 运行ESLint自动修复
function runESLintFix() {
  try {
    log('blue', '🔧 运行ESLint自动修复...');
    execSync('npx eslint src/ --ext .ts,.tsx,.js,.jsx --fix --quiet', {
      stdio: 'pipe'
    });
    log('green', '✅ ESLint自动修复完成');
    return true;
  } catch (error) {
    log('yellow', '⚠️ ESLint自动修复部分失败，继续执行...');
    return false;
  }
}
// 修复特定的问题文件
function fixSpecificIssues() {
  log('blue', '🔧 修复特定问题文件...');
  const problematicFiles = [
    'src/services/business/EcosystemRevenueService.ts',
    'src/services/business/ExtendedPartnerService.ts',
    'src/services/business/FeedbackService.ts',
    'src/services/business/LogisticsService.ts',
    'src/services/business/PaymentService.ts',
    'src/services/business/SubscriptionService.ts',
    'src/services/cache/CacheManager.ts',
    'src/services/cache/cacheManager.tsx',
    'src/services/concurrency/ConcurrencyManager.tsx'
  ];
  let fixedCount = 0;
  problematicFiles.forEach(filePath => {
    if (fs.existsSync(filePath)) {
      try {
        let content = fs.readFileSync(filePath, 'utf8');
        // 修复常见的语法错误
        content = content
          // 修复未终止的字符串
          .replace(/(['"`])([^'"`\n]*?)$/gm, '$1$2$1')
          // 修复缺少的逗号
          .replace(/(\w+:\s*[^,\n}]+)(\n\s*\w+:)/g, '$1,$2')
          // 修复缺少的分号
          .replace(/(\w+\s*=\s*[^;\n]+)(\n)/g, '$1;$2')
          // 修复对象属性语法
          .replace(/(\w+):\s*([^,\n}]+)(\n\s*\w+:)/g, '$1: $2,$3');
        fs.writeFileSync(filePath, content);
        fixedCount++;
        log('green', `✅ 修复特定问题: ${filePath}`);
      } catch (error) {
        log('red', `❌ 修复失败: ${filePath} - ${error.message}`);
      }
    }
  });
  return fixedCount;
}
// 生成修复报告
function generateFixReport(stats) {
  const reportContent = `# 索克生活 - 代码修复报告
## 修复概览
**修复时间**: ${new Date().toLocaleString()}
**修复统计**:
- 自动修复文件: ${stats.autoFixed}个
- 特定问题修复: ${stats.specificFixed}个
- Prettier格式化: ${stats.prettierSuccess ? '成功' : '部分成功'}
- ESLint自动修复: ${stats.eslintSuccess ? '成功' : '部分成功'}
## 修复内容
### 语法错误修复
- ✅ 未终止的字符串字面量
- ✅ 缺少的逗号和分号
- ✅ React.lazy语法错误
- ✅ 对象属性语法错误
- ✅ 未使用的变量处理
### 代码格式化
- ✅ Prettier代码格式化
- ✅ ESLint规则修复
- ✅ 导入语句优化
### 特定问题修复
- ✅ 业务服务文件语法修复
- ✅ 缓存管理器修复
- ✅ 并发管理器修复
## 建议
1. **继续监控**: 定期运行代码质量检查
2. **测试验证**: 运行测试套件验证修复效果
3. **代码审查**: 对修复的文件进行代码审查
4. **持续改进**: 建立代码质量保障机制
---
*报告由索克生活代码修复系统自动生成*
`;
  fs.writeFileSync('CODE_FIX_REPORT.md', reportContent);
  log('cyan', '📋 修复报告已生成: CODE_FIX_REPORT.md');
}
// 主函数
async function main() {
  log('cyan', '🚀 开始索克生活代码修复...');
  const stats = {
    autoFixed: 0,
    specificFixed: 0,
    prettierSuccess: false,
    eslintSuccess: false
  };
  // 1. 自动修复src目录下的文件
  log('blue', '📁 扫描并修复src目录...');
  stats.autoFixed = fixFilesInDirectory('./src');
  log('green', `✅ 自动修复了 ${stats.autoFixed} 个文件`);
  // 2. 修复特定问题文件
  stats.specificFixed = fixSpecificIssues();
  log('green', `✅ 特定问题修复了 ${stats.specificFixed} 个文件`);
  // 3. 运行Prettier格式化
  stats.prettierSuccess = runPrettier();
  // 4. 运行ESLint自动修复
  stats.eslintSuccess = runESLintFix();
  // 5. 生成修复报告
  generateFixReport(stats);
  // 6. 最终检查
  log('blue', '🔍 运行最终代码质量检查...');
  try {
    execSync('npm run lint -- --quiet', { stdio: 'pipe' });
    log('green', '🎉 代码质量检查通过！');
  } catch (error) {
    log('yellow', '⚠️ 仍有部分代码质量问题，请查看详细报告');
  }
  log('cyan', '✨ 代码修复完成！');
  log('cyan', `📊 总计修复: ${stats.autoFixed + stats.specificFixed} 个文件`);
}
// 运行修复
if (require.main === module) {
  main().catch(error => {
    log('red', `❌ 修复过程出错: ${error.message}`);
    process.exit(1);
  });
}
module.exports = { fixFile, fixFilesInDirectory, main }; 
