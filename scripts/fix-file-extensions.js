#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * 智能文件扩展名修复脚本
 * 索克生活APP - 自动修复.ts文件中包含JSX的扩展名问题
 */

class FileExtensionFixer {
  constructor() {
    this.fixedFiles = [];
    this.errors = [];
    this.jsxPatterns = [
      /<[A-Z][a-zA-Z0-9]*[\s\S]*?>/,  // JSX标签
      /<\/[A-Z][a-zA-Z0-9]*>/,        // JSX闭合标签
      /<[a-z]+[\s\S]*?\/>/,           // 自闭合标签
      /React\.createElement/,          // React.createElement
      /jsx:/,                         // JSX命名空间
    ];
  }

  /**
   * 检查文件是否包含JSX语法
   */
  containsJSX(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      return this.jsxPatterns.some(pattern => pattern.test(content));
    } catch (error) {
      console.error(`读取文件失败: ${filePath}`, error.message);
      return false;
    }
  }

  /**
   * 递归查找所有.ts文件
   */
  findTsFiles(dir) {
    const files = [];
    
    try {
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // 跳过node_modules等目录
          if (!['node_modules', '.git', '.expo', 'android', 'ios'].includes(item)) {
            files.push(...this.findTsFiles(fullPath));
          }
        } else if (item.endsWith('.ts') && !item.endsWith('.d.ts')) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      console.error(`读取目录失败: ${dir}`, error.message);
    }
    
    return files;
  }

  /**
   * 重命名文件
   */
  renameFile(oldPath, newPath) {
    try {
      fs.renameSync(oldPath, newPath);
      console.log(`✅ 重命名: ${oldPath} -> ${newPath}`);
      return true;
    } catch (error) {
      console.error(`❌ 重命名失败: ${oldPath}`, error.message);
      this.errors.push({
        file: oldPath,
        error: error.message,
        type: 'rename'
      });
      return false;
    }
  }

  /**
   * 更新导入语句中的文件扩展名
   */
  updateImportStatements(dir) {
    const allFiles = this.findAllFiles(dir, ['.ts', '.tsx', '.js', '.jsx']);
    
    for (const filePath of allFiles) {
      try {
        let content = fs.readFileSync(filePath, 'utf8');
        let updated = false;
        
        // 更新import语句
        content = content.replace(
          /import\s+.*?\s+from\s+['"]([^'"]+)\.ts['"]/g,
          (match, importPath) => {
            const fullImportPath = path.resolve(path.dirname(filePath), importPath + '.ts');
            const tsxPath = fullImportPath.replace(/\.ts$/, '.tsx');
            
            if (fs.existsSync(tsxPath)) {
              updated = true;
              return match.replace('.ts', '.tsx');
            }
            return match;
          }
        );
        
        // 更新require语句
        content = content.replace(
          /require\(['"]([^'"]+)\.ts['"]\)/g,
          (match, importPath) => {
            const fullImportPath = path.resolve(path.dirname(filePath), importPath + '.ts');
            const tsxPath = fullImportPath.replace(/\.ts$/, '.tsx');
            
            if (fs.existsSync(tsxPath)) {
              updated = true;
              return match.replace('.ts', '.tsx');
            }
            return match;
          }
        );
        
        if (updated) {
          fs.writeFileSync(filePath, content, 'utf8');
          console.log(`📝 更新导入语句: ${filePath}`);
        }
      } catch (error) {
        console.error(`更新导入语句失败: ${filePath}`, error.message);
      }
    }
  }

  /**
   * 查找所有指定扩展名的文件
   */
  findAllFiles(dir, extensions) {
    const files = [];
    
    try {
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!['node_modules', '.git', '.expo', 'android', 'ios'].includes(item)) {
            files.push(...this.findAllFiles(fullPath, extensions));
          }
        } else if (extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      console.error(`读取目录失败: ${dir}`, error.message);
    }
    
    return files;
  }

  /**
   * 执行修复
   */
  async fix() {
    console.log('🔧 开始修复文件扩展名...\n');
    
    const projectRoot = process.cwd();
    const tsFiles = this.findTsFiles(projectRoot);
    
    console.log(`📁 找到 ${tsFiles.length} 个 .ts 文件`);
    
    // 第一步：重命名包含JSX的.ts文件为.tsx
    for (const tsFile of tsFiles) {
      if (this.containsJSX(tsFile)) {
        const tsxFile = tsFile.replace(/\.ts$/, '.tsx');
        if (this.renameFile(tsFile, tsxFile)) {
          this.fixedFiles.push({
            old: tsFile,
            new: tsxFile,
            reason: 'Contains JSX syntax'
          });
        }
      }
    }
    
    // 第二步：更新所有文件中的导入语句
    console.log('\n📝 更新导入语句...');
    this.updateImportStatements(projectRoot);
    
    // 第三步：更新Jest配置以支持.tsx文件
    this.updateJestConfig();
    
    // 第四步：更新TypeScript配置
    this.updateTsConfig();
    
    this.generateReport();
  }

  /**
   * 更新Jest配置
   */
  updateJestConfig() {
    const jestConfigPath = path.join(process.cwd(), 'jest.config.js');
    
    try {
      if (fs.existsSync(jestConfigPath)) {
        let content = fs.readFileSync(jestConfigPath, 'utf8');
        
        // 确保Jest支持.tsx文件
        if (!content.includes('tsx')) {
          content = content.replace(
            /testMatch:\s*\[[^\]]*\]/,
            `testMatch: [
    '**/__tests__/**/*.(ts|tsx|js)',
    '**/*.(test|spec).(ts|tsx|js)'
  ]`
          );
          
          content = content.replace(
            /moduleFileExtensions:\s*\[[^\]]*\]/,
            `moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node']`
          );
          
          fs.writeFileSync(jestConfigPath, content, 'utf8');
          console.log('✅ 更新Jest配置以支持.tsx文件');
        }
      }
    } catch (error) {
      console.error('更新Jest配置失败:', error.message);
    }
  }

  /**
   * 更新TypeScript配置
   */
  updateTsConfig() {
    const tsConfigPath = path.join(process.cwd(), 'tsconfig.json');
    
    try {
      if (fs.existsSync(tsConfigPath)) {
        const content = fs.readFileSync(tsConfigPath, 'utf8');
        const config = JSON.parse(content);
        
        // 确保包含.tsx文件
        if (config.include && !config.include.some(pattern => pattern.includes('tsx'))) {
          config.include.push('**/*.tsx');
          fs.writeFileSync(tsConfigPath, JSON.stringify(config, null, 2), 'utf8');
          console.log('✅ 更新TypeScript配置以支持.tsx文件');
        }
      }
    } catch (error) {
      console.error('更新TypeScript配置失败:', error.message);
    }
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    console.log('\n📊 文件扩展名修复报告');
    console.log('='.repeat(50));
    
    console.log(`✅ 成功修复文件: ${this.fixedFiles.length}`);
    console.log(`❌ 修复失败: ${this.errors.length}`);
    
    if (this.fixedFiles.length > 0) {
      console.log('\n📝 修复的文件:');
      this.fixedFiles.forEach(file => {
        console.log(`  ${file.old} -> ${file.new}`);
        console.log(`    原因: ${file.reason}`);
      });
    }
    
    if (this.errors.length > 0) {
      console.log('\n❌ 修复失败的文件:');
      this.errors.forEach(error => {
        console.log(`  ${error.file}: ${error.error}`);
      });
    }
    
    // 保存报告到文件
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        fixedFiles: this.fixedFiles.length,
        errors: this.errors.length,
        totalProcessed: this.fixedFiles.length + this.errors.length
      },
      fixedFiles: this.fixedFiles,
      errors: this.errors
    };
    
    fs.writeFileSync(
      'FILE_EXTENSION_FIX_REPORT.json',
      JSON.stringify(report, null, 2),
      'utf8'
    );
    
    console.log('\n📄 详细报告已保存到: FILE_EXTENSION_FIX_REPORT.json');
  }
}

// 执行修复
if (require.main === module) {
  const fixer = new FileExtensionFixer();
  fixer.fix().catch(console.error);
}

module.exports = FileExtensionFixer; 