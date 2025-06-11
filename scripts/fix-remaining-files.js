const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 获取当前错误最多的文件
function getCurrentTopErrorFiles() {
  try {
    const output = execSync('npx tsc --noEmit 2>&1 | grep -E "error TS[0-9]+" | cut -d\'(\' -f1 | sort | uniq -c | sort -nr | head -15', { encoding: 'utf8' });
    const lines = output.trim().split('\n');
    const files = [];
    
    for (const line of lines) {
      const match = line.trim().match(/^\s*(\d+)\s+(.+)$/);
      if (match) {
        const errorCount = parseInt(match[1]);
        const filePath = match[2].trim();
        if (errorCount > 300) { // 只处理错误数量超过300的文件
          files.push({  path: filePath, errors: errorCount  });
        }
      }
    }
    
    return files;
  } catch (error) {
    console.error('获取错误文件列表失败:', error.message);
    return [];
  }
}

// 强力修复规则
const aggressiveFixRules = [
  // 修复导入语句问题
  {
    pattern: /import\s*([^;]*?)\s*from\s*["']([^"']+)["']\s*\/\/[^\n]*\n/g,
    replacement: 'import $1 from "$2";\n',
    description: '清理导入语句注释'
  },
  
  // 修复多行导入语句
  {
    pattern: /import\s*{\s*([^}]*?)\s*}\s*from\s*["']([^"']+)["']\s*\/\/[^\n]*import\s*{\s*([^}]*?)\s*}\s*from\s*["']([^"']+)["']/g,
    replacement: 'import { $1 } from "$2";\nimport { $3 } from "$4"',
    description: '分离混合的导入语句'
  },
  
  // 修复JSX属性问题
  {
    pattern: /accessibilityLabel=["'][^"']*["']\s*\/>/g,
    replacement: (match) => match.replace(/\s*\/>/, ' />'),
    description: '修复JSX闭合标签'
  },
  
  // 修复函数定义问题
  {
    pattern: /export\s+const\s+(\w+):\s*React\.FC<([^>]*)>\s*\/>\s*=\s*\(/g,
    replacement: 'export const $1: React.FC<$2> = (',
    description: '修复React组件定义'
  },
  
  // 修复对象属性定义
  {
    pattern: /{\s*([^:]+):\s*["']([^"']+)["'],\s*([^:]+):\s*["']([^"']+)["'],\s*([^:]+):\s*[([^]]*)\]\s*}/g,
    replacement: '{\n  $1: "$2",\n  $3: "$4",\n  $5: [$6]\n}',
    description: '格式化对象定义'
  },
  
  // 修复useState定义
  {
    pattern: /const\s+[([^]]+)\]\s*=\s*useState<([^>]+)>\s*\/\s*>\s*\(\[/g,
    replacement: 'const [$1] = useState<$2>([]',
    description: '修复useState数组初始化'
  },
  
  // 修复模板字符串
  {
    pattern: /`([^`]*?)\$\{([^}]+)\}([^`]*?)`/g,
    replacement: '`$1${$2}$3`',
    description: '修复模板字符串格式'
  },
  
  // 修复条件渲染
  {
    pattern: /{\s*([^}]+)\s*&&\s*\(\s*<([^>]+)>/g,
    replacement: '{ $1 && (\n    <$2>',
    description: '格式化条件渲染'
  },
  
  // 修复样式对象
  {
    pattern: /style=\{\s*[\s*([^]]+)\s*\]\s*\}/g,
    replacement: 'style={[$1]}',
    description: '修复样式数组格式'
  },
  
  // 修复函数调用
  {
    pattern: /\(\s*([^)]+)\s*\)\s*=>\s*accessibilityLabel="[^"]*"\s*\/>/g,
    replacement: '($1) => ',
    description: '清理函数调用中的JSX属性'
  }
];

// 文件特定修复策略
const fileSpecificFixes = {
  'BlockchainHealthData.tsx': [
    {
      pattern: /blockchain/gi,
      replacement: 'blockchain',
      description: '统一blockchain命名'
    }
  ],
  'ServiceManagementScreen.tsx': [
    {
      pattern: /service/gi,
      replacement: 'service',
      description: '统一service命名'
    }
  ],
  'IntegrationDemoScreen.tsx': [
    {
      pattern: /demo/gi,
      replacement: 'demo',
      description: '统一demo命名'
    }
  ]
};

function applyAggressiveFixes(content, fileName) {
  let fixedContent = content;
  let totalFixes = 0;
  const appliedFixes = [];

  // 应用通用修复规则
  for (const rule of aggressiveFixRules) {
    const beforeLength = fixedContent.length;
    if (typeof rule.replacement === 'function') {
      fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
    } else {
      fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
    }
    const afterLength = fixedContent.length;
    
    if (beforeLength !== afterLength) {
      const matches = content.match(rule.pattern);
      if (matches) {
        totalFixes += matches.length;
        appliedFixes.push(`${rule.description} (${matches.length}处)`);
      }
    }
  }

  // 应用文件特定修复
  const specificFixes = fileSpecificFixes[fileName];
  if (specificFixes) {
    for (const rule of specificFixes) {
      const beforeLength = fixedContent.length;
      fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
      const afterLength = fixedContent.length;
      
      if (beforeLength !== afterLength) {
        appliedFixes.push(rule.description);
      }
    }
  }

  // 额外的清理工作
  fixedContent = fixedContent
    // 清理多余的空行
    .replace(/\n\s*\n\s*\n/g, '\n\n')
    // 修复缺失的分号
    .replace(/}\s*(?=\s*const|let|var|function|interface|type|export)/g, '};\n\n')
    // 修复JSX闭合标签
    .replace(/\/>\s*\/>/g, '/>')
    // 修复多余的逗号
    .replace(/,\s*,/g, ',')
    // 修复括号匹配
    .replace(/\)\)\)\)\)/g, ')')
    .replace(/}}}}/g, '}')
    // 修复字符串引号
    .replace(/["']([^"']*?)["']\s*\/\//g, '"$1" //');

  return { content: fixedContent, fixes: totalFixes, appliedFixes };
}

function fixFile(fileInfo) {
  const { path: filePath, errors } = fileInfo;
  const fileName = path.basename(filePath);
  
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`⚠️  文件不存在: ${filePath}`);
      return false;
    }

    console.log(`\n🔧 修复文件: ${fileName} (${errors}个错误)`);
    
    const originalContent = fs.readFileSync(filePath, 'utf8');
    
    // 备份原文件
    fs.writeFileSync(filePath + '.aggressive-backup', originalContent);
    
    // 应用强力修复
    const result = applyAggressiveFixes(originalContent, fileName);
    
    if (result.content !== originalContent) {
      fs.writeFileSync(filePath, result.content);
      console.log(`✅ 修复完成: ${fileName}`);
      console.log(`   - 修复数量: ${result.fixes}处`);
      if (result.appliedFixes.length > 0) {
        console.log(`   - 主要修复: ${result.appliedFixes.slice(0, 2).join(', ')}`);
      }
      return true;
    } else {
      console.log(`ℹ️  文件无需修复: ${fileName}`);
      return false;
    }

  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath} - ${error.message}`);
    return false;
  }
}

function main() {
  console.log('🚀 开始批量修复剩余高错误文件...\n');
  
  // 获取当前错误最多的文件
  const topErrorFiles = getCurrentTopErrorFiles();
  
  if (topErrorFiles.length === 0) {
    console.log('🎉 没有发现错误数量超过300的文件！');
    return;
  }
  
  console.log(`📋 发现 ${topErrorFiles.length} 个高错误文件:`);
  topErrorFiles.forEach((file, index) => {
    console.log(`   ${index + 1}. ${path.basename(file.path)} - ${file.errors}个错误`);
  });
  
  let totalFixed = 0;
  let totalAttempted = 0;
  
  // 逐个修复文件
  for (const fileInfo of topErrorFiles) {
    totalAttempted++;
    if (fixFile(fileInfo)) {
      totalFixed++;
    }
  }
  
  console.log(`\n📊 批量修复完成:`);
  console.log(`   - 尝试修复文件数: ${totalAttempted}`);
  console.log(`   - 成功修复文件数: ${totalFixed}`);
  console.log(`   - 修复率: ${((totalFixed / totalAttempted) * 100).toFixed(1)}%`);
  console.log(`\n💡 提示: 原文件已备份为 .aggressive-backup 后缀`);
  console.log(`   如需恢复，请运行: find src -name "*.aggressive-backup" -exec bash -c 'mv "$1" "\${1%.aggressive-backup}"' _ {} \\;`);
  
  // 检查修复效果
  console.log(`\n🔍 检查修复效果...`);
  try {
    const newErrorCount = execSync('npx tsc --noEmit 2>&1 | grep -E "error TS[0-9]+" | wc -l', { encoding: 'utf8' }).trim();
    console.log(`📈 当前错误数量: ${newErrorCount}`);
  } catch (error) {
    console.log('⚠️  无法获取当前错误数量');
  }
}

main(); 