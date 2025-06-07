const fs = require('fs');
const path = require('path');

// 需要修复的高错误文件列表
const highErrorFiles = [
  'src/agents/zkp_health_report.tsx',
  'src/screens/demo/ApiIntegrationDemo.tsx',
  'src/components/blockchain/BlockchainDataManager.tsx',
  'src/screens/suoke/components/EcoLifestyleNavigator.tsx',
  'src/components/ui/UserExperienceEnhancer.tsx',
  'src/services/paymentService.tsx',
  'src/services/ApiIntegrationService.tsx'
];

// TypeScript类型错误修复规则
const typeFixRules = [
  // 修复any类型
  {
    pattern: /:\s*any\b/g,
    replacement: ': unknown',
    description: '将any类型替换为unknown'
  },
  {
    pattern: /any\[\]/g,
    replacement: 'unknown[]',
    description: '修复any数组类型'
  },
  
  // 修复常见的类型定义问题
  {
    pattern: /interface\s+(\w+)\s*{\s*}/g,
    replacement: 'interface $1 {\n  [key: string]: unknown;\n}',
    description: '修复空接口定义'
  },
  
  // 修复React组件类型
  {
    pattern: /React\.FC<>/g,
    replacement: 'React.FC',
    description: '修复空泛型React.FC'
  },
  {
    pattern: /React\.Component<>/g,
    replacement: 'React.Component',
    description: '修复空泛型React.Component'
  },
  
  // 修复useState类型
  {
    pattern: /useState\(\)/g,
    replacement: 'useState<unknown>(undefined)',
    description: '修复无类型useState'
  },
  {
    pattern: /useState\(null\)/g,
    replacement: 'useState<unknown>(null)',
    description: '修复null初始值useState'
  },
  
  // 修复事件处理器类型
  {
    pattern: /\(\s*event\s*\)\s*=>/g,
    replacement: '(event: React.SyntheticEvent) =>',
    description: '修复事件处理器参数类型'
  },
  {
    pattern: /\(\s*e\s*\)\s*=>/g,
    replacement: '(e: React.SyntheticEvent) =>',
    description: '修复事件处理器参数类型(简写)'
  },
  
  // 修复函数参数类型
  {
    pattern: /function\s+(\w+)\s*\(\s*([^)]+)\s*\)\s*{/g,
    replacement: 'function $1($2: unknown) {',
    description: '修复函数参数类型'
  },
  
  // 修复对象类型
  {
    pattern: /:\s*{}\s*=/g,
    replacement: ': Record<string, unknown> =',
    description: '修复空对象类型'
  },
  
  // 修复数组类型
  {
    pattern: /:\s*\[\]\s*=/g,
    replacement: ': unknown[] =',
    description: '修复空数组类型'
  },
  
  // 修复Promise类型
  {
    pattern: /Promise<>/g,
    replacement: 'Promise<unknown>',
    description: '修复空Promise类型'
  },
  
  // 修复常见的导入类型问题
  {
    pattern: /import\s*{\s*([^}]+)\s*}\s*from\s*["']([^"']+)["']/g,
    replacement: (match, imports, module) => {
      // 清理导入语句中的类型注解
      const cleanImports = imports.replace(/:\s*[^,}]+/g, '').replace(/\s+/g, ' ').trim();
      return `import { ${cleanImports} } from "${module}"`;
    },
    description: '清理导入语句中的类型注解'
  }
];

// 特殊修复规则（针对特定文件模式）
const specialFixRules = [
  // 修复React Native组件导入
  {
    pattern: /from\s*["']react-native["']/g,
    replacement: 'from "react-native"',
    description: '标准化React Native导入'
  },
  
  // 修复样式对象类型
  {
    pattern: /StyleSheet\.create\(\s*{\s*([^}]+)\s*}\s*\)/g,
    replacement: (match, styles) => {
      return `StyleSheet.create({\n${styles.replace(/,/g, ',\n')}\n})`;
    },
    description: '格式化StyleSheet定义'
  },
  
  // 修复组件props类型
  {
    pattern: /interface\s+(\w+)Props\s*{\s*([^}]*)\s*}/g,
    replacement: (match, componentName, props) => {
      if (!props.trim()) {
        return `interface ${componentName}Props {\n  children?: React.ReactNode;\n}`;
      }
      return match;
    },
    description: '修复空Props接口'
  }
];

function analyzeTypeErrors(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    const issues = {
      anyTypes: (content.match(/:\s*any\b/g) || []).length,
      emptyInterfaces: (content.match(/interface\s+\w+\s*{\s*}/g) || []).length,
      untypedFunctions: (content.match(/\(\s*[^)]*\s*\)\s*=>/g) || []).length,
      missingImports: (content.match(/React\./g) || []).length > 0 && !content.includes('import React'),
      totalLines: lines.length
    };
    
    return issues;
  } catch (error) {
    return null;
  }
}

function fixTypeErrors(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`⚠️  文件不存在: ${filePath}`);
      return false;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let fixCount = 0;
    const appliedFixes = [];

    // 分析文件问题
    const issues = analyzeTypeErrors(filePath);
    if (issues) {
      console.log(`📊 分析 ${path.basename(filePath)}:`);
      console.log(`   - any类型: ${issues.anyTypes}个`);
      console.log(`   - 空接口: ${issues.emptyInterfaces}个`);
      console.log(`   - 无类型函数: ${issues.untypedFunctions}个`);
      console.log(`   - 总行数: ${issues.totalLines}行`);
    }

    // 备份原文件
    fs.writeFileSync(filePath + '.type-backup', content);

    // 应用类型修复规则
    for (const rule of typeFixRules) {
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
          fixCount += matches.length;
          appliedFixes.push(`${rule.description} (${matches.length}处)`);
        }
      }
    }

    // 应用特殊修复规则
    for (const rule of specialFixRules) {
      const beforeLength = content.length;
      if (typeof rule.replacement === 'function') {
        content = content.replace(rule.pattern, rule.replacement);
      } else {
        content = content.replace(rule.pattern, rule.replacement);
      }
      const afterLength = content.length;
      
      if (beforeLength !== afterLength) {
        appliedFixes.push(rule.description);
      }
    }

    // 额外的清理和格式化
    // 确保React导入存在
    if (content.includes('React.') && !content.includes('import React')) {
      content = 'import React from "react";\n' + content;
    }
    
    // 清理多余空行
    content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    // 修复缩进
    content = content.replace(/^(\s*)(.*)/gm, (match, indent, line) => {
      if (line.trim() === '') return '';
      const indentLevel = Math.floor(indent.length / 2) * 2;
      return ' '.repeat(indentLevel) + line.trim();
    });

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      console.log(`✅ 修复文件: ${path.basename(filePath)}`);
      console.log(`   - 修复数量: ${fixCount}处`);
      if (appliedFixes.length > 0) {
        console.log(`   - 应用修复: ${appliedFixes.slice(0, 3).join(', ')}${appliedFixes.length > 3 ? '...' : ''}`);
      }
      return true;
    } else {
      console.log(`ℹ️  文件无需修复: ${path.basename(filePath)}`);
      return false;
    }

  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath} - ${error.message}`);
    return false;
  }
}

function fixHighErrorFiles() {
  console.log('🔧 开始修复TypeScript类型错误...\n');
  
  let totalFixed = 0;
  let totalAttempted = 0;

  for (const filePath of highErrorFiles) {
    console.log(`\n🔍 处理文件: ${filePath}`);
    totalAttempted++;
    if (fixTypeErrors(filePath)) {
      totalFixed++;
    }
  }

  console.log(`\n📊 类型错误修复完成:`);
  console.log(`   - 尝试修复文件数: ${totalAttempted}`);
  console.log(`   - 成功修复文件数: ${totalFixed}`);
  console.log(`   - 修复率: ${((totalFixed / totalAttempted) * 100).toFixed(1)}%`);
  console.log(`\n💡 提示: 原文件已备份为 .type-backup 后缀`);
  console.log(`   如需恢复，请运行: find src -name "*.type-backup" -exec bash -c 'mv "$1" "\${1%.type-backup}"' _ {} \\;`);
}

fixHighErrorFiles(); 