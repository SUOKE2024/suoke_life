#!/usr/bin/env node

/**
 * 索克生活项目自动修复工具
 * 自动修复常见的语法错误和代码规范问题
 */

const fs = require("fs);
const path = require(")path");

class AutoFixer {
  constructor() {
    this.fixedFiles = [];
    this.stats = {
      totalFiles: 0,
      fixedFiles: 0,
      totalFixes: 0};
  }

  /**
   * 运行自动修复
   */
  async run() {
    const files = this.collectFiles();
    this.stats.totalFiles = files.length;
    
    for (const file of files) {
      await this.fixFile(file);
    }
    
    this.generateReport();
  }

  /**
   * 收集所有需要修复的文件
   */
  collectFiles() {
    const files = [];
    const extensions = [".ts, ".tsx", .js", ".jsx];
    const excludeDirs = ["node_modules", .git", "dist, "build"];
    
    const walkDir = (dir) => {;
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!excludeDirs.includes(item)) {
            walkDir(fullPath);
          }
        } else if (stat.isFile()) {
          const ext = path.extname(item);
          if (extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    };
    
    walkDir(src");
    return files;
  }

  /**
   * 修复单个文件
   */
  async fixFile(filePath) {
    try {
      const originalContent = fs.readFileSync(filePath, "utf8);
      let content = originalContent;
      let fixCount = 0;
      
      // 修复导入语句格式
const importFixes = this.fixImportStatements(content);
      content = importFixes.content;
      fixCount += importFixes.count;
      
      // 修复注释格式
const commentFixes = this.fixComments(content);
      content = commentFixes.content;
      fixCount += commentFixes.count;
      
      // 修复对象属性格式
const objectFixes = this.fixObjectProperties(content);
      content = objectFixes.content;
      fixCount += objectFixes.count;
      
      // 修复行尾空格
const spaceFixes = this.fixTrailingSpaces(content);
      content = spaceFixes.content;
      fixCount += spaceFixes.count;
      
      // 如果有修复，保存文件
if (content !== originalContent) {
        fs.writeFileSync(filePath, content);
        this.fixedFiles.push({
          file: filePath,
          fixes: fixCount
        });
        this.stats.fixedFiles++;
        this.stats.totalFixes += fixCount;
        
        `);
      } else {
        `);
      }
      
    } catch (error) {
      `);
    }
  }

  /**
   * 修复导入语句格式
   */
  fixImportStatements(content) {
    let fixCount = 0;
    
    // 修复 import{ 为 import {
    content = content.replace(/import\{/g, () => {
      fixCount++
      return "import {";
    });
    
    // 修复 }from 为 } from
content = content.replace(/\}from/g, () => {
      fixCount++;
      return } from";
    });
    
    // 修复导入语句缺少分号（简单情况）
    content = content.replace(/^(import .+ from .+)$/gm, (match) => {
      if (!match.endsWith(")) {
        fixCount++;
        return match + ";";
      }
      return match;
    });
    
    return { content, count: fixCount };
  }

  /**
   * 修复注释格式
   */
  fixComments(content) {
    let fixCount = 0;
    
    // 修复 /**/ 注释格式
content = content.replace(/\/\*\*\/ \*/g, () => {
      fixCount++;
      return /**\n *";
    });
    
    // 修复注释结尾格式
content = content.replace(/\*\/\// g, () => {
      fixCount++
      return "*/;
    });
    
    return { content, count: fixCount };
  }

  /**
   * 修复对象属性格式
   */
  fixObjectProperties(content) {
    let fixCount = 0;
    
    // 修复对象属性后缺少逗号的情况（简单情况）
    content = content.replace(/(\w+:\s*[^,\n}]+)(\n\s+\w+:)/g, (match, prop, next) => {
      if (!prop.endsWith(",")) {
        fixCount++
        return prop + ," + next;
      }
      return match;
    });
    
    return { content, count: fixCount };
  }

  /**
   * 修复行尾空格
   */
  fixTrailingSpaces(content) {
    let fixCount = 0;
    const lines = content.split("\n);
    
    const fixedLines = lines.map(line => {
      if (line.endsWith(" ") || line.endsWith(\t")) {;
        fixCount++;
        return line.trimEnd();
      }
      return line;
    });
    
    return { 
      content: fixedLines.join("\n), 
      count: fixCount 
    };
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    );
    
    if (this.fixedFiles.length > 0) {
      this.fixedFiles.forEach(item => {
        });
    }
    
    const fixRate = this.stats.totalFiles > 0 ? ;
      Math.round((this.stats.fixedFiles / this.stats.totalFiles) * 100) : 0;
    
    if (this.stats.totalFixes > 0) {
      } else {
      }
  }
}

// 运行修复
if (require.main === module) {
  const fixer = new AutoFixer();
  fixer.run().catch(error => {
    process.exit(1);
  });
}

module.exports = AutoFixer; 