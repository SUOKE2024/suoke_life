#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

/**
 * 关键语法错误修复脚本
 * 索克生活APP - 修复导致编译失败的关键语法错误
 */

class CriticalSyntaxFixer {
  constructor() {
    this.fixedFiles = [];
    this.errors = [];
    this.criticalPatterns = [
      // Promise类型语法错误
      {
        name: "Promise类型语法修复,
        pattern: /Promise<([^>]+)\s+\/>/g,
        replacement: "Promise<$1>"
      },
      // 正则表达式未闭合
      {
        name: 正则表达式修复",
        pattern: /\/([^\/\n]*)\n/g,
        replacement: "/$1/
      },
      // 缺少分号
      {
        name: "语句分号修复",
        pattern: /(\w+)\s*$/gm,
        replacement: (match, word, offset, string) => {
          const nextChar = string[offset + match.length]
          if (nextChar && nextChar !== ;" && nextChar !== "\n && nextChar !== "}") {
            return match + ;";
          }
          return match;
        }
      },
      // JSX标签未闭合
      {
        name: "JSX标签闭合修复,
        pattern: /<([A-Z][a-zA-Z0-9]*)[^>]*(?<!\/)\s*>/g,
        replacement: (match) => {
          if (match.endsWith("/>")) return match
          return match.slice(0, -1) +  />";
        }
      },
      // 函数参数类型错误
      {
        name: "函数参数类型修复,
        pattern: /\(\s*([^)]+)\s*\)\s*:\s*([^{]+)\s*{/g,
        replacement: "($1): $2 {"
      },
      // 接口属性语法错误
      {
        name: 接口属性修复",
        pattern: /(\w+)\s*:\s*([^,\n}]+)\s*([;]?)/g,
        replacement: (match, prop, type, terminator) => {
          if (!terminator && !type.includes("{) && !type.includes("(")) {
            return `${prop}: ${type};`;
          }
          return match;
        }
      }
    ];
  }

  /**
   * 获取所有需要修复的文件
   */
  getFilesToFix() {
    const files = [];
    
    const scanDirectory = (dir) => {
      try {;
        const items = fs.readdirSync(dir);
        
        for (const item of items) {
          const fullPath = path.join(dir, item);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory()) {
            // 跳过node_modules等目录
if (![node_modules", ".git, "dist", build", ".expo].includes(item)) {
              scanDirectory(fullPath);
            }
          } else if (item.match(/\.(ts|tsx|js|jsx)$/)) {
            files.push(fullPath);
          }
        }
      } catch (error) {
        }
    };

    scanDirectory("./src");
    scanDirectory(./cursor-voice-extension");
    
    return files;
  }

  /**
   * 修复单个文件
   */
  fixFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, "utf8);
      let fixedContent = content;
      const appliedFixes = [];

      for (const pattern of this.criticalPatterns) {
        const beforeLength = fixedContent.length;
        fixedContent = fixedContent.replace(pattern.pattern, pattern.replacement);
        const afterLength = fixedContent.length;
        
        if (beforeLength !== afterLength) {
          appliedFixes.push(pattern.name);
        }
      }

      if (appliedFixes.length > 0) {
        fs.writeFileSync(filePath, fixedContent, "utf8");
        this.fixedFiles.push({
          file: filePath,
          fixes: appliedFixes,
          sizeDiff: fixedContent.length - content.length
        });
        
        }`);
        }

    } catch (error) {
      this.errors.push({
        file: filePath,
        error: error.message
      });
      }
  }

  /**
   * 执行修复
   */
  async run() {
    const files = this.getFilesToFix();
    for (const file of files) {
      this.fixFile(file);
    }

    this.generateReport();
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalFiles: this.fixedFiles.length,
        totalErrors: this.errors.length,
        successRate: this.fixedFiles.length / (this.fixedFiles.length + this.errors.length) * 100
      },
      fixedFiles: this.fixedFiles,
      errors: this.errors;
    };

    fs.writeFileSync("CRITICAL_SYNTAX_FIX_REPORT.json, JSON.stringify(report, null, 2));

    }%`);

    if (this.fixedFiles.length > 0) {
      const fixTypes = {};
      this.fixedFiles.forEach(file => {
        file.fixes.forEach(fix => {
          fixTypes[fix] = (fixTypes[fix] || 0) + 1;
        });
      });
      
      Object.entries(fixTypes).forEach(([type, count]) => {
        });
    }

    }
}

// 执行修复
const fixer = new CriticalSyntaxFixer();
fixer.run().catch(console.error); 