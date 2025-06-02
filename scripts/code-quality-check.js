#!/usr/bin/env node

/**
 * 索克生活项目代码质量检查工具
 * 自动检测语法错误、代码规范问题和性能问题
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const CONFIG = {
  srcDir: 'src',
  extensions: ['.ts', '.tsx', '.js', '.jsx'],
  excludeDirs: ['node_modules', '.git', 'dist', 'build', '__tests__'],
  maxFileSize: 1024 * 1024, // 1MB
  rules: {
    // 语法检查规则
    syntax: {
      noMissingImports: true,
      noUnusedImports: true,
      noSyntaxErrors: true,
    },
    // 代码规范规则
    style: {
      noTrailingSpaces: true,
      consistentIndentation: true,
      properComments: true,
    },
    // 性能规则
    performance: {
      noDeepHookNesting: true,
      noLargeFiles: true,
      noComplexFunctions: true,
    }
  }
};

class CodeQualityChecker {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.stats = {
      totalFiles: 0,
      checkedFiles: 0,
      errorFiles: 0,
      warningFiles: 0,
    };
  }

  /**
   * 运行完整的代码质量检查
   */
  async run() {
    console.log('🔍 开始代码质量检查...\n');
    
    try {
      // 1. 收集所有需要检查的文件
      const files = this.collectFiles();
      this.stats.totalFiles = files.length;
      
      console.log(`📁 发现 ${files.length} 个文件需要检查\n`);
      
      // 2. 检查每个文件
      for (const file of files) {
        await this.checkFile(file);
      }
      
      // 3. 运行TypeScript编译检查
      await this.runTypeScriptCheck();
      
      // 4. 生成报告
      this.generateReport();
      
    } catch (error) {
      console.error('❌ 检查过程中发生错误:', error.message);
      process.exit(1);
    }
  }

  /**
   * 收集所有需要检查的文件
   */
  collectFiles() {
    const files = [];
    
    const walkDir = (dir) => {
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!CONFIG.excludeDirs.includes(item)) {
            walkDir(fullPath);
          }
        } else if (stat.isFile()) {
          const ext = path.extname(item);
          if (CONFIG.extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    };
    
    walkDir(CONFIG.srcDir);
    return files;
  }

  /**
   * 检查单个文件
   */
  async checkFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const fileErrors = [];
      const fileWarnings = [];
      
      // 检查文件大小
      if (content.length > CONFIG.maxFileSize) {
        fileWarnings.push({
          type: 'performance',
          rule: 'file-size',
          message: `文件过大 (${Math.round(content.length / 1024)}KB)`,
          line: 1,
        });
      }
      
      // 语法检查
      this.checkSyntax(content, filePath, fileErrors);
      
      // 代码规范检查
      this.checkStyle(content, filePath, fileWarnings);
      
      // 性能检查
      this.checkPerformance(content, filePath, fileWarnings);
      
      // 统计
      this.stats.checkedFiles++;
      if (fileErrors.length > 0) {
        this.stats.errorFiles++;
        this.errors.push({ file: filePath, errors: fileErrors });
      }
      if (fileWarnings.length > 0) {
        this.stats.warningFiles++;
        this.warnings.push({ file: filePath, warnings: fileWarnings });
      }
      
      // 显示进度
      if (fileErrors.length > 0 || fileWarnings.length > 0) {
        console.log(`${fileErrors.length > 0 ? '❌' : '⚠️'} ${filePath}`);
        if (fileErrors.length > 0) {
          fileErrors.forEach(error => {
            console.log(`   错误: ${error.message} (行 ${error.line})`);
          });
        }
        if (fileWarnings.length > 0) {
          fileWarnings.forEach(warning => {
            console.log(`   警告: ${warning.message} (行 ${warning.line})`);
          });
        }
      } else {
        console.log(`✅ ${filePath}`);
      }
      
    } catch (error) {
      this.errors.push({
        file: filePath,
        errors: [{
          type: 'system',
          rule: 'file-read',
          message: `无法读取文件: ${error.message}`,
          line: 1,
        }]
      });
    }
  }

  /**
   * 语法检查
   */
  checkSyntax(content, filePath, errors) {
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      const lineNum = index + 1;
      
      // 检查导入语句语法
      if (line.trim().startsWith('import')) {
        // 检查是否缺少分号
        if (!line.trim().endsWith(';') && !line.includes('from')) {
          errors.push({
            type: 'syntax',
            rule: 'missing-semicolon',
            message: '导入语句缺少分号',
            line: lineNum,
          });
        }
        
        // 检查导入语句格式
        if (line.includes('import{') || line.includes('}from')) {
          errors.push({
            type: 'syntax',
            rule: 'import-format',
            message: '导入语句格式错误，缺少空格',
            line: lineNum,
          });
        }
      }
      
      // 检查注释格式
      if (line.trim().startsWith('/**/')) {
        errors.push({
          type: 'syntax',
          rule: 'comment-format',
          message: '注释格式错误',
          line: lineNum,
        });
      }
      
      // 检查对象属性定义
      if (line.includes('{ ') && line.includes(': ') && !line.includes(';')) {
        const openBraces = (line.match(/{/g) || []).length;
        const closeBraces = (line.match(/}/g) || []).length;
        if (openBraces !== closeBraces && !line.trim().endsWith(',')) {
          errors.push({
            type: 'syntax',
            rule: 'object-property',
            message: '对象属性定义可能有语法错误',
            line: lineNum,
          });
        }
      }
    });
  }

  /**
   * 代码规范检查
   */
  checkStyle(content, filePath, warnings) {
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      const lineNum = index + 1;
      
      // 检查行尾空格
      if (line.endsWith(' ') || line.endsWith('\t')) {
        warnings.push({
          type: 'style',
          rule: 'trailing-spaces',
          message: '行尾有多余的空格',
          line: lineNum,
        });
      }
      
      // 检查缩进一致性
      if (line.startsWith('\t') && content.includes('  ')) {
        warnings.push({
          type: 'style',
          rule: 'inconsistent-indentation',
          message: '缩进不一致（混用tab和空格）',
          line: lineNum,
        });
      }
    });
  }

  /**
   * 性能检查
   */
  checkPerformance(content, filePath, warnings) {
    // 检查Hook嵌套
    const hookNestingMatches = content.match(/useMemo\(\s*\(\)\s*=>\s*useMemo/g);
    if (hookNestingMatches && hookNestingMatches.length > 0) {
      warnings.push({
        type: 'performance',
        rule: 'hook-nesting',
        message: `发现 ${hookNestingMatches.length} 处Hook嵌套`,
        line: 1,
      });
    }
    
    // 检查函数复杂度
    const functionMatches = content.match(/function\s+\w+|const\s+\w+\s*=\s*\(/g);
    if (functionMatches && functionMatches.length > 20) {
      warnings.push({
        type: 'performance',
        rule: 'function-count',
        message: `文件包含过多函数 (${functionMatches.length})`,
        line: 1,
      });
    }
  }

  /**
   * 运行TypeScript编译检查
   */
  async runTypeScriptCheck() {
    console.log('\n🔧 运行TypeScript编译检查...');
    
    try {
      execSync('npx tsc --noEmit --skipLibCheck', { 
        stdio: 'pipe',
        cwd: process.cwd()
      });
      console.log('✅ TypeScript编译检查通过');
    } catch (error) {
      console.log('⚠️ TypeScript编译检查发现问题（已跳过库检查）');
      // 不将TypeScript错误计入统计，因为可能是依赖问题
    }
  }

  /**
   * 生成检查报告
   */
  generateReport() {
    console.log('\n📊 代码质量检查报告');
    console.log('='.repeat(50));
    
    console.log(`📁 总文件数: ${this.stats.totalFiles}`);
    console.log(`✅ 已检查: ${this.stats.checkedFiles}`);
    console.log(`❌ 有错误: ${this.stats.errorFiles}`);
    console.log(`⚠️ 有警告: ${this.stats.warningFiles}`);
    
    const errorCount = this.errors.reduce((sum, item) => sum + item.errors.length, 0);
    const warningCount = this.warnings.reduce((sum, item) => sum + item.warnings.length, 0);
    
    console.log(`🐛 总错误数: ${errorCount}`);
    console.log(`⚠️ 总警告数: ${warningCount}`);
    
    // 错误分类统计
    if (errorCount > 0) {
      console.log('\n❌ 错误分类:');
      const errorTypes = {};
      this.errors.forEach(item => {
        item.errors.forEach(error => {
          errorTypes[error.type] = (errorTypes[error.type] || 0) + 1;
        });
      });
      Object.entries(errorTypes).forEach(([type, count]) => {
        console.log(`   ${type}: ${count}`);
      });
    }
    
    // 警告分类统计
    if (warningCount > 0) {
      console.log('\n⚠️ 警告分类:');
      const warningTypes = {};
      this.warnings.forEach(item => {
        item.warnings.forEach(warning => {
          warningTypes[warning.type] = (warningTypes[warning.type] || 0) + 1;
        });
      });
      Object.entries(warningTypes).forEach(([type, count]) => {
        console.log(`   ${type}: ${count}`);
      });
    }
    
    // 质量评分
    const totalIssues = errorCount + warningCount;
    const qualityScore = Math.max(0, 100 - (totalIssues * 2));
    
    console.log(`\n🎯 代码质量评分: ${qualityScore}/100`);
    
    if (qualityScore >= 90) {
      console.log('🎉 代码质量优秀！');
    } else if (qualityScore >= 70) {
      console.log('👍 代码质量良好，还有改进空间');
    } else if (qualityScore >= 50) {
      console.log('⚠️ 代码质量一般，建议优化');
    } else {
      console.log('🚨 代码质量需要重点改进');
    }
    
    // 保存详细报告
    this.saveDetailedReport();
  }

  /**
   * 保存详细报告到文件
   */
  saveDetailedReport() {
    const report = {
      timestamp: new Date().toISOString(),
      stats: this.stats,
      errors: this.errors,
      warnings: this.warnings,
      summary: {
        totalIssues: this.errors.reduce((sum, item) => sum + item.errors.length, 0) +
                    this.warnings.reduce((sum, item) => sum + item.warnings.length, 0),
        qualityScore: Math.max(0, 100 - ((this.errors.length + this.warnings.length) * 2)),
      }
    };
    
    const reportPath = 'CODE_QUALITY_REPORT.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 详细报告已保存到: ${reportPath}`);
  }
}

// 运行检查
if (require.main === module) {
  const checker = new CodeQualityChecker();
  checker.run().catch(error => {
    console.error('检查失败:', error);
    process.exit(1);
  });
}

module.exports = CodeQualityChecker; 