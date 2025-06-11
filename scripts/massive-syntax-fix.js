const fs = require('fs');
const path = require('path');
console.log('🚀 开始大规模语法修复...');
console.log('==================================================');
// 获取所有需要修复的文件
function getAllFiles(dir, extensions = ['.ts', '.tsx', '.js', '.jsx']) {
  const files = [];
  try {
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const fullPath = path.join(dir, item);
      try {
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
          files.push(...getAllFiles(fullPath, extensions));
        } else if (extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      } catch (error) {
        console.log(`⚠️ 跳过文件 ${fullPath}: ${error.message}`);
      }
    }
  } catch (error) {
    console.log(`⚠️ 跳过目录 ${dir}: ${error.message}`);
  }
  return files;
}
// 强力语法修复
function massiveSyntaxFix(content) {
  let fixed = content;
  let fixCount = 0;
  // 1. 修复所有未终止的字符串字面量
  const patterns = [
    // 修复import语句
    { pattern: /import\s+.*?from\s+['"][^'"]*$/gm, fix: (match) => match + ", desc: "import语句" },
    { pattern: /import\s+.*?from\s+['"][^'"]*['"][^;]*$/gm, fix: (match) => match.replace(/['"]([^'"]*)['"]([^;]*)$/, "'$1), desc: "import语句结尾" },
    // 修复export语句
    { pattern: /export\s+.*?from\s+['"][^'"]*$/gm, fix: (match) => match + ", desc: "export语句" },
    // 修复字符串字面量
    { pattern: /(['"`])([^'"`\\n]*?)$/gm, fix: (match, quote, content) => quote + content + quote, desc: "字符串字面量" },
    // 修复对象属性
    { pattern: /(\w+):\s*(['"`])([^'"`]*?)$/gm, fix: (match, prop, quote, value) => `${prop}: ${quote}${value}${quote}`, desc: "对象属性" },
    // 修复函数调用
    { pattern: /(\w+)\(([^)]*?)$/gm, fix: (match, func, args) => `${func}(${args})`, desc: "函数调用" },
    // 修复JSX属性
    { pattern: /(\w+)={(['"`])([^'"`]*?)$/gm, fix: (match, attr, quote, value) => `${attr}={${quote}${value}${quote}}`, desc: "JSX属性" },
    // 修复注释
    { pattern: /\/\/([^/\n]*?)$/gm, fix: (match, comment) => `//${comment}`, desc: "单行注释" },
    // 修复正则表达式
    { pattern: /\/([^/\n]*?)$/gm, fix: (match, regex) => `/${regex}/`, desc: "正则表达式" },
    // 修复模板字符串
    { pattern: /`([^`]*?)$/gm, fix: (match, template) => `\`${template}\``, desc: "模板字符串" },
    // 修复数组
    { pattern: /\[([^\]]*?)$/gm, fix: (match, array) => `[${array}]`, desc: "数组" },
    // 修复对象
    { pattern: /{([^}]*?)$/gm, fix: (match, obj) => `{${obj}}`, desc: "对象" },
    // 修复括号
    { pattern: /\(([^)]*?)$/gm, fix: (match, paren) => `(${paren})`, desc: "括号" },
    // 修复分号
    { pattern: /([^;{}\n])$/gm, fix: (match, line) => `${line};`, desc: "分号" }];
  patterns.forEach(({ pattern, fix, desc }) => {
    const matches = fixed.match(pattern);
    if (matches) {
      fixed = fixed.replace(pattern, fix);
      fixCount += matches.length;
      console.log(`  ✅ 修复 ${matches.length} 个 ${desc}`);
    }
  });
  // 2. 修复特殊语法错误
  const specialFixes = [
    // 修复多余的引号和符号
    { pattern: /'''/g, fix: "'", desc: "多余引号" },
    { pattern: /"""/g, fix: '"', desc: "多余双引号" },
    { pattern: /\/g$/gm, fix: '', desc: "行尾/g" },
    { pattern: /;'''/g, fix: , desc: "分号后多余引号" },
    { pattern: /,'''/g, fix: ',', desc: "逗号后多余引号" },
    { pattern: /}'''/g, fix: '}', desc: "大括号后多余引号" },
    { pattern: />'''/g, fix: '>', desc: "大于号后多余引号" },
    { pattern: /\)'''/g, fix: ')', desc: "括号后多余引号" },
    // 修复错误的语法结构
    { pattern: /\s*\/g\s*$/gm, fix: '', desc: "行尾/g标记" },
    { pattern: /\s*'''\s*$/gm, fix: '', desc: "行尾三引号" },
    { pattern: /\s*\/\/g\s*$/gm, fix: '', desc: "行尾//g标记" },
    // 修复JSX语法
    { pattern: /<([^>]*?)\/>/g, fix: '<$1 />', desc: "JSX自闭合标签" },
    { pattern: /<\/([^>]*?)>/g, fix: '</$1>', desc: "JSX闭合标签" },
    // 修复TypeScript语法
    { pattern: /:\s*([^;})\n]*?);/g, fix: ': $1;', desc: "TypeScript类型注解" },
    // 修复React组件
    { pattern: /React\.lazy\(\s*\(\)\s*=>\s*import\((['"`])([^'"`]*?)\1\)\s*\)/g, 
      fix: "React.lazy(() => import('$2'))", desc: "React.lazy导入" }];
  specialFixes.forEach(({ pattern, fix, desc }) => {
    const beforeLength = fixed.length;
    fixed = fixed.replace(pattern, fix);
    const afterLength = fixed.length;
    if (beforeLength !== afterLength) {
      fixCount++;
      console.log(`  ✅ 修复 ${desc}`);
    }
  });
  return { fixed, fixCount };
}
// 处理单个文件
function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const { fixed, fixCount } = massiveSyntaxFix(content);
    if (fixCount > 0) {
      fs.writeFileSync(filePath, fixed, 'utf8');
      console.log(`✅ ${filePath}: 修复 ${fixCount} 个问题`);
      return fixCount;
    }
    return 0;
  } catch (error) {
    console.log(`❌ 处理文件失败 ${filePath}: ${error.message}`);
    return 0;
  }
}
// 主修复流程
function main() {
  const files = getAllFiles('src');
  console.log(`📁 找到 ${files.length} 个文件需要检查`);
  let totalFixes = 0;
  let processedFiles = 0;
  files.forEach(file => {
    const fixes = processFile(file);
    if (fixes > 0) {
      processedFiles++;
      totalFixes += fixes;
    }
  });
  console.log('==================================================');
  console.log(`✅ 大规模语法修复完成!`);
  console.log(`📊 处理了 ${processedFiles} 个文件`);
  console.log(`🔧 总共修复 ${totalFixes} 个问题`);
}
main(); 
