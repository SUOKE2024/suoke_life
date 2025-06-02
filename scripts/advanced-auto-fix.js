const fs = require('fs');
const path = require('path');

class AdvancedAutoFixer {
  constructor() {
    this.fixCount = 0;
    this.fileCount = 0;
    this.fixedFiles = [];
  }

  // 高级修复规则
  getAdvancedFixRules() {
    return [
      // 修复注释格式错误
      {
        pattern: /\/\/([^\/\n]*)/g,
        replacement: '/* $1 */',
        description: '修复注释格式'
      },
      
      // 修复对象属性定义错误 - 多余的逗号
      {
        pattern: /,(\s*})/g,
        replacement: '$1',
        description: '移除对象末尾多余的逗号'
      },
      
      // 修复对象属性定义错误 - 缺少逗号
      {
        pattern: /(\w+:\s*[^,}\n]+)(\s+)(\w+:)/g,
        replacement: '$1,$2$3',
        description: '添加缺少的逗号'
      },
      
      // 修复导入语句缺少分号
      {
        pattern: /(import\s+.*from\s+['"][^'"]+['"])(?!\s*;)/g,
        replacement: '$1;',
        description: '添加导入语句分号'
      },
      
      // 修复导出语句缺少分号
      {
        pattern: /(export\s+.*[^;])(\s*$)/gm,
        replacement: '$1;$2',
        description: '添加导出语句分号'
      },
      
      // 修复函数调用缺少分号
      {
        pattern: /(\w+\([^)]*\))(?!\s*[;,.\[\]{}])/g,
        replacement: '$1;',
        description: '添加函数调用分号'
      },
      
      // 修复变量声明缺少分号
      {
        pattern: /(const\s+\w+\s*=\s*[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加变量声明分号'
      },
      
      // 修复let声明缺少分号
      {
        pattern: /(let\s+\w+\s*=\s*[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加let声明分号'
      },
      
      // 修复var声明缺少分号
      {
        pattern: /(var\s+\w+\s*=\s*[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加var声明分号'
      },
      
      // 修复JSX属性错误
      {
        pattern: /(\w+)=\{([^}]+)\}\s*\/>/g,
        replacement: '$1={$2} />',
        description: '修复JSX属性格式'
      },
      
      // 修复StyleSheet对象语法错误
      {
        pattern: /(\w+):\s*\{,/g,
        replacement: '$1: {',
        description: '修复StyleSheet对象语法'
      },
      
      // 修复React组件导入错误
      {
        pattern: /import\s+React\s*,\s*\{([^}]+)\}\s*from\s*['"]react['"]/g,
        replacement: 'import React, { $1 } from \'react\'',
        description: '修复React导入格式'
      },
      
      // 修复React Native导入错误
      {
        pattern: /import\s*\{([^}]+)\}\s*from\s*['"]react-native['"]/g,
        replacement: 'import { $1 } from \'react-native\'',
        description: '修复React Native导入格式'
      },
      
      // 修复接口定义错误
      {
        pattern: /interface\s+(\w+)\s*\{([^}]*),(\s*}\s*)/g,
        replacement: 'interface $1 {$2$3',
        description: '修复接口定义末尾逗号'
      },
      
      // 修复类型定义错误
      {
        pattern: /type\s+(\w+)\s*=\s*([^;]+)(?!\s*;)/g,
        replacement: 'type $1 = $2;',
        description: '添加类型定义分号'
      },
      
      // 修复枚举定义错误
      {
        pattern: /enum\s+(\w+)\s*\{([^}]*),(\s*}\s*)/g,
        replacement: 'enum $1 {$2$3',
        description: '修复枚举定义末尾逗号'
      },
      
      // 修复箭头函数语法错误
      {
        pattern: /=>\s*\{([^}]*),(\s*}\s*)/g,
        replacement: '=> {$1$2',
        description: '修复箭头函数末尾逗号'
      },
      
      // 修复数组定义错误
      {
        pattern: /\[([^\]]*),(\s*\])/g,
        replacement: '[$1$2',
        description: '修复数组末尾逗号'
      },
      
      // 修复对象方法定义错误
      {
        pattern: /(\w+)\s*:\s*\(([^)]*)\)\s*=>\s*\{/g,
        replacement: '$1: ($2) => {',
        description: '修复对象方法定义'
      },
      
      // 修复条件语句缺少分号
      {
        pattern: /(if\s*\([^)]+\)\s*[^{;]+)(?!\s*[;{])/g,
        replacement: '$1;',
        description: '添加条件语句分号'
      },
      
      // 修复return语句缺少分号
      {
        pattern: /(return\s+[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加return语句分号'
      },
      
      // 修复throw语句缺少分号
      {
        pattern: /(throw\s+[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加throw语句分号'
      },
      
      // 修复break语句缺少分号
      {
        pattern: /(break)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加break语句分号'
      },
      
      // 修复continue语句缺少分号
      {
        pattern: /(continue)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加continue语句分号'
      },
      
      // 修复模板字符串错误
      {
        pattern: /`([^`]*)\$\{([^}]*)\}([^`]*)`/g,
        replacement: '`$1\${$2}$3`',
        description: '修复模板字符串格式'
      },
      
      // 修复解构赋值错误
      {
        pattern: /const\s*\{\s*([^}]+)\s*\}\s*=\s*([^;]+)(?!\s*;)/g,
        replacement: 'const { $1 } = $2;',
        description: '修复解构赋值分号'
      },
      
      // 修复数组解构错误
      {
        pattern: /const\s*\[\s*([^\]]+)\s*\]\s*=\s*([^;]+)(?!\s*;)/g,
        replacement: 'const [$1] = $2;',
        description: '修复数组解构分号'
      },
      
      // 修复async/await语法错误
      {
        pattern: /(await\s+[^;]+)(?!\s*;)/g,
        replacement: '$1;',
        description: '添加await语句分号'
      },
      
      // 修复Promise语法错误
      {
        pattern: /\.then\s*\(\s*([^)]+)\s*\)(?!\s*[;.])/g,
        replacement: '.then($1);',
        description: '添加Promise分号'
      },
      
      // 修复catch语法错误
      {
        pattern: /\.catch\s*\(\s*([^)]+)\s*\)(?!\s*[;.])/g,
        replacement: '.catch($1);',
        description: '添加catch分号'
      }
    ];
  }

  // 检查文件是否需要修复
  shouldProcessFile(filePath) {
    const ext = path.extname(filePath);
    return ['.ts', '.tsx', '.js', '.jsx'].includes(ext);
  }

  // 修复单个文件
  fixFile(filePath) {
    try {
      if (!this.shouldProcessFile(filePath)) {
        return false;
      }

      const content = fs.readFileSync(filePath, 'utf8');
      let fixedContent = content;
      let fileFixCount = 0;
      const rules = this.getAdvancedFixRules();

      // 应用所有修复规则
      for (const rule of rules) {
        const matches = fixedContent.match(rule.pattern);
        if (matches) {
          fixedContent = fixedContent.replace(rule.pattern, rule.replacement);
          fileFixCount += matches.length;
        }
      }

      // 如果有修复，写回文件
      if (fileFixCount > 0) {
        fs.writeFileSync(filePath, fixedContent, 'utf8');
        this.fixCount += fileFixCount;
        this.fixedFiles.push({
          file: filePath,
          fixes: fileFixCount
        });
        console.log(`✅ ${path.relative(process.cwd(), filePath)} (修复 ${fileFixCount} 处)`);
        return true;
      } else {
        console.log(`⚪ ${path.relative(process.cwd(), filePath)} (无需修复)`);
        return false;
      }
    } catch (error) {
      console.error(`❌ ${path.relative(process.cwd(), filePath)}: ${error.message}`);
      return false;
    }
  }

  // 递归处理目录
  processDirectory(dirPath) {
    try {
      const items = fs.readdirSync(dirPath);
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // 跳过某些目录
          if (['node_modules', '.git', 'dist', 'build', '.expo'].includes(item)) {
            continue;
          }
          this.processDirectory(fullPath);
        } else if (stat.isFile()) {
          this.fileCount++;
          this.fixFile(fullPath);
        }
      }
    } catch (error) {
      console.error(`处理目录 ${dirPath} 时出错: ${error.message}`);
    }
  }

  // 生成报告
  generateReport() {
    console.log('\n📊 高级自动修复报告');
    console.log('==================================================');
    console.log(`📁 总文件数: ${this.fileCount}`);
    console.log(`🔧 已修复文件: ${this.fixedFiles.length}`);
    console.log(`✨ 总修复数: ${this.fixCount}`);
    
    if (this.fixedFiles.length > 0) {
      console.log('\n🔧 修复详情:');
      this.fixedFiles.forEach(({ file, fixes }) => {
        console.log(`   ${path.relative(process.cwd(), file)}: ${fixes} 处修复`);
      });
    }
    
    const fixRate = this.fileCount > 0 ? Math.round((this.fixedFiles.length / this.fileCount) * 100) : 0;
    console.log(`\n📈 修复率: ${fixRate}%`);
    console.log('🎉 高级自动修复完成！建议运行代码质量检查验证结果。');
  }

  // 运行修复
  run() {
    console.log('🚀 开始高级自动修复...\n');
    
    const srcPath = path.join(process.cwd(), 'src');
    if (fs.existsSync(srcPath)) {
      this.processDirectory(srcPath);
    } else {
      console.error('❌ src 目录不存在');
      process.exit(1);
    }
    
    this.generateReport();
  }
}

// 运行修复器
const fixer = new AdvancedAutoFixer();
fixer.run(); 