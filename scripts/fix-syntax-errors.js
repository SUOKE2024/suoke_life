#!/usr/bin/env node

/**
 * 语法错误修复脚本
 * 修复优化过程中引入的重复import语句等语法错误
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class SyntaxErrorFixer {
  constructor() {
    this.fixedFiles = [];
    this.errors = [];
  }

  /**
   * 修复重复的import语句
   */
  fixDuplicateImports(filePath) {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      let modified = false;

      // 修复重复的 "import type {" 语句
      const duplicateImportTypeRegex = /import type \{\s*\nimport type \{/g;
      if (duplicateImportTypeRegex.test(content)) {
        content = content.replace(duplicateImportTypeRegex, 'import type {');
        modified = true;
      }

      // 修复重复的 "import {" 语句
      const duplicateImportRegex = /import \{\s*\nimport \{/g;
      if (duplicateImportRegex.test(content)) {
        content = content.replace(duplicateImportRegex, 'import {');
        modified = true;
      }

      // 修复孤立的 "import {" 行
      const orphanImportRegex = /^import \{\s*$/gm;
      if (orphanImportRegex.test(content)) {
        content = content.replace(orphanImportRegex, '');
        modified = true;
      }

      // 修复孤立的 "import type {" 行
      const orphanImportTypeRegex = /^import type \{\s*$/gm;
      if (orphanImportTypeRegex.test(content)) {
        content = content.replace(orphanImportTypeRegex, '');
        modified = true;
      }

      // 清理多余的空行
      content = content.replace(/\n\n\n+/g, '\n\n');

      if (modified) {
        fs.writeFileSync(filePath, content);
        this.fixedFiles.push(filePath);
        console.log(`✅ 修复: ${filePath}`);
      }

      return modified;
    } catch (error) {
      this.errors.push({ file: filePath, error: error.message });
      console.error(`❌ 错误: ${filePath} - ${error.message}`);
      return false;
    }
  }

  /**
   * 修复错误的文件引用
   */
  fixFileReferences(filePath) {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      let modified = false;

      // 修复错误的App引用
      if (content.includes('import App from "../../Appx"')) {
        content = content.replace('import App from "../../Appx"', 'import App from "../../App"');
        modified = true;
      }

      if (modified) {
        fs.writeFileSync(filePath, content);
        this.fixedFiles.push(filePath);
        console.log(`✅ 修复文件引用: ${filePath}`);
      }

      return modified;
    } catch (error) {
      this.errors.push({ file: filePath, error: error.message });
      console.error(`❌ 错误: ${filePath} - ${error.message}`);
      return false;
    }
  }

  /**
   * 扫描并修复所有TypeScript文件
   */
  async fixAllFiles() {
    console.log('🔧 开始修复语法错误...\n');

    // 获取所有TypeScript文件
    const tsFiles = glob.sync('src/**/*.{ts,tsx}', {
      ignore: ['node_modules/**', '.backup/**', 'coverage/**']
    });

    const testFiles = glob.sync('src/**/*.test.{ts,tsx}', {
      ignore: ['node_modules/**', '.backup/**', 'coverage/**']
    });

    const allFiles = [...tsFiles, ...testFiles];

    console.log(`📁 找到 ${allFiles.length} 个文件需要检查`);

    for (const file of allFiles) {
      // 修复重复import语句
      this.fixDuplicateImports(file);
      
      // 修复文件引用
      this.fixFileReferences(file);
    }

    // 生成报告
    this.generateReport();
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    console.log('\n📊 语法错误修复报告');
    console.log('='.repeat(50));
    console.log(`✅ 修复的文件数量: ${this.fixedFiles.length}`);
    console.log(`❌ 错误的文件数量: ${this.errors.length}`);

    if (this.fixedFiles.length > 0) {
      console.log('\n修复的文件:');
      this.fixedFiles.forEach(file => {
        console.log(`  - ${file}`);
      });
    }

    if (this.errors.length > 0) {
      console.log('\n错误的文件:');
      this.errors.forEach(({ file, error }) => {
        console.log(`  - ${file}: ${error}`);
      });
    }

    // 保存报告
    const report = {
      timestamp: new Date().toISOString(),
      fixedFiles: this.fixedFiles,
      errors: this.errors,
      summary: {
        totalFixed: this.fixedFiles.length,
        totalErrors: this.errors.length
      }
    };

    fs.writeFileSync('SYNTAX_FIX_REPORT.json', JSON.stringify(report, null, 2));
    console.log('\n📄 详细报告已保存到: SYNTAX_FIX_REPORT.json');
  }
}

// 运行修复
async function main() {
  const fixer = new SyntaxErrorFixer();
  await fixer.fixAllFiles();
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = SyntaxErrorFixer; 