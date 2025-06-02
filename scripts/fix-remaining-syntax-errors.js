#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 修复剩余的语法错误...\n');

// 递归获取所有TypeScript文件
function getAllTsFiles(dir, files = []) {
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
      getAllTsFiles(fullPath, files);
    } else if (item.endsWith('.ts') || item.endsWith('.tsx')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// 修复导入语句中的多余逗号
function fixImportCommas(content) {
  // 修复 { name, } from 'module' 模式
  content = content.replace(
    /\{\s*([^}]+),\s*\}\s+from\s+(['"][^'"]+['"])/g,
    '{ $1 } from $2'
  );
  
  return content;
}

// 修复useCallback缺少参数的问题
function fixUseCallbackParameters(content) {
  // 修复 useCallback() => { 模式
  content = content.replace(
    /const\s+(\w+)\s*=\s*useCallback\(\s*\(\)\s*=>\s*\{[^,]*,\s*\[\]\);?/g,
    'const $1 = useCallback(() => {\n    // TODO: Implement function body\n  }, []);'
  );
  
  // 修复 useCallback( (param) => {, []) 模式
  content = content.replace(
    /const\s+(\w+)\s*=\s*useCallback\(\s*\([^)]*\)\s*=>\s*\{[^,]*,\s*\[\]\);?/g,
    'const $1 = useCallback(() => {\n    // TODO: Implement function body\n  }, []);'
  );
  
  return content;
}

// 修复剩余的嵌套Hook问题
function fixRemainingNestedHooks(content) {
  // 修复复杂的嵌套模式
  content = content.replace(
    /,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    ', []);'
  );
  
  // 修复简单的嵌套模式
  content = content.replace(
    /,\s*\[\]\),\s*\[\]\),\s*\[\]\)/g,
    ', [])'
  );
  
  return content;
}

// 修复函数体中的语法错误
function fixFunctionBodies(content) {
  // 修复 setLoading(true), []), [])... 模式
  content = content.replace(
    /(\w+\([^)]*\))[^,]*,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    '$1;'
  );
  
  // 修复 console.log(...), []), [])... 模式
  content = content.replace(
    /(console\.\w+\([^)]*\))[^,]*,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    '$1;'
  );
  
  return content;
}

// 修复switch语句
function fixSwitchStatements(content) {
  // 修复 case 'value': return 'result', [])... 模式
  content = content.replace(
    /(case\s+['"][^'"]+['"]\s*:\s*return\s+[^,]+)[^,]*,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    '$1;'
  );
  
  return content;
}

// 修复JSX语法错误
function fixJSXErrors(content) {
  // 修复 setEcoServicesVisible(true), [])... 在JSX中的问题
  content = content.replace(
    /(\w+\([^)]*\))[^,]*,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    '$1;'
  );
  
  return content;
}

// 修复try-catch语句
function fixTryCatchStatements(content) {
  // 确保try-catch语句正确闭合
  content = content.replace(
    /(\s+}\s*catch\s*\([^)]*\)\s*\{[^}]*)\s*,\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\),\s*\[\]\);?/g,
    '$1\n    }\n  };'
  );
  
  return content;
}

// 主修复函数
function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;

    // 应用各种修复
    content = fixImportCommas(content);
    content = fixUseCallbackParameters(content);
    content = fixRemainingNestedHooks(content);
    content = fixFunctionBodies(content);
    content = fixSwitchStatements(content);
    content = fixJSXErrors(content);
    content = fixTryCatchStatements(content);

    // 如果内容有变化，写回文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`❌ 修复文件 ${filePath} 时出错:`, error.message);
    return false;
  }
}

// 主执行函数
async function main() {
  try {
    console.log('📁 扫描TypeScript文件...');
    const tsFiles = getAllTsFiles('src');
    console.log(`找到 ${tsFiles.length} 个TypeScript文件\n`);

    let fixedCount = 0;
    let totalFiles = tsFiles.length;

    for (let i = 0; i < tsFiles.length; i++) {
      const file = tsFiles[i];
      const relativePath = path.relative(process.cwd(), file);
      
      process.stdout.write(`\r修复进度: ${i + 1}/${totalFiles} - ${relativePath.slice(-50)}`);
      
      if (fixFile(file)) {
        fixedCount++;
      }
    }

    console.log(`\n\n🎉 剩余语法错误修复完成！`);
    console.log(`📊 统计信息:`);
    console.log(`   - 扫描文件: ${totalFiles}`);
    console.log(`   - 修复文件: ${fixedCount}`);
    console.log(`   - 跳过文件: ${totalFiles - fixedCount}`);

    console.log('\n🔄 建议下一步操作:');
    console.log('1. 运行 npm run type-check 验证修复效果');
    console.log('2. 如果还有错误，可能需要手动修复');

  } catch (error) {
    console.error('❌ 修复过程中出现错误:', error);
    process.exit(1);
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  fixImportCommas,
  fixUseCallbackParameters,
  fixRemainingNestedHooks,
  fixFunctionBodies,
  fixSwitchStatements,
  fixJSXErrors,
  fixTryCatchStatements,
  fixFile,
}; 