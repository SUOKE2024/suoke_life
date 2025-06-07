const fs = require('fs');

// 需要修复的文件列表
const problematicFiles = [
  'src/screens/life/components/BlockchainHealthData.tsx',
  'src/screens/profile/ServiceManagementScreen.tsx',
  'src/screens/demo/IntegrationDemoScreen.tsx'
];

// 高级语法修复规则
const advancedFixRules = [
  // 修复混乱的导入语句
  {
    pattern: /import\s+([^;]+?)\s*from\s*["']([^"']+)["']\s*\/\/.*?import/g,
    replacement: 'import $1 from "$2";\nimport'
  },
  {
    pattern: /import\s+([^;]+?)\s*from\s*["']([^"']+)["']\s*\/\/.*?["']/g,
    replacement: 'import $1 from "$2";'
  },
  // 修复函数组件定义问题
  {
    pattern: /export\s+const\s+(\w+):\s*React\.FC<([^>]+)>\s*\/>\s*=\s*\({/g,
    replacement: 'export const $1: React.FC<$2> = ({'
  },
  // 修复缺失的分号
  {
    pattern: /}\s*(?=\s*const|let|var|function|interface|type|export)/g,
    replacement: '};\n\n'
  },
  // 修复JSX属性问题
  {
    pattern: /accessibilityLabel="TODO:\s*添加无障碍标签"\s*\/>/g,
    replacement: 'accessibilityLabel="TODO: 添加无障碍标签"'
  }
];

function fixFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`⚠️  文件不存在: ${filePath}`);
      return false;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let fixCount = 0;

    // 备份原文件
    fs.writeFileSync(filePath + '.advanced-backup', content);

    // 应用修复规则
    for (const rule of advancedFixRules) {
      const matches = content.match(rule.pattern);
      if (matches) {
        content = content.replace(rule.pattern, rule.replacement);
        fixCount += matches.length;
      }
    }

    // 额外的清理规则
    content = content
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      .replace(/}\s*{/g, '},\n{')
      .replace(/\/>\s*\/>/g, '/>')
      .replace(/;;\s*;/g, ';')
      .replace(/\)\)\)\)\)/g, ')')
      .replace(/}}}}/g, '}');

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      console.log(`✅ 修复文件: ${filePath} (${fixCount} 处修改)`);
      return true;
    } else {
      console.log(`ℹ️  文件无需修复: ${filePath}`);
      return false;
    }

  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath} - ${error.message}`);
    return false;
  }
}

function fixTopErrorFiles() {
  console.log('🔧 开始修复错误最多的文件...\n');
  
  let totalFixed = 0;
  let totalAttempted = 0;

  for (const filePath of problematicFiles) {
    totalAttempted++;
    if (fixFile(filePath)) {
      totalFixed++;
    }
  }

  console.log(`\n📊 修复完成:`);
  console.log(`   - 尝试修复文件数: ${totalAttempted}`);
  console.log(`   - 成功修复文件数: ${totalFixed}`);
  console.log(`   - 修复率: ${((totalFixed / totalAttempted) * 100).toFixed(1)}%`);
}

fixTopErrorFiles(); 