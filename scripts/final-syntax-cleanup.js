const fs = require('fs');
const path = require('path');

// 修复计数器
let fixCount = 0;
let fileCount = 0;

// 修复模式
const fixPatterns = [
  // 1. 修复未终止的字符串字面量
  {
    pattern: /(['"`])([^'"`\n]*?)$/gm,
    replacement: (match, quote, content) => {
      if (content.includes('\\')) {
        return `${quote}${content}${quote}`;
      }
      return `${quote}${content}${quote}`;
    },
    description: '修复未终止的字符串字面量'
  },
  
  // 2. 修复导入语句错误
  {
    pattern: /import\s+([^;]+)$/gm,
    replacement: 'import $1;',
    description: '修复导入语句缺少分号'
  },
  
  // 3. 修复导出语句错误
  {
    pattern: /export\s+([^;]+)$/gm,
    replacement: 'export $1;',
    description: '修复导出语句缺少分号'
  },
  
  // 4. 修复接口/类型定义错误
  {
    pattern: /interface\s+(\w+)\s*\{([^}]*)\s*$/gm,
    replacement: 'interface $1 {\n$2\n}',
    description: '修复接口定义缺少闭合括号'
  },
  
  // 5. 修复类定义错误
  {
    pattern: /class\s+(\w+)\s*\{([^}]*)\s*$/gm,
    replacement: 'class $1 {\n$2\n}',
    description: '修复类定义缺少闭合括号'
  },
  
  // 6. 修复函数定义错误
  {
    pattern: /function\s+(\w+)\s*\([^)]*\)\s*\{([^}]*)\s*$/gm,
    replacement: 'function $1() {\n$2\n}',
    description: '修复函数定义缺少闭合括号'
  },
  
  // 7. 修复对象字面量错误
  {
    pattern: /\{\s*([^}]*)\s*$/gm,
    replacement: '{\n$1\n}',
    description: '修复对象字面量缺少闭合括号'
  },
  
  // 8. 修复数组字面量错误
  {
    pattern: /\[\s*([^\]]*)\s*$/gm,
    replacement: '[\n$1\n]',
    description: '修复数组字面量缺少闭合括号'
  },
  
  // 9. 修复JSX标签错误
  {
    pattern: /<(\w+)([^>]*?)$/gm,
    replacement: '<$1$2 />',
    description: '修复JSX标签未闭合'
  },
  
  // 10. 修复注释错误
  {
    pattern: /\/\*([^*]|\*(?!\/))*$/gm,
    replacement: '/* $1 */',
    description: '修复未闭合的块注释'
  },
  
  // 11. 修复正则表达式错误
  {
    pattern: /\/([^\/\n]*?)$/gm,
    replacement: '/$1/',
    description: '修复未闭合的正则表达式'
  },
  
  // 12. 修复模板字符串错误
  {
    pattern: /`([^`\n]*?)$/gm,
    replacement: '`$1`',
    description: '修复未闭合的模板字符串'
  },
  
  // 13. 修复枚举定义错误
  {
    pattern: /enum\s+(\w+)\s*\{([^}]*)\s*$/gm,
    replacement: 'enum $1 {\n$2\n}',
    description: '修复枚举定义缺少闭合括号'
  },
  
  // 14. 修复类型别名错误
  {
    pattern: /type\s+(\w+)\s*=\s*([^;]+)$/gm,
    replacement: 'type $1 = $2;',
    description: '修复类型别名缺少分号'
  },
  
  // 15. 修复变量声明错误
  {
    pattern: /(const|let|var)\s+([^;=]+)$/gm,
    replacement: '$1 $2;',
    description: '修复变量声明缺少分号'
  }
];

// 特殊文件修复规则
const specialFixes = {
  // 修复测试文件
  '.test.ts': (content) => {
    return content
      .replace(/describe\s*\(\s*['"`]([^'"`]*?)$/gm, "describe('$1', () => {")
      .replace(/it\s*\(\s*['"`]([^'"`]*?)$/gm, "it('$1', () => {")
      .replace(/expect\s*\(\s*([^)]*?)\s*$/gm, 'expect($1)')
      .replace(/\.toBe\s*\(\s*([^)]*?)\s*$/gm, '.toBe($1)')
      .replace(/\.toEqual\s*\(\s*([^)]*?)\s*$/gm, '.toEqual($1)');
  },
  
  // 修复React组件文件
  '.tsx': (content) => {
    return content
      .replace(/export\s+default\s+([^;]+)$/gm, 'export default $1;')
      .replace(/import\s+React\s+from\s+['"`]react['"`]$/gm, "import React from 'react';")
      .replace(/import\s*\{\s*([^}]*?)\s*\}\s*from\s*['"`]([^'"`]*?)['"`]$/gm, "import { $1 } from '$2';")
      .replace(/<\/([^>]+)>$/gm, '</$1>')
      .replace(/className\s*=\s*['"`]([^'"`]*?)$/gm, 'className="$1"');
  },
  
  // 修复TypeScript定义文件
  '.d.ts': (content) => {
    return content
      .replace(/declare\s+module\s+['"`]([^'"`]*?)['"`]\s*\{([^}]*)\s*$/gm, "declare module '$1' {\n$2\n}")
      .replace(/declare\s+namespace\s+(\w+)\s*\{([^}]*)\s*$/gm, 'declare namespace $1 {\n$2\n}')
      .replace(/export\s*\{\s*([^}]*?)\s*\}$/gm, 'export { $1 };');
  }
};

function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let localFixCount = 0;
    
    // 应用通用修复模式
    fixPatterns.forEach(({ pattern, replacement, description }) => {
      const matches = content.match(pattern);
      if (matches) {
        if (typeof replacement === 'function') {
          content = content.replace(pattern, replacement);
        } else {
          content = content.replace(pattern, replacement);
        }
        localFixCount += matches.length;
      }
    });
    
    // 应用特殊文件修复规则
    const ext = path.extname(filePath);
    if (specialFixes[ext]) {
      content = specialFixes[ext](content);
    }
    
    // 通用清理
    content = content
      // 移除多余的空行
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      // 修复缺少的分号
      .replace(/([^;{}\n])\n/g, '$1;\n')
      // 修复缺少的逗号
      .replace(/([^,{}\n])\n\s*([a-zA-Z_$])/g, '$1,\n$2')
      // 修复缺少的括号
      .replace(/\(\s*([^)]*?)\s*\n/g, '($1)')
      .replace(/\[\s*([^\]]*?)\s*\n/g, '[$1]')
      .replace(/\{\s*([^}]*?)\s*\n/g, '{$1}');
    
    // 如果内容有变化，写回文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      fileCount++;
      fixCount += localFixCount;
      console.log(`✅ 修复文件: ${filePath} (${localFixCount} 个修复)`);
    }
    
  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath}`, error.message);
  }
}

function processDirectory(dir) {
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      // 跳过 node_modules 和其他不需要的目录
      if (!['node_modules', '.git', 'dist', 'build', '.next'].includes(item)) {
        processDirectory(fullPath);
      }
    } else if (stat.isFile()) {
      // 只处理相关的文件类型
      const ext = path.extname(fullPath);
      if (['.ts', '.tsx', '.js', '.jsx', '.d.ts'].includes(ext)) {
        fixFile(fullPath);
      }
    }
  }
}

console.log('🚀 开始最终语法清理...');
console.log('='.repeat(50));

// 从 src 目录开始处理
const srcDir = path.join(process.cwd(), 'src');
if (fs.existsSync(srcDir)) {
  processDirectory(srcDir);
}

console.log('='.repeat(50));
console.log(`✅ 最终语法清理完成!`);
console.log(`📊 统计信息:`);
console.log(`   - 修复文件数: ${fileCount}`);
console.log(`   - 总修复数: ${fixCount}`);
console.log(`   - 平均每文件修复数: ${fileCount > 0 ? (fixCount / fileCount).toFixed(1) : 0}`); 