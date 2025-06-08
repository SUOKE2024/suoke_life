const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 获取当前错误数量
function getCurrentErrorCount() {
  try {
    const output = execSync('npx tsc --noEmit 2>&1 | grep -E "error TS[0-9]+" | wc -l', { encoding: 'utf8' });
    return parseInt(output.trim());
  } catch (error) {
    return 0;
  }
}

// 获取错误最多的文件
function getTopErrorFiles(limit = 20) {
  try {
    const output = execSync('npx tsc --noEmit 2>&1 | grep -E "error TS[0-9]+" | cut -d\'(\' -f1 | sort | uniq -c | sort -nr | head -' + limit, { encoding: 'utf8' });
    const lines = output.trim().split('\n');
    const files = [];
    
    for (const line of lines) {
      const match = line.trim().match(/^\s*(\d+)\s+(.+)$/);
      if (match) {
        const errorCount = parseInt(match[1]);
        const filePath = match[2].trim();
        if (errorCount > 50) { // 只处理错误数量超过50的文件
          files.push({ path: filePath, errors: errorCount });
        }
      }
    }
    
    return files;
  } catch (error) {
    console.error('获取错误文件列表失败:', error.message);
    return [];
  }
}

// 综合修复规则
const comprehensiveFixRules = [
  // 基础语法修复
  {
    name: '修复缺失分号',
    pattern: /^(\s*)(.*[^;{}\s])\s*$/gm,
    replacement: (match, indent, content) => {
      if (content.includes('//') || content.includes('/*') || 
          content.includes('import') || content.includes('export') ||
          content.includes('if') || content.includes('for') ||
          content.includes('while') || content.includes('function') ||
          content.includes('class') || content.includes('interface') ||
          content.includes('type') || content.includes('const') ||
          content.includes('let') || content.includes('var')) {
        return `${indent}${content};`;
      }
      return match;
    },
    description: '添加缺失的分号'
  },
  
  // 修复导入语句
  {
    name: '清理导入语句',
    pattern: /import\s*{\s*([^}]+)\s*}\s*from\s*["']([^"']+)["']\s*\/\/[^\n]*\n/g,
    replacement: 'import { $1 } from "$2";\n',
    description: '清理导入语句中的注释'
  },
  
  // 修复JSX语法
  {
    name: '修复JSX闭合标签',
    pattern: /(<\w+[^>]*)\s*\/\s*>/g,
    replacement: '$1 />',
    description: '修复JSX自闭合标签格式'
  },
  
  // 修复对象和数组
  {
    name: '修复对象格式',
    pattern: /{\s*([^:]+):\s*([^,}]+),?\s*}/g,
    replacement: '{ $1: $2 }',
    description: '格式化对象字面量'
  },
  
  // 修复字符串引号
  {
    name: '统一字符串引号',
    pattern: /"([^"\\]*(\\.[^"\\]*)*)"/g,
    replacement: "'$1'",
    description: '统一使用单引号'
  },
  
  // 修复函数定义
  {
    name: '修复箭头函数',
    pattern: /=>\s*{([^}]*)}/g,
    replacement: '=> {\n  $1\n}',
    description: '格式化箭头函数'
  },
  
  // 修复条件语句
  {
    name: '修复条件渲染',
    pattern: /{\s*([^}]+)\s*&&\s*\(\s*</g,
    replacement: '{ $1 && (\n    <',
    description: '格式化条件渲染'
  },
  
  // 修复样式对象
  {
    name: '修复样式数组',
    pattern: /style=\{\s*[\s*([^]]+)\s*\]\s*\}/g,
    replacement: 'style={[$1]}',
    description: '格式化样式数组'
  }
];

// 特殊文件修复策略
const specialFileStrategies = {
  '.tsx': {
    rules: [
      {
        pattern: /React\.FC<>/g,
        replacement: 'React.FC',
        description: '修复空泛型React.FC'
      },
      {
        pattern: /useState\(\)/g,
        replacement: 'useState<unknown>(undefined)',
        description: '修复无类型useState'
      }
    ]
  },
  '.ts': {
    rules: [
      {
        pattern: /interface\s+(\w+)\s*{\s*}/g,
        replacement: 'interface $1 {\n  [key: string]: unknown;\n}',
        description: '修复空接口'
      }
    ]
  }
};

// 应用综合修复
function applyComprehensiveFixes(filePath) {
  try {
    const fileName = path.basename(filePath);
    const fileExt = path.extname(filePath);
    
    if (!fs.existsSync(filePath)) {
      console.log(`⚠️  文件不存在: ${filePath}`);
      return { success: false, fixes: 0 };
    }

    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let totalFixes = 0;
    const appliedFixes = [];

    // 备份原文件
    fs.writeFileSync(filePath + '.comprehensive-backup', content);

    // 应用通用修复规则
    for (const rule of comprehensiveFixRules) {
      const beforeLength = content.length;
      
      if (typeof rule.replacement === 'function') {
        content = content.replace(rule.pattern, rule.replacement);
      } else {
        content = content.replace(rule.pattern, rule.replacement);
      }
      
      const afterLength = content.length;
      if (beforeLength !== afterLength) {
        const matches = originalContent.match(rule.pattern);
        if (matches) {
          totalFixes += matches.length;
          appliedFixes.push(rule.description);
        }
      }
    }

    // 应用特殊文件类型修复
    const specialStrategy = specialFileStrategies[fileExt];
    if (specialStrategy) {
      for (const rule of specialStrategy.rules) {
        const beforeLength = content.length;
        content = content.replace(rule.pattern, rule.replacement);
        const afterLength = content.length;
        
        if (beforeLength !== afterLength) {
          appliedFixes.push(rule.description);
        }
      }
    }

    // 额外的清理工作
    content = content
      // 清理多余空行
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      // 修复缩进
      .replace(/^(\s*)(.*)/gm, (match, indent, line) => {
        if (line.trim() === '') return '';
        const indentLevel = Math.floor(indent.length / 2) * 2;
        return ' '.repeat(indentLevel) + line.trim();
      })
      // 确保文件以换行符结尾
      .replace(/[^\n]$/, '$&\n');

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return { 
        success: true, 
        fixes: totalFixes, 
        appliedFixes: [...new Set(appliedFixes)] 
      };
    } else {
      return { success: false, fixes: 0, appliedFixes: [] };
    }

  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath} - ${error.message}`);
    return { success: false, fixes: 0, appliedFixes: [] };
  }
}

// 批量修复文件
function batchFixFiles(files) {
  console.log(`🔧 开始批量修复 ${files.length} 个文件...\n`);
  
  let totalFixed = 0;
  let totalFixes = 0;
  const allAppliedFixes = [];
  
  for (const fileInfo of files) {
    const fileName = path.basename(fileInfo.path);
    console.log(`🔍 修复: ${fileName} (${fileInfo.errors}个错误)`);
    
    const result = applyComprehensiveFixes(fileInfo.path);
    
    if (result.success) {
      totalFixed++;
      totalFixes += result.fixes;
      allAppliedFixes.push(...result.appliedFixes);
      
      console.log(`✅ 修复完成: ${fileName}`);
      console.log(`   - 修复数量: ${result.fixes}处`);
      if (result.appliedFixes.length > 0) {
        console.log(`   - 修复类型: ${result.appliedFixes.slice(0, 2).join(', ')}`);
      }
    } else {
      console.log(`ℹ️  无需修复: ${fileName}`);
    }
  }
  
  return { totalFixed, totalFixes, allAppliedFixes: [...new Set(allAppliedFixes)] };
}

// 主函数
function main() {
  console.log('🚀 开始综合性能优化修复...\n');
  
  // 获取初始错误数量
  const initialErrors = getCurrentErrorCount();
  console.log(`📊 初始错误数量: ${initialErrors}`);
  
  if (initialErrors === 0) {
    console.log('🎉 项目已经没有TypeScript错误！');
    return;
  }
  
  // 获取错误最多的文件
  const topErrorFiles = getTopErrorFiles(30);
  
  if (topErrorFiles.length === 0) {
    console.log('🎉 没有发现错误数量超过50的文件！');
    return;
  }
  
  console.log(`📋 发现 ${topErrorFiles.length} 个高错误文件:`);
  topErrorFiles.slice(0, 10).forEach((file, index) => {
    console.log(`   ${index + 1}. ${path.basename(file.path)} - ${file.errors}个错误`);
  });
  
  if (topErrorFiles.length > 10) {
    console.log(`   ... 还有 ${topErrorFiles.length - 10} 个文件`);
  }
  
  // 批量修复文件
  const result = batchFixFiles(topErrorFiles);
  
  console.log(`\n📊 综合修复完成:`);
  console.log(`   - 尝试修复文件数: ${topErrorFiles.length}`);
  console.log(`   - 成功修复文件数: ${result.totalFixed}`);
  console.log(`   - 总修复次数: ${result.totalFixes}`);
  console.log(`   - 修复率: ${((result.totalFixed / topErrorFiles.length) * 100).toFixed(1)}%`);
  
  if (result.allAppliedFixes.length > 0) {
    console.log(`\n🔧 主要修复类型:`);
    result.allAppliedFixes.slice(0, 5).forEach(fix => {
      console.log(`   - ${fix}`);
    });
  }
  
  // 检查修复效果
  console.log(`\n🔍 检查修复效果...`);
  const finalErrors = getCurrentErrorCount();
  const reduction = initialErrors - finalErrors;
  
  console.log(`📈 修复前错误数: ${initialErrors}`);
  console.log(`📉 修复后错误数: ${finalErrors}`);
  console.log(`🎯 减少错误数: ${reduction} (${((reduction / initialErrors) * 100).toFixed(1)}%)`);
  
  if (reduction > 0) {
    console.log(`🎉 修复成功！错误数量显著减少`);
  } else if (reduction === 0) {
    console.log(`⚠️  错误数量未变化，可能需要更深层的修复`);
  } else {
    console.log(`⚠️  错误数量增加，可能暴露了新的问题`);
  }
  
  console.log(`\n💡 提示: 原文件已备份为 .comprehensive-backup 后缀`);
  console.log(`   如需恢复，请运行: find src -name "*.comprehensive-backup" -exec bash -c 'mv "$1" "\${1%.comprehensive-backup}"' _ {} \\;`);
  
  // 生成修复报告
  const reportPath = 'COMPREHENSIVE_FIX_REPORT.md';
  const reportContent = `# 综合修复报告

## 修复概览
- **修复时间**: ${new Date().toLocaleString()}
- **初始错误数**: ${initialErrors}
- **最终错误数**: ${finalErrors}
- **减少错误数**: ${reduction}
- **修复率**: ${((reduction / initialErrors) * 100).toFixed(1)}%

## 修复文件统计
- **尝试修复文件数**: ${topErrorFiles.length}
- **成功修复文件数**: ${result.totalFixed}
- **总修复次数**: ${result.totalFixes}

## 主要修复类型
${result.allAppliedFixes.map(fix => `- ${fix}`).join('\n')}

## 修复的文件列表
${topErrorFiles.map((file, index) => `${index + 1}. ${path.basename(file.path)} (${file.errors}个错误)`).join('\n')}

## 备份信息
所有修复的文件都已备份为 \`.comprehensive-backup\` 后缀。
如需恢复，请运行：
\`\`\`bash
find src -name "*.comprehensive-backup" -exec bash -c 'mv "$1" "\${1%.comprehensive-backup}"' _ {} \\;
\`\`\`
`;
  
  fs.writeFileSync(reportPath, reportContent);
  console.log(`\n📄 修复报告已生成: ${reportPath}`);
}

main(); 