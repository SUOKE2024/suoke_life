const fs = require('fs');
const path = require('path');

// 复杂语法错误修复规则
const complexFixRules = [
  // 修复混乱的导入语句
  {
    pattern: /import\s+([^;]+?)\s*from\s*["']([^"']+)["']\s*\/\/.*?import/g,
    replacement: 'import $1 from "$2";\nimport'
  },
  {
    pattern: /import\s+([^;]+?)\s*from\s*["']([^"']+)["']\s*\/\/.*?["']/g,
    replacement: 'import $1 from "$2";'
  },
  {
    pattern: /import\s+([^;]+?)\s*from\s*["']([^"']+)["']\s*\/\/.*?$/gm,
    replacement: 'import $1 from "$2";'
  },
  
  // 修复混乱的导入语句 - 特殊情况
  {
    pattern: /import\s*([^;]+?)\s*from\s*["'];([^"']+)["']\/import/g,
    replacement: 'import $1 from "$2";\nimport'
  },
  {
    pattern: /importIcon\s+from\s*["'];([^"']+)["']\/import/g,
    replacement: 'import Icon from "$1";\nimport'
  },
  {
    pattern: /import\s*([^;]+?)\s*from\s*["']([^"']+)["']\/\/.*?["']/g,
    replacement: 'import $1 from "$2";'
  },
  
  // 修复React导入
  {
    pattern: /import\s+React\s*from\s*["']react["'];\s*importReact,/g,
    replacement: 'import React,'
  },
  {
    pattern: /importReact,/g,
    replacement: 'import React,'
  },
  
  // 修复from react-native语句
  {
    pattern: /}\s*from\s*react-native;/g,
    replacement: '} from "react-native";'
  },
  
  // 修复接口定义
  {
    pattern: /interface\s+([A-Za-z0-9_]+)\s*{\s*([^}]+?)\s*}/g,
    replacement: (match, name, content) => {
      const fixedContent = content
        .replace(/([a-zA-Z0-9_]+):\s*([^,;]+?)([,;]?)\s*$/gm, '$1: $2;')
        .replace(/,\s*$/gm, ';')
        .replace(/;\s*;/g, ';');
      return `interface ${name} {\n  ${fixedContent}\n}`;
    }
  },
  
  // 修复函数组件定义
  {
    pattern: /export\s+const\s+([A-Za-z0-9_]+):\s*React\.FC<([^>]+)>\s*\/>\s*=/g,
    replacement: 'export const $1: React.FC<$2> ='
  },
  
  // 修复useState调用
  {
    pattern: /useState<([^>]+)>\(([^)]+)\);"/g,
    replacement: 'useState<$1>($2);'
  },
  
  // 修复useRef调用
  {
    pattern: /useRef\(new\s+([^)]+)\(\);?\)\s*\.current,\s*\[\]\)\)\)\)\)\);/g,
    replacement: 'useRef(new $1()).current'
  },
  
  // 修复useMemo调用
  {
    pattern: /useMemo\(\);\s*=>\s*useMemo\(\);\s*=>\s*useMemo\(\);\s*=>\s*useMemo\(\);\s*=>\s*useMemo\(\);\s*=>\s*useMemo\(\);\s*=>\s*/g,
    replacement: 'useMemo(() => '
  },
  
  // 修复多余的分号和逗号
  {
    pattern: /;;\s*\)/g,
    replacement: ');'
  },
  {
    pattern: /,\s*;/g,
    replacement: ';'
  },
  {
    pattern: /;\s*,/g,
    replacement: ','
  },
  
  // 修复字符串引号问题
  {
    pattern: /["']([^"']*?)["']\s*,\s*["']/g,
    replacement: '"$1",'
  },
  
  // 修复对象属性定义
  {
    pattern: /{\s*([a-zA-Z0-9_]+):\s*["']([^"']*?)["']\s*,\s*([a-zA-Z0-9_]+):/g,
    replacement: '{\n      $1: "$2",\n      $3:'
  },
  
  // 修复数组定义
  {
    pattern: /\[\s*["']([^"']*?)["']\s*,\s*["']([^"']*?)["']\s*,\s*["']([^"']*?)["']\s*\]/g,
    replacement: '["$1", "$2", "$3"]'
  },
  
  // 修复JSX属性
  {
    pattern: /style=\{styles\.([a-zA-Z0-9_]+)\}\s*\/>/g,
    replacement: 'style={styles.$1}>'
  },
  
  // 修复注释问题
  {
    pattern: /\/\/.*?\/\//g,
    replacement: ''
  },
  {
    pattern: /\/\*.*?\*\//g,
    replacement: ''
  },
  
  // 修复多余的括号和花括号
  {
    pattern: /\)\)\)\)\)\);/g,
    replacement: ');'
  },
  {
    pattern: /\/\/\/\/\/\s*/g,
    replacement: ''
  },
  
  // 修复箭头函数
  {
    pattern: /\(\)\s*=>\s*accessibilityLabel="TODO: 添加无障碍标签"\s*\/>\s*/g,
    replacement: '() => '
  },
  
  // 修复map函数调用
  {
    pattern: /\.map\(([^,)]+),\s*([^)]+)\)\s*=>/g,
    replacement: '.map(($1, $2) =>'
  },
  
  // 修复条件渲染
  {
    pattern: /&&\s*\(\s*<View/g,
    replacement: '&& (\n        <View'
  }
];

function fixComplexSyntaxErrors(content) {
  let fixedContent = content;
  let changesCount = 0;
  
  // 应用所有修复规则
  complexFixRules.forEach(rule => {
    const before = fixedContent;
    if (typeof rule.replacement === 'function') {
      fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
    } else {
      fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
    }
    if (before !== fixedContent) {
      changesCount++;
    }
  });
  
  // 基本清理
  fixedContent = fixedContent
    // 移除多余的空行
    .replace(/\n\s*\n\s*\n/g, '\n\n')
    // 修复缩进
    .replace(/^(\s*)(.*)/gm, (match, indent, content) => {
      if (content.trim() === '') return '';
      const level = (indent.match(/  /g) || []).length;
      return '  '.repeat(level) + content.trim();
    });
  
  return { content: fixedContent, changesCount };
}

function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const { content: fixedContent, changesCount } = fixComplexSyntaxErrors(content);
    
    if (changesCount > 0) {
      // 备份原文件
      fs.writeFileSync(filePath + '.backup', content);
      // 写入修复后的内容
      fs.writeFileSync(filePath, fixedContent);
      console.log(`✅ 修复文件: ${filePath} (${changesCount} 处修改)`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`❌ 处理文件失败: ${filePath}`, error.message);
    return false;
  }
}

function findTSXFiles(dir) {
  const files = [];
  
  function traverse(currentDir) {
    const items = fs.readdirSync(currentDir);
    
    for (const item of items) {
      const fullPath = path.join(currentDir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
        traverse(fullPath);
      } else if (item.endsWith('.tsx') || item.endsWith('.ts')) {
        files.push(fullPath);
      }
    }
  }
  
  traverse(dir);
  return files;
}

// 主执行函数
function main() {
  console.log('🔧 开始复杂语法错误修复...\n');
  
  const srcDir = path.join(process.cwd(), 'src');
  const files = findTSXFiles(srcDir);
  
  let fixedCount = 0;
  const totalFiles = files.length;
  
  // 优先处理错误最多的文件
  const priorityFiles = [
    'src/screens/life/components/ARConstitutionVisualization.tsx',
    'src/screens/life/components/BlockchainHealthData.tsx',
    'src/screens/suoke/components/EcoLifestyleNavigator.tsx',
    'src/screens/profile/ServiceManagementScreen.tsx',
    'src/components/blockchain/BlockchainDataManager.tsx'
  ];
  
  // 先处理优先文件
  for (const file of priorityFiles) {
    if (fs.existsSync(file)) {
      if (processFile(file)) {
        fixedCount++;
      }
    }
  }
  
  // 处理其他文件
  for (const file of files) {
    if (!priorityFiles.includes(file)) {
      if (processFile(file)) {
        fixedCount++;
      }
    }
  }
  
  console.log(`\n📊 修复完成:`);
  console.log(`   - 总文件数: ${totalFiles}`);
  console.log(`   - 修复文件数: ${fixedCount}`);
  console.log(`   - 修复率: ${((fixedCount / totalFiles) * 100).toFixed(1)}%`);
  
  if (fixedCount > 0) {
    console.log(`\n💡 提示: 原文件已备份为 .backup 后缀`);
    console.log(`   如需恢复，请运行: find src -name "*.backup" -exec bash -c 'mv "$1" "\${1%.backup}"' _ {} \\;`);
  }
}

main(); 