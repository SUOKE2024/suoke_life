#!/usr/bin/env node

/**
 * 索克生活项目 - 精确自动修复工具
 * 只修复明确的语法错误，避免破坏代码逻辑
 */

const fs = require("fs");
const path = require("path");
const glob = require("glob");

class PreciseAutoFixer {
  constructor() {
    this.fixedFiles = [];
    this.totalFixes = 0;
  }

  // 精确修复规则 - 只修复明确的语法错误
  getPreciseFixRules() {
    return [
      // 修复对象末尾多余的逗号
      {
        pattern: /,(\s*})/g,
        replacement: "$1",
        description: "移除对象末尾多余的逗号"
      },

      // 修复数组末尾多余的逗号
      {
        pattern: /,(\s*\])/g,
        replacement: "$1",
        description: "移除数组末尾多余的逗号"
      },

      // 修复函数参数末尾多余的逗号
      {
        pattern: /,(\s*\))/g,
        replacement: "$1",
        description: "移除函数参数末尾多余的逗号"
      },

      // 修复接口定义末尾多余的逗号
      {
        pattern: /(interface\s+\w+\s*\{[^}]*),(\s*})/g,
        replacement: "$1$2",
        description: "修复接口定义末尾逗号"
      },

      // 修复枚举定义末尾多余的逗号
      {
        pattern: /(enum\s+\w+\s*\{[^}]*),(\s*})/g,
        replacement: "$1$2",
        description: "修复枚举定义末尾逗号"
      },

      // 修复StyleSheet对象末尾多余的逗号
      {
        pattern: /(StyleSheet\.create\(\{[^}]*),(\s*}\))/g,
        replacement: "$1$2",
        description: "修复StyleSheet对象末尾逗号"
      },

      // 修复简单的注释格式错误（只修复单行注释）
      {
        pattern: /\/\*\s*([^*\n]+?)\s*\*\//g,
        replacement: "// $1",
        description: "修复单行注释格式"
      },

      // 修复明确的导入语句缺少分号
      {
        pattern: /(import\s+[^]+from\s+["'][^"']+["'])(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加导入语句分号"
      },

      // 修复明确的导出语句缺少分号
      {
        pattern: /(export\s+default\s+\w+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加导出语句分号"
      },

      // 修复明确的变量声明缺少分号
      {
        pattern: /(const\s+\w+\s*=\s*[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加const声明分号"
      },

      // 修复明确的let声明缺少分号
      {
        pattern: /(let\s+\w+\s*=\s*[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加let声明分号"
      },

      // 修复明确的类型定义缺少分号
      {
        pattern: /(type\s+\w+\s*=\s*[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加类型定义分号"
      },

      // 修复明确的return语句缺少分号
      {
        pattern: /(return\s+[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加return语句分号"
      },

      // 修复明确的throw语句缺少分号
      {
        pattern: /(throw\s+[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加throw语句分号"
      },

      // 修复break语句缺少分号
      {
        pattern: /(break)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加break语句分号"
      },

      // 修复continue语句缺少分号
      {
        pattern: /(continue)(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加continue语句分号"
      },

      // 修复明确的函数调用缺少分号（行末）
      {
        pattern: /(\w+\([^)]*\))(\s*$)/gm,
        replacement: "$1;$2",
        description: "添加函数调用分号"
      },

      // 修复明确的解构赋值缺少分号
      {
        pattern: /(const\s*\{\s*[^}]+\s*\}\s*=\s*[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "修复解构赋值分号"
      },

      // 修复明确的数组解构缺少分号
      {
        pattern: /(const\s*[\s*[^]]+\s*\]\s*=\s*[^;]+)(\s*$)/gm,
        replacement: "$1;$2",
        description: "修复数组解构分号"
      }
    ];
  }

  /**
   * 运行精确修复
   */
  async run() {
    console.log("🔧 开始精确自动修复...");
    
    const files = glob.sync("src/**/*.{ts,tsx,js,jsx}", {
      ignore: ["**/node_modules/**", "**/dist/**", "**/*.d.ts"]
    });

    const rules = this.getPreciseFixRules();
    
    for (const file of files) {
      await this.fixFile(file, rules);
    }

    this.generateReport();
  }

  /**
   * 修复单个文件
   */
  async fixFile(filePath, rules) {
    try {
      let content = fs.readFileSync(filePath, "utf8");
      const originalContent = content;
      let fileFixCount = 0;

      for (const rule of rules) {
        const beforeMatches = content.match(rule.pattern);
        if (beforeMatches) {
          content = content.replace(rule.pattern, rule.replacement);
          const afterMatches = content.match(rule.pattern);
          const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
          if (fixedCount > 0) {
            fileFixCount += fixedCount;
            console.log(`  ✅ ${rule.description}: ${fixedCount} 处修复`);
          }
        }
      }

      if (content !== originalContent) {
        fs.writeFileSync(filePath, content);
        this.fixedFiles.push({
          file: filePath,
          fixes: fileFixCount
        });
        this.totalFixes += fileFixCount;
        console.log(`📝 修复文件: ${path.relative(process.cwd(), filePath)} (${fileFixCount} 处修复)`);
      }
    } catch (error) {
      console.error(`❌ 修复文件失败: ${filePath} - ${error.message}`);
    }
  }

  /**
   * 生成修复报告
   */
  generateReport() {
    console.log("\n📊 精确修复报告:");
    console.log(`✅ 修复的文件数: ${this.fixedFiles.length}`);
    console.log(`🔧 总修复数: ${this.totalFixes}`);

    if (this.fixedFiles.length > 0) {
      console.log("\n📝 修复详情:");
      this.fixedFiles.slice(0, 10).forEach(({ file, fixes }) => {
        console.log(`  - ${path.relative(process.cwd(), file)}: ${fixes} 处修复`);
      });
      if (this.fixedFiles.length > 10) {
        console.log(`  ... 还有 ${this.fixedFiles.length - 10} 个文件`);
      }
    }
  }
}

// 运行修复器
if (require.main === module) {
  const fixer = new PreciseAutoFixer();
  fixer.run().catch(console.error);
}

module.exports = PreciseAutoFixer;